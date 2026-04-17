# SHARE_BASE_URL Approach Comparison Diagrams

**Date**: 2026-03-26  
**Purpose**: Visual comparison of configuration approaches

---

## Architecture Comparison

### Before: Implicit Coupling

```mermaid
graph TB
    subgraph "Before Implementation"
        A[ALLOWED_ORIGINS Array]
        B[CORS Middleware]
        C[Share URL Generation]
        D[Exports: WhatsApp, Telegram, Email]
        
        A -->|First element used for| C
        A -->|All elements used for| B
        C --> D
        
        style A fill:#ffcccc
        style C fill:#ffcccc
    end
    
    style A stroke:#ff0000,stroke-width:3px
    style C stroke:#ff0000,stroke-width:3px
```

**Problem**: Share URLs implicitly depend on CORS configuration array ordering

---

### After: Explicit Configuration

```mermaid
graph TB
    subgraph "After Implementation"
        A[ALLOWED_ORIGINS Array]
        B[CORS Middleware]
        C[SHARE_BASE_URL Optional]
        D[Share URL Generator]
        E[Exports: WhatsApp, Telegram, Email]
        
        A -->|All elements| B
        C -->|Explicit or fallback| D
        D --> E
        
        F{Fallback Logic}
        G[Priority 1: SHARE_BASE_URL]
        H[Priority 2: ALLOWED_ORIGINS[0]]
        I[Priority 3: localhost:3000]
        
        D --> F
        F --> G
        G -->|Not set| H
        H -->|Not set| I
        
        style C fill:#90EE90
        style D fill:#90EE90
        style F fill:#87CEEB
    end
    
    style C stroke:#00aa00,stroke-width:3px
    style D stroke:#00aa00,stroke-width:3px
```

**Solution**: Share URLs have explicit configuration with intelligent fallback

---

## Decision Flow

```mermaid
flowchart TD
    Start[Need Share Base URL] --> Check{SHARE_BASE_URL set?}
    
    Check -->|Yes| Explicit[Use SHARE_BASE_URL]
    Check -->|No| Origins{ALLOWED_ORIGINS has values?}
    
    Origins -->|Yes| Fallback[Use ALLOWED_ORIGINS[0]]
    Origins -->|No| Default[Use localhost:3000]
    
    Explicit --> Return[Return URL]
    Fallback --> Return
    Default --> Return
    
    style Explicit fill:#90EE90
    style Fallback fill:#FFD700
    style Default fill:#FFA500
```

---

## Comparison Matrix

```mermaid
graph LR
    subgraph "Quick Fix"
        Q1[Time: 5 min]
        Q2[Risk: High]
        Q3[Maintainability: Low]
    end
    
    subgraph "Dedicated Config"
        D1[Time: 30 min]
        D2[Risk: Medium]
        D3[Maintainability: High]
    end
    
    subgraph "Hybrid Implemented"
        H1[Time: 45 min]
        H2[Risk: Low]
        H3[Maintainability: High]
        H4[Backward Compatible: Yes]
    end
    
    subgraph "Environment-Specific"
        E1[Time: 2 hours]
        E2[Risk: Medium]
        E3[Maintainability: Medium]
    end
    
    subgraph "Service Discovery"
        S1[Time: 1 week+]
        S2[Risk: Medium]
        S3[Maintainability: High]
    end
```

---

## Scoring Visualization

```mermaid
graph TB
    subgraph "Approach Scores (1-10)"
        Quick[Quick Fix: 4.0]
        Dedicated[Dedicated Config: 7.8]
        Hybrid["Hybrid (Current): 9.0"]
        Env["Environment-Specific: 6.9"]
        Service["Service Discovery: 8.3"]
        
        Quick -->|Score| Q((4.0))
        Dedicated -->|Score| D((7.8))
        Hybrid -->|Score| H((9.0))
        Env -->|Score| E((6.9))
        Service -->|Score| S((8.3))
        
        style Q fill:#ff6b6b
        style D fill:#ffd93d
        style H fill:#6bcf7f
        style E fill:#ffd93d
        style S fill:#6bcf7f
    end
```

---

## Configuration Flow by Environment

```mermaid
flowchart TD
    subgraph Development
        Dev1[.env file]
        Dev2[SHARE_BASE_URL not set]
        Dev3[Fallback to localhost:3000]
        Dev1 --> Dev2
        Dev2 --> Dev3
    end
    
    subgraph Staging
        Stage1[Environment Variables]
        Stage2[SHARE_BASE_URL optional]
        Stage3[Fallback to ALLOWED_ORIGINS[0]]
        Stage1 --> Stage2
        Stage2 -->|If set| Stage4[Use SHARE_BASE_URL]
        Stage2 -->|If not set| Stage3
    end
    
    subgraph Production
        Prod1[Environment Variables]
        Prod2[SHARE_BASE_URL required]
        Prod3[Use explicit value]
        Prod1 --> Prod2
        Prod2 --> Prod3
    end
    
    style Dev3 fill:#90EE90
    style Stage3 fill:#FFD700
    style Stage4 fill:#90EE90
    style Prod3 fill:#90EE90
```

---

## Risk Assessment Matrix

```mermaid
graph TB
    subgraph "Risk vs Probability"
        HighImpactHighProb[High Impact / High Prob: Wrong domain in env]
        HighImpactLowProb[High Impact / Low Prob: Cache issues]
        LowImpactHighProb[Low Impact / High Prob: None identified]
        LowImpactLowProb[Low Impact / Low Prob: Fallback issues]
        
        HighImpactHighProb --> P1[Priority 1: URL Validation]
        HighImpactLowProb --> P2[Priority 2: Health Check]
        LowImpactLowProb --> P3[Priority 3: Monitoring]
        
        style HighImpactHighProb fill:#ff6b6b
        style HighImpactLowProb fill:#ffd93d
        style P1 fill:#ff6b6b
        style P2 fill:#ffd93d
        style P3 fill:#6bcf7f
    end
```

---

## Implementation Timeline

```mermaid
gantt
    title SHARE_BASE_URL Enhancement Timeline
    dateFormat  YYYY-MM-DD
    section Phase 1
    URL Validation      :a1, 2026-03-26, 1d
    Health Check        :a2, after a1, 1d
    
    section Phase 2
    Config Drift Detect :b1, after a2, 2d
    Multi-Env Support   :b2, after b1, 1d
    
    section Phase 3
    Enhanced Logging    :c1, after b2, 1d
    Documentation       :c2, after c1, 2d
```

---

## Configuration Hierarchy

```mermaid
graph TD
    subgraph "Configuration Priority"
        P1[Priority 1: SHARE_BASE_URL<br/>Explicit configuration]
        P2[Priority 2: ALLOWED_ORIGINS[0]<br/>Backward compatibility]
        P3[Priority 3: localhost:3000<br/>Development default]
        
        P1 -->|If set| Use[Use this value]
        P1 -->|If not set| P2
        P2 -->|If has values| Use
        P2 -->|If empty| P3
        P3 --> Use
        
        style P1 fill:#6bcf7f
        style P2 fill:#ffd93d
        style P3 fill:#ff9f43
        style Use fill:#a8e6cf
    end
```

---

**Note**: This document uses Mermaid diagram syntax. Render in any Mermaid-compatible viewer.
