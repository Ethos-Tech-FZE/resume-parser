# Render Deployment Checklist - ResuMate Backend

> **Last Updated**: 2026-03-26 - Bug Fixes #26 & #27 Applied

## ✅ Pre-Deployment Verification

- [x] Connection string tested locally
- [x] PgBouncer transaction mode compatibility verified
- [x] statement_cache_size=0 fix implemented
- [x] Environment variables prepared
- [x] Documentation updated
- [x] Health check logic reviewed

## 📋 Render Environment Variables

**Critical - Use these exact values**:

```bash
# Database (Supabase Transaction Pooler)
DATABASE_URL="postgresql+asyncpg://postgres.piqltpksqaldndikmaob:j%3CTN%7DXs%2Aph%25%3D%7B%3Enb8L.w%5CclD%260C%24W7%21q%3FM%27%3A%5DKt5@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres?ssl=require"

DATABASE_URL_SYNC="postgresql://postgres.piqltpksqaldndikmaob:j%3CTN%7DXs%2Aph%25%3D%7B%3Enb8L.w%5CclD%260C%24W7%21q%3FM%27%3A%5DKt5@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres?ssl=require"

# Application Settings
ALLOWED_ORIGINS=https://resumate-frontend.vercel.app,https://resumate-backend.onrender.com
ENVIRONMENT=production
MAX_UPLOAD_SIZE=10485760
PYTHON_VERSION=3.12.8
SECRET_KEY="0Erjj1jbR8n3+2ehw9IU5ZAa40Pc56SI0W+LB8F1a6Y="
USE_CELERY=false
USE_DATABASE=true

# AI (Optional)
OPENAI_API_KEY=sk-proj-...
```

## 🔧 Code Changes Applied

### Bug Fix #26: Supabase Pooler Migration
**Commit**: `2dcdc8e`  
**Changes**: Updated connection strings to regional pooler format

### Bug Fix #27: PgBouncer Transaction Mode
**Commit**: `a23eeb8`  
**File**: `app/core/database.py`  
**Change**: Added `statement_cache_size=0` to connect_args

```python
# app/core/database.py:115-122
"connect_args": {
    # Required for Supabase PgBouncer transaction mode
    # Disables asyncpg statement cache to avoid prepared statement errors
    "statement_cache_size": 0,
    "server_settings": {"jit": "off"}
}
```

## 🚀 Deployment Steps

### 1. Update Render Environment (If Needed)

If environment variables are not yet updated:
- Go to: Render Dashboard → resumate-backend → Environment
- Update `DATABASE_URL` with new pooler format
- Update `DATABASE_URL_SYNC` with new pooler format
- Click "Save Changes"

### 2. Deploy from Git (Recommended)

```bash
# Changes already committed and pushed
git push origin main  # Triggers automatic Render deployment
```

### 3. Monitor Deployment

```bash
# Using Render CLI
render logs --follow resumate-backend

# Or watch in dashboard:
# Dashboard → resumate-backend → Events → Logs
```

### 4. Verify Success

```bash
# Health check
curl https://resumate-backend-4s4r.onrender.com/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0",
  "environment": "production",
  "timestamp": "2026-03-26T..."
}
```

## 🧪 Post-Deployment Testing

1. **Health Endpoint**
   ```bash
   curl https://resumate-backend-4s4r.onrender.com/health
   ```
   Expected: `{"status": "healthy", "database": "connected"}`

2. **Resume Upload** (via frontend)
   - Navigate to: https://resumate-frontend.vercel.app
   - Upload a PDF resume
   - Verify parsing progress updates via WebSocket
   - Confirm extracted data is displayed

3. **Database Operations**
   - Upload should create resume record in Supabase
   - Check Supabase dashboard: Table Editor → resumes
   - Verify new rows appear

4. **WebSocket Connection**
   - Verify real-time progress updates work
   - No connection drops during parsing

## ⚠️ Troubleshooting

### Issue: "[Errno -2] Name or service not known"
**Cause**: Old pooler hostname format  
**Fix**: Use `aws-1-ap-northeast-2.pooler.supabase.com`  
**Status**: ✅ Fixed in Bug #26

### Issue: "InvalidSQLStatementNameError"
**Cause**: PgBouncer transaction mode + prepared statements  
**Fix**: Added `statement_cache_size=0` to connect_args  
**Status**: ✅ Fixed in Bug #27

### Issue: "authentication failed"
**Cause**: Wrong username format  
**Fix**: Use `postgres.piqltpksqaldndikmaob` not `postgres`  
**Status**: ✅ Fixed in Bug #26

### Issue: Application shuts down repeatedly
**Cause**: Health check failures  
**Fix**: Verify both fixes #26 and #27 are deployed  
**Status**: Verify logs show "database: connected"

### Issue: "SSL required"
**Cause**: Missing SSL parameter  
**Fix**: Add `?ssl=require` to connection string  
**Status**: ✅ Fixed in Bug #26

## 📊 Success Metrics

- ✅ Health check returns `database: connected`
- ✅ Application stays running (no shutdown)
- ✅ No DNS errors in logs
- ✅ No prepared statement errors in logs
- ✅ PostgreSQL 17.6 connection established
- ✅ SSL connection active
- ✅ Resume upload works end-to-end

## 🔗 Useful Links

- **Render Dashboard**: https://dashboard.render.com
- **Backend URL**: https://resumate-backend-4s4r.onrender.com
- **Health Endpoint**: https://resumate-backend-4s4r.onrender.com/health
- **Frontend URL**: https://resumate-frontend.vercel.app
- **Supabase Dashboard**: https://supabase.com/dashboard

## 📝 Technical Notes

### Configuration Details
- **Pooler Mode**: Transaction (port 6543)
- **Region**: ap-northeast-2 (Tokyo)
- **PostgreSQL Version**: 17.6
- **Python Version**: 3.12.8
- **asyncpg**: statement_cache_size=0
- **Connection Pool**: SQLAlchemy with pool_pre_ping=True

### Why Transaction Mode?
- ✅ Designed for serverless (Vercel/Render)
- ✅ Better connection management
- ✅ Prevents connection exhaustion
- ✅ Required for Supabase free tier

### Why statement_cache_size=0?
- ✅ Required for PgBouncer transaction mode
- ✅ Disables prepared statements (not supported)
- ✅ Forces simple query protocol
- ✅ Minimal performance impact for serverless

## 🎯 Deployment History

| Date | Commit | Description | Status |
|------|--------|-------------|--------|
| 2026-03-26 | `2dcdc8e` | Supabase pooler migration (Bug #26) | ✅ Applied |
| 2026-03-26 | `a23eeb8` | PgBouncer compatibility fix (Bug #27) | ✅ Deploying |
| 2026-03-25 | `dbf847a` | Render deployment documentation | ✅ Stable |

## 📚 Documentation

- **Progress Log**: `docs/PROGRESS.md` (Bug fixes #26 & #27)
- **Supabase Migration**: `docs/SUPABASE-POOLER-MIGRATION.md`
- **This Checklist**: `docs/RENDER-DEPLOYMENT-CHECKLIST.md`

## 🚀 Next Steps

After successful deployment:

1. ✅ Verify health endpoint returns `database: connected`
2. ✅ Test resume upload from frontend
3. ✅ Verify WebSocket progress updates
4. ✅ Test share functionality
5. ✅ Verify PDF export works
6. ✅ Monitor logs for 24 hours
7. ⏳ Load testing (optional)
8. ⏳ Set up monitoring/alerts (optional)

---

**Deployment Status**: ⏳ In Progress (Auto-deployment triggered by push to main)

**Last Updated**: 2026-03-26 10:30 GST
