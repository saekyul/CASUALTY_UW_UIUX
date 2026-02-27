@echo off
REM 백엔드 초기 설정 스크립트 (Windows)

echo.
echo ========================================
echo CASUALTY LLM PoC - Backend Setup
echo ========================================
echo.

cd /d "%~dp0"

REM Python 버전 확인
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo Error: Python not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org
    pause
    exit /b 1
)

REM 가상환경 생성
if not exist venv (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists
)

REM 가상환경 활성화
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM pip 업그레이드
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM 패키지 설치
echo.
echo Installing required packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install packages
    pause
    exit /b 1
)

REM .env 파일 생성
if not exist .env (
    echo.
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo WARNING: Please edit .env file with your API keys:
    echo   - CLAUDE_API_KEY
    echo   - GEMINI_API_KEY
    echo   - OUTLOOK_CLIENT_ID
    echo   - OUTLOOK_CLIENT_SECRET
    echo   - OUTLOOK_TENANT_ID
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
echo 1. Edit .env file with your API keys
echo 2. Run: run_backend.bat
echo.
echo Backend will start at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.

pause
