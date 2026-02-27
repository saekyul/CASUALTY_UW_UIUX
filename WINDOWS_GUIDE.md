# Windows 환경 설정 가이드

이 가이드는 Windows 환경에서 CASUALTY LLM PoC를 설정하고 실행하는 방법을 설명합니다.

## ⚙️ 사전 요구사항

### 1. Python 설치
- **Python 3.10 이상** 필요
- [python.org](https://www.python.org/downloads/)에서 다운로드
- **설치 시 중요**: "Add Python to PATH" 체크박스 선택

설치 확인:
```bash
python --version
```

### 2. Node.js 설치
- **Node.js 18 이상** 필요
- [nodejs.org](https://nodejs.org/)에서 LTS 버전 다운로드
- npm도 함께 설치됨

설치 확인:
```bash
node --version
npm --version
```

### 3. Git 설치 (선택사항이지만 권장)
- [git-scm.com](https://git-scm.com/download/win)에서 다운로드

## 🚀 빠른 시작 (자동화 스크립트 이용)

### Step 1: 프로젝트 디렉토리에 진입

```bash
# 예: C:\Users\사용자명\Desktop\CASUALTY_UW_UIUX
cd path\to\CASUALTY_UW_UIUX
```

### Step 2: 백엔드 설정 실행

**backend** 폴더로 이동:
```bash
cd backend
```

**setup_backend.bat** 실행:
```bash
setup_backend.bat
```

이 스크립트가 자동으로:
- ✅ Python 설치 확인
- ✅ 가상환경 생성 (venv)
- ✅ 필요한 패키지 설치
- ✅ .env 파일 생성

### Step 3: API 키 설정

**backend/.env** 파일을 텍스트 편집기로 열기:
```
DATABASE_URL=postgresql://casualty_user:casualty_password@localhost:5432/casualty_db

CLAUDE_API_KEY=sk-ant-your-key-here
GEMINI_API_KEY=your-gemini-key-here
OUTLOOK_CLIENT_ID=your-client-id
OUTLOOK_CLIENT_SECRET=your-client-secret
OUTLOOK_TENANT_ID=your-tenant-id

PREFERRED_LLM=claude
DEBUG=true
ENV=development
```

**필요한 API 키 획득:**
1. **Claude API Key**: https://console.anthropic.com/account/keys
2. **Gemini API Key**: https://makersuite.google.com/app/apikey
3. **Outlook 정보**: Azure Portal에서 앱 등록

### Step 4: 프론트엔드 설정 실행

**다른 터미널** 열기:
```bash
cd path\to\CASUALTY_UW_UIUX\frontend
setup_frontend.bat
```

## ▶️ 실행하기

### 방법 1: 자동 실행 스크립트 (권장)

**백엔드 실행** (터미널 1):
```bash
cd backend
run_backend.bat
```

**프론트엔드 실행** (터미널 2):
```bash
cd frontend
run_frontend.bat
```

### 방법 2: 수동 실행

**백엔드 실행** (터미널 1):
```bash
cd backend
venv\Scripts\activate.bat
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**프론트엔드 실행** (터미널 2):
```bash
cd frontend
npm start
```

## ✅ 실행 확인

모든 것이 정상 작동하면:

- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

## 🐛 트러블슈팅

### 1. "ModuleNotFoundError: No module named 'app'"

**해결책:**
```bash
# 올바른 방법으로 실행
python -m uvicorn app.main:app --reload

# 또는 backend 폴더에서
run_backend.bat
```

### 2. "No module named 'sqlalchemy'" 또는 기타 패키지 누락

**해결책:**
```bash
# 가상환경이 활성화되었는지 확인
venv\Scripts\activate.bat

# 패키지 재설치
pip install -r requirements.txt
```

### 3. "PyJWT==2.8.1 not found"

**해결책:**
- ✅ 이미 수정됨! requirements.txt가 업데이트되었습니다.
- 다시 설치:
```bash
pip install --upgrade -r requirements.txt
```

### 4. "Port 8000 is already in use"

**해결책:**
```bash
# 다른 포트 사용
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

또는 기존 프로세스 종료:
```bash
# Task Manager에서 python.exe 프로세스 종료
taskkill /IM python.exe /F
```

### 5. "Port 3000 is already in use"

**해결책:**
```bash
# 다른 포트 사용
set PORT=3001 && npm start

# 또는 기존 프로세스 종료
taskkill /IM node.exe /F
```

### 6. Spyder IDE에서 실행 문제

**권장 방법:**
- ✅ PowerShell 또는 Command Prompt에서 위의 배치 파일 사용
- ✅ Spyder IDE의 내장 터미널은 사용하지 않음
- Spyder IDE는 코드 편집용으로 사용

## 📁 디렉토리 구조 확인

다음과 같은 구조여야 합니다:

```
CASUALTY_UW_UIUX/
├── backend/
│   ├── venv/              (setup 후 생성)
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   ├── api/
│   │   ├── services/
│   │   └── tests/
│   ├── .env               (setup 후 생성)
│   ├── requirements.txt
│   ├── setup_backend.bat
│   └── run_backend.bat
├── frontend/
│   ├── node_modules/      (setup 후 생성)
│   ├── src/
│   ├── public/
│   ├── .env               (setup 후 생성)
│   ├── package.json
│   ├── setup_frontend.bat
│   └── run_frontend.bat
└── docker-compose.yml
```

## 🔧 고급: 수동 설정 (Spyder IDE 사용 시)

### 백엔드 설정 스크린샷 가이드

1. **Spyder IDE 열기**
2. **Tools → PYTHONPATH manager** 메뉴에서:
   - `C:\Users\사용자명\Desktop\CASUALTY_UW_UIUX\backend` 추가

3. **콘솔에서:**
```python
import sys
sys.path.insert(0, r'C:\Users\사용자명\Desktop\CASUALTY_UW_UIUX\backend')

from app.main import app
import uvicorn

uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 💡 팁

### 터미널 여러 개 열기
- **PowerShell**: Ctrl+Shift+T (새 탭)
- **Command Prompt**: 시작 메뉴에서 "cmd" 여러 번 실행

### 로그 확인
- 백엔드는 `http://localhost:8000/docs`에서 API 테스트 가능
- 프론트엔드는 브라우저 F12에서 Console 탭 확인

### 변경 사항 자동 재로드
- 백엔드: `--reload` 플래그로 자동 재시작
- 프론트엔드: npm은 자동으로 파일 감시

## 📞 추가 지원

문제가 해결되지 않으면:
1. 콘솔 에러 메시지 전체 복사
2. `python --version` 출력 확인
3. `pip list` 명령으로 설치된 패키지 확인
4. GitHub Issues에 질문하기

---

**이 가이드로 Windows 환경에서 성공적으로 프로젝트를 실행할 수 있습니다!** 🎉
