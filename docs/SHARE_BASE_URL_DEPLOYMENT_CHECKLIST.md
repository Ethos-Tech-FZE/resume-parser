# SHARE_BASE_URL Production Deployment Checklist

**Deployment Date**: _____________  
**Deployed By**: _____________  
**Status**: _____________

---

## Pre-Deployment Checklist

### Code Verification

- [ ] Code reviewed by at least one team member
- [ ] All unit tests passing (9/9 tests)
- [ ] Integration tests passing
- [ ] Documentation updated (CLAUDE.md)
- [ ] Changelog updated
- [ ] No merge conflicts in main branch

### Configuration Validation

- [ ] `SHARE_BASE_URL` environment variable documented
- [ ] Default value documented for fallback
- [ ] Example configuration provided in `.env.example`

### Risk Assessment

- [ ] Risk assessment completed
- [ ] Rollback procedure documented
- [ ] Monitoring in place
- [ ] On-call team notified

---

## Deployment Steps

### 1. Environment Variable Setup

#### Render Dashboard Configuration

```bash
# Log in to Render Dashboard
# Navigate to: resumate-backend service
# Go to: Environment section
```

Add/Update the following environment variables:

| Variable | Value | Required |
|----------|-------|----------|
| `SHARE_BASE_URL` | `https://resumate-frontend-three.vercel.app` | Yes |
| `ALLOWED_ORIGINS` | `https://resumate-frontend-three.vercel.app,https://resumate-backend.onrender.com` | Yes |

- [ ] `SHARE_BASE_URL` added to Render environment
- [ ] `ALLOWED_ORIGINS` updated to remove old domains
- [ ] Values verified for typos
- [ ] Save changes applied

### 2. Deploy Backend

```bash
# Option A: Auto-deploy (Render Blueprint)
git push origin main

# Option B: Manual deploy from Render Dashboard
# Click "Manual Deploy" button
```

- [ ] Deployment triggered
- [ ] Build logs show success
- [ ] No errors in build output
- [ ] Deployment marked as "Live"

### 3. Post-Deployment Verification

#### Health Check

```bash
curl https://resumate-backend.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "share_base_url": "https://resumate-frontend-three.vercel.app",
  ...
}
```

- [ ] Health endpoint returns 200
- [ ] `share_base_url` shows correct value
- [ ] No errors in response

#### Share Link Creation Test

```bash
# Create a test share link
curl -X POST https://resumate-backend.onrender.com/v1/resumes/{test-id}/share
```

Expected response:
```json
{
  "share_token": "...",
  "share_url": "https://resumate-frontend-three.vercel.app/shared/...",
  "expires_at": "..."
}
```

- [ ] Share link created successfully
- [ ] `share_url` uses correct domain
- [ ] `share_url` format is correct
- [ ] Token is valid UUID format

#### Share Link Access Test

```bash
# Access the share link
curl https://resumate-frontend-three.vercel.app/shared/{token}
```

- [ ] Share link is accessible
- [ ] Resume data loads correctly
- [ ] No 404 errors
- [ ] No CORS errors

---

## Smoke Tests

### Functional Tests

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| Create share link | Returns 202 | | [ ] |
| Share URL domain | resumate-frontend-three.vercel.app | | [ ] |
| Access share link | Returns 200 | | [ ] |
| Share shows resume | Resume data displayed | | [ ] |
| WhatsApp export | Valid WhatsApp URL | | [ ] |
| Telegram export | Valid Telegram URL | | [ ] |
| Email export | Valid mailto URL | | [ ] |

### Integration Tests

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| Frontend can create share | Success | | [ ] |
| Frontend can access share | Success | | [ ] |
| Share link in email works | Success | | [ ] |
| Share link in WhatsApp works | Success | | [ ] |

---

## Monitoring Setup

### Metrics to Monitor

- [ ] Share link creation rate
- [ ] Share link access rate
- [ ] 404 errors on share links
- [ ] Health check endpoint response time
- [ ] Error rate in logs

### Alerts to Configure

- [ ] Alert if `share_base_url` changes
- [ ] Alert if share links contain wrong domain
- [ ] Alert if 404 rate increases > 1%
- [ ] Alert if health check fails

---

## Rollback Procedure

### If Critical Issues Detected

#### Step 1: Immediate Rollback

```bash
# In Render Dashboard:
# 1. Navigate to resumate-backend service
# 2. Click "Deploy" -> "Previous Deployments"
# 3. Click "Rollback" on the last successful deployment
```

- [ ] Previous deployment selected
- [ ] Rollback triggered
- [ ] Rollback completed

#### Step 2: Remove SHARE_BASE_URL

```bash
# In Render Dashboard:
# 1. Navigate to Environment section
# 2. Remove SHARE_BASE_URL variable
# 3. Ensure ALLOWED_ORIGINS[0] has correct domain
```

- [ ] `SHARE_BASE_URL` removed
- [ ] `ALLOWED_ORIGINS[0]` verified
- [ ] Save changes applied

#### Step 3: Verify Rollback

```bash
curl https://resumate-backend.onrender.com/health
```

- [ ] Health check returns 200
- [ ] Share links work with fallback

---

## Post-Deployment Actions

### Documentation

- [ ] Deployment runbook updated
- [ ] Change log updated
- [ ] Team notified of deployment
- [ ] Stakeholders notified

### Monitoring Review (24 hours)

- [ ] No critical alerts triggered
- [ ] Share link creation rate stable
- [ ] 404 error rate within normal
- [ ] No customer complaints

---

## Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Developer | | | |
| Code Reviewer | | | |
| QA Engineer | | | |
| On-Call Engineer | | | |
| Product Owner | | | |

---

## Notes

```
Add any deployment notes, issues encountered, or lessons learned here:

___________________________________________________________________________

___________________________________________________________________________

___________________________________________________________________________

___________________________________________________________________________
```

---

**Document Version**: 1.0  
**Last Updated**: 2026-03-26  
**Next Review**: Post-deployment
