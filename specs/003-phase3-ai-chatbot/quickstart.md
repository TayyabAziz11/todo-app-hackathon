# Quickstart Guide: AI-Powered Todo Chatbot (Phase 3)

**Feature**: `003-phase3-ai-chatbot`
**Created**: 2026-01-21
**Purpose**: Step-by-step guide for local development and testing of Phase 3

---

## Prerequisites

Before starting Phase 3 development, ensure you have completed Phase 1 and Phase 2:

✅ **Phase 1/2 Requirements**:
- Python 3.11+ installed
- Node.js 18+ installed
- PostgreSQL database (Neon Serverless PostgreSQL)
- Backend API running (FastAPI from Phase 1/2)
- Frontend UI running (Next.js from Phase 2)
- Better Auth configured and working
- User authentication with JWT tokens functional

✅ **New Dependencies for Phase 3**:
- OpenAI API key (for OpenAI Agents SDK)
- MCP SDK Python package
- OpenAI Agents SDK Python package
- OpenAI ChatKit npm package

---

## Step 1: Environment Setup

### 1.1 Backend Environment Variables

Create or update `backend/.env` with Phase 3 variables:

```bash
# Existing from Phase 1/2
DATABASE_URL=postgresql://user:password@host:5432/database
BETTER_AUTH_SECRET=your_jwt_secret_key_here

# NEW for Phase 3
OPENAI_API_KEY=sk-your-openai-api-key-here
PORT=7860  # Hugging Face Spaces default port

# Optional
LOG_LEVEL=INFO
AGENT_MODEL=gpt-4  # or gpt-4-turbo
MAX_AGENT_TURNS=10
```

**How to get OPENAI_API_KEY**:
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy and paste into `.env`

### 1.2 Frontend Environment Variables

Create or update `frontend/.env.local` with Phase 3 variables:

```bash
# Existing from Phase 2
NEXT_PUBLIC_API_URL=http://localhost:7860
BETTER_AUTH_URL=http://localhost:3000

# NEW for Phase 3
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your_domain_key_here
```

**How to get NEXT_PUBLIC_OPENAI_DOMAIN_KEY**:
1. Go to https://platform.openai.com/settings/organization/security/domain-allowlist
2. Add `localhost` to the allowlist (if testing locally)
3. Generate domain key
4. Copy and paste into `.env.local`

**⚠️ CRITICAL**: Domain allowlist MUST be configured or ChatKit widget won't render.

---

## Step 2: Install Dependencies

### 2.1 Backend Dependencies

```bash
cd backend

# Install Phase 3 Python packages
pip install openai-agents mcp python-jose[cryptography]

# Verify installation
python -c "import openai_agents; import mcp; print('Dependencies installed successfully')"
```

**Requirements additions** (`backend/requirements.txt`):
```
openai-agents>=0.1.0
mcp>=0.1.0
python-jose[cryptography]>=3.3.0
```

### 2.2 Frontend Dependencies

```bash
cd frontend

# Install Phase 3 npm packages
npm install @openai/chatkit

# Verify installation
npm list @openai/chatkit
```

**Package.json additions**:
```json
{
  "dependencies": {
    "@openai/chatkit": "^1.0.0"
  }
}
```

---

## Step 3: Database Migration

### 3.1 Generate Migration

```bash
cd backend

# Auto-generate migration from SQLModel changes
alembic revision --autogenerate -m "add conversation tables"
```

This creates a new migration file in `backend/alembic/versions/` with SQL to:
- Create `conversations` table
- Create `messages` table
- Add indexes (composite index on `conversation_id, created_at`)
- Add foreign key constraints

### 3.2 Review Migration

**IMPORTANT**: Always review auto-generated migrations before applying.

```bash
# Open the generated migration file
cat alembic/versions/xxx_add_conversation_tables.py
```

**Check for**:
- ✅ `conversations` table created with correct columns
- ✅ `messages` table created with correct columns
- ✅ Composite index on `(conversation_id, created_at)`
- ✅ Foreign keys to `users` and `conversations` tables
- ✅ Cascade delete rules

