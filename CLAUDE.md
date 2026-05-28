# CLAUDE.md — Personal Work Agent

## 프로젝트 개요

회사 업무 자동화 AI 개인 비서 에이전트.
이메일 요약 / 회의록 정리 / 할일 추출 / 사내 문서 Q&A를 하나의 에이전트가 처리.

**현재 Phase**: Phase 2 — FastAPI 엔드포인트 완료 / Phase 3 준비 중
> Phase 바뀔 때마다 이 줄 업데이트

---

## 기술 스택

| 레이어 | 기술 |
|--------|------|
| Language | Python 3.11 + Poetry |
| Agent | LangGraph 0.2.x + LangChain 0.3.x |
| LLM | OpenAI GPT-4o-mini (`LLM_MODEL` env로 교체 가능) |
| VectorDB | Qdrant (로컬 Docker → Qdrant Cloud 전환 가능) |
| API | FastAPI + uvicorn |
| Scheduler | Apache Airflow (에이전트 파이프라인 스케줄링) |
| Automation | n8n self-hosted (Phase 4) |
| Container | Docker + docker-compose |
| Dev Server | Oracle VirtualBox (RedHAT 9.X)|
| Message Queue | Kafka + Kafka Connect (Phase 5) |

---

## 폴더 구조

```
personal-work-agent/
├── CLAUDE.md
├── pyproject.toml
├── .env                       ← git 제외
├── .env.example               ← git 포함
├── docker-compose.yml
├── docker-compose.kafka.yml   ← Phase 5에서 활성화
├── dags/                      ← Airflow DAG 정의
│   ├── daily_email_summary.py ← 매일 오전 이메일 요약 트리거
│   └── doc_sync_pipeline.py   ← 문서 벡터 동기화
├── app/
│   ├── main.py                ← FastAPI 진입점
│   ├── api/
│   │   ├── routes/
│   │   │   ├── documents.py   ← POST /api/v1/upload-doc
│   │   │   └── agent.py       ← POST /api/v1/ask
│   │   └── deps.py            ← LLM, VectorStore 의존성 주입
│   ├── agents/
│   │   ├── graph.py           ← LangGraph 메인 그래프
│   │   ├── nodes/
│   │   │   ├── retriever.py
│   │   │   ├── summarizer.py
│   │   │   ├── task_extractor.py
│   │   │   └── router.py
│   │   └── tools/
│   │       ├── calendar.py
│   │       └── email.py
│   ├── rag/
│   │   ├── vectorstore.py     ← Qdrant 클라이언트 추상화
│   │   ├── embeddings.py
│   │   └── loader.py          ← PDF, DOCX, TXT 로더
│   └── core/
│       ├── config.py          ← pydantic Settings
│       └── logger.py
└── tests/
    ├── unit/
    └── integration/
```

---

## 환경변수

```env
# LLM
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=work-agent
# 운영 전환 시 아래 두 줄 활성화
# QDRANT_URL=https://xxx.qdrant.io
# QDRANT_API_KEY=

# Airflow
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:////opt/airflow/airflow.db

# Google Tools (Phase 3)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Kafka (Phase 5)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# App
APP_ENV=development
LOG_LEVEL=INFO
```

---

## 코딩 규칙

- 모든 I/O는 `async def` 사용
- 타입힌트 필수, 파일 상단에 `from __future__ import annotations`
- Pydantic v2로 입출력 검증
- 엔드포인트 prefix는 `/api/v1`
- LangGraph 노드 시그니처 고정: `async def node_name(state: AgentState) -> AgentState`
- `AgentState`는 `TypedDict`, `app/agents/graph.py` 상단에 정의
- Qdrant 컬렉션명은 `QDRANT_COLLECTION` env에서 읽어올 것 (하드코딩 금지)
- Airflow DAG은 `dags/` 폴더에만 작성, 비즈니스 로직은 `app/` 안에 두고 DAG에서 호출

---

## 자주 쓰는 명령어

```bash
# 의존성 설치
poetry install

# 개발 서버 실행
poetry run uvicorn app.main:app --reload --port 8000

# 전체 서비스 실행 (FastAPI + Qdrant + Airflow)
docker-compose up -d

# 재빌드
docker-compose up -d --build app

# 로그 확인
docker-compose logs -f app

# Qdrant 컬렉션 상태 확인
curl http://localhost:6333/collections

# Airflow 웹 UI
open http://localhost:8080
```

---

## 서비스 포트 정리

| 서비스 | 포트 |
|--------|------|
| FastAPI | 8000 |
| Qdrant REST | 6333 |
| Qdrant gRPC | 6334 |
| Airflow Web UI | 8080 |
| n8n (Phase 4) | 5678 |
| Kafka (Phase 5) | 9092 |

---

## Git

**Repository**: https://github.com/hansu0317/WorkAgent

### 브랜치 전략

```
main       ← 동작하는 완성본만. 직접 커밋 금지
feat/*     ← 기능 단위 (강의 섹션 하나 = feat 브랜치 하나)
fix/*      ← 버그 수정
```

### 커밋 메시지

```
feat(rag): Qdrant retriever 노드 구현
feat(api): POST /api/v1/ask 엔드포인트 추가
fix(agent): summarizer 노드 async 누락 수정
docs(claude): Phase 2 완료 업데이트
```

### 자주 쓰는 Git 명령어

```bash
# 새 기능 시작
git checkout main
git checkout -b feat/rag-retriever

# 작업 후 main에 머지
git add .
git commit -m "feat(rag): Qdrant retriever 노드 구현"
git checkout main
git merge feat/rag-retriever
git push origin main
```

### .gitignore 필수 항목

```
.env
__pycache__/
.venv/
*.pyc
.DS_Store
/dags/logs/
```

---

## 구현 상태

### Phase 1 — 환경 세팅
- [x] poetry 프로젝트 생성
- [x] .env 설정
- [x] docker-compose 기본 구성 (Qdrant on Docker, FastAPI on-prem)
- [x] FastAPI 앱 기본 구조

### Phase 2 — FastAPI 엔드포인트
- [x] POST /api/v1/upload-doc
- [x] POST /api/v1/ask
- [x] Qdrant 연동

### Phase 3 — LangGraph 에이전트
- [ ] RAG 노드 (Qdrant 검색 → GPT 답변 생성)
- [ ] Text-to-SQL 노드 (자연어 → SQL → DB 조회)
- [ ] Tool Calling (Gmail, Calendar)
- [ ] 에이전트 라우터 (RAG vs SQL 자동 판단)
- [ ] Multi-Agent 그래프

### Phase 4 — 스케줄링 + 자동화
- [ ] Airflow DAG — 이메일 요약 스케줄
- [ ] Airflow DAG — 문서 벡터 동기화
- [ ] n8n 자동화 연동

### Phase 5 — Kafka
- [ ] 에이전트 이벤트 파이프라인
- [ ] Kafka Connect 연동

> 완성 시 체크박스 체크, Phase 완료 시 상단 현재 Phase 업데이트