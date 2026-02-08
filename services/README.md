# Services Directory

This directory contains microservices for the Todo application.

---

## Current Services

### 1. Todo Service (Phase V.4)

**Location**: `todo-service/`
**Port**: 8001
**Status**: ✅ Ready to start

**Purpose**: Advanced search, tag management, priority filtering, due dates

**Endpoints**:
- `GET /api/v1/todos/search` - Advanced search with 13+ filters
- `GET /tags` - List all unique tags
- `GET /api/v1/tags/autocomplete` - Tag suggestions
- `GET /api/v1/tags/popular` - Most-used tags

**Quick Start**:
```bash
cd todo-service

# 1. Set up PostgreSQL (see DATABASE_SETUP.md)
docker run -d --name todoapp-postgres \
  -e POSTGRES_DB=todoapp_db -e POSTGRES_USER=todoapp \
  -e POSTGRES_PASSWORD=dev_password -p 5432:5432 postgres:15

# 2. Install extensions and create table (see DATABASE_SETUP.md)

# 3. Start service
./start.sh
```

**Documentation**:
- `DATABASE_SETUP.md` - Database setup guide
- `docs/phase-v4-progress/` - Phase V.4 progress

**Used By**: Frontend `/dashboard-v4` route

---

## Service Architecture

```
Frontend (port 3000)
    │
    ├─ /dashboard-v4 → Todo Service (port 8001)
    │                   ├─ Advanced search
    │                   ├─ Tag management
    │                   ├─ Priority filtering
    │                   └─ Due dates
    │
    └─ /chat → Chatbot Backend (port 8000)
                ├─ AI conversations
                ├─ MCP tools
                └─ Basic task CRUD
```

---

## Service Separation

### Todo Service (Phase V.4) vs Chatbot Backend (Phase 3)

| Feature | Todo Service (8001) | Chatbot Backend (8000) |
|---------|---------------------|------------------------|
| **Purpose** | Advanced search & filtering | AI chatbot & MCP tools |
| **Database** | PostgreSQL (Dapr state) | PostgreSQL (direct tables) |
| **Storage** | asyncpg | SQLAlchemy |
| **Search** | Full-text + fuzzy | Basic query |
| **Tags** | Full management API | Not supported |
| **Priority** | Filter & sort | Not supported |
| **Due Dates** | Smart status calculation | Not supported |
| **Frontend Route** | `/dashboard-v4` | `/chat` |

**Why Separate?**
- Different storage patterns (Dapr vs direct)
- Different features (search vs chat)
- Independent scaling
- Clear boundaries

---

## Development Workflow

### Starting All Services

**Terminal 1**: PostgreSQL
```bash
docker run -d --name todoapp-postgres \
  -e POSTGRES_DB=todoapp_db -e POSTGRES_USER=todoapp \
  -e POSTGRES_PASSWORD=dev_password -p 5432:5432 postgres:15
```

**Terminal 2**: Todo Service (Phase V.4)
```bash
cd services/todo-service
./start.sh
```

**Terminal 3**: Chatbot Backend (Phase 3)
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 4**: Frontend
```bash
cd frontend
npm run dev
```

**Access**:
- Frontend: http://localhost:3000
- Dashboard V4: http://localhost:3000/dashboard-v4 (uses Todo Service)
- Chat: http://localhost:3000/chat (uses Chatbot Backend)

---

## Environment Configuration

### Todo Service

**File**: `todo-service/.env`
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=todoapp_db
DB_USER=todoapp
DB_PASSWORD=dev_password
SERVICE_PORT=8001
```

### Frontend

**File**: `frontend/.env.local`
```bash
# Todo Service endpoint
NEXT_PUBLIC_API_BASE_URL=http://localhost:8001

# Chatbot endpoint
NEXT_PUBLIC_CHAT_API_URL=http://localhost:8000
```

---

## Troubleshooting

### "Connection refused on port 8001"

**Cause**: Todo Service not started

**Solution**:
```bash
cd services/todo-service
./start.sh
```

### "Frontend shows 404 for /api/v1/todos/search"

**Cause**: Frontend not pointing to correct backend

**Solution**:
```bash
# Check frontend/.env.local
grep NEXT_PUBLIC_API_BASE_URL frontend/.env.local
# Should show: http://localhost:8001

# If not, update and restart frontend
cd frontend
npm run dev
```

### "Database connection failed"

**Cause**: PostgreSQL not running or wrong credentials

**Solution**:
```bash
# Check PostgreSQL
docker ps | grep todoapp-postgres

# Start if not running
docker start todoapp-postgres

# Or create new
docker run -d --name todoapp-postgres \
  -e POSTGRES_DB=todoapp_db -e POSTGRES_USER=todoapp \
  -e POSTGRES_PASSWORD=dev_password -p 5432:5432 postgres:15
```

---

## Future Services (Planned)

### User Service
- Authentication
- User profiles
- Notification preferences

### Notification Service
- Email reminders
- Push notifications
- Notification history

### Analytics Service
- Usage metrics
- Completion trends
- Insights generation

### Audit Service
- Event logging
- Compliance tracking
- Audit trail

---

**For detailed setup**: See `todo-service/DATABASE_SETUP.md` and `docs/phase-v4-progress/v4-t007-backend-activation.md`
