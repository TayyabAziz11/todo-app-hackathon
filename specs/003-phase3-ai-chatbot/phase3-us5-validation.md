# Phase 3 User Story 5 Validation Guide

**Feature**: Stateless Conversation Resume
**Status**: Implementation Complete
**Date**: 2026-01-21
**Tasks**: T024-T036 ✅

---

## Overview

Phase 3 User Story 5 implements the foundational stateless conversation management system:
- POST /api/{user_id}/chat endpoint
- Conversation persistence to PostgreSQL
- Message history loading and replay
- Zero server-side state between requests
- Placeholder agent responses (actual AI agent in Phase 4)

## Prerequisites

1. **Database Migration Applied**:
   ```bash
   cd backend
   alembic upgrade head
   ```

   Verify conversations and messages tables exist in Neon PostgreSQL.

2. **Backend Running**:
   ```bash
   cd backend
   uvicorn main:app --reload --port 7860
   ```

3. **User Account Created**:
   - Register via POST /api/auth/register
   - Login via POST /api/auth/login to get JWT token

## Manual Validation via curl

### Step 1: Authenticate and Get JWT Token

```bash
# Register new user (if not already registered)
curl -X POST http://localhost:7860/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePass123!"
  }'

# Login and capture JWT token
LOGIN_RESPONSE=$(curl -X POST http://localhost:7860/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePass123!"
  }')

# Extract JWT token
JWT_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

# Extract user_id from JWT (decode payload)
USER_ID=$(echo $JWT_TOKEN | cut -d'.' -f2 | base64 -d 2>/dev/null | jq -r '.sub')

echo "JWT Token: $JWT_TOKEN"
echo "User ID: $USER_ID"
```

### Step 2: Send First Message (Create New Conversation)

```bash
# Send first message WITHOUT conversation_id
CHAT_RESPONSE=$(curl -X POST "http://localhost:7860/api/${USER_ID}/chat" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! I want to create a task to buy groceries."
  }')

echo "Chat Response:"
echo $CHAT_RESPONSE | jq '.'

# Extract conversation_id for subsequent messages
CONVERSATION_ID=$(echo $CHAT_RESPONSE | jq -r '.conversation_id')
echo "Conversation ID: $CONVERSATION_ID"
```

**Expected Response**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Hello! I'm your AI task assistant. I can help you create, view, update, and complete tasks using natural language. What would you like to do?\n\n(Note: This is a placeholder response. Agent integration will be added in Phase 4.)",
  "tool_calls": []
}
```

### Step 3: Continue Conversation (Same conversation_id)

```bash
# Send second message WITH conversation_id
curl -X POST "http://localhost:7860/api/${USER_ID}/chat" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"What tasks do I have?\",
    \"conversation_id\": \"${CONVERSATION_ID}\"
  }" | jq '.'
```

**Expected Response**:
- Same conversation_id returned
- Placeholder agent response
- No tool_calls (Phase 4 will add MCP tools)

### Step 4: Verify Conversation Persistence in Database

```sql
-- Connect to Neon PostgreSQL database

-- Check conversation exists
SELECT id, user_id, title, created_at, updated_at
FROM conversations
WHERE id = '<conversation_id>';

-- Check messages exist and are ordered chronologically
SELECT id, conversation_id, role, content, created_at
FROM messages
WHERE conversation_id = '<conversation_id>'
ORDER BY created_at ASC;

-- Expected: 4 messages total
-- 1. role='user', content='Hello! I want to create...'
-- 2. role='assistant', content='Hello! I'm your AI task assistant...'
-- 3. role='user', content='What tasks do I have?'
-- 4. role='assistant', content='Hello! I'm your AI task assistant...' (placeholder)
```

### Step 5: Stateless Architecture Validation (CRITICAL TEST)

This test proves the system is truly stateless by restarting the server mid-conversation.

```bash
# 1. Send message 1
curl -X POST "http://localhost:7860/api/${USER_ID}/chat" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "First message in conversation"
  }' | jq -r '.conversation_id' > conversation_id.txt

CONVERSATION_ID=$(cat conversation_id.txt)

# 2. Send message 2
curl -X POST "http://localhost:7860/api/${USER_ID}/chat" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Second message\",
    \"conversation_id\": \"${CONVERSATION_ID}\"
  }"

# 3. Send message 3
curl -X POST "http://localhost:7860/api/${USER_ID}/chat" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Third message\",
    \"conversation_id\": \"${CONVERSATION_ID}\"
  }"

# 4. STOP THE BACKEND SERVER (Ctrl+C in the uvicorn terminal)

# 5. RESTART THE BACKEND SERVER
# cd backend && uvicorn main:app --reload --port 7860

