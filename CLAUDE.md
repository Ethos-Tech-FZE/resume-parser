# ResuMate - AI-Powered Resume Parser

> **Updated**: 2026-04-17 | **Status**: Production Ready | **Tests**: 228+

## Overview

ResuMate extracts structured data from resumes using **OCR -> NLP -> AI Enhancement**.

```
pdfplumber + Tesseract OCR -> spaCy NLP -> OpenAI GPT-4o-mini (optional)
```

**Graceful Degradation**: Works without AI if `OPENAI_API_KEY` not set.

## Quick Start

```bash
# Clone & setup
git clone <repo> && cd resume-parser

# Backend (port 8001 - port 8000 may be in use)
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001

# Frontend (port 5173)
cd frontend && npm install && npm run dev

# Test database connection
cd backend && python scripts/test_supabase_connection.py

# Test
cd backend && python -m pytest tests/ -v
cd frontend && npm test -- --run && npm run type-check
```

## Environment Configuration

### Backend (.env)
```bash
# Database - Supabase PostgreSQL (pooler for local & production)
# Uses connection pooling via PgBouncer in transaction mode
# Pool config in database.py: pool_size=3, max_overflow=2 (optimized for ap-northeast-2 latency)
DATABASE_URL=postgresql+asyncpg://postgres.PROJECT_REF:PASSWORD@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres?ssl=require
DATABASE_URL_SYNC=postgresql://postgres.PROJECT_REF:PASSWORD@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres?ssl=require
USE_DATABASE=true

# AI (optional - graceful fallback if unset)
OPENAI_API_KEY=sk-...

# OCR
TESSERACT_PATH=/usr/local/bin/tesseract
ENABLE_OCR_FALLBACK=true

# App
SECRET_KEY=...  # openssl rand -hex 32
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8000,https://resumate-frontend-three.vercel.app
SHARE_BASE_URL=http://localhost:3000  # Use production URL when deploying
USE_CELERY=false
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=https://resumate-backend-4s4r.onrender.com/v1
VITE_WS_BASE_URL=wss://resumate-backend-4s4r.onrender.com/ws
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/resumes/upload` | POST | Upload resume |
| `/v1/resumes/{id}` | GET/PUT | Fetch/save parsed data |
| `/v1/resumes/{id}/share` | POST | Create share token |
| `/v1/resumes/{id}/export/pdf` | GET | Download PDF export |
| `/ws/resumes/{id}` | WebSocket | Real-time progress |
| `/health` | GET | Health check (200 OK, may show "degraded") |

## Critical Code Patterns

```python
# 1. Lifespan Manager - Auto DB init for local/Render (ignored by Vercel)
@asynccontextmanager
async def lifespan(app: FastAPI):
    db_manager.init_engine(echo=settings.is_development)
    yield
    await db_manager.close()
app = FastAPI(lifespan=lifespan)

# 2. Lazy DB Init - Serverless fallback
engine = None
def get_engine():
    global engine
    if engine is None:
        engine = db_manager.init_engine(...)
    return engine

# 3. Vercel Handler - Module-level (AST detection)
handler = Mangum(app, lifespan="off")  # NOT inside a function

# 4. Graceful Health - Always return 200
health_status["status"] = "degraded"  # NOT "unhealthy"
return JSONResponse(content=health_status, status_code=200)
```

## Deployment

### Production URLs
| Service | URL |
|---------|-----|
| Backend (Render) | https://resumate-backend-4s4r.onrender.com |
| Frontend (Vercel) | https://resumate-frontend-three.vercel.app |

### Critical Rules (Both Platforms)
- `git commit && git push` before deploying (platforms read from git)
- Sync `pyproject.toml` and `requirements.txt`
- Use `>=` in pyproject.toml, `==` in requirements.txt

### Render (Primary Backend)
```yaml
# render.yaml
services:
  - type: web
    runtime: python
    rootDir: backend
    buildCommand: "pip install --upgrade pip && pip install -r requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    healthCheckPath: /health
    autoDeployTrigger: commit
```

### Vercel (Frontend + Backup Backend)
```bash
vercel --prod --scope nilukushs-projects
# backend/ and frontend/ are separate projects
```

## Tech Stack & Dependencies

| Component | Technology | Key Versions |
|-----------|------------|--------------|
| Backend | FastAPI, Python 3.12.8 | SQLAlchemy 2.0.48, Pydantic 2.12.5 |
| NLP | spaCy | >=3.8.0 (confection>=0.1.4, thinc>=8.3.4) |
| AI | OpenAI | 1.10.0 (GPT-4o-mini, optional) |
| Serverless | Mangum | >=0.21.0 |
| Frontend | React 18, TypeScript 5.3 | Vite 5.0, Tailwind 3.4 |

**Pin Python 3.12.8** in `backend/runtime.txt` for spaCy compatibility.

## Troubleshooting & Bug Fixes

| Issue | Fix |
|-------|-----|
| DB pool timeout | See `backend/app/core/database.py` - pool_size=3, max_overflow=2 for ap-northeast-2 latency |
| TypeError / FUNCTION_INVOCATION_FAILED | Update Mangum>=0.21.0, wait 24-48h for cache |
| ModuleNotFoundError | Check requirements.txt, redeploy |
| Vercel deploying old code | `git add . && git commit && git push` |
| spaCy import error | Add confection>=0.1.4, thinc>=8.3.4 |
| Local DB not initialized | Lifespan manager handles startup (#26) |

**Bug Fix History**: See `docs/PROGRESS.md` for complete #18-#26 details.

## Documentation

| Document | Purpose |
|----------|---------|
| `docs/PROGRESS.md` | Complete bug fix history |
| `docs/RENDER-DEPLOYMENT-GUIDE.md` | Render Blueprint setup |
| `docs/SESSION_SUMMARY_2026-03-26-DATABASE-FIX.md` | Lifespan manager implementation |
| `docs/SHARE_BASE_URL_DEPLOYMENT.md` | Share URL configuration |
| `backend/scripts/test_supabase_connection.py` | DB health check |
| `backend/scripts/test_server_init.py` | Full initialization diagnostic |
