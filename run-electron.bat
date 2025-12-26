@echo off
echo ========================================
echo Starting Electron App...
echo ========================================

REM Stop old Electron and Frontend processes
echo Stopping old Electron processes...
taskkill /F /IM electron.exe >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

cd Frontend

REM Check dependencies
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

REM Start Electron app
echo ========================================
echo Launching Electron Desktop App...
echo ========================================
npm run electron:dev