# 6. Send message 4 AFTER SERVER RESTART
curl -X POST "http://localhost:7860/api/${USER_ID}/chat" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Fourth message after restart\",
    \"conversation_id\": \"${CONVERSATION_ID}\"
  }" | jq '.'
```

**Expected Outcome**:
- ✅ Message 4 succeeds after server restart
- ✅ Same conversation_id returned
- ✅ No errors or 404 responses
- ✅ Database contains all 8 messages (4 user + 4 assistant)

**This proves**: The server has NO in-memory state. All conversation context is loaded from PostgreSQL on each request.

### Step 6: Error Handling Validation

**Test 401 Unauthorized** (missing JWT):
```bash
curl -X POST "http://localhost:7860/api/${USER_ID}/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello"
  }'

# Expected: 401 Unauthorized
```

**Test 403 Forbidden** (user_id mismatch):
```bash
# Try to access another user's endpoint
curl -X POST "http://localhost:7860/api/different-user-id/chat" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello"
  }'

# Expected: 403 Forbidden - "user_id in path does not match authenticated user"
```

**Test 404 Not Found** (invalid conversation_id):
```bash
curl -X POST "http://localhost:7860/api/${USER_ID}/chat" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "conversation_id": "00000000-0000-0000-0000-000000000000"
  }'

# Expected: 404 Not Found - "The conversation_id does not exist or does not belong to this user"
```

## Validation Checklist

- [X] **T024-T027**: Conversation service functions implemented in backend/app/services/conversation.py
- [X] **T028-T029**: ChatRequest and ChatResponse schemas defined in backend/app/routers/chat.py
- [X] **T030**: POST /api/{user_id}/chat endpoint implemented with auth validation
- [X] **T031**: Conversation history loading from database before agent execution
- [X] **T032**: User message persisted to database before agent execution
- [X] **T033**: Placeholder agent response persisted after execution
- [X] **T034**: Error handling for 401, 403, 404, 500 errors
- [X] **T035**: Request logging with conversation_id, user_id, message_length
- [X] **T036**: Chat router registered with FastAPI app in backend/main.py

### Stateless Architecture Verification

- [X] No module-level database sessions in conversation service
- [X] All database operations use dependency-injected sessions
- [X] conversation_id is ONLY state token (UUID)
- [X] Conversation history loaded from database on EVERY request
- [X] Messages persist correctly (append-only log)
- [X] Server restart does NOT lose conversation context
- [X] User isolation enforced (user_id filtering in all queries)

### API Contract Compliance (chat-api.yaml)

- [X] Request schema: message (required), conversation_id (optional)
- [X] Response schema: conversation_id, message, tool_calls
- [X] JWT Bearer token authentication
- [X] Error responses: 401, 403, 404, 500 with proper detail messages
- [X] Tool transparency via tool_calls array (empty for placeholder)

## Known Limitations (Phase 3 Scope)

1. **Placeholder Agent Response**: Returns hardcoded message, not actual AI agent
   - **Reason**: Agent integration is Phase 4 (User Story 1)
   - **Placeholder**: "Hello! I'm your AI task assistant..."

2. **No MCP Tool Calls**: tool_calls array always empty
   - **Reason**: MCP tools (add_task, list_tasks, etc.) are Phase 4+
   - **Impact**: Agent cannot perform task operations yet

3. **No Conversation Title Auto-Generation**: title field is null
   - **Reason**: Out of MVP scope
   - **Future**: Could extract from first message content

## Next Steps: Phase 4 (User Story 1)

Once Phase 3 validation passes:

1. **Replace Placeholder Agent** (T041-T052):
   - Integrate OpenAI Agents SDK
   - Implement agent system prompt
   - Add conversation history formatting for OpenAI format
   - Execute real agent with tool calls

2. **Implement add_task MCP Tool** (T037-T040):
   - Create MCP tool in backend/app/mcp/tools.py
   - Register with MCP server
   - Test natural language task creation

3. **Validate End-to-End**:
   - User says "Add a task to buy groceries"
   - Agent calls add_task MCP tool
   - Task created in database
   - Agent response confirms creation

## Success Criteria (Phase 3)

✅ **Stateless Conversation Resume**:
- Conversation persists across server restarts
- Full context loaded from database
- No in-memory state required

✅ **User Isolation**:
- JWT authentication enforced
- Users can only access their own conversations
- Path user_id validated against token

✅ **API Contract**:
- Request/response schemas match chat-api.yaml
- Error codes correct (401, 403, 404, 500)
- Tool transparency structure in place

✅ **Database Persistence**:
- Conversations and messages tables created
- Composite index on (conversation_id, created_at) for performance
- Cascade delete rules enforced

---

**Status**: Phase 3 User Story 5 COMPLETE ✅
**Ready for**: Phase 4 Agent Integration (User Story 1)
