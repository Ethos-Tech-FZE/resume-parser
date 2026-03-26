# ResuMate Development Progress

> Last Updated: 2026-03-26

---

## Bug Fix #26 - Supabase Pooler Connection Format (2026-03-26)

### Problem
Render deployment failed with DNS resolution error:
```
Health check: database unavailable - [Errno -2] Name or service not known
```

### Root Cause
Supabase migrated pooler endpoints from project-specific format to regional format:

**Old Format (Deprecated)**:
- Host: `[project-ref]-pooler.supabase.co`
- User: `postgres`
- Example: `piqltpksqaldndikmaob-pooler.supabase.co`

**New Format (Current)**:
- Host: `aws-1-[region].pooler.supabase.com`
- User: `postgres.[project-ref]`
- Example: `aws-1-ap-northeast-2.pooler.supabase.com`

The old hostname no longer exists in DNS, causing connection failures.

### Solution

Updated Render environment variables with correct connection strings:

```bash
# DATABASE_URL (Async)
DATABASE_URL="postgresql+asyncpg://postgres.piqltpksqaldndikmaob:j%3CTN%7DXs%2Aph%25%3D%7B%3Enb8L.w%5CclD%260C%24W7%21q%3FM%27%3A%5DKt5@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres?ssl=require"

# DATABASE_URL_SYNC (Sync for Alembic)
DATABASE_URL_SYNC="postgresql://postgres.piqltpksqaldndikmaob:j%3CTN%7DXs%2Aph%25%3D%7B%3Enb8L.w%5CclD%260C%24W7%21q%3FM%27%3A%5DKt5@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres?ssl=require"
```

### Key Changes
| Component | Before | After |
|-----------|--------|-------|
| Host | `piqltpksqaldndikmaob-pooler.supabase.co` | `aws-1-ap-northeast-2.pooler.supabase.com` |
| User | `postgres` | `postgres.piqltpksqaldndikmaob` |
| Port | `6543` | `6543` (unchanged) |
| Password | URL-encoded | URL-encoded (unchanged) |
| SSL | `?ssl=require` | `?ssl=require` (unchanged) |

### Testing
Created test script to validate connection before deployment:
```bash
cd backend
source .venv/bin/activate
python /tmp/test_supabase_connection.py
```

Result: ✅ Connected successfully to PostgreSQL 17.6

### Verification Steps
1. Update Render environment variables
2. Click "Save Changes" (triggers automatic redeploy)
3. Monitor logs: `/health` should show `{"database": "connected"}`
4. Verify application stays running

### Status
- ✅ Connection tested locally
- ⏳ Awaiting Render deployment update
- 📝 Documented in CLAUDE.md (pending)

### Lessons Learned
- Supabase connection pooler format changed to regional endpoints
- Always verify current format in Supabase dashboard
- Use project-specific username: `postgres.[project-ref]`
- Test connection strings before deploying to production

### References
- Test script: `/tmp/test_supabase_connection.py`
- Supabase Dashboard: Settings > Database > Connection String

---

## Previous Fixes (See CLAUDE.md for details)

- Bug Fix #18-25: Vercel/Render deployment issues, Python 3.12 compatibility, bundle optimization

---

## Bug Fix #27 - PgBouncer Transaction Mode Compatibility (2026-03-26)

### Problem
After fixing the DNS resolution issue (#26), Render deployment failed with:
```
InvalidSQLStatementNameError: prepared statement "__asyncpg_stmt_52__" does not exist
```

### Root Cause
**PgBouncer Transaction Mode Limitation**:
- Supabase uses PgBouncer with `pool_mode=transaction`
- Transaction mode doesn't support PostgreSQL prepared statements
- asyncpg uses prepared statements by default (for performance)
- This incompatibility causes the prepared statement error

### Solution
Disable asyncpg's statement cache by adding `statement_cache_size=0` to engine creation.

**File Changed**: `app/core/database.py`

```python
engine_kwargs = {
    "echo": echo,
    "pool_pre_ping": pool_pre_ping,
    "pool_size": pool_size,
    "max_overflow": max_overflow,
    # Pass connect_args for asyncpg configuration
    "connect_args": {
        # Required for Supabase PgBouncer transaction mode
        # Disables asyncpg statement cache to avoid prepared statement errors
        "statement_cache_size": 0,
        "server_settings": {"jit": "off"}  # Improve query planning
    },
}
```

### Why This Works
1. **Forces simple query protocol**: asyncpg won't use prepared statements
2. **Compatible with transaction mode**: No prepared statement dependencies
3. **Minimal performance impact**: Statement cache only helps with repeated queries
4. **Serverless-friendly**: Connection lifetime is short anyway

### Testing
```bash
cd backend
source .venv/bin/activate
python test_pg_bouncer.py
```

Results:
- ✅ Simple query: `SELECT 1` 
- ✅ Version check: PostgreSQL 17.6
- ✅ Multiple sequential queries: 5/5 passed
- ✅ Connection pooling: Working

### Deployment
- **Commit**: `a23eeb8` - "fix: disable asyncpg statement cache for PgBouncer transaction mode"
- **Push**: `main` branch
- **Render**: Auto-deployment triggered

### Expected Outcome
After Render deployment completes, health checks should show:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0",
  "environment": "production"
}
```

### Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `InvalidSQLStatementNameError` | Missing `statement_cache_size=0` | Add to `connect_args` |
| `TypeError: Invalid argument` | Wrong parameter placement | Use `connect_args` dict |
| Connection still fails | Not using transaction pooler | Verify port 6543 |

### References
- asyncpg issue #523: https://github.com/magicstack/asyncpg/issues/523
- Supabase connection pooling: https://supabase.com/docs/guides/database/connection-pooling
- PgBouncer documentation: https://www.pgbouncer.org/usage.html

### Status
- ✅ Fix implemented locally
- ✅ Tests passing
- ✅ Committed to git
- ✅ Pushed to main
- ⏳ Render deployment in progress
- 📝 Documented

### Lessons Learned
- Supabase transaction pooler requires `statement_cache_size=0`
- Parameter must be in `connect_args`, not engine kwargs
- Always test with real Supabase pooler before deploying
- Serverless deployments need transaction mode, not session mode

### Related Fixes
- Bug Fix #26: Supabase pooler migration (regional endpoints)
- Bug Fix #25: Render deployment configuration

