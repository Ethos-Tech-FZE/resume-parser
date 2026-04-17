# SHARE_BASE_URL Enhancement Roadmap

**Status**: Active  
**Last Updated**: 2026-03-26  
**Implementation Priority**: High

---

## Overview

This document outlines the prioritized enhancements for the SHARE_BASE_URL configuration implementation. Enhancements are ordered by impact vs. effort analysis.

---

## Priority Matrix

```
┌────────────────────────────────────────────────────────────────────┐
│                    ENHANCEMENT PRIORITY MATRIX                      │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  HIGH IMPACT     │  [P1] URL Validation     │  [P3] Config Drift  │
│                  │  Implementation         │  Detection            │
│                  │  Effort: 2 hours        │  Effort: 3 hours      │
│                  │  Impact: Production     │  Impact: Production   │
│                  │  Reliability            │  Reliability          │
│                  │                         │                       │
│  MEDIUM IMPACT   │  [P2] Health Check      │  [P4] Multi-Env       │
│                  │  Enhancement            │  Support              │
│                  │  Effort: 1 hour         │  Effort: 2 hours      │
│                  │  Impact: Observability  │  Impact: Safety       │
│                  │                         │                       │
│  LOW IMPACT      │  [F1] Logging           │  [F2] Documentation   │
│                  │  Effort: 1 hour         │  Effort: 2 hours      │
│                  │  Impact: Debugging       │  Impact: Onboarding   │
│                  │                         │                       │
├──────────────────┼─────────────────────────┼───────────────────────┤
│                  │     LOW EFFORT          │    MEDIUM EFFORT      │
└────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Critical Production Enhancements (Week 1)

### P1: URL Validation Implementation

**Status**: Pending  
**Effort**: 2 hours  
**Impact**: High  
**Risk**: Low

#### Problem

Currently, invalid URLs in SHARE_BASE_URL are not detected until share links are created, potentially causing runtime errors or incorrect URLs.

#### Solution

Add Pydantic field validation to catch configuration errors at startup:

```python
from pydantic import field_validator, Field

class Settings(BaseSettings):
    SHARE_BASE_URL: str = Field(
        default="",
        description="Base URL for share links (defaults to first ALLOWED_ORIGIN if empty)"
    )
    
    @field_validator("SHARE_BASE_URL", mode="before")
    @classmethod
    def validate_share_base_url(cls, v: str) -> str:
        """
        Validate SHARE_BASE_URL format.
        
        Ensures:
        - URL starts with http:// or https://
        - No trailing slash
        - No whitespace
        - Valid hostname format
        """
        if v and v.strip():
            url = v.strip()
            
            # Protocol validation
            if not url.startswith(("http://", "https://")):
                raise ValueError(
                    f"SHARE_BASE_URL must start with http:// or https://. Got: {url[:20]}..."
                )
            
            # Remove trailing slash for consistency
            url = url.rstrip("/")
            
            # Basic hostname validation
            from urllib.parse import urlparse
            parsed = urlparse(url)
            if not parsed.netloc:
                raise ValueError(
                    f"SHARE_BASE_URL must be a valid URL. Got: {url}"
                )
            
            return url
        
        return v
```

#### Tests

```python
class TestShareBaseURLValidation:
    """Test SHARE_BASE_URL validation."""
    
    def test_rejects_url_without_protocol(self, monkeypatch):
        """Should reject URLs without http/https."""
        monkeypatch.setenv("SHARE_BASE_URL", "example.com")
        with pytest.raises(ValueError, match="must start with"):
            Settings()
    
    def test_accepts_valid_urls(self, monkeypatch):
        """Should accept valid URLs."""
        monkeypatch.setenv("SHARE_BASE_URL", "https://example.com")
        settings = Settings()
        assert settings.share_base_url == "https://example.com"
    
    def test_removes_trailing_slash(self, monkeypatch):
        """Should remove trailing slash."""
        monkeypatch.setenv("SHARE_BASE_URL", "https://example.com/")
        settings = Settings()
        assert settings.share_base_url == "https://example.com"
