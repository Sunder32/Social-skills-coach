"""
Сервис пользователей - управление пользователями и аутентификация
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import secrets

from app.models.user import User
from app.models.progress import Progress
from app.schemas.user import UserCreate, UserProfileUpdate, UserProgress
from app.config import settings
from app.services.email_service import email_service

ph = PasswordHasher()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login", auto_error=False)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30


def hash_password(password: str) -> str:
    """Хеширование пароля с использованием Argon2"""
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля по хешу"""
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False


class UserService:
    """Сервис для работы с пользователями"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, user_data: UserCreate) -> User:
        """Создание нового пользователя"""
        hashed = hash_password(user_data.password)
        
        verification_code = self._generate_verification_code()
        
        user = User(
            email=user_data.email,
            hashed_password=hashed,
            name=user_data.name,
            is_verified=False,
            verification_code=verification_code,
            verification_code_expires=datetime.utcnow() + timedelta(hours=24)
        )
        
        self.db.add(user)
        await self.db.flush()
        
        progress = Progress(user_id=user.id)
        self.db.add(progress)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        email_service.send_verification_email(
            to_email=user.email,
            verification_code=verification_code,
            user_name=user.name
        )
        
        return user
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Аутентификация пользователя по email и паролю"""
        user = await self.get_by_email(email)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email не подтверждён. Проверьте почту и введите код подтверждения."
            )
        
        user.last_login = datetime.utcnow()
        await self.db.commit()
        
        return user
    
    def create_access_token(self, user_id: int) -> str:
        """Создание JWT токена доступа"""
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        
        to_encode = {
            "sub": str(user_id),
            "exp": expire
        }
        
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
        """Получение ID текущего пользователя из токена"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
        if settings.APP_ENV == "development" and not token:
            return 1
        
        if not token:
            raise credentials_exception
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            
            if user_id is None:
                raise credentials_exception
            
            return int(user_id)
        
        except JWTError:
            raise credentials_exception
    
    async def update_profile(self, user_id: int, profile_data: UserProfileUpdate) -> User:
        """Обновление профиля пользователя"""
        user = await self.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_progress(self, user_id: int) -> UserProgress:
        """Получение статистики прогресса пользователя"""
        result = await self.db.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        progress = result.scalar_one_or_none()
        
        if not progress:
            return UserProgress()
        
        return UserProgress(
            total_conversations=progress.total_conversations,
            total_analyses=progress.total_analyses,
            total_exercises=progress.total_exercises,
            current_streak=progress.current_streak,
            longest_streak=progress.longest_streak,
            skill_improvements=progress.skill_levels or {},
            achievements=progress.achievements or []
        )
    
    async def delete(self, user_id: int) -> None:
        """Удаление аккаунта пользователя"""
        user = await self.get_by_id(user_id)
        
        if user:
            await self.db.delete(user)
            await self.db.commit()
    
    def _generate_verification_code(self) -> str:
        """Генерация 6-значного кода подтверждения"""
        import random
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    async def verify_email(self, email: str, code: str) -> bool:
        """
        Подтверждение email по коду
        
        Args:
            email: Email пользователя
            code: Код подтверждения
        
        Returns:
            True если email успешно подтверждён
        """
        user = await self.get_by_email(email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email уже подтверждён"
            )
        
        if not user.verification_code or not user.verification_code_expires:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Код подтверждения не найден"
            )
        
        if user.verification_code_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Срок действия кода истёк. Запросите новый код."
            )
        
        if user.verification_code != code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный код подтверждения"
            )
        
        user.is_verified = True
        user.verification_code = None
        user.verification_code_expires = None
        
        await self.db.commit()
        
        return True
    
    async def resend_verification_code(self, email: str) -> bool:
        """
        Повторная отправка кода подтверждения
        
        Args:
            email: Email пользователя
        
        Returns:
            True если код отправлен успешно
        """
        user = await self.get_by_email(email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email уже подтверждён"
            )
        
        verification_code = self._generate_verification_code()
        
        user.verification_code = verification_code
        user.verification_code_expires = datetime.utcnow() + timedelta(hours=24)
        
        await self.db.commit()
        
        return email_service.send_verification_email(
            to_email=user.email,
            verification_code=verification_code,
            user_name=user.name
        )
    
    async def request_password_reset(self, email: str) -> bool:
        """
        Запрос на восстановление пароля
        Генерирует токен и отправляет письмо на email
        
        Args:
            email: Email пользователя
        
        Returns:
            True если письмо отправлено успешно
        """
        user = await self.get_by_email(email)
        
        if not user:
            return True
        
        reset_token = secrets.token_urlsafe(32)
        
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        
        await self.db.commit()
        
        return email_service.send_password_reset_email(
            to_email=user.email,
            reset_token=reset_token,
            user_name=user.name
        )
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """
        Сброс пароля по токену
        
        Args:
            token: Токен для сброса пароля
            new_password: Новый пароль
        
        Returns:
            True если пароль успешно изменён
        """
        result = await self.db.execute(
            select(User).where(User.reset_token == token)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный токен восстановления"
            )
        
        if not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Срок действия токена истёк. Запросите новую ссылку для восстановления пароля."
            )
        
        user.hashed_password = hash_password(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        
        await self.db.commit()
        
        email_service.send_password_changed_notification(
            to_email=user.email,
            user_name=user.name
        )
        
        return True
    
    async def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        Изменение пароля (с проверкой старого пароля)
        
        Args:
            user_id: ID пользователя
            old_password: Старый пароль
            new_password: Новый пароль
        
        Returns:
            True если пароль успешно изменён
        """
        user = await self.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        if not verify_password(old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный текущий пароль"
            )
        
        user.hashed_password = hash_password(new_password)
        await self.db.commit()
        
        email_service.send_password_changed_notification(
            to_email=user.email,
            user_name=user.name
        )
        
        return True
