"""
Users API endpoints
Handles user registration, authentication, and profile management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, UserProfileUpdate,
    Token, UserProgress, PasswordResetRequest, PasswordReset, MessageResponse
)
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Регистрация нового пользователя
    
    - **email**: Email адрес пользователя
    - **password**: Пароль (минимум 8 символов)
    - **name**: Имя пользователя
    """
    service = UserService(db)
    
    existing_user = await service.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    user = await service.create(user_data)
    return user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Аутентификация пользователя и получение JWT токена
    
    - **email**: Email пользователя
    - **password**: Пароль пользователя
    """
    service = UserService(db)
    
    user = await service.authenticate(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = service.create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """Получение профиля текущего пользователя"""
    service = UserService(db)
    user = await service.get_by_id(current_user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """
    Обновление профиля пользователя
    
    - **name**: Имя пользователя
    - **occupation**: Профессия/сфера деятельности
    - **goals**: Цели коммуникации
    - **problem_areas**: Области для улучшения
    - **skill_level**: Самооценка навыков (1-10)
    """
    service = UserService(db)
    user = await service.update_profile(current_user_id, profile_data)
    return user


@router.get("/progress", response_model=UserProgress)
async def get_progress(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """Получение статистики прогресса обучения"""
    service = UserService(db)
    progress = await service.get_progress(current_user_id)
    return progress


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """Удаление аккаунта пользователя и всех связанных данных"""
    service = UserService(db)
    await service.delete(current_user_id)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Запрос на восстановление пароля
    
    Отправляет письмо с инструкциями на указанный email
    
    - **email**: Email адрес пользователя
    """
    service = UserService(db)
    
    success = await service.request_password_reset(request.email)
    
    # Всегда возвращаем успех (в целях безопасности)
    return {
        "message": "Если указанный email зарегистрирован, на него будет отправлено письмо с инструкциями по восстановлению пароля."
    }


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_db)
):
    """
    Сброс пароля по токену из email
    
    - **token**: Токен из письма для восстановления
    - **new_password**: Новый пароль (минимум 8 символов)
    """
    service = UserService(db)
    
    await service.reset_password(reset_data.token, reset_data.new_password)
    
    return {
        "message": "Пароль успешно изменён. Теперь вы можете войти с новым паролем."
    }


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    old_password: str,
    new_password: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(UserService.get_current_user_id)
):
    """
    Изменение пароля (требует аутентификации)
    
    - **old_password**: Текущий пароль
    - **new_password**: Новый пароль (минимум 8 символов)
    """
    service = UserService(db)
    
    await service.change_password(current_user_id, old_password, new_password)
    
    return {
        "message": "Пароль успешно изменён."
    }
