@echo off
echo Starting Backend Server...

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

REM Load environment variables if .env exists
if exist ".env" (
    echo Loading environment variables from .env
)

REM Start the server
echo Starting uvicorn server...
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