```

#### Benefits

- Catches misconfiguration at startup
- Clear error messages for operators
- Consistent URL formatting
- Prevents production incidents

---

### P2: Health Check Enhancement

**Status**: Pending  
**Effort**: 1 hour  
**Impact**: Medium  
**Risk**: Low

#### Problem

Current health endpoint does not expose share_base_url, making it difficult to verify configuration at runtime.

#### Solution

Enhance the health check endpoint to include share configuration:

```python
@router.get("/health")
async def health_check(settings: Settings = Depends(get_settings)):
    """
    Health check endpoint with configuration summary.
    
    Returns overall health status and key configuration for
    runtime verification.
    """
    health_status = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "configuration": {
            "share_base_url": settings.share_base_url,
            "allowed_origins": settings.allowed_origins_list[:3],  # First 3 only
            "has_database": settings.USE_DATABASE,
        }
    }
    
    # Check database connection if enabled
    if settings.USE_DATABASE:
        try:
            # Quick database health check
            health_status["database"] = "connected"
        except Exception as e:
            health_status["status"] = "degraded"
            health_status["database"] = f"disconnected: {str(e)[:50]}"
    
    return JSONResponse(content=health_status, status_code=200)
```

#### Benefits

- Runtime visibility into configuration
- Easier troubleshooting
- Supports automated monitoring
- No sensitive data exposed

---

## Phase 2: Production Reliability (Week 2)

### P3: Configuration Drift Detection

**Status**: Pending  
**Effort**: 3 hours  
**Impact**: High  
**Risk**: Low

#### Problem

Configuration can drift over time, leading to share links using incorrect domains without immediate detection.

#### Solution

Add admin endpoint for proactive configuration validation:

```python
@router.get("/admin/config/validate", tags=["admin"])
async def validate_configuration(
    settings: Settings = Depends(get_settings),
    admin_key: str = Header(None, alias="X-Admin-Key")
):
    """
    Validate configuration for common issues.
    
    This endpoint performs proactive checks for:
    - Missing SHARE_BASE_URL in production
    - Old domains in ALLOWED_ORIGINS
    - URL format validation
    - Configuration consistency
    
    Requires admin authentication via X-Admin-Key header.
    """
    # Admin authentication (implement as needed)
    if admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    issues = []
    warnings = []
    
    # Check 1: Production requires explicit SHARE_BASE_URL
    if settings.is_production and not settings.SHARE_BASE_URL:
        issues.append({
            "severity": "critical",
            "check": "production_share_base_url",
            "message": "SHARE_BASE_URL not set in production environment",
            "recommendation": "Set SHARE_BASE_URL environment variable"
        })
    
    # Check 2: Old domain detection
    old_domains = [
        "resumate-frontend.vercel.app",
        "resumate-frontend-two.vercel.app"
    ]
    found_old = [d for d in old_domains if d in settings.allowed_origins_list]
    if found_old:
        issues.append({
            "severity": "warning",
            "check": "old_domains",
            "message": f"Old domains found in ALLOWED_ORIGINS: {found_old}",
            "recommendation": "Remove old domains from ALLOWED_ORIGINS"
        })
    
    # Check 3: Protocol mismatch
    if settings.share_base_url.startswith("http://"):
        warnings.append({
            "severity": "info",
            "check": "https_protocol",
            "message": "SHARE_BASE_URL uses http:// instead of https://",
            "recommendation": "Use https:// for production"
        })
    
    # Check 4: Allowed origins includes share base
    if settings.share_base_url not in settings.allowed_origins_list:
        warnings.append({
            "severity": "info",
            "check": "cors_consistency",
            "message": "SHARE_BASE_URL not in ALLOWED_ORIGINS",
            "recommendation": "Add SHARE_BASE_URL to ALLOWED_ORIGINS for CORS"
        })
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "current_config": {
            "share_base_url": settings.share_base_url,
            "allowed_origins": settings.allowed_origins_list,
            "share_base_url_source": (
                "explicit" if settings.SHARE_BASE_URL 
                else "fallback"
            )
        },
        "timestamp": datetime.utcnow().isoformat()
    }
