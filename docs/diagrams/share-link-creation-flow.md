# ResuMate Share Link Creation Flow - Detailed Architecture Diagram

> **Document**: Share Link Creation Flow  
> **Updated**: 2026-03-26  
> **Status**: Production  
> **Related Issue**: Share URL Domain Configuration Issue

## Overview

This document provides a comprehensive visual representation of how share links are created in the ResuMate application, from user interaction through to URL generation.

## Mermaid Flow Diagram

```mermaid
flowchart TD
    %% Define styles
    classDef frontend fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#01579b
    classDef backend fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#4a148c
    classDef database fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#1b5e20
    classDef config fill:#fff8e1,stroke:#ff8f00,stroke-width:2px,color:#ff8f00
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#c62828
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#2e7d32
    classDef problem fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px,color:#ef6c00

    %% ==================== FRONTEND LAYER ====================
    subgraph FRONTEND["Frontend Layer (React)"]
        direction TB
        F1[User Clicks Share Resume Button]:::frontend
        F2[ReviewPage.tsx handleShare]:::frontend
        F3[resumeAPI.createShare]:::frontend
        F4[POST /v1/resumes/{id}/share]:::frontend
        F5[Navigation to ShareManagementPage]:::frontend
        F6[ShareLinkCard Display]:::frontend
        
        F1 --> F2
        F2 --> F3
        F3 --> F4
        F4 --> F5
        F5 --> F6
    end

    %% ==================== BACKEND API LAYER ====================
    subgraph BACKEND["Backend Layer (FastAPI)"]
        direction TB
        B1[FastAPI Router]:::backend
        B2[POST /v1/resumes/{resume_id}/share Endpoint]:::backend
        B3[create_resume_share Handler]:::backend
        B4[Verify Resume Exists]:::backend
        B5[_create_share Storage Call]:::backend
        B6[Construct Share URL]:::backend
        B7[Return JSON Response]:::backend
        
        B1 --> B2
        B2 --> B3
        B3 --> B4
        B4 -->|Resume Found| B5
        B4 -->|Resume Not Found| E1[HTTP 404 Error]:::error
        B5 --> B6
        B6 --> B7
    end

    %% ==================== CONFIG LAYER ====================
    subgraph CONFIG["Configuration Layer"]
        direction TB
        C1[Environment Variable: ALLOWED_ORIGINS]:::config
        C2[Config.py Settings Class]:::config
        C3[allowed_origins_list Property]:::config
        C4[settings.allowed_origins_list[0]]:::config
        C5[First Domain Extraction]:::config
        
        C1 --> C2
        C2 --> C3
        C3 --> C4
        C4 --> C5
        
        C1_VALUE["ALLOWED_ORIGINS = 'https://resumate-frontend.vercel.app,https://resumate-backend.onrender.com,https://resumate-frontend-three.vercel.app'"]:::problem
        C1_VALUE -.-> C1
    end

    %% ==================== DATABASE LAYER ====================
    subgraph DATABASE["Database Layer (PostgreSQL)"]
        direction TB
        D1[ResumeShare Model]:::database
        D2[Generate UUID Share Token]:::database
        D3[Calculate Expiry +30 Days]:::database
        D4[Insert to resume_shares Table]:::database
        D5[Return share_token & expires_at]:::database
        
        D1 --> D2
        D2 --> D3
        D3 --> D4
        D4 --> D5
    end

    %% ==================== CONNECTIONS ====================
    F4 -->|HTTP Request| B1
    B5 -->|Call| D1
    B6 -->|Uses Domain From| C5
    D5 -->|Returns Data| B6
    B7 -->|JSON Response| F4

    %% ==================== SUCCESS PATH ====================
    subgraph SUCCESS_FLOW["Success Flow"]
        direction LR
        S1[Share Token Generated]:::success
        S2[Share URL Constructed]:::success
        S3[Response: {share_token, share_url, expires_at}]:::success
        
        S1 --> S2 --> S3
    end

    B7 --> S1

    %% ==================== PROBLEM IDENTIFICATION ====================
    subgraph PROBLEM["Current Configuration Issue"]
        direction TB
        P1[Problem: Wrong Domain Used]:::problem
        P2[Current: resumate-frontend.vercel.app<br/>Old/Incorrect Domain]:::problem
        P3[Expected: resumate-frontend-three.vercel.app<br/>Current Production Frontend]:::problem
        P4[Root Cause: First element in ALLOWED_ORIGINS]:::problem
        P5[Share URL Points to Non-Existent Frontend]:::problem
        P6[User Gets 404 When Clicking Share Link]:::problem
        
        P1 --> P2
        P1 --> P3
        P1 --> P4
        P4 --> P5
        P5 --> P6
    end

    C5 -.->|Creates Problem| P1

    %% ==================== SOLUTION ====================
    subgraph SOLUTION["Solution"]
        direction TB
        SL1[Reorder ALLOWED_ORIGINS]:::success
        SL2["Put correct domain first: https://resumate-frontend-three.vercel.app"]:::success
        SL3[Share URL will use correct domain]:::success
        
        SL1 --> SL2 --> SL3
    end

    %% Connect frontend response to display
    S3 --> F6

    %% Add note about URL format
    URL_FMT["Share URL Format: {first_domain}/shared/{share_token}"]:::config
    B6 --> URL_FMT
```

