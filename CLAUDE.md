# ResuMate - AI-Powered Resume Parser

> **Updated**: 2026-03-25 | **Status**: Production Ready | **Tests**: 228+

---

## Overview

ResuMate extracts structured data from resumes using **OCR -> NLP -> AI Enhancement**.

```
Text Extraction (pdfplumber) + OCR Fallback (Tesseract)
         -> NLP Entity Extraction (spaCy 3.8+)
         -> AI Enhancement (OpenAI GPT-4o-mini, optional)
```

**Graceful Degradation**: Works without AI if `OPENAI_API_KEY` not set.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI 0.109.0, Python 3.12.8 |
| OCR | Tesseract + pdf2image 1.16.3 |
| NLP | spaCy 3.8+ (Pydantic 2.x compatible) |
| AI | OpenAI 1.10.0 (GPT-4o-mini) |
| Database | Supabase PostgreSQL / Render PostgreSQL + async SQLAlchemy 2.0.36 |
| Frontend | React 18 + TypeScript 5.3 + Vite 5.0 |
| Styling | Tailwind CSS 3.4 (navy/gold theme) |
| State | Zustand 4.5 |
| Deployment | Vercel serverless / Render Blueprints |

---

## Quick Start

```bash
# Clone & database setup
git clone <repo> && cd resume-parser
docker compose up -d
cd backend && ./scripts/init_database.sh

# Backend development
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend development
cd frontend && npm install && npm run dev

# Testing
cd backend && python -m pytest tests/ -v
cd frontend && npm test -- --run && npm run type-check
```

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/resumes/upload` | POST | Upload resume, returns {resume_id, websocket_url} |
| `/v1/resumes/{id}` | GET | Fetch parsed resume data |
| `/v1/resumes/{id}` | PUT | Save user edits |
| `/v1/resumes/{id}/share` | POST | Create share token, returns {share_token, share_url, expires_at} |
| `/v1/resumes/{id}/export/pdf` | GET | Download PDF export |
| `/ws/resumes/{id}` | WebSocket | Real-time parsing progress |
| `/health` | GET | Health check with graceful degradation |

---

## Environment Configuration

### Backend (.env)
```bash
# Database (URL-encode passwords)
DATABASE_URL=postgresql+asyncpg://postgres:ENCODED_PASSWORD@host:5432/postgres
DATABASE_URL_SYNC=postgresql://postgres:ENCODED_PASSWORD@host:5432/postgres
USE_DATABASE=true

# AI (Optional - graceful fallback)
OPENAI_API_KEY=sk-...

# OCR
TESSERACT_PATH=/usr/local/bin/tesseract
ENABLE_OCR_FALLBACK=true

# App
SECRET_KEY=...
ALLOWED_ORIGINS=https://resumate-frontend.vercel.app,http://localhost:3000
USE_CELERY=false
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=https://resumate-backend-4s4r.onrender.com/v1
VITE_WS_BASE_URL=wss://resumate-backend-4s4r.onrender.com/ws
```

---

## Dependency Compatibility Matrix

| Package | Version | Python 3.12.8 | Notes |
|---------|---------|---------------|-------|
| spaCy | >=3.8.0,<4.0.0 | Yes | Native Pydantic 2.x support |
| Pydantic | >=2.7.4,<3.0.0 | Yes | Python 3.12.4+ compatible |
| SQLAlchemy | >=2.0.36,<3.0.0 | Yes | Python 3.14 forward-compatible |
| Mangum | >=0.21.0,<1.0.0 | Yes | Lambda/Vercel compatible |
| numpy | ==1.26.4 | Yes | Prebuilt wheels |
| confection | >=0.1.4,<1.0.0 | Yes | spaCy Pydantic v2 support |
| thinc | >=8.3.4,<9.0.0 | Yes | spaCy Pydantic v2 support |

---

## Production Deployment

### Vercel Serverless

**Deployment Workflow:**
```bash
# 1. Commit changes (CRITICAL - Vercel deploys from git)
git add . && git commit -m "feat: description"
git push origin main

