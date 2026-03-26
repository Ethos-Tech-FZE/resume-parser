# CORS Health Check Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-step. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add automated CORS health check endpoint to validate configuration and catch misconfigurations during deployment.

**Architecture:** Create a new `/cors-check` endpoint in the FastAPI application that returns the current CORS configuration, including allowed origins list, environment, and a validation check for frontend URLs. This enables automated validation after deployments without manual browser testing.

**Tech Stack:** FastAPI, Pydantic Settings, existing CORS middleware configuration

---

## File Structure

```
backend/app/api/
├── __init__.py          # Existing (no changes)
├── resumes.py           # Existing (no changes)
├── shares.py            # Existing (no changes)
├── websocket.py         # Existing (no changes)
└── health.py            # NEW: Health check endpoints including CORS validation

backend/tests/integration/
├── test_health_check.py        # Existing (add CORS tests)
└── test_cors_validation.py     # NEW: Dedicated CORS validation tests

backend/docs/
└── CORS-TROUBLESHOOTING.md     # NEW: CORS diagnostic procedures
```

**Design Decisions:**
- **Single Responsibility:** `health.py` contains only health/check endpoints, not business logic
- **Integration Testing:** CORS tests validate the full request/response cycle with actual middleware
- **Documentation Focus:** Troubleshooting guide provides reusable diagnostic procedures
- **Minimal Changes:** No modifications to existing CORS middleware or settings - only read access

---

## Task 1: Create Health Check Module

**Files:**
- Create: `backend/app/api/health.py`

- [ ] **Step 1: Write the failing test for CORS check endpoint**

```python
# backend/tests/integration/test_cors_validation.py
"""
Integration tests for CORS validation endpoint.

These tests validate that the CORS check endpoint returns
accurate configuration information for deployment validation.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_cors_check_returns_configuration():
    """Test that CORS check returns current configuration"""
    response = client.get("/cors-check")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "allowed_origins" in data
    assert "environment" in data
    assert "frontend_check" in data
    assert isinstance(data["allowed_origins"], list)


def test_cors_check_includes_localhost_in_development():
    """Test that localhost origins are included in development"""
    response = client.get("/cors-check")
    
    data = response.json()
    
    # In development, should include localhost URLs
    if data["environment"] == "development":
        assert any("localhost" in origin for origin in data["allowed_origins"])


def test_cors_check_detects_frontend_origins():
    """Test that frontend_check flag detects resumate-frontend origins"""
    response = client.get("/cors-check")
    
    data = response.json()
    
    # If any resumate-frontend origin is present, frontend_check should be True
    has_frontend = any(
        "resumate-frontend" in origin 
        for origin in data["allowed_origins"]
    )
    assert data["frontend_check"] == has_frontend


def test_cors_check_returns_environment():
    """Test that CORS check returns current environment"""
    response = client.get("/cors-check")
    
    data = response.json()
    assert data["environment"] in ["development", "staging", "production", "testing"]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend
pytest tests/integration/test_cors_validation.py -v
```

