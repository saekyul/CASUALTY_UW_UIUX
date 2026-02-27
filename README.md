# CASUALTY UW UIUX - LLM Data Integration PoC

PostgreSQL, Microsoft Outlook, 그리고 LLM (Claude/Gemini) APIs를 통합한 지능형 데이터 처리 및 이메일 관리 시스템입니다.

## 주요 기능

- 📧 **이메일 요약**: Microsoft Outlook의 이메일 자동 요약
- 🎯 **액션 추출**: 이메일과 데이터에서 할 일 항목 추출
- 🤖 **자동 응답 생성**: AI를 활용한 자동 응답 제안
- 🔄 **Text-to-SQL**: 자연어를 SQL로 변환하여 데이터 쿼리
- 📊 **대시보드**: 웹 기반 통합 대시보드

## 기술 스택

### Backend
- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL 12+
- **LLM APIs**:
  - Claude (Anthropic)
  - Gemini (Google)
- **External APIs**:
  - Microsoft Graph API (Outlook)

### Frontend
- **Framework**: React 18+
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **State Management**: Zustand

## 프로젝트 구조

```
CASUALTY_UW_UIUX/
├── backend/                 # Python FastAPI 백엔드
│   ├── app/
│   │   ├── main.py         # FastAPI 앱 진입점
│   │   ├── config.py       # 설정 관리
│   │   ├── database.py     # DB 연결
│   │   ├── models/         # ORM 및 Pydantic 모델
│   │   ├── api/            # REST API 라우트
│   │   ├── services/       # 비즈니스 로직
│   │   └── tests/          # 유닛 테스트
│   └── requirements.txt
├── frontend/               # React 프론트엔드
│   ├── src/
│   │   ├── components/     # React 컴포넌트
│   │   ├── pages/          # 페이지 컴포넌트
│   │   ├── services/       # API 클라이언트
│   │   └── hooks/          # Custom Hooks
│   └── package.json
└── docker-compose.yml      # PostgreSQL 컨테이너 설정
```

## 시작하기

### 필수 요구사항
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- API Keys (Claude, Gemini, Microsoft)

### 설치

1. **리포지토리 클론**
```bash
git clone <repository-url>
cd CASUALTY_UW_UIUX
```

2. **환경 설정**
```bash
# 루트 디렉토리
cp .env.example .env

# 백엔드
cp backend/.env.example backend/.env

# 프론트엔드
cp frontend/.env.example frontend/.env
```

3. **API Keys 설정**
`.env` 및 `backend/.env` 파일에서:
- `CLAUDE_API_KEY`: Anthropic Claude API 키
- `GEMINI_API_KEY`: Google Gemini API 키
- `OUTLOOK_CLIENT_ID`: Microsoft Azure 앱 ID
- `OUTLOOK_CLIENT_SECRET`: Microsoft Azure 클라이언트 시크릿
- `DATABASE_URL`: PostgreSQL 연결 문자열

### 개발 실행

#### 1. PostgreSQL 시작
```bash
docker-compose up -d postgres
```

#### 2. 백엔드 설정
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app/main.py
```

#### 3. 프론트엔드 설정
```bash
cd frontend
npm install
npm start
```

### 개발 서버 접근
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **프론트엔드**: http://localhost:3000

## API 엔드포인트

### 이메일 관리
- `GET /api/emails` - 이메일 목록 조회
- `POST /api/emails/{id}/summarize` - 이메일 요약 생성
- `GET /api/emails/{id}/actions` - 추출된 액션 조회

### 데이터 처리
- `GET /api/data` - PostgreSQL 데이터 조회
- `POST /api/data/query` - Text-to-SQL 쿼리

### 자동 응답
- `GET /api/responses` - 제안된 응답 조회
- `POST /api/responses/{id}/send` - 응답 전송

### 시스템
- `GET /api/status` - 시스템 상태 확인

## 환경 변수

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/casualty_db
CLAUDE_API_KEY=sk-...
GEMINI_API_KEY=...
OUTLOOK_CLIENT_ID=...
OUTLOOK_CLIENT_SECRET=...
OUTLOOK_TENANT_ID=...
PREFERRED_LLM=claude
DEBUG=true
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_LLM_MODEL=claude
```

## 테스트

### 백엔드 테스트
```bash
cd backend
pytest tests/ -v
```

### 프론트엔드 테스트
```bash
cd frontend
npm test
```

## 배포

Docker를 사용한 프로덕션 배포:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## 라이선스

MIT License

## 연락처

문의사항은 [프로젝트 레포지토리](.)에 이슈를 등록해주세요.
