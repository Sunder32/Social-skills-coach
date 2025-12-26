"""
Social Skills Coach - Backend Application
Main entry point for FastAPI server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.database import engine, Base
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"[INFO] Starting {settings.APP_NAME}...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("[INFO] Database tables created")
    
    # Create default user for development
    if settings.APP_ENV == "development":
        from app.database import AsyncSessionLocal
        from app.models.user import User
        from app.models.progress import Progress
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.id == 1))
            user = result.scalar_one_or_none()
            
            if not user:
                from app.services.user_service import hash_password
                
                user = User(
                    id=1,
                    email="dev@localhost",
                    hashed_password=hash_password("dev123"),
                    name="Developer"
                )
                session.add(user)
                await session.flush()
                
                progress = Progress(user_id=user.id)
                session.add(progress)
                
                await session.commit()
                print("[INFO] Default development user created")
    
    print(f"[INFO] API running at http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}")
    
    yield
    
    # Shutdown
    print("[INFO] Shutting down...")
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered application for developing communication skills",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS for Electron app
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "app://.",  # Electron
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG
    )
