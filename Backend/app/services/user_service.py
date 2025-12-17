"""
User service - handles user operations and authentication
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

from app.models.user import User
from app.models.progress import Progress
from app.schemas.user import UserCreate, UserProfileUpdate, UserProgress
from app.config import settings

# Password hashing with Argon2
ph = PasswordHasher()

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login", auto_error=False)

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30


def hash_password(password: str) -> str:
    """Hash a password using Argon2"""
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False


class UserService:
    """User service for handling user operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, user_data: UserCreate) -> User:
        """Create a new user"""
        hashed = hash_password(user_data.password)
        
        user = User(
            email=user_data.email,
            hashed_password=hashed,
            name=user_data.name
        )
        
        self.db.add(user)
        await self.db.flush()
        
        # Create progress record
        progress = Progress(user_id=user.id)
        self.db.add(progress)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await self.get_by_email(email)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        await self.db.commit()
        
        return user
    
    def create_access_token(self, user_id: int) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        
        to_encode = {
            "sub": str(user_id),
            "exp": expire
        }
        
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
        """Dependency to get current user ID from token"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
        # In development mode, allow anonymous access with default user
        if settings.APP_ENV == "development" and not token:
            return 1  # Default development user ID
        
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
        """Update user profile"""
        user = await self.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields
        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_progress(self, user_id: int) -> UserProgress:
        """Get user progress statistics"""
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
        """Delete user account"""
        user = await self.get_by_id(user_id)
        
        if user:
            await self.db.delete(user)
            await self.db.commit()
