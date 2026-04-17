# Hybrid Approach Implementation - Complete Architecture

> **Updated**: 2026-03-26  
> **Status**: Production Ready  
> **Implementation**: Hybrid SHARE_BASE_URL with Backward Compatibility

## Mermaid Architecture Diagram

```mermaid
flowchart TD
    %% Define styles
    classDef config fill:#fff8e1,stroke:#ff8f00,stroke-width:2px,color:#ff8f00
    classDef logic fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#1976d2
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#2e7d32
    classDef problem fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#c62828

    %% Configuration Layer
    subgraph CONFIG["Configuration Layer"]
        C1[Environment Variables]:::config
        C2[SHARE_BASE_URL Field]:::config
        C3[ALLOWED_ORIGINS Field]:::config
        
        C1 --> C2
        C1 --> C3
        
        C2_VALUE["SHARE_BASE_URL=https://resumate-frontend-three.vercel.app"]:::success
        C3_VALUE["ALLOWED_ORIGINS=https://old.vercel.app,..."]:::problem
        
        C2_VALUE -.-> C2
        C3_VALUE -.-> C3
    end

    %% Logic Layer
    subgraph LOGIC["share_base_url Property Logic"]
        L1[Check 1: Is SHARE_BASE_URL set?]:::logic
        L2{YES}:::logic
        L3[Return SHARE_BASE_URL]:::success
        L4{NO}:::logic
        L5[Check 2: Does ALLOWED_ORIGINS have values?]:::logic
        L6{YES}:::logic
        L7[Return ALLOWED_ORIGINS[0]]:::success
        L8{NO}:::logic
        L9[Return http://localhost:3000]:::success
        
        L1 --> L2
        L2 -->|Yes| L3
        L2 -->|No| L4
        L4 --> L5
        L5 --> L6
        L6 -->|Yes| L7
        L6 -->|No| L8
        L8 --> L9
    end

    %% Usage Layer
    subgraph USAGE["Usage in shares.py"]
        U1[POST /v1/resumes/{id}/share]:::logic
        U2[GET /v1/resumes/{id}/share]:::logic
        U3[WhatsApp Export]:::logic
        U4[Telegram Export]:::logic
        U5[Email Export]:::logic
        
        U1 --> U6["share_url = f\"{settings.share_base_url}/shared/{token}\""]:::success
        U2 --> U6
        U3 --> U7["base_url = settings.share_base_url"]:::success
        U4 --> U7
        U5 --> U7
    end

    %% Connections
    C2 --> L1
    C3 --> L5
    L3 --> U6
    L7 --> U6
    L9 --> U6
```