# 2. Deploy backend
cd /path/to/repo
vercel --prod --scope nilukushs-projects

# 3. Verify
vercel inspect <deployment-url> --wait && curl <url>/health
```

**Current Bundle Status:**
| Metric | Value | Status |
|--------|-------|--------|
| Bundle size | 394.92 MB | Above 250MB threshold |
| Function size | 79.18 MB | Excellent |
| Runtime cache | N/A | Deployed successfully |

**Key Rules:**
- Run `vercel` from repo root, not subdirectories
- Bundle >250MB triggers 24-48h runtime cache (no CLI clear available)
- `vercel --force` clears build cache only, NOT runtime cache
- backend/ and frontend/ are separate Vercel projects

---

### Render Blueprint

**render.yaml Configuration:**
```yaml
services:
  - type: web
    name: resumate-backend
    runtime: python
    region: oregon
    plan: free
    rootDir: backend
    buildCommand: "pip install --upgrade pip && pip install -r requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    healthCheckPath: /health
    autoDeployTrigger: commit  # FIXED: was deployOnPush

databases:
  - name: resumate-db
    databaseName: resumate
    user: resumate_user
    plan: free
    region: oregon
```

**Setup Steps:**
```bash
# 1. Create Blueprint from dashboard
# https://dashboard.render.com -> New + -> Blueprint
# Connect GitHub repo, select render.yaml

# 2. Configure environment variables in dashboard
DATABASE_URL=postgresql+asyncpg://...
DATABASE_URL_SYNC=postgresql://...
SECRET_KEY=...
OPENAI_API_KEY=sk-...  # optional
ALLOWED_ORIGINS=https://resumate-frontend.vercel.app
USE_DATABASE=true
USE_CELERY=false

# 3. Deploy and test
curl https://resumate-backend.onrender.com/health
```

**Bug Fix #25 - Render Configuration Fixes:**
| Issue | Fix |
|-------|-----|
| `deployOnPush` deprecated | Changed to `autoDeployTrigger: commit` |
| Persistent disk error | Removed disk (free tier limitation) |
| Module path errors | Added `rootDir: backend` |
| Python 3.14 incompatibility | Upgraded SQLAlchemy to 2.0.36 |
| spaCy compatibility | Pinned Python to 3.12.8 in runtime.txt |

**Render-Specific Troubleshooting:**
```bash
# View logs in dashboard: Logs tab
# Common issue: Port binding - Render uses $PORT env var automatically
# Database: Use Internal URL for connections within Render
```

---

## Critical Patterns

### 1. Lazy Database Initialization
```python
# BROKEN - crashes at import in serverless
engine = db_manager.init_engine(...)

# WORKING - lazy initialization
engine: Optional[AsyncEngine] = None

def get_engine() -> AsyncEngine:
    global engine
    if engine is None:
        engine = db_manager.init_engine(...)
    return engine
```

### 2. Vercel Function Detection
```python
# BROKEN - function not detected
def handler(event, context):
    return Mangum(app, lifespan="off")(event, context)