```

#### Benefits

- Proactive issue detection
- Automated monitoring support
- Clear remediation guidance
- Prevents configuration drift

---

### P4: Multi-Environment Support

**Status**: Pending  
**Effort**: 2 hours  
**Impact**: Medium  
**Risk**: Low

#### Problem

Development environments might accidentally use production URLs, and production requires explicit configuration.

#### Solution

Add environment-aware validation:

```python
@property
def share_base_url(self) -> str:
    """
    Get share base URL with environment-aware logic.
    
    Behavior by environment:
    - Production: Requires explicit SHARE_BASE_URL
    - Staging: Warns if not explicit
    - Development: Falls back to localhost
    """
    # Explicit configuration always wins
    if self.SHARE_BASE_URL and self.SHARE_BASE_URL.strip():
        return self.SHARE_BASE_URL.strip()
    
    # Production requires explicit configuration
    if self.is_production:
        raise ValueError(
            "SHARE_BASE_URL must be set in production environment. "
            "Add SHARE_BASE_URL to your environment variables."
        )
    
    # Staging should have explicit config
    if self.ENVIRONMENT == "staging":
        import warnings
        warnings.warn(
            "SHARE_BASE_URL not set in staging. "
            "Using ALLOWED_ORIGINS[0] fallback."
        )
    
    # Non-production: use first allowed origin
    if self.allowed_origins_list:
        return self.allowed_origins_list[0]
    
    # Development fallback
    return "http://localhost:3000"
```

#### Benefits

- Prevents production misconfiguration
- Environment-specific behavior
- Clear error messages
- Enforces best practices

---

## Phase 3: Future Enhancements (Future)

### F1: Enhanced Logging

**Status**: Backlog  
**Effort**: 1 hour  
**Impact**: Low

Add structured logging for share URL generation:

```python
import logging

logger = logging.getLogger(__name__)

# In share creation endpoint
logger.info(
    "share_link_created",
    extra={
        "resume_id": resume_id,
        "share_token": share_data["share_token"],
        "share_base_url": settings.share_base_url,
        "share_base_url_source": (
            "explicit" if settings.SHARE_BASE_URL else "fallback"
        )
    }
)
```

### F2: Documentation Updates

**Status**: Backlog  
**Effort**: 2 hours  
**Impact**: Medium

Update documentation with:
- SHARE_BASE_URL configuration guide
- Troubleshooting section
- Environment variable reference
- Deployment checklist

---

## Implementation Timeline

```
Week 1: Critical Enhancements
├── Day 1: P1 - URL Validation (2 hours)
├── Day 2: P1 Testing (1 hour)
├── Day 3: P2 - Health Check (1 hour)
├── Day 4: P2 Testing (1 hour)
└── Day 5: Deploy to staging

Week 2: Production Reliability
├── Day 1: P3 - Config Drift Detection (3 hours)
├── Day 2: P3 Testing (1 hour)
├── Day 3: P4 - Multi-Env Support (2 hours)
├── Day 4: P4 Testing (1 hour)
└── Day 5: Deploy to production

Week 3: Monitoring & Documentation
├── Day 1: F1 - Enhanced Logging (1 hour)
├── Day 2: F2 - Documentation (2 hours)
├── Day 3: Monitoring setup (2 hours)
└── Day 4: Team training (1 hour)
```

---

## Success Criteria

Each enhancement is considered complete when:

1. Code is implemented and reviewed
2. Unit tests pass (100% coverage)
3. Integration tests pass
4. Documentation is updated
5. Deployed to staging for verification
6. Production deployment completed

---

## Monitoring & Metrics

Track the following metrics to measure enhancement success:

| Metric | Target | Current |
|--------|--------|---------|
| Configuration errors at startup | 0% | N/A |
| Share link 404 rate | <1% | Measuring |
| Health check availability | 100% | 100% |
| Configuration drift incidents | 0 | N/A |

---

**Document Owner**: Development Team  
**Review Date**: 2026-04-02  
**Version**: 1.0
