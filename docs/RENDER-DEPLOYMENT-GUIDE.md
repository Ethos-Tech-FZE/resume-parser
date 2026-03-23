# Render Deployment Guide for ResuMate

**Date:** 2026-03-23
**Platform:** Render Free Tier
**Status:** Ready for Blueprint Setup

---

## **Overview**

This guide walks you through deploying ResuMate Backend to Render using **Blueprints** - which doesn't count against your project limit!

---

## **Why Render Blueprints?**

**Problem:** You've used your free project slots on Railway and Render.

**Solution:** Render **Blueprints** allow you to deploy from a GitHub repository WITHOUT creating a new project!

**How it works:**
- Blueprint = Template configuration + GitHub connection
- Doesn't count against project limit
- Auto-deploys when you push to main branch
- **render.yaml** tells Render how to build and run your app

---

## **Prerequisites**

✅ **Already Done:**
- `render.yaml` created at repository root
- Python 3.12 compatible code
- Dependencies optimized (Celery, Redis, Sentry, boto3 removed)

**You Need:**
- Render account (already have one)
- GitHub repository connected to Render
- Supabase account (for PostgreSQL database)

---

## **Step-by-Step Setup**

### **Step 1: Connect GitHub Repository to Render**

1. Go to: https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Click **"Connect GitHub"**
4. Select `nilukush/resume-parser` repository
5. Authorize Render access

### **Step 2: Configure Blueprint**

1. **Blueprint Name**: `resumate-backend`
2. **Blueprint Path**: `render.yaml` (should auto-detect)
3. **Root Directory**: Leave blank (defaults to repo root)
4. **Branch**: `main`
5. **Region**: `Oregon` (free tier default)
6. **Click "Create Blueprint"**

### **Step 3: Configure Database**

Render will create a PostgreSQL database automatically (defined in `render.yaml`):

1. After blueprint creation, click on **"resumate-db"** database
2. Note the **Internal Database URL** (format: `postgresql://user:pass@host:port/db`)
3. Convert to asyncpg format:
   ```
   postgresql://user:pass@host:port/db  →  postgresql+asyncpg://user:pass@host:port/db
   ```

### **Step 4: Add Environment Variables**

Go to your deployed service → **"Environment"** tab → Add these:

| Variable | Value | Notes |
|---------|-------|-------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | From Step 3 (asyncpg format) |
| `DATABASE_URL_SYNC` | `postgresql://...` | Same URL but without `+asyncpg` |
| `SECRET_KEY` | [Auto-generated] | Or use `openssl rand -hex 32` |
| `OPENAI_API_KEY` | `sk-...` | From OpenAI dashboard (optional) |
| `ALLOWED_ORIGINS` | `https://resumate-frontend.vercel.app` | Your frontend URL |
| `USE_DATABASE` | `true` | Enable PostgreSQL |
| `USE_CELERY` | `false` | Background tasks disabled |
| `ENVIRONMENT` | `production` | Production mode |

### **Step 5: Deploy**

1. Click **"Manual Deploy"** → **"Deploy latest commit"**
2. Wait for build to complete (~2-3 minutes)
3. Visit: `https://resumate-backend.onrender.com/health`
4. Should return: `{"status": "healthy"}` ✅

---

## **Post-Deployment Configuration**

### **Database Setup**

Run migrations to create tables:

```bash
# SSH into the service (via Render dashboard → Terminal)
cd backend
python -m alembic upgrade head
```

### **Verify Deployment**

```bash
# Health check
curl https://resumate-backend.onrender.com/health

# API docs (if in development mode)
curl https://resumate-backend.onrender.com/docs
```

---

## **Frontend Configuration**

Update frontend environment variables:

```bash
# frontend/.env.production
VITE_API_BASE_URL=https://resumate-backend.onrender.com/v1
VITE_WS_BASE_URL=wss://resumate-backend.onrender.com/ws
```

Deploy frontend to Vercel:
```bash
cd frontend
npm run build
vercel --prod
```

---

## **Cost Breakdown**

| Service | Plan | Monthly Cost |
|---------|------|--------------|
| Backend (Web Service) | Free | **$0** |
| PostgreSQL | Free | **$0** |
| **Total** | | **$0** |

---

## **Troubleshooting**

### **Issue: Database Connection Failed**

**Solution:**
1. Check DATABASE_URL format (must be `postgresql+asyncpg://...`)
2. Verify database is running in Render dashboard
3. Test connection in Render shell: `psql $DATABASE_URL`

### **Issue: Port Conflict**

**Solution:**
- Render uses `$PORT` environment variable automatically
- Your `uvicorn` command uses `$PORT` correctly
- No need to change port (Render handles this)

### **Issue: Build Fails**

**Solution:**
1. Check `requirements.txt` has all dependencies
2. Verify Python version (3.12+ required)
3. Check build logs in Render dashboard

---

## **Next Steps**

1. ✅ Create Render Blueprint (using `render.yaml`)
2. ✅ Configure environment variables
3. ✅ Deploy and test
4. ✅ Run database migrations
5. ✅ Update frontend to point to Render backend
6. ✅ Deploy frontend to Vercel
7. ✅ Test full application

---

## **Rollback Plan**

If issues occur:
1. **Vercel frontend**: Already working, no changes needed
2. **Render backend**: Can delete blueprint and redeploy
3. **Database**: Render databases can be recreated from scratch

---

**Prepared by:** Claude (Sonnet 4.5)
**Date:** 2026-03-23 12:30 GST
