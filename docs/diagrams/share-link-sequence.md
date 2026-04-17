# ResuMate Share Link Creation - Sequence Diagram

> **Document**: Share Link Creation Sequence Diagram  
> **Updated**: 2026-03-26  
> **Type**: Sequence Diagram  

## Mermaid Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant User as User
    participant UI as ReviewPage.tsx
    participant API as resumeAPI.ts
    participant Backend as FastAPI Backend
    participant Config as Settings Config
    participant DB as PostgreSQL Database
    participant SharePage as ShareManagementPage
    participant Card as ShareLinkCard

    Note over User,Card: Share Link Creation Flow

    %% Step 1: User initiates share
    User->>UI: Click "Share Resume" button
    activate UI
    UI->>UI: handleShare() called
    UI->>API: resumeAPI.createShare(resumeId)
    activate API
    
    %% Step 2: API makes HTTP request
    API->>API: POST {VITE_API_BASE_URL}/v1/resumes/{id}/share
    API->>Backend: HTTP POST /v1/resumes/{resume_id}/share
    activate Backend
    
    %% Step 3: Backend processes request
    Backend->>Backend: Router receives request
    Backend->>Backend: create_resume_share(resume_id, db)
    
    %% Step 4: Verify resume exists
    Backend->>Backend: _get_parsed_resume(resume_id, db)
    alt Resume Not Found
        Backend-->>API: HTTP 404 Not Found
        API-->>UI: Throw Error
        UI-->>User: Display "Resume not found"
    else Resume Found
        Note over Backend: Resume data retrieved successfully
        
        %% Step 5: Create share in database
        Backend->>DB: _create_share(resume_id, db)
        activate DB
        DB->>DB: Generate UUID share_token
        DB->>DB: Calculate expires_at (now + 30 days)
        DB->>DB: INSERT INTO resume_shares
        DB-->>Backend: {share_token, expires_at}
        deactivate DB
        
        %% Step 6: Construct share URL
        Backend->>Config: settings.allowed_origins_list
        activate Config
        Config->>Config: Parse ALLOWED_ORIGINS env var
        Note over Config: ALLOWED_ORIGINS =<br/>'https://resumate-frontend.vercel.app,<br/>https://resumate-backend.onrender.com,<br/>https://resumate-frontend-three.vercel.app'
        Config->>Config: Split by comma and strip
        Config->>Config: Return [origin.strip() for origin in ...]
        Config-->>Backend: [<br/>'resumate-frontend.vercel.app',<br/>'resumate-backend.onrender.com',<br/>'resumate-frontend-three.vercel.app'<br/>]
        deactivate Config
        
        Backend->>Backend: share_url = settings.allowed_origins_list[0] + "/shared/" + share_token
        Note over Backend: share_url = "https://resumate-frontend.vercel.app/shared/{token}"
        Note over Backend: WARNING: This domain is OLD/INCORRECT!
        
        %% Step 7: Return response
        Backend-->>API: HTTP 202 Accepted
        Backend-->>API: {<br/>share_token: "...",<br/>share_url: "https://resumate-frontend.vercel.app/shared/...",<br/>expires_at: "2026-04-25..."<br/>}
        deactivate Backend
        
        %% Step 8: Frontend receives response
        API-->>UI: Share data received
        deactivate API
        UI->>UI: Navigate to ShareManagementPage
        deactivate UI
        
        %% Step 9: Display share link
        activate SharePage
        SharePage->>API: resumeAPI.getShare(resumeId)
        activate API
        API->>Backend: GET /v1/resumes/{id}/share
        activate Backend
        Backend-->>API: Share details
        deactivate Backend
        API-->>SharePage: Share details
        deactivate API
        
        SharePage->>Card: Render ShareLinkCard
        activate Card
        Card-->>User: Display share URL
        Note over User,Card: User sees: https://resumate-frontend.vercel.app/shared/...
        Note over User,Card: PROBLEM: Clicking this URL will result in 404!
        deactivate Card
        deactivate SharePage
    end
