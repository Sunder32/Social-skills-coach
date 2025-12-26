@echo off
echo ========================================
echo Starting Backend Server...
echo ========================================

REM Stop old Backend processes
echo Stopping old Backend processes...
for /f "tokens=2" %%a in ('tasklist ^| findstr "python.exe"') do (
    netstat -ano ^| findstr ":8001" ^| findstr "%%a" >nul 2>&1
    if not errorlevel 1 (
        echo Stopping process %%a
        taskkill /F /PID %%a >nul 2>&1
    )
)

cd Backend

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Load environment variables
if exist ".env" (
    echo Loading environment variables from .env
) else (
    echo WARNING: .env file not found!
)

REM Start the server
echo ========================================
echo Starting uvicorn server on port 8001...
echo ========================================
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
