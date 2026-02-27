# CASUALTY UW UIUX - LLM Data Integration PoC 설정 가이드

## 📋 필수 요구사항

### 시스템 요구사항
- **OS**: Linux, macOS, Windows (WSL2)
- **Docker & Docker Compose**: 최신 버전
- **Git**: 2.25+
- 네트워크 연결 (외부 API 호출용)

### API 키
다음 서비스의 API 키가 필요합니다:
1. **Claude API** (Anthropic)
   - 획득: https://console.anthropic.com
2. **Gemini API** (Google)
   - 획득: https://makersuite.google.com/app/apikey
3. **Microsoft Azure** (Outlook 연동용)
   - Azure Portal에서 애플리케이션 등록
   - 필요한 정보: Client ID, Client Secret, Tenant ID

## 🚀 빠른 시작

### 1단계: 저장소 클론 및 디렉토리 이동

```bash
git clone <repository-url>
cd CASUALTY_UW_UIUX
```

### 2단계: 환경 변수 설정

```bash
# 루트 디렉토리에 .env 파일 생성
cp .env.example .env

# 백엔드 환경 설정
cp backend/.env.example backend/.env

# 프론트엔드 환경 설정
cp frontend/.env.example frontend/.env
```

### 3단계: .env 파일 수정

#### 루트 `.env`
```
POSTGRES_USER=casualty_user
POSTGRES_PASSWORD=casualty_password
POSTGRES_DB=casualty_db
POSTGRES_PORT=5432

PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=admin
PGADMIN_PORT=5050

BACKEND_URL=http://localhost:8000
BACKEND_PORT=8000

FRONTEND_URL=http://localhost:3000
FRONTEND_PORT=3000
```

#### 백엔드 `backend/.env`
```
DATABASE_URL=postgresql://casualty_user:casualty_password@localhost:5432/casualty_db

# Claude API (https://console.anthropic.com에서 획득)
CLAUDE_API_KEY=sk-ant-...

# Gemini API (https://makersuite.google.com/app/apikey에서 획득)
GEMINI_API_KEY=...

# Microsoft Outlook (Azure Portal에서 설정)
OUTLOOK_CLIENT_ID=...
OUTLOOK_CLIENT_SECRET=...
OUTLOOK_TENANT_ID=...

PREFERRED_LLM=claude
DEBUG=true
ENV=development

CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

#### 프론트엔드 `frontend/.env`
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_LLM_MODEL=claude
REACT_APP_DEBUG=true
```

### 4단계: Docker Compose로 실행

#### 개발 환경
```bash
# PostgreSQL 시작
docker-compose up -d postgres pgadmin

# 잠깐 기다린 후 다른 터미널에서:

# 백엔드 시작
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app/main.py

# 또 다른 터미널에서:

# 프론트엔드 시작
cd frontend
npm install
npm start
```

#### 프로덕션 환경
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📝 설정 후 확인

### 서비스 접근
- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **PgAdmin**: http://localhost:5050

### 초기 데이터베이스 설정 (필요시)
```bash
# 백엔드 디렉토리에서
cd backend
python -c "from app.database import engine; from app.models.database import Base; Base.metadata.create_all(bind=engine)"
```

## 🧪 테스트 실행

### 백엔드 테스트
```bash
cd backend
pip install pytest pytest-asyncio
pytest tests/ -v
```

### 테스트 커버리지 확인
```bash
cd backend
pytest tests/ --cov=app --cov-report=html
# htmlcov/index.html에서 확인
```

## 🔧 주요 API 엔드포인트

### 시스템
- `GET /health` - 헬스 체크
- `GET /api/status` - 시스템 상태 확인

### 이메일
- `GET /api/emails` - 이메일 목록 조회
- `GET /api/emails/{id}` - 이메일 상세 조회
- `POST /api/emails/{id}/summarize` - 이메일 요약 생성
- `POST /api/emails/{id}/extract-actions` - 액션 아이템 추출
- `GET /api/emails/{id}/actions` - 추출된 액션 조회

### 데이터 쿼리
- `POST /api/data/query` - 자연어 쿼리 실행
- `POST /api/data/convert-to-sql` - 자연어를 SQL로 변환
- `GET /api/data/schema` - 데이터베이스 스키마 조회

### 작업 및 응답
- `GET /api/actions` - 작업 아이템 목록
- `GET /api/actions/high-priority` - 우선순위 높은 작업
- `PATCH /api/actions/{id}` - 작업 상태 업데이트
- `GET /api/responses` - 자동 응답 제안 목록
- `POST /api/responses/{id}/approve` - 응답 승인 및 전송

## 📚 프로젝트 구조

```
CASUALTY_UW_UIUX/
├── backend/                    # Python FastAPI 백엔드
│   ├── app/
│   │   ├── main.py            # 메인 애플리케이션
│   │   ├── config.py          # 설정 관리
│   │   ├── database.py        # DB 연결
│   │   ├── models/            # ORM 모델
│   │   ├── api/               # API 라우트
│   │   ├── services/          # 비즈니스 로직
│   │   └── tests/             # 테스트
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pytest.ini
├── frontend/                   # React 프론트엔드
│   ├── src/
│   │   ├── pages/            # 페이지 컴포넌트
│   │   ├── components/       # 재사용 컴포넌트
│   │   ├── services/         # API 클라이언트
│   │   └── hooks/            # Custom hooks
│   ├── package.json
│   ├── Dockerfile
│   └── public/
├── docker-compose.yml         # 개발용 Docker Compose
├── docker-compose.prod.yml    # 프로덕션용 Docker Compose
├── nginx.conf                 # Nginx 설정
└── README.md
```

## 🐛 트러블슈팅

### PostgreSQL 연결 실패
```bash
# 데이터베이스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs postgres

# 포트 충돌 확인 (이미 5432 사용 중인 경우)
netstat -tulpn | grep 5432
```

### API 키 오류
- `.env` 파일에서 API 키 값이 올바른지 확인
- API 키에 공백이나 개행이 없는지 확인
- 각 서비스의 공식 문서에서 올바른 키 형식 확인

### Frontend 빌드 오류
```bash
cd frontend
rm -rf node_modules
npm install
npm start
```

### 포트 이미 사용 중
```bash
# 기존 프로세스 중단
docker-compose down

# 다른 포트 사용 (선택사항)
# BACKEND_PORT=8001 docker-compose up
```

## 📖 추가 문서

- [API 문서](http://localhost:8000/docs) - Swagger UI
- [README.md](./README.md) - 프로젝트 개요
- 각 서비스 공식 문서:
  - [FastAPI](https://fastapi.tiangolo.com)
  - [React](https://react.dev)
  - [SQLAlchemy](https://docs.sqlalchemy.org)

## 🤝 기여하기

1. 새로운 브랜치 생성: `git checkout -b feature/your-feature`
2. 변경사항 커밋: `git commit -am 'Add some feature'`
3. 브랜치에 푸시: `git push origin feature/your-feature`
4. Pull Request 생성

## 📄 라이선스

MIT License

## 📞 지원

문제가 발생하면 [GitHub Issues](https://github.com/saekyul/CASUALTY_UW_UIUX/issues)에서 이슈를 작성해주세요.