### 3.3 Apply Migration

```bash
# Apply migration to database
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
# Should show: conversations, messages, tasks, users
```

### 3.4 Rollback (if needed)

```bash
# Rollback last migration
alembic downgrade -1

# Verify tables removed
psql $DATABASE_URL -c "\dt"
```

---

## Step 4: Backend Startup

### 4.1 Start FastAPI Server

```bash
cd backend

# Start with reload for development
uvicorn app.main:app --host 0.0.0.0 --port 7860 --reload
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:7860
INFO:     MCP server initialized with 5 tools
INFO:     Agent system prompt loaded (7250 characters)
INFO:     Database connection pool created
```

### 4.2 Verify Backend Health

Open browser to http://localhost:7860/docs

**Check**:
- ✅ Swagger UI loads
- ✅ `/api/{user_id}/chat` endpoint visible
- ✅ POST method with request/response schemas

**Test Authentication**:
1. Get JWT token from Better Auth login
2. Click "Authorize" in Swagger UI
3. Enter: `Bearer <your_jwt_token>`
4. Try POST `/api/{user_id}/chat` with test message

---

## Step 5: Frontend Startup

### 5.1 Start Next.js Development Server

```bash
cd frontend

npm run dev
```

**Expected Output**:
```
ready - started server on 0.0.0.0:3000
info  - Using webpack 5
```

### 5.2 Verify Frontend

Open browser to http://localhost:3000

**Check**:
- ✅ Login page loads (from Phase 2)
- ✅ Login with test user works
- ✅ Navigate to `/chat` route
- ✅ ChatKit component renders (if implemented)

**⚠️ Troubleshooting**: If ChatKit doesn't render:
1. Check browser console for errors
2. Verify `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` is set
3. Verify `localhost` is in OpenAI domain allowlist
4. Check network tab for failed API calls

---

## Step 6: Test Chat Interface

### 6.1 First Message (New Conversation)

**Action**: Send message in chat UI or via curl

```bash
curl -X POST http://localhost:7860/api/{user_id}/chat \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries"
  }'
```

**Expected Response**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "I've created the task 'Buy groceries' for you. It's been added to your task list.",
  "tool_calls": [
    {
      "tool": "add_task",
      "arguments": {
        "user_id": "user_abc123",
        "title": "Buy groceries",
        "description": ""
      },
      "result": {
        "success": true,
        "task": {
          "id": 1,
          "title": "Buy groceries",
          "completed": false
        }
      }
    }
  ]
}
```

**Verification**:
- ✅ `conversation_id` is a valid UUID
- ✅ `message` is conversational (not raw JSON)
- ✅ `tool_calls` array shows add_task was called
- ✅ Task appears in database

### 6.2 Continue Conversation

**Action**: Send another message with same `conversation_id`

```bash
curl -X POST http://localhost:7860/api/{user_id}/chat \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show my tasks",
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Expected Response**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "You have 1 pending task:\n1. Buy groceries",
  "tool_calls": [
    {
      "tool": "list_tasks",
      "arguments": {
        "user_id": "user_abc123",
        "status": "all"
      },
      "result": {
        "success": true,
        "tasks": [
          {
            "id": 1,
            "title": "Buy groceries",
            "completed": false
          }
        ]
      }
    }
  ]
}
```

**Verification**:
- ✅ Same `conversation_id` returned
- ✅ Agent has context from previous message
- ✅ list_tasks tool called with user_id

### 6.3 Test Multi-Step Operation

**Action**: Send complex request requiring tool chaining

```bash
curl -X POST http://localhost:7860/api/{user_id}/chat \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show my tasks and complete the first one",
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Expected Response**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "You have 1 task. I've marked 'Buy groceries' as complete.",
  "tool_calls": [
    {
      "tool": "list_tasks",
      "arguments": { "user_id": "user_abc123", "status": "pending" },
      "result": { "success": true, "tasks": [...] }
    },
    {
      "tool": "complete_task",
      "arguments": { "user_id": "user_abc123", "task_id": 1 },
      "result": { "success": true, "task": { "id": 1, "completed": true } }
    }
  ]
}
```

**Verification**:
- ✅ Two tools called in sequence
- ✅ Agent used result from first tool to inform second tool call
- ✅ Response is conversational and summarizes both actions

---

## Step 7: Verify Stateless Architecture

### 7.1 Server Restart Test

**Purpose**: Prove conversation resume works after backend restart

**Steps**:
1. Start backend and create conversation with 3 messages
2. Note the `conversation_id`
3. **Stop backend server** (Ctrl+C)
4. **Restart backend server**
5. Send new message with same `conversation_id`
6. Verify agent has full context from messages 1-3

**Expected Behavior**: Agent responds with context from previous messages, proving conversation history was loaded from database (not in-memory state).

**Example**:
```bash
# Message 1
curl ... -d '{"message": "Add task to buy milk"}'
# Response: conversation_id = "abc123"

