@echo off
REM Windows 환경에서 React 프론트엔드 실행 스크립트

echo Setting up environment...
cd /d "%~dp0"

REM Node modules 설치 확인
if not exist node_modules (
    echo Installing Node packages...
    call npm install
) else (
    echo Node packages already installed. Updating...
    call npm update
)

REM React 개발 서버 실행
echo.
echo Starting React development server...
echo Application will be available at: http://localhost:3000
echo.
call npm start

pause
