"""
Social Skills Coach - Backend Application
Main entry point for FastAPI server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

# Add AI module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'AI'))

from app.config import settings
from app.database import engine, Base
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME}...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created")
    print(f"📡 API running at http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")
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