Expected: FAIL with "404 Not Found" (endpoint doesn't exist yet)

- [ ] **Step 3: Create health check module with CORS check endpoint**

```python
# backend/app/api/health.py
"""
Health check endpoints for system monitoring and deployment validation.

This module provides endpoints for checking system health and validating
CORS configuration after deployments.
"""

from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/cors-check")
async def cors_check():
    """
    Return current CORS configuration for validation.
    
    This endpoint enables automated validation of CORS configuration
    after deployments, ensuring that frontend origins are properly
    configured before users encounter CORS errors.
    
    Returns:
        dict: CORS configuration including:
            - allowed_origins: List of configured allowed origins
            - environment: Current application environment
            - frontend_check: Boolean indicating if resumate-frontend URLs are present
    
    Example:
        {
            "allowed_origins": [
                "https://resumate-frontend-three.vercel.app",
                "http://localhost:3000"
            ],
            "environment": "production",
            "frontend_check": true
        }
    """
    return {
        "allowed_origins": settings.allowed_origins_list,
        "environment": settings.ENVIRONMENT,
        "frontend_check": any(
            "resumate-frontend" in origin 
            for origin in settings.allowed_origins_list
        )
    }
```

- [ ] **Step 4: Register health router in main application**

```python
# backend/app/main.py (modifications only)

# Add after line 14 (after other imports):
from app.api import health

# Add after line 48 (after existing router includes):
app.include_router(health.router, tags=["health"])
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd backend
pytest tests/integration/test_cors_validation.py -v
```

Expected: PASS (all 4 tests pass)

- [ ] **Step 6: Verify endpoint is accessible**

```bash
cd backend
curl http://localhost:8000/cors-check | jq .
```

Expected:
```json
{
  "allowed_origins": ["http://localhost:3000", "http://localhost:8000"],
  "environment": "development",
  "frontend_check": false
}
```

- [ ] **Step 7: Commit**

```bash
git add backend/app/api/health.py backend/app/main.py backend/tests/integration/test_cors_validation.py
git commit -m "feat: add CORS health check endpoint for deployment validation

- Add /cors-check endpoint to validate CORS configuration
- Return allowed_origins, environment, and frontend_check flag
- Add integration tests for CORS validation
- Enables automated deployment validation

This prevents CORS misconfigurations from reaching production
by providing a quick validation endpoint after deployments."
```

---

## Task 2: Update Existing Health Check Tests

**Files:**
- Modify: `backend/tests/integration/test_health_check.py`

- [ ] **Step 1: Add test for CORS check endpoint**

```python
# Add to backend/tests/integration/test_health_check.py

def test_cors_check_endpoint_exists():
    """Test that CORS check endpoint is available"""
    response = client.get("/cors-check")
    assert response.status_code == 200
    
    data = response.json()
    assert "allowed_origins" in data
    assert "environment" in data
```

- [ ] **Step 2: Run all health check tests**

```bash
cd backend
pytest tests/integration/test_health_check.py -v
```

Expected: PASS (all 6 tests pass - 4 existing + 1 new + 1 existing updated)

- [ ] **Step 3: Commit**

```bash
git add backend/tests/integration/test_health_check.py
git commit -m "test: add CORS check endpoint to health check suite

- Verify CORS check endpoint is accessible
- Validate response structure
- Ensure health check tests cover all monitoring endpoints"
```

---

## Task 3: Create CORS Troubleshooting Documentation

**Files:**
- Create: `backend/docs/CORS-TROUBLESHOOTING.md`

- [ ] **Step 1: Create comprehensive troubleshooting guide**

```markdown
# CORS Troubleshooting Guide

## Quick Diagnosis

### Symptom: Browser shows CORS error

```
Access to fetch at 'https://backend-url.com' from origin 'https://frontend-url.com' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
```

### Root Cause
Frontend origin is not in backend's `ALLOWED_ORIGINS` environment variable.

---

## Diagnostic Steps

### 1. Check CORS Configuration

```bash
curl https://resumate-backend-4s4r.onrender.com/cors-check | jq .
```

**Expected Response:**
```json
{
  "allowed_origins": ["https://resumate-frontend-three.vercel.app"],
  "environment": "production",
  "frontend_check": true
}
```

**If `frontend_check` is `false`:** Your frontend URL is not in `ALLOWED_ORIGINS`.

### 2. Verify CORS Headers

```bash
curl -X OPTIONS https://resumate-backend-4s4r.onrender.com/v1/resumes/upload \
  -H "Origin: https://your-frontend-url.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v 2>&1 | grep "Access-Control"
```

**Expected Output:**
```
< Access-Control-Allow-Origin: https://your-frontend-url.com
< Access-Control-Allow-Credentials: true
< Access-Control-Allow-Methods: *
< Access-Control-Allow-Headers: *
```

**If missing:** Backend CORS middleware is not configured correctly.

### 3. Test in Incognito Mode

Browser caching can mask CORS fixes:

1. Open incognito/private window
2. Navigate to frontend
3. Open Developer Tools → Console
4. Attempt upload
5. Check for CORS errors

**If incognito works but regular window doesn't:** Clear browser cache.

---

## Resolution Procedures

### Scenario 1: Frontend URL Changed

**Symptoms:**
- New Vercel deployment with different URL
- Existing backend deployment
- CORS errors appear immediately

**Resolution:**

1. **Get new frontend URL**
   ```bash
   # From Vercel dashboard or deployment logs
   FRONTEND_URL="https://resumate-frontend-three.vercel.app"
   ```

2. **Update ALLOWED_ORIGINS in Render**
   - Go to: https://dashboard.render.com
   - Navigate to: resumate-backend → Environment
   - Find or create: `ALLOWED_ORIGINS`
   - Set value:
     ```
     https://resumate-frontend-three.vercel.app,https://resumate-frontend.vercel.app,http://localhost:3000,http://localhost:5173
     ```
   - Click "Save Changes"

3. **Trigger Manual Redeploy**
   - Go to: Events tab
   - Click: "Manual Deploy" → "Clear build cache & deploy"
   - Wait for: "Live" status (~2-3 minutes)

4. **Validate Fix**
   ```bash
   # Check CORS configuration
   curl https://resumate-backend-4s4r.onrender.com/cors-check | jq .
   
   # Verify headers
   curl -X OPTIONS https://resumate-backend-4s4r.onrender.com/v1/resumes/upload \
     -H "Origin: $FRONTEND_URL" \
     -v 2>&1 | grep "Access-Control-Allow-Origin"
   
   # Test upload in incognito mode
   ```

5. **Verify Production Upload**
   - Open frontend in incognito window
   - Upload test resume
   - Check console for CORS errors
   - Verify parsed resume displays

### Scenario 2: Local Development CORS Issues

**Symptoms:**
- CORS errors when running `npm run dev` (localhost:5173)
- Backend running on localhost:8000

**Resolution:**

1. **Check frontend port**
   ```bash
   # Vite uses 5173 by default
   # Check actual port in terminal output
   ```

2. **Update backend .env**
   ```bash
   # backend/.env
   ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8000
   ```

3. **Restart backend**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

4. **Verify**
   ```bash
   curl http://localhost:8000/cors-check | jq .
   # Should include "http://localhost:5173"
   ```

---

## Prevention Checklist

### Before Frontend Deployment

- [ ] Document new frontend URL if it will change
- [ ] Plan to update backend `ALLOWED_ORIGINS` immediately after
- [ ] Add CORS check to deployment verification

### After Frontend Deployment

- [ ] Run `curl /cors-check` to verify configuration
- [ ] Test upload from incognito window
- [ ] Check production logs for CORS errors
- [ ] Update documentation with new URLs

### After Backend Deployment

- [ ] Verify `/cors-check` returns correct origins
- [ ] Test CORS headers with curl
- [ ] Upload test resume from production frontend
- [ ] Monitor logs for 403/404 CORS errors

---

## Common Mistakes

### ❌ Don't

- Use wildcard origins with credentials:
  ```python
  # BROKEN - Security risk
  allow_origins=["*"]
  allow_credentials=True
  ```

- Forget redeploy after updating environment variables
- Test in regular browser window (cache interference)
- Assume old frontend URLs can be removed immediately

### ✅ Do

- Keep old frontend URLs for backward compatibility
- Test in incognito mode to bypass cache
- Use `/cors-check` endpoint for automated validation
- Document all frontend URLs in deployment documentation

---

## Advanced Diagnostics

### Check Render Environment Variables

```bash
render env --service=srv-d70lkgvdiees73do87a0 | grep ALLOWED_ORIGINS
```

### View Backend Logs for CORS Errors

```bash
render logs --resources=srv-d70lkgvdiees73do87a0 --limit=50 -f
```

Look for:
- Missing CORS headers in logs
- Origin mismatch errors
- Failed preflight OPTIONS requests

### Test WebSocket CORS

```javascript
// In browser console
const ws = new WebSocket('wss://resumate-backend-4s4r.onrender.com/ws/resumes/test-id');
ws.onopen = () => console.log('WebSocket connected');
ws.onerror = (error) => console.error('WebSocket error:', error);
```

---

## Related Documentation

- `RENDER-DEPLOYMENT-GUIDE.md` - Full deployment procedures
- `CLAUDE.md` - CORS configuration patterns
- `app/core/config.py` - Settings definition
- `app/main.py` - CORS middleware setup

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `curl /cors-check \| jq .` | Check CORS configuration |
| `curl -X OPTIONS ... -v` | Verify CORS headers |
| `render logs --resources=...` | View backend logs |
| `render env --service=...` | Check environment variables |
| Test in incognito | Bypass browser cache |
```

- [ ] **Step 2: Commit documentation**

```bash
git add backend/docs/CORS-TROUBLESHOOTING.md
git commit -m "docs: add comprehensive CORS troubleshooting guide

- Quick diagnosis procedures
- Step-by-step resolution for common scenarios
- Prevention checklists for deployments
- Common mistakes and best practices
- Advanced diagnostic commands

This guide provides reusable procedures for diagnosing and
resolving CORS issues, reducing incident resolution time."
```

---

## Task 4: Update CLAUDE.md with CORS Reference

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add CORS validation section to CLAUDE.md**

Find the section "## Production Deployment" and add after it:

```markdown
## CORS Configuration

### Validation After Deployment

After any frontend or backend deployment, validate CORS configuration:

```bash
# 1. Check CORS configuration
curl https://resumate-backend-4s4r.onrender.com/cors-check | jq .

# 2. Verify headers for your frontend origin
curl -X OPTIONS https://resumate-backend-4s4r.onrender.com/v1/resumes/upload \
  -H "Origin: https://resumate-frontend-three.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -v 2>&1 | grep "Access-Control"

# 3. Test upload in incognito mode
# Open frontend in incognito → Upload resume → Check console
```

### When Frontend URL Changes

1. Update `ALLOWED_ORIGINS` in Render dashboard
2. Trigger "Clear build cache & deploy"
3. Run validation commands above
4. Test in incognito mode (browser caching masks CORS fixes)

### Troubleshooting

See `backend/docs/CORS-TROUBLESHOOTING.md` for comprehensive diagnostic procedures.
```

- [ ] **Step 2: Verify documentation is accurate**

```bash
# Check that CORS endpoint is accessible
curl http://localhost:8000/cors-check | jq .

# Verify CLAUDE.md commands work
grep -A 10 "## CORS Configuration" CLAUDE.md
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add CORS validation section to CLAUDE.md

- Document CORS validation procedures
- Add quick reference for deployment verification
- Link to comprehensive troubleshooting guide
- Include incognito mode testing guidance"
```

---

## Task 5: Update Deployment Documentation

**Files:**
- Modify: `docs/RENDER-DEPLOYMENT-GUIDE.md` (or create if doesn't exist)

- [ ] **Step 1: Add CORS validation to deployment checklist**

```markdown
## Post-Deployment Verification

Add to the deployment checklist:

### Backend Deployment

- [ ] Service status: "Live"
- [ ] Health check returns 200: `curl /health`
- [ ] **CORS configuration validated**: `curl /cors-check | jq .`
- [ ] **Frontend URL present in allowed_origins**
- [ ] **CORS headers verified with curl**
- [ ] Test upload from production frontend (incognito mode)

### Frontend Deployment (if URL changes)

- [ ] Document new frontend URL
- [ ] Update backend `ALLOWED_ORIGINS` in Render dashboard
- [ ] Trigger backend redeploy
- [ ] Run CORS validation commands
- [ ] Test upload from new frontend URL
```

- [ ] **Step 2: Commit**

```bash
git add docs/RENDER-DEPLOYMENT-GUIDE.md
git commit -m "docs: add CORS validation to deployment checklist

- Add CORS check endpoint validation
- Include frontend URL verification
- Document incognito mode testing
- Link to troubleshooting guide"
```

---

## Self-Review

### Spec Coverage
✅ All requirements implemented:
- CORS health check endpoint created
- Integration tests added
- Comprehensive documentation created
- Deployment checklists updated
- CLAUDE.md updated with CORS procedures

### Placeholder Scan
✅ No placeholders found - all code is complete and executable

### Type Consistency
✅ All function signatures, variable names, and types are consistent:
- `settings.allowed_origins_list` used consistently
- `frontend_check` boolean flag consistent across tests and implementation
- Response structure matches tests expectations

### Test Coverage
✅ Tests cover:
- CORS check endpoint exists and returns 200
- Response structure validation
- Environment detection
- Frontend origin detection
- Development environment includes localhost

---

## Success Criteria

✅ All tasks complete when:
1. `/cors-check` endpoint returns configuration
2. All integration tests pass (6 tests)
3. Troubleshooting guide is comprehensive
4. CLAUDE.md references CORS procedures
5. Deployment checklist includes CORS validation
6. No regressions in existing health check tests

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-03-26-cors-health-check.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**

---

**If Subagent-Driven chosen:**
- **REQUIRED SUB-SKILL:** Use superpowers:subagent-driven-development
- Fresh subagent per task + two-stage review

**If Inline Execution chosen:**
- **REQUIRED SUB-SKILL:** Use superpowers:executing-plans
- Batch execution with checkpoints for review
