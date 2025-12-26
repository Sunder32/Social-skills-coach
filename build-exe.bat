@echo off
echo ========================================
echo Building Social Skills Coach EXE
echo ========================================

echo.
echo Step 1: Building Backend EXE with PyInstaller...
echo ========================================

cd Backend

REM Activate venv
call venv\Scripts\activate.bat

REM Install PyInstaller if not present
pip install pyinstaller --quiet

REM Build backend
echo Building backend.exe...
pyinstaller --clean --noconfirm backend.spec

if errorlevel 1 (
    echo ERROR: Backend build failed!
    pause
    exit /b 1
)

echo Backend built successfully!

REM Copy production.env to dist folder
copy production.env dist\backend\production.env

REM Create data directory
mkdir dist\backend\data 2>nul

cd ..

echo.
echo Step 2: Building Frontend and Electron...
echo ========================================

cd Frontend

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing npm dependencies...
    npm install
)

REM Build React app
echo Building React app...
npm run build

if errorlevel 1 (
    echo ERROR: React build failed!
    pause
    exit /b 1
)

REM Build Electron installer
echo Building Electron installer...
npm run dist:win

if errorlevel 1 (
    echo ERROR: Electron build failed!
    pause
    exit /b 1
)

cd ..

echo.
echo ========================================
echo BUILD COMPLETE!
echo ========================================
echo.
echo Installer location: Frontend\dist\
echo.
pause
