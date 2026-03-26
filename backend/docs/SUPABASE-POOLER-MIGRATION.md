# Supabase Pooler Migration Guide

## Quick Reference

### New Connection String Format (2026)

Supabase migrated to regional pooler endpoints. Use this format for ALL new deployments.

### Transaction Pooler (Recommended for Serverless)

```bash
DATABASE_URL="postgresql+asyncpg://postgres.PROJECT_REF:ENCODED_PASSWORD@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres?ssl=require"
DATABASE_URL_SYNC="postgresql://postgres.PROJECT_REF:ENCODED_PASSWORD@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres?ssl=require"
```

### Components

| Component | Value | Notes |
|-----------|-------|-------|
| Protocol | `postgresql+asyncpg://` | Async engine |
| Protocol (sync) | `postgresql://` | Sync for Alembic |
| User | `postgres.PROJECT_REF` | Project-specific! |
| Host | `aws-1-ap-northeast-2.pooler.supabase.com` | Regional endpoint |
| Port | `6543` | Transaction mode |
| Database | `postgres` | Default database |
| SSL | `?ssl=require` | Required by Supabase |

### Migration Steps

1. **Get Current Values from Supabase**:
   - Go to Supabase Dashboard
   - Navigate to: Settings → Database
   - Find "Connection Pooling" section
   - Select "Transaction" mode
   - Copy the connection string

2. **URL-Encode Password**:
   ```python
   from urllib.parse import quote_plus
   password = "your-raw-password"
   encoded = quote_plus(password, safe='')
   # Use encoded password in connection string
   ```

3. **Update Deployment Environment**:
   - Render: Dashboard → Environment → Update variables → Save
   - Vercel: Settings → Environment Variables → Update → Redeploy
   - Local: Update `.env` file

4. **Verify Connection**:
   ```bash
   # Test health endpoint
   curl https://your-backend.onrender.com/health
   
   # Should return:
   {
     "status": "healthy",
     "database": "connected",
     ...
   }
   ```

### Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `[Errno -2] Name or service not known` | Old pooler hostname | Use `aws-1-[region].pooler.supabase.com` |
| `authentication failed` | Wrong username | Use `postgres.PROJECT_REF` not `postgres` |
| `connection refused` | Wrong port | Use `6543` for transaction mode |
| `SSL required` | Missing SSL parameter | Add `?ssl=require` to connection string |

### Region Mapping

Your pooler region depends on your Supabase project region:

| Supabase Region | Pooler Host |
|-----------------|-------------|
| ap-northeast-2 (Tokyo) | `aws-1-ap-northeast-2.pooler.supabase.com` |
| ap-southeast-1 (Singapore) | `aws-1-ap-southeast-1.pooler.supabase.com` |
| us-east-1 (N. Virginia) | `aws-1-us-east-1.pooler.supabase.com` |
| us-west-1 (N. California) | `aws-1-us-west-1.pooler.supabase.com` |
| eu-west-1 (Ireland) | `aws-1-eu-west-1.pooler.supabase.com` |

Check your Supabase dashboard for your specific region.

### Testing Script

Save as `test_supabase_connection.py`:

```python
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

async def test_connection():
    DATABASE_URL = "your-database-url-here"
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        result = await session.execute(text("SELECT version()"))
        print(f"✅ Connected: {result.scalar()}")
    
    await engine.dispose()

asyncio.run(test_connection())
```

### References

- Supabase Docs: https://supabase.com/docs/guides/database/connecting-to-postgres
- Connection Pooling: https://supabase.com/docs/guides/database/connection-pooling
- Render Deployment: See `docs/BUG-FIX-25-RENDER-DEPLOYMENT.md`
