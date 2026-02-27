@echo off
REM Windows 환경에서 FastAPI 백엔드 실행 스크립트

echo Setting up environment...
cd /d "%~dp0"

REM 가상환경 활성화
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Error: Virtual environment not found at venv\Scripts\activate.bat
    echo Please create virtual environment first: python -m venv venv
    pause
    exit /b 1
)

REM 필요한 패키지 설치 확인
echo Installing/checking required packages...
pip install -q -r requirements.txt

REM FastAPI 서버 실행
echo.
echo Starting FastAPI server...
echo Server will be available at: http://localhost:8000
echo API Documentation at: http://localhost:8000/docs
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