```

## Problem Analysis Sequence

```mermaid
sequenceDiagram
    autonumber
    participant Env as .env File
    participant Config as Settings Class
    participant Shares as shares.py
    participant URL as Share URL
    participant User as End User

    Note over Env,User: Domain Configuration Problem Flow

    Env->>Config: ALLOWED_ORIGINS env var
    Note over Env: "https://resumate-frontend.vercel.app,<br/>https://resumate-backend.onrender.com,<br/>https://resumate-frontend-three.vercel.app"
    
    Config->>Config: Parse comma-separated string
    Config->>Config: allowed_origins_list property
    Config-->>Shares: [<br/>[0] resumate-frontend.vercel.app,<br/>[1] resumate-backend.onrender.com,<br/>[2] resumate-frontend-three.vercel.app<br/>]
    
    Shares->>Shares: Extract index [0]
    Shares->>URL: Construct share_url
    Note over Shares: share_url = allowed_origins_list[0] + "/shared/" + token
    
    URL-->>URL: https://resumate-frontend.vercel.app/shared/{token}
    Note over URL: Points to OLD deployment!
    
    URL->>User: Share link displayed
    User->>URL: Click link to view shared resume
    URL-->>User: 404 Page Not Found
    Note over User: Broken user experience!
    
    rect rgb(255, 200, 200)
        Note over Env,User: The Problem
        Note right of Config: First domain [0] is used for share URL
        Note right of Shares: Old frontend domain is first in list
        Note right of User: Result: Share links don't work
    end
```

## Solution Flow

```mermaid
sequenceDiagram
    autonumber
    participant Dev as Developer
    participant Env as .env File
    participant Config as Settings Class
    participant Shares as shares.py
    participant URL as Share URL
    participant User as End User

    Note over Dev,User: Solution Implementation

    Dev->>Env: Reorder ALLOWED_ORIGINS
    Note over Env: Put correct domain FIRST
    
    Env->>Env: ALLOWED_ORIGINS =<br/>"https://resumate-frontend-three.vercel.app,<br/>https://resumate-backend.onrender.com,<br/>https://resumate-frontend.vercel.app"
    
    Config->>Config: Parse and re-sort
    Config-->>Shares: [<br/>[0] resumate-frontend-three.vercel.app,<br/>[1] resumate-backend.onrender.com,<br/>[2] resumate-frontend.vercel.app<br/>]
    
    Shares->>Shares: Extract index [0] (now correct!)
    Shares->>URL: Construct share_url
    URL-->>URL: https://resumate-frontend-three.vercel.app/shared/{token}
    Note over URL: Points to CORRECT deployment!
    
    Dev->>Dev: Redeploy backend with new env var
    URL->>User: New share link created
    User->>URL: Click link
    URL-->>User: Shared resume loads successfully!
    
    rect rgb(200, 255, 200)
        Note over Dev,User: Success
        Note right of Dev: Reorder domains in ALLOWED_ORIGINS
        Note right of Config: Correct domain is now at index [0]
        Note right of User: Share links work!
    end
```

## Alternative Solution: Dedicated Config

```mermaid
sequenceDiagram
    autonumber
    participant Dev as Developer
    participant Config as config.py
    participant Env as .env File
    participant Shares as shares.py
    participant URL as Share URL

    Note over Dev,URL: Alternative: Dedicated SHARE_BASE_URL Config

    Dev->>Config: Add SHARE_BASE_URL field
    activate Config
    Config->>Config: SHARE_BASE_URL: str = Field(<br/>default="http://localhost:3000",<br/>description="Base URL for share links"<br/>)
    Config->>Config: @property def share_base_url(self)
    deactivate Config
    
    Dev->>Env: Set SHARE_BASE_URL env var
    Env->>Env: SHARE_BASE_URL=https://resumate-frontend-three.vercel.app
    
    Config->>Env: Load SHARE_BASE_URL
    Config-->>Shares: settings.share_base_url
    
    Shares->>Shares: Use dedicated config
    Shares->>URL: share_url = settings.share_base_url + "/shared/" + token
    URL-->>URL: https://resumate-frontend-three.vercel.app/shared/{token}
    
    Note over Dev,URL: Benefits: Explicit configuration<br/>Independent of CORS origins<br/>Clearer intent
```