## Flow Details

### 1. Frontend Action

```
User Action: Click "Share Resume" Button
    |
    v
ReviewPage.tsx: handleShare()
    |
    v
resumeAPI.createShare(resumeId)
    |
    v
POST /v1/resumes/{resume_id}/share
```

### 2. Backend Processing

```
FastAPI Router Receives Request
    |
    v
create_resume_share Handler
    |
    +--> Verify resume exists (_get_parsed_resume)
    |     |
    |     +--> If not found: HTTP 404
    |     |
    |     +--> If found: Continue
    |
    v
Create Share (_create_share)
    |
    v
Database Share Creation
    |
    +--> Generate UUID share_token
    +--> Calculate expires_at (now + 30 days)
    +--> Insert into resume_shares table
    |
    v
Return: {share_token, expires_at}
```

### 3. Share URL Construction

```
Share URL Construction Logic:
    |
    v
settings.allowed_origins_list[0]
    |
    v
Extracts FIRST domain from ALLOWED_ORIGINS
    |
    v
Format: {first_domain}/shared/{share_token}
```

### 4. Current Configuration

**Environment Variable: ALLOWED_ORIGINS**
```
https://resumate-frontend.vercel.app,https://resumate-backend.onrender.com,https://resumate-frontend-three.vercel.app
```

**Parsed by Config.py:**
```python
@property
def allowed_origins_list(self) -> List[str]:
    return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
```

**Usage in shares.py:**
```python
share_url = f"{settings.allowed_origins_list[0]}/shared/{share_data['share_token']}"
```

### 5. Problem Identified

| Element | Value | Status |
|---------|-------|--------|
| First Domain (index 0) | `resumate-frontend.vercel.app` | Old/Incorrect |
| Current Production Frontend | `resumate-frontend-three.vercel.app` | Correct |
| Share URL Generated | `https://resumate-frontend.vercel.app/shared/{token}` | Points to old domain |
| User Experience | 404 error when clicking share link | Broken |

### 6. Solution

**Option 1: Reorder ALLOWED_ORIGINS**
```bash
# Before
ALLOWED_ORIGINS=https://resumate-frontend.vercel.app,https://resumate-backend.onrender.com,https://resumate-frontend-three.vercel.app

# After
ALLOWED_ORIGINS=https://resumate-frontend-three.vercel.app,https://resumate-backend.onrender.com,https://resumate-frontend.vercel.app
```

**Option 2: Add Dedicated SHARE_BASE_URL Config**
```python
# In config.py
SHARE_BASE_URL: str = Field(
    default="http://localhost:3000",
    description="Base URL for share links"
)
```

## Database Schema

```sql
CREATE TABLE resume_shares (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_id UUID NOT NULL,
    share_token VARCHAR(64) UNIQUE NOT NULL,
    access_count INTEGER DEFAULT 0,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## API Response Example

**Success Response (202):**
```json
{
  "share_token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "share_url": "https://resumate-frontend.vercel.app/shared/a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "expires_at": "2026-04-25T12:34:56.789Z"
}
```

## Files Involved

| Layer | File | Purpose |
|-------|------|---------|
| Frontend | `frontend/src/pages/ReviewPage.tsx` | Share button handler |
| Frontend | `frontend/src/services/api.ts` | API call to create share |
| Frontend | `frontend/src/pages/ShareManagementPage.tsx` | Share display page |
| Frontend | `frontend/src/components/ShareLinkCard.tsx` | URL display component |
| Backend | `backend/app/api/shares.py` | Share endpoint implementation |
| Backend | `backend/app/core/config.py` | Configuration parsing |
| Backend | `backend/app/services/database_share_storage.py` | Database operations |
| Backend | `backend/app/models/resume.py` | ResumeShare model |

## Related Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/v1/resumes/{id}/share` | POST | Create share link |
| `/v1/resumes/{id}/share` | GET | Get share details |
| `/v1/resumes/{id}/share` | DELETE | Revoke share link |
| `/v1/share/{token}` | GET | Public share access |
| `/shared/{token}` | GET | Frontend public share page |
| `/share/{id}` | GET | Frontend owner share management |

