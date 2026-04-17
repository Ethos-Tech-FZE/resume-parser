# SHARE_BASE_URL Configuration - Deployment Guide

> **Updated**: 2026-03-26  
> **Status**: Production Ready  
> **Implementation**: Hybrid Approach with Fallback

## Overview

This guide explains the new `SHARE_BASE_URL` configuration that solves the share link domain problem while maintaining backward compatibility.

## Problem Solved

**Previous Issue**: Share URLs were generated using `ALLOWED_ORIGINS[0]`, which caused:
- Fragile dependency on CORS configuration ordering
- Share links broke when ALLOWED_ORIGINS was reordered
- Old domain remained in configuration causing 404 errors

**Solution**: Dedicated `SHARE_BASE_URL` configuration with intelligent fallback

## Configuration Priority

The `share_base_url` property uses this priority order:

```
1. Explicit SHARE_BASE_URL (if set and non-empty)
   ↓
2. ALLOWED_ORIGINS[0] (backward compatibility)
   ↓
3. http://localhost:3000 (development default)
```

## Environment Variables

### Option 1: Explicit SHARE_BASE_URL (Recommended for Production)

**Render Dashboard → resumate-backend → Environment**

```bash
SHARE_BASE_URL=https://resumate-frontend-three.vercel.app
```

**Benefits**:
- ✅ Explicit and self-documenting
- ✅ Independent of CORS configuration
- ✅ Won't break if ALLOWED_ORIGINS is reordered
- ✅ Clear intent for future developers

### Option 2: Reorder ALLOWED_ORIGINS (Fallback)

**Current (Incorrect):**
```bash
ALLOWED_ORIGINS=https://resumate-frontend.vercel.app,https://resumate-backend.onrender.com,https://resumate-frontend-three.vercel.app
```

**Fixed (Correct):**
```bash
ALLOWED_ORIGINS=https://resumate-frontend-three.vercel.app,https://resumate-backend.onrender.com
```

**Note**: This still works but is less maintainable than Option 1

## Deployment Steps

### Phase 1: Deploy Code Changes (✅ Completed)

The following code changes have been implemented:

1. **config.py**: Added `SHARE_BASE_URL` field and `share_base_url` property
2. **shares.py**: Updated all share URL generation to use `settings.share_base_url`
3. **Tests**: Added comprehensive unit tests (9 tests, all passing)

**Status**: ✅ Code changes complete and tested

### Phase 2: Update Render Environment

**Step 1**: Go to Render Dashboard
```
https://dashboard.render.com
```

**Step 2**: Open resumate-backend service

**Step 3**: Navigate to Environment section

**Step 4**: Add new environment variable
```
Name: SHARE_BASE_URL
Value: https://resumate-frontend-three.vercel.app
```

**Step 5**: (Optional) Clean up ALLOWED_ORIGINS
```bash
# Remove old domain from ALLOWED_ORIGINS
ALLOWED_ORIGINS=https://resumate-frontend-three.vercel.app,https://resumate-backend.onrender.com
```

**Step 6**: Save Changes (Render auto-redeploys)

### Phase 3: Verify Deployment

**Test 1**: Health Check
```bash
curl https://resumate-backend-4s4r.onrender.com/health
```

**Test 2**: Create Share Link
```bash
# Upload a resume via frontend
# Navigate to /share/{resume_id}
# Verify share URL shows: https://resumate-frontend-three.vercel.app/shared/{token}
```

**Test 3**: Access Share Link
```bash
# Open the share link in browser
# Verify shared resume loads successfully
```

## Backward Compatibility

The implementation is **fully backward compatible**:

| Scenario | SHARE_BASE_URL | ALLOWED_ORIGINS | Result |
|----------|----------------|-----------------|--------|
| Production (Recommended) | Set explicitly | Any value | Uses SHARE_BASE_URL ✅ |
| Production (Legacy) | Not set | Correct domain first | Uses ALLOWED_ORIGINS[0] ✅ |
| Development | Not set | Default localhost | Uses localhost ✅ |

**No Breaking Changes**: Existing deployments continue to work without modification

## Code Changes Summary

### Files Modified

1. **app/core/config.py**
   - Added `SHARE_BASE_URL` field (line ~85)
   - Added `share_base_url` property with fallback logic (line ~155)

2. **app/api/shares.py**
   - Updated share URL construction (lines 168, 213)
   - Updated export endpoints (lines 419, 460, 497)
   - Removed unused `DEFAULT_BASE_URL` constant

3. **tests/unit/test_share_base_url_config.py** (NEW)
   - 9 comprehensive unit tests
   - All edge cases covered
   - Real-world scenarios tested

## Testing

### Unit Tests
```bash
cd backend
python3 -m pytest tests/unit/test_share_base_url_config.py -v
```

**Result**: ✅ 9/9 tests passing

### Integration Test
```bash
python3 /tmp/test_share_url_generation.py
```

**Result**: ✅ All scenarios passing

## Troubleshooting

### Share links still show old domain

**Cause**: SHARE_BASE_URL not set or not deployed

**Solution**:
1. Verify SHARE_BASE_URL is set in Render dashboard
2. Check Render logs for deployment errors
3. Clear settings cache if needed

### 500 errors when accessing share links

**Cause**: Frontend domain mismatch

**Solution**:
1. Verify SHARE_BASE_URL matches actual frontend URL
2. Check ALLOWED_ORIGINS includes the frontend domain
3. Test share link manually in browser

### Tests failing locally

**Cause**: Settings cache not cleared

**Solution**:
```python
from app.core.config import clear_settings_cache
clear_settings_cache()
```

## Related Documentation

- **Architecture**: `docs/diagrams/share-link-creation-flow.md`
- **Sequence Diagrams**: `docs/diagrams/share-link-sequence.md`
- **Bug Analysis**: Memory `bug-share-link-domain-mismatch`
- **Flow Analysis**: Memory `share-link-complete-flow-analysis`

## Migration Checklist

- [x] Code changes implemented
- [x] Unit tests passing (9/9)
- [x] Integration tests passing
- [x] Documentation updated
- [ ] Add SHARE_BASE_URL to Render environment
- [ ] Verify deployment on Render
- [ ] Test share link generation
- [ ] Test share link access
- [ ] Update CLAUDE.md
- [ ] Remove old domain from ALLOWED_ORIGINS (optional)

## Summary

**✅ Implementation Complete**: Hybrid approach with backward compatibility

**🚀 Ready to Deploy**: Add `SHARE_BASE_URL` environment variable to Render

**📚 Next Steps**: Update production environment and verify share links work