# Message 2
curl ... -d '{"message": "What tasks do I have?", "conversation_id": "abc123"}'
# Response: "You have 1 task: Buy milk"

# RESTART SERVER HERE

# Message 3
curl ... -d '{"message": "Mark it as done", "conversation_id": "abc123"}'
# Response: "I've completed 'Buy milk'" (agent knows which task from context)
```

### 7.2 Horizontal Scaling Test (Optional)

**Purpose**: Prove any backend instance can handle any request

**Steps**:
1. Start two backend instances on different ports (7860, 7861)
2. Send message 1 to instance 1 (port 7860)
3. Send message 2 to instance 2 (port 7861) with same `conversation_id`
4. Verify message 2 has context from message 1

**Expected Behavior**: Both instances use same database; conversation continues seamlessly.

---

## Step 8: Manual Validation Scenarios

### Scenario 1: Natural Language Task Creation

**User Messages**:
- "Add a task to buy groceries"
- "Remind me to call mom tomorrow"
- "I need to finish the report"

**Verify**:
- ✅ Tasks created with extracted titles
- ✅ Agent confirms with specific task details
- ✅ tool_calls show add_task invocations

### Scenario 2: Conversational Task Querying

**User Messages**:
- "Show my tasks"
- "What do I need to do today?"
- "What have I completed?"

**Verify**:
- ✅ Agent returns task list in conversational format
- ✅ Agent handles empty task list gracefully
- ✅ Agent filters by status when requested

### Scenario 3: Context-Aware Completion

**User Messages**:
1. "Add task to buy groceries"
2. "I finished buying groceries"

**Verify**:
- ✅ Agent finds task by title match (without explicit ID)
- ✅ Agent completes correct task
- ✅ Agent confirms specific task completed

### Scenario 4: Error Handling

**User Messages**:
- "Complete task 9999" (non-existent ID)
- "Delete the shopping task" (when no task matches)

**Verify**:
- ✅ Agent returns friendly error (not raw JSON)
- ✅ Agent suggests alternative actions
- ✅ tool_calls show success=false with error message

---

## Step 9: Database Verification

### 9.1 Check Conversations Table

```sql
SELECT * FROM conversations WHERE user_id = 'user_abc123';
```

**Expected**:
- ✅ Conversation exists with correct user_id
- ✅ created_at and updated_at timestamps set
- ✅ title is null (or auto-generated)

### 9.2 Check Messages Table

```sql
SELECT role, content, created_at
FROM messages
WHERE conversation_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY created_at ASC;
```

**Expected**:
- ✅ Messages ordered chronologically
- ✅ Alternating user/assistant roles
- ✅ tool_calls JSON populated for assistant messages

### 9.3 Check Tasks Table

```sql
SELECT id, title, completed FROM tasks WHERE user_id = 'user_abc123';
```

**Expected**:
- ✅ Tasks created via chat interface appear
- ✅ Completed tasks show completed=true
- ✅ No tasks from other users visible

---

## Step 10: Troubleshooting Common Issues

### Issue: ChatKit Widget Doesn't Render

**Symptoms**: Blank screen where chat should be, no errors in console

**Solution**:
1. Verify `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` is set
2. Go to https://platform.openai.com/settings/organization/security/domain-allowlist
3. Add your domain (localhost for development)
4. Restart Next.js dev server

### Issue: Agent Not Calling Tools

**Symptoms**: Agent responds but tool_calls array is empty, tasks not created

**Solution**:
1. Check MCP server logs for tool registration
2. Verify agent system prompt includes tool descriptions
3. Test MCP tools directly (bypass agent)
4. Check OpenAI API key is valid

### Issue: "Conversation Not Found" Error

**Symptoms**: 404 error when sending message with conversation_id

**Solutions**:
1. Verify conversation_id is valid UUID
2. Check conversation belongs to authenticated user (user_id mismatch)
3. Verify database migration ran successfully
4. Check PostgreSQL connection

### Issue: "Forbidden: User ID Mismatch"

**Symptoms**: 403 error even with valid JWT token

**Solutions**:
1. Verify JWT token's `sub` claim matches {user_id} path parameter
2. Check token hasn't expired
3. Verify BETTER_AUTH_SECRET matches between services
4. Test JWT decoding manually

### Issue: Server Crashes After Restart

**Symptoms**: Backend won't start after restart, database connection errors

**Solutions**:
1. Check DATABASE_URL is correct
2. Verify PostgreSQL is running
3. Check connection pool limits (max_connections in Postgres config)
4. Review logs for specific error messages

---

## Step 11: Local Development Workflow

### Daily Development Flow

1. **Start Services**:
   ```bash
   # Terminal 1: Backend
   cd backend && uvicorn app.main:app --reload --port 7860

   # Terminal 2: Frontend
   cd frontend && npm run dev
   ```

2. **Make Changes**:
   - Edit code (hot reload enabled)
   - Changes apply automatically

3. **Test Changes**:
   - Use Swagger UI for API testing
   - Use chat interface for end-to-end testing
   - Check database for persistence

4. **Commit Changes**:
   ```bash
   git add .
   git commit -m "feat: implement agent system prompt"
   git push
   ```

### Database Reset (If Needed)

```bash
# Rollback all Phase 3 migrations
cd backend
alembic downgrade -1  # or specific revision

