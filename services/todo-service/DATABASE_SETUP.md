# Phase V.4 Database Setup Guide

This service requires PostgreSQL with specific extensions for advanced search functionality.

---

## Quick Start with Docker (Recommended)

### 1. Start PostgreSQL with Docker

```bash
docker run --name todoapp-postgres \
  -e POSTGRES_DB=todoapp_db \
  -e POSTGRES_USER=todoapp \
  -e POSTGRES_PASSWORD=dev_password \
  -p 5432:5432 \
  -d postgres:15

# Wait for PostgreSQL to start (about 5 seconds)
sleep 5
```

### 2. Install Required Extensions

```bash
docker exec -it todoapp-postgres psql -U todoapp -d todoapp_db -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

### 3. Create Dapr State Store Table

```bash
docker exec -it todoapp-postgres psql -U todoapp -d todoapp_db << 'EOF'
CREATE TABLE IF NOT EXISTS dapr_state (
    key VARCHAR(255) PRIMARY KEY,
    value JSONB NOT NULL,
    search_vector tsvector,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- GIN index for full-text search
CREATE INDEX IF NOT EXISTS idx_dapr_state_search
    ON dapr_state USING GIN (search_vector);

-- GIN index for tag queries
CREATE INDEX IF NOT EXISTS idx_dapr_state_value_tags
    ON dapr_state USING GIN ((value->'tags'));

-- B-tree indexes for common queries
CREATE INDEX IF NOT EXISTS idx_dapr_state_user_id
    ON dapr_state ((value->>'user_id'));

CREATE INDEX IF NOT EXISTS idx_dapr_state_completed
    ON dapr_state ((value->>'completed'));

-- Composite index for user + completed queries
CREATE INDEX IF NOT EXISTS idx_dapr_state_user_completed
    ON dapr_state ((value->>'user_id'), (value->>'completed'));
EOF
```

### 4. Verify Setup

```bash
docker exec -it todoapp-postgres psql -U todoapp -d todoapp_db -c "\d dapr_state"
```

You should see the table structure with all indexes.

---

## Alternative: Local PostgreSQL Installation

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### macOS (with Homebrew)

```bash
brew install postgresql@15
brew services start postgresql@15
```

### Create Database and User

```bash
sudo -u postgres psql << 'EOF'
CREATE DATABASE todoapp_db;
CREATE USER todoapp WITH ENCRYPTED PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE todoapp_db TO todoapp;
\c todoapp_db
CREATE EXTENSION IF NOT EXISTS pg_trgm;
\q
EOF
```

Then run the table creation SQL from step 3 above.

---

## Environment Configuration

Update `.env` file in this directory:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=todoapp_db
DB_USER=todoapp
DB_PASSWORD=dev_password
```

---

## Testing Database Connection

```bash
python3 << 'EOF'
import asyncpg
import asyncio

async def test_connection():
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            database='todoapp_db',
            user='todoapp',
            password='dev_password'
        )
        print("✅ Database connection successful!")
        version = await conn.fetchval('SELECT version()')
        print(f"PostgreSQL version: {version}")
        await conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")

asyncio.run(test_connection())
EOF
```

---

## Required Extensions

### pg_trgm (Trigram Similarity)

**Purpose**: Fuzzy string matching for search
**Install**: `CREATE EXTENSION IF NOT EXISTS pg_trgm;`

This extension provides:
- Fuzzy string matching
- Similarity search for typos
- GIN indexes for fast searches

---

## Troubleshooting

### "asyncpg.exceptions.InvalidCatalogNameError: database does not exist"

**Solution**: Create the database first
```bash
sudo -u postgres createdb todoapp_db
# OR with Docker:
docker exec todoapp-postgres createdb -U postgres todoapp_db
```

### "permission denied to create extension"

**Solution**: Connect as superuser
```bash
sudo -u postgres psql -d todoapp_db -c "CREATE EXTENSION pg_trgm;"
# OR with Docker:
docker exec todoapp-postgres psql -U postgres -d todoapp_db -c "CREATE EXTENSION pg_trgm;"
```

### "port 5432 already in use"

**Solution**: Change port in `.env`
```bash
DB_PORT=5433  # Use different port
```

And start PostgreSQL on that port.

---

## Migration from Phase 3 Backend

If you have existing data in the Phase 3 backend (SQLAlchemy + tasks table), you'll need to:

1. Export existing tasks
2. Transform to Dapr state store format
3. Import to new database

Migration script available in `migrations/phase3-to-v4.py` (if needed).

---

## Production Considerations

For production deployments:

- Use managed PostgreSQL (AWS RDS, Google Cloud SQL, Neon, etc.)
- Enable SSL: `DB_SSL_MODE=require`
- Use connection pooling (already handled by asyncpg)
- Set up automated backups
- Monitor connection pool usage
- Use secrets manager for credentials

---

**Quick Setup Summary** (Docker):

```bash
# 1. Start PostgreSQL
docker run -d --name todoapp-postgres \
  -e POSTGRES_DB=todoapp_db -e POSTGRES_USER=todoapp \
  -e POSTGRES_PASSWORD=dev_password -p 5432:5432 postgres:15

# 2. Install extensions
docker exec todoapp-postgres psql -U todoapp -d todoapp_db -c "CREATE EXTENSION pg_trgm;"

# 3. Create table (see step 3 above for full SQL)

# 4. Start service
./start.sh
```

Done! ✅
