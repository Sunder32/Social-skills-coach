@echo off
echo ========================================
echo  Social Skills Coach - Setup Script
echo ========================================
echo.

:: Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

:: Check Node.js
echo Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Setting up Backend
echo ========================================
cd Backend
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Installing dependencies...
pip install -r requirements.txt
cd ..

echo.
echo ========================================
echo  Setting up AI Module
echo ========================================
cd AI
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Installing dependencies...
pip install -r requirements.txt
cd ..

echo.
echo ========================================
echo  Setting up Frontend
echo ========================================
cd Frontend
echo Installing npm dependencies...
call npm install
cd ..

echo.
echo ========================================
echo  Creating .env file
echo ========================================
if not exist ".env" (
    copy .env.example .env
    echo Created .env file from template
    echo Please edit .env with your configuration
) else (
    echo .env file already exists
)

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo To start the application:
echo   1. Start Backend:  run-backend.bat
echo   2. Start AI:       run-ai.bat
echo   3. Start Frontend: run-frontend.bat
echo.
echo Or use Docker:
echo   docker-compose up
echo.
pause
