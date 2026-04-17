# Supabase Database Configuration

## Project Details

| Property | Value |
|----------|-------|
| Project URL | https://piqltpksqaldndikmaob.supabase.co |
| Region | ap-northeast-2 (Tokyo) |
| Database Version | PostgreSQL 17.6 |

## Connection Endpoints

### Direct Connection (not recommended for serverless)
```
postgresql://postgres:[PASSWORD]@db.piqltpksqaldndikmaob.supabase.co:5432/postgres
```

### Pooler Connection (recommended)
```
# Transaction mode (for SQLAlchemy, serverless)
postgresql://postgres:[PASSWORD]@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres?ssl=require

# Session mode (for long-running transactions, admin tasks)
postgresql://postgres:[PASSWORD]@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres?ssl=require
```

## Local Development Configuration

Update `backend/.env` with the following:

```bash
# Async (for SQLAlchemy)
DATABASE_URL=postgresql+asyncpg://postgres.piqltpksqaldndikmaob:[PASSWORD]@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres?ssl=require

# Sync (for Alembic migrations)
DATABASE_URL_SYNC=postgresql://postgres.piqltpksqaldndikmaob:[PASSWORD]@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres?ssl=require

USE_DATABASE=true
```

## Tables

| Table | Description |
|-------|-------------|
| `resumes` | Uploaded resume metadata |
| `parsed_resume_data` | Extracted resume data |
| `resume_corrections` | User corrections to parsed data |
| `resume_shares` | Share tokens for resume sharing |
| `alembic_version` | Database migration tracking |

## Testing Connection

```bash
cd backend
python scripts/test_supabase_connection.py
```

## Production Configuration

The same pooler endpoint is used in Render production environment. See `docs/render.md` for production environment variables.

## Security Notes

1. **RLS Warning**: The `alembic_version` table shows an RLS warning in Supabase dashboard. This is expected and safe - it's an internal migration tracking table.
2. **Password**: The database password is stored in Render environment variables, not in this repository.
3. **SSL**: Always use `?ssl=require` for connections.
