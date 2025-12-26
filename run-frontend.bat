@echo off
echo ========================================
echo Starting Frontend Development Server...
echo ========================================

REM Stop old Frontend processes on port 3000
echo Stopping old Frontend processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
    echo Stopping process %%a
    taskkill /F /PID %%a >nul 2>&1
)

cd Frontend

REM Check dependencies
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

REM Start the server
echo ========================================
echo Starting React Dev Server on port 3000...
echo ========================================
npm start
