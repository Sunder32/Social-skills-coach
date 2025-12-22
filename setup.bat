@echo off
echo ========================================
echo  Social Skills Coach - Setup Script
echo ========================================
echo.

:: Set Python path - prefer Python 3.12 or 3.11
set "PYTHON_PATH="
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
) else if exist "C:\Python312\python.exe" (
    set "PYTHON_PATH=C:\Python312\python.exe"
) else if exist "C:\Python311\python.exe" (
    set "PYTHON_PATH=C:\Python311\python.exe"
)

:: Check Python
echo Checking Python installation...
if defined PYTHON_PATH (
    echo Found Python at: %PYTHON_PATH%
    "%PYTHON_PATH%" --version
) else (
    echo WARNING: Python 3.11/3.12 not found in standard locations
    echo Falling back to system Python...
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python is not installed or not in PATH
        echo Please install Python 3.11 or 3.12 from https://python.org
        pause
        exit /b 1
    )
    set "PYTHON_PATH=python"
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
    "%PYTHON_PATH%" -m venv venv
)
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Upgrading pip...
python -m pip install --upgrade pip
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
    echo.
    echo IMPORTANT: Edit .env and set AI_API_URL and AI_API_KEY
    echo to connect to your DASA AI server!
) else (
    echo .env file already exists
)

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo IMPORTANT: This application requires DASA AI Server!
echo Make sure to:
echo   1. Set up DASA AI Server (separate project)
echo   2. Configure AI_API_URL and AI_API_KEY in .env
echo.
echo To start the application:
echo   1. Start Backend:  run-backend.bat
echo   2. Start Frontend: run-frontend.bat
echo.
echo Or use Docker:
echo   docker-compose up
echo.
pause
