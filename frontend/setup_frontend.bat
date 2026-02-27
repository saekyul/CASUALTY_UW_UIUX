@echo off
REM 프론트엔드 초기 설정 스크립트 (Windows)

echo.
echo ========================================
echo CASUALTY LLM PoC - Frontend Setup
echo ========================================
echo.

cd /d "%~dp0"

REM Node 버전 확인
echo Checking Node.js installation...
node --version
if errorlevel 1 (
    echo Error: Node.js not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)

echo npm version:
npm --version

REM package.json 확인
if not exist package.json (
    echo Error: package.json not found
    echo Please ensure you are in the frontend directory
    pause
    exit /b 1
)

REM node_modules 설치
echo.
echo Installing Node packages...
call npm install
if errorlevel 1 (
    echo Error: Failed to install npm packages
    pause
    exit /b 1
)

REM .env 파일 생성
if not exist .env (
    echo.
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo Created .env file with default settings.
    echo You can customize it if needed.
) else (
    echo .env file already exists
)

REM 설정 확인
echo.
echo ========================================
echo Setup completed!
echo ========================================
echo.
echo Next steps:
echo 1. Backend must be running on http://localhost:8000
echo 2. Run: run_frontend.bat
echo.
echo Frontend will start at: http://localhost:3000
echo.

pause