# Re-apply migrations
alembic upgrade head

# Seed test data (optional)
python scripts/seed_test_data.py
```

---

## Step 12: Next Steps

After completing local development and testing:

1. **Phase 2 Implementation**: Begin coding Phase 2 (Foundational Tasks)
2. **User Story Implementation**: Implement US5 → US1 → US2 (MVP)
3. **Frontend Integration**: Integrate ChatKit UI (Phase 10)
4. **Deployment**: Configure for Hugging Face Spaces (Phase 11)
5. **Documentation**: Complete README and demo script (Phase 12)
6. **Validation**: Manual testing against acceptance scenarios (Phase 13)

---

## Quick Reference: Essential Commands

```bash
# Backend
cd backend
uvicorn app.main:app --reload --port 7860
alembic upgrade head
alembic downgrade -1

# Frontend
cd frontend
npm run dev
npm install <package>

# Database
psql $DATABASE_URL
psql $DATABASE_URL -c "\dt"  # List tables
psql $DATABASE_URL -c "SELECT * FROM conversations;"

# Testing
curl -X POST http://localhost:7860/api/{user_id}/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "test message"}'
```

---

## Summary Checklist

Before proceeding to implementation, verify:

- [ ] Environment variables configured (backend + frontend)
- [ ] Dependencies installed (Python + npm packages)
- [ ] Database migration applied successfully
- [ ] Backend starts without errors (port 7860)
- [ ] Frontend starts without errors (port 3000)
- [ ] ChatKit widget renders (domain allowlist configured)
- [ ] First message creates conversation + task
- [ ] Conversation resume works after restart
- [ ] Tool calls visible in response
- [ ] Database tables populated correctly

**Status**: ✅ QUICKSTART COMPLETE - Ready for Phase 2 Implementation

**Next Document**: Agent System Prompt Design (`specs/003-phase3-ai-chatbot/agent-system-prompt.md`)