# WORKING - module-level variable
handler = Mangum(app, lifespan="off")
```

### 3. Graceful Health Degradation
```python
health_status["status"] = "degraded"  # NOT "unhealthy"
return JSONResponse(content=health_status, status_code=200)  # Always 200
```

---

## Dependency Management

| Rule | Details |
|------|---------|
| Sync files | Keep `pyproject.toml` and `requirements.txt` synchronized |
| Version specifiers | Use `>=` in pyproject.toml, `==` in requirements.txt |
| Verification | Compare versions across both files before deploying |
| Before removing | Verify: `grep -r "import <lib>" backend/app/` |
| Git workflow | Deploy from git - commit & push before deploying |

---

## Common Issues

| Symptom | Root Cause | Fix |
|---------|------------|-----|
| TypeError in vc_init.py | Old Mangum version in runtime cache | Update pyproject.toml, wait 24-48h |
| FUNCTION_INVOCATION_FAILED | Runtime cache incompatibility | Same as above |
| ModuleNotFoundError | Missing dependency | Check requirements.txt, redeploy |
| Vercel deploying old code | Forgot to commit/push git | `git add . && git commit && git push` |
| Render build fails | Python version mismatch | Pin to 3.12.8 in runtime.txt |
| spaCy import error | Pydantic v2 incompatibility | Add confection>=0.1.4, thinc>=8.3.4 |

---

## Recent Fixes (#18-#25)

| # | Issue | Resolution |
|---|-------|------------|
| #18 | Function detection + lazy DB | Module-level handler + lazy init |
| #19 | Python 3.12 + spaCy 3.7.2 | Upgraded to spaCy 3.8+ |
| #20 | Pydantic v2 compatibility | Added confection>=0.1.4, thinc>=8.3.4 |
| #21 | Python 3.12.4 + Pydantic | Upgraded to pydantic>=2.7.4 |
| #22 | Mangum 0.17.0 + Python 3.12 | Upgraded to mangum>=0.21.0 |
| #23 | Mangum version mismatch | Fixed pyproject.toml mangum>=0.21.0 |
| #24 | Bundle size 401MB | Removed Celery, Redis, Sentry (-54MB) |
| #25 | Render deployment errors | deployOnPush->autoDeployTrigger, rootDir, SQLAlchemy 2.0.48, Python 3.12.8 pin |

---

## Deployment URLs

| Service | URL | Status |
|---------|-----|--------|
| **Backend (Render)** | https://resumate-backend-4s4r.onrender.com | ✅ LIVE |
| **Frontend (Vercel)** | https://resumate-frontend.vercel.app | ✅ LIVE |

### Health Endpoints
- **Render**: https://resumate-backend-4s4r.onrender.com/health

---

## Test Coverage

- Backend: 175+ tests passing
- Frontend: 53 tests passing
- Total: 228+ tests

---

## Documentation Index

| Document | Purpose |
|----------|---------|
| `docs/PROGRESS.md` | Progress tracking with all bug fixes |
| `docs/BUG-FIX-25-RENDER-DEPLOYMENT.md` | Render deployment complete guide |
| `docs/BUG-FIX-24-OPTIMIZE-BUNDLE-SIZE.md` | Celery/Redis/Sentry removal |
| `docs/BUG-FIX-25-HANDLER-PATH-CORRECTION.md` | Vercel handler path fix |
| `docs/RENDER-DEPLOYMENT-GUIDE.md` | Render Blueprint setup |
| `docs/DATABASE_SETUP.md` | Database setup |
| `docs/SUPABASE_SETUP.md` | Supabase-specific setup |

---

## Session Learnings

**Git Workflow**: Always commit and push before deploying - platforms read from git repository

**Dependency Safety**: Before removing, verify: `grep -r "import <lib>" backend/app/`

**Runtime vs Build Cache**: `vercel --force` clears build cache only; runtime cache has no CLI clear

**Render Deployment** (2026-03-25):
- Render aggressively caches Python runtimes - use `runtime.txt` + `PYTHON_VERSION` env var
- `autoDeployTrigger: commit` replaces deprecated `deployOnPush`
- `rootDir` critical for monorepo module paths
- `buildFilter: "*"` helps with cache invalidation
- Python 3.12.8 is the sweet spot for spaCy 3.8 + Pydantic 2.7+ + SQLAlchemy 2.0.36+
- Free tier doesn't support persistent disks

**Render Blueprints**: Don't count against project limits - use render.yaml for IaC deployment

**Python Pinning**: Always pin Python version in runtime.txt for spaCy compatibility
