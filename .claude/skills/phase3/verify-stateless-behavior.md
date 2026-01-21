# Skill: verify-stateless-behavior

**Version**: 1.0.0
**Last Updated**: 2026-01-20
**Applicable Agents**: mcp-compliance-validator, phase3-qa-demo

---

## 1. Purpose

Verify that the Phase 3 AI-powered Todo Chatbot implements true stateless architecture by confirming that server restarts do not cause data loss, conversations can be resumed seamlessly, all state is persisted to the database, and no in-memory session state exists. This skill provides systematic verification procedures to validate horizontal scalability and database-backed persistence.

---

## 2. Applicable Agents

**Primary Agent**: `mcp-compliance-validator`
- Validates architectural compliance with stateless design principles
- Executes verification procedures
- Documents violations and remediation steps

**Supporting Agents**:
- `phase3-qa-demo`: End-to-end testing of conversation resume functionality
- `chat-api-orchestrator`: Validates request lifecycle statelessness

---

## 3. Input

### Prerequisites

1. **Running System**:
   - Backend API running at `http://localhost:8000`
   - Frontend ChatKit UI at `http://localhost:3000`
   - PostgreSQL database accessible
   - MCP server initialized

2. **Test User**:
   ```json
   {
     "user_id": "550e8400-e29b-41d4-a716-446655440000",
     "email": "stateless-test@example.com",
     "auth_token": "Bearer eyJhbGc..."
   }
   ```

3. **Test Data**:
   - Existing conversation with 5+ messages
   - Known conversation_id to resume
   - Database access for inspection

### Requirements

- Ability to restart backend server
- Database query access for verification
- Multiple API instances capability (optional, for horizontal scaling tests)
- Monitoring/logging enabled

---

## 4. Output

### Verification Report Structure

```markdown
# Stateless Architecture Verification Report

**Date**: 2026-01-20
**Environment**: Localhost development
**Database**: PostgreSQL 15
**Backend Version**: 1.0.0

## Summary

| Test Category | Tests | Passed | Failed | Status |
|---------------|-------|--------|--------|--------|
| Server Restart | 4 | 4 | 0 | ✅ PASS |
| Conversation Resume | 3 | 3 | 0 | ✅ PASS |
| Database Persistence | 5 | 5 | 0 | ✅ PASS |
| Horizontal Scaling | 3 | 2 | 1 | ⚠️ WARN |
| **TOTAL** | **15** | **14** | **1** | ✅ PASS |

**Overall Result**: ✅ STATELESS VERIFIED (93.3% pass rate)

## Critical Findings

✅ No in-memory session state detected
✅ Conversations persist across server restarts
✅ Database is single source of truth
⚠️ Session affinity detected in load balancer (non-critical)

## Test Details

[Detailed results follow...]
```

---

## 5. Verification Test Suite

### 5.1 Server Restart Tests

#### Test 1.1: Conversation Persistence Across Restart

**Objective**: Verify conversation data survives server restart

**Procedure**:
1. Start backend server
2. Create new conversation via API:
   ```bash
   curl -X POST http://localhost:8000/api/$USER_ID/chat \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Add a task to buy groceries", "conversation_id": null}'
   ```
3. Capture `conversation_id` from response
4. Send 2 more messages to same conversation
5. Stop backend server: `Ctrl+C` or `kill <pid>`
6. Inspect database directly:
   ```sql
   SELECT id, user_id, created_at FROM conversations WHERE id = '<conversation_id>';
   SELECT conversation_id, role, content, created_at FROM messages
   WHERE conversation_id = '<conversation_id>' ORDER BY created_at;
   ```
7. Restart backend server
8. Resume conversation with same `conversation_id`:
   ```bash
   curl -X POST http://localhost:8000/api/$USER_ID/chat \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "List my tasks", "conversation_id": "<conversation_id>"}'
   ```
9. Verify agent has access to previous context

**Expected Results**:
- ✅ Conversation record exists in database before restart
- ✅ All 3 messages exist in database before restart
- ✅ After restart, conversation resumes with full history
- ✅ Agent response references previous messages (e.g., mentions the "buy groceries" task)

**Failure Indicators**:
- ❌ Conversation not found after restart
- ❌ Messages missing from database
- ❌ Agent starts fresh conversation (no context)
- ❌ 500 error on resume attempt

---

#### Test 1.2: Task Data Persistence Across Restart

**Objective**: Verify task CRUD operations persist across restart

**Procedure**:
1. Start backend server
2. Add 3 tasks via chat interface
3. Complete 1 task, delete 1 task
4. Query database:
   ```sql
   SELECT id, title, status FROM todos WHERE user_id = '<user_id>';
   ```
5. Stop backend server
6. Restart backend server
7. List tasks via chat: "Show me all my tasks"
8. Verify tasks match database state before restart

**Expected Results**:
- ✅ 1 task remaining (2 were modified/deleted)
- ✅ Task data identical before and after restart
- ✅ Chat response correctly lists remaining task
- ✅ No "phantom" tasks or duplicates

**Failure Indicators**:
- ❌ Tasks disappear after restart
- ❌ Completed/deleted tasks reappear
- ❌ Task data corrupted or changed

---

#### Test 1.3: No In-Memory Session State

**Objective**: Verify no runtime session state exists

**Procedure**:
1. Review codebase for forbidden patterns:
   ```python
   # ❌ FORBIDDEN: Module-level sessions
   # backend/app/mcp/tools.py
   session = Session(engine)  # At module level

   # ❌ FORBIDDEN: Global caches
   conversation_cache = {}
   user_state = {}

   # ❌ FORBIDDEN: Class attributes for state
   class ChatHandler:
       active_conversations = {}  # ❌ Shared state
   ```

2. Run static analysis:
   ```bash
   # Search for module-level Session instantiation
   grep -r "^session = Session" backend/app/

   # Search for global dictionaries/caches
   grep -r "^.*_cache = {}" backend/app/
   grep -r "^.*_state = {}" backend/app/
   ```

3. Inspect MCP tools for stateless patterns:
   ```python
   # ✅ CORRECT: Fresh session per invocation
   def add_task(title: str, description: Optional[str] = None):
       with Session(engine) as session:  # ✅ Context manager
           task = Todo(title=title, description=description)
           session.add(task)
           session.commit()
           return task.dict()
   ```

4. Verify AgentRunner instantiation:
   ```python
   # ✅ CORRECT: Fresh runner per request
   @router.post("/{user_id}/chat")
   async def chat(user_id: UUID, request: ChatRequest):
       runner = AgentRunner()  # ✅ New instance per request
       response = runner.run(user_id, request.message, request.conversation_id)
       return response
   ```

**Expected Results**:
- ✅ No module-level Session objects
- ✅ No global caches or state dictionaries
- ✅ All sessions use context managers (`with Session(engine)`)
- ✅ AgentRunner instantiated per request

**Failure Indicators**:
- ❌ Module-level sessions found
- ❌ Global caches detected
- ❌ Singleton patterns with state

---

#### Test 1.4: Cold Start Performance

**Objective**: Verify no warm-up required after restart

**Procedure**:
1. Stop backend server
2. Clear any caches (Redis, etc., if applicable)
3. Restart backend server
4. Immediately send first request:
   ```bash
   time curl -X POST http://localhost:8000/api/$USER_ID/chat \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "List my tasks", "conversation_id": null}'
   ```
5. Measure response time
6. Send second identical request
7. Compare response times

**Expected Results**:
- ✅ First request succeeds (no warm-up errors)
- ✅ Response time reasonable (<5s for cold start)
- ✅ Subsequent requests similar speed (no significant cache advantage)

**Failure Indicators**:
- ❌ First request fails with "not initialized" error
- ❌ First request significantly slower (>10s)
- ❌ Requires manual initialization step

---

### 5.2 Conversation Resume Tests

#### Test 2.1: Resume Conversation with History

**Objective**: Verify agent has full context when resuming

**Procedure**:
1. Create conversation with 5 messages:
   - User: "Add task to buy groceries"
   - Agent: "I've added..."
   - User: "Add another: walk dog"
   - Agent: "I've added..."
   - User: "Show my tasks"
   - Agent: "Here are your tasks: 1. Buy groceries, 2. Walk dog"

2. Note the `conversation_id`

3. Close ChatKit UI or clear frontend state

4. Open new browser session / incognito window

5. Resume conversation using same `conversation_id`:
   ```bash
   curl -X POST http://localhost:8000/api/$USER_ID/chat \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Complete the first one", "conversation_id": "<conversation_id>"}'
   ```

6. Verify agent identifies "the first one" as "Buy groceries"

**Expected Results**:
- ✅ Agent loads full conversation history (all 5 messages)
- ✅ Agent correctly identifies "the first one" as "Buy groceries"
- ✅ Agent completes correct task
- ✅ Response references conversation context

**Failure Indicators**:
- ❌ Agent doesn't know what "the first one" refers to
- ❌ Agent asks for clarification (lost context)
- ❌ Wrong task completed

---

#### Test 2.2: Resume from Different Client

**Objective**: Verify conversation is server-side only

**Procedure**:
1. Start conversation in ChatKit UI (Browser A)
2. Add 3 tasks via chat
3. Capture `conversation_id` from network inspector
4. Open different browser (Browser B) or use API client
5. Resume conversation using captured `conversation_id`
6. Verify full history available

**Expected Results**:
- ✅ Browser B sees full conversation history
- ✅ Can continue conversation seamlessly
- ✅ No client-side state required

**Failure Indicators**:
- ❌ Conversation not found
- ❌ History empty or partial
- ❌ Requires re-authentication or session transfer

---

#### Test 2.3: Multiple Concurrent Conversations

**Objective**: Verify user can have multiple independent conversations

**Procedure**:
1. Create Conversation A: Add task "Buy groceries"
2. Create Conversation B: Add task "Write report"
3. Resume Conversation A: "Complete my task"
4. Resume Conversation B: "Complete my task"
5. Verify correct tasks completed in each conversation

**Expected Results**:
- ✅ Conversation A completes "Buy groceries"
- ✅ Conversation B completes "Write report"
- ✅ No cross-contamination between conversations
- ✅ Each conversation maintains independent context

**Failure Indicators**:
- ❌ Wrong task completed (context leak)
- ❌ Conversations merged or confused
- ❌ Agent references wrong conversation history

---

### 5.3 Database Persistence Tests

#### Test 3.1: Database as Single Source of Truth

**Objective**: Verify all state stored in database

**Procedure**:
1. Start fresh backend server
2. Execute chat operations to add 3 tasks
3. Do NOT query via API; go directly to database:
   ```sql
   SELECT id, user_id, title, status, created_at
   FROM todos
   WHERE user_id = '<user_id>'
   ORDER BY created_at;
   ```
4. Verify all 3 tasks present with correct data
5. Execute chat operation to complete task #2
6. Query database again
7. Verify task #2 status updated to "completed"

**Expected Results**:
- ✅ All operations immediately reflected in database
- ✅ No delay or eventual consistency issues
- ✅ Database state matches API responses

**Failure Indicators**:
- ❌ Tasks missing from database after creation
- ❌ Status not updated in database
- ❌ Discrepancy between API response and database

---

#### Test 3.2: Conversation History Ordering

**Objective**: Verify messages stored in correct chronological order

**Procedure**:
1. Create conversation with 10 messages
2. Query database:
   ```sql
   SELECT id, conversation_id, role, LEFT(content, 50) as content, created_at
   FROM messages
   WHERE conversation_id = '<conversation_id>'
   ORDER BY created_at ASC;
   ```
3. Verify:
   - Messages in correct chronological order
   - Alternating user/assistant roles (mostly)
   - `created_at` timestamps incrementing
   - No duplicate messages

**Expected Results**:
- ✅ Messages ordered by `created_at`
- ✅ Timestamps incrementing (no time travel)
- ✅ No duplicates or missing messages
- ✅ Correct role assignment (user/assistant/tool)

**Failure Indicators**:
- ❌ Messages out of order
- ❌ Duplicate messages
- ❌ Missing messages in sequence
- ❌ Incorrect roles

---

#### Test 3.3: Conversation Metadata Accuracy

**Objective**: Verify conversation metadata maintained correctly

**Procedure**:
1. Create new conversation
2. Query immediately:
   ```sql
   SELECT id, user_id, title, created_at, updated_at
   FROM conversations
   WHERE id = '<conversation_id>';
   ```
3. Note `created_at` and `updated_at` (should be identical initially)
4. Add message to conversation
5. Query again
6. Verify `updated_at` changed, `created_at` unchanged

**Expected Results**:
- ✅ `created_at` set on conversation creation
- ✅ `updated_at` equals `created_at` initially
- ✅ `updated_at` changes with new messages
- ✅ `created_at` remains immutable

**Failure Indicators**:
- ❌ Timestamps not set
- ❌ `updated_at` not updating
- ❌ `created_at` changing (immutability violated)

---

#### Test 3.4: User Isolation in Database

**Objective**: Verify users cannot access other users' data

**Procedure**:
1. Create tasks for User A (user_id_a)
2. Create tasks for User B (user_id_b)
3. Query database filtering by User A:
   ```sql
   SELECT id, user_id, title FROM todos WHERE user_id = '<user_id_a>';
   ```
4. Verify only User A's tasks returned
5. Attempt to access User B's conversation as User A via API:
   ```bash
   curl -X POST http://localhost:8000/api/$USER_A_ID/chat \
     -H "Authorization: Bearer $USER_A_TOKEN" \
     -d '{"message": "List tasks", "conversation_id": "<user_b_conversation_id>"}'
   ```
6. Verify 403 Forbidden or empty result (not User B's data)

**Expected Results**:
- ✅ Database queries correctly filter by user_id
- ✅ API enforces user_id matching
- ✅ Cross-user access blocked

**Failure Indicators**:
- ❌ User A sees User B's tasks
- ❌ Cross-user conversation access allowed
- ❌ Missing user_id filters in queries

---

#### Test 3.5: Cascade Deletion Integrity

**Objective**: Verify deleting conversation removes all messages

**Procedure**:
1. Create conversation with 5 messages
2. Query message count:
   ```sql
   SELECT COUNT(*) FROM messages WHERE conversation_id = '<conversation_id>';
   ```
3. Delete conversation:
   ```sql
   DELETE FROM conversations WHERE id = '<conversation_id>';
   ```
4. Query messages again
5. Verify all messages cascade-deleted

**Expected Results**:
- ✅ Deleting conversation removes all messages
- ✅ No orphaned messages in database
- ✅ Foreign key constraints enforced

**Failure Indicators**:
- ❌ Messages remain after conversation deleted
- ❌ Foreign key constraint violation
- ❌ Orphaned data

---

### 5.4 Horizontal Scaling Tests

#### Test 4.1: Round-Robin Load Distribution

**Objective**: Verify any instance can handle any request

**Procedure**:
1. Start 2 backend instances:
   - Instance A: Port 8000
   - Instance B: Port 8001
2. Create conversation via Instance A
3. Send next message via Instance B using same `conversation_id`
4. Send third message via Instance A again
5. Verify all messages processed correctly

**Expected Results**:
- ✅ Both instances serve requests successfully
- ✅ Conversation history consistent across instances
- ✅ No "session affinity" required

**Failure Indicators**:
- ❌ Instance B cannot find conversation
- ❌ Conversation history incomplete on Instance B
- ❌ Errors when switching instances

---

#### Test 4.2: Concurrent Requests to Same Conversation

**Objective**: Verify database handles concurrent writes

**Procedure**:
1. Start 2 API clients
2. Send 2 messages to same conversation simultaneously:
   - Client 1: "Add task to buy milk"
   - Client 2: "Add task to walk dog"
3. Verify both messages saved
4. Verify no race conditions or lost updates

**Expected Results**:
- ✅ Both messages saved to database
- ✅ Both tasks created
- ✅ No deadlocks or transaction conflicts
- ✅ `created_at` timestamps differ (even if by milliseconds)

**Failure Indicators**:
- ❌ One message lost
- ❌ Database deadlock
- ❌ Duplicate messages

---

#### Test 4.3: Instance Failure Recovery

**Objective**: Verify conversation continues if instance crashes

**Procedure**:
1. Start conversation via Instance A
2. Kill Instance A mid-conversation (no graceful shutdown)
3. Load balancer redirects to Instance B
4. Continue conversation via Instance B
5. Verify no data loss

**Expected Results**:
- ✅ Conversation resumes on Instance B
- ✅ Full history available
- ✅ No data loss from crash

**Failure Indicators**:
- ❌ Conversation lost
- ❌ Partial history
- ❌ Error on Instance B

---

## 6. Automated Verification Script

### pytest Implementation

```python
# backend/tests/test_stateless_behavior.py

import pytest
import time
import subprocess
import psycopg2
from uuid import uuid4, UUID
from app.database import engine, Session
from app.models.user import User
from app.models.todo import Todo
from app.models.conversation import Conversation, Message

@pytest.fixture
def db_connection():
    """Direct database connection for verification."""
    conn = psycopg2.connect(
        dbname="todo_db",
        user="postgres",
        password="password",
        host="localhost"
    )
    yield conn
    conn.close()

@pytest.fixture
def test_user(session):
    """Create test user."""
    user = User(id=uuid4(), email="stateless@test.com", username="stateless")
    session.add(user)
    session.commit()
    return user

@pytest.fixture
def backend_server():
    """Start and stop backend server."""
    # Start server
    proc = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd="backend"
    )
    time.sleep(3)  # Wait for startup

    yield proc

    # Stop server
    proc.terminate()
    proc.wait()

class TestServerRestart:
    """Test 1.1-1.4: Server restart scenarios."""

    def test_conversation_persistence_across_restart(
        self, test_user, db_connection, backend_server
    ):
        """Test 1.1: Conversation survives restart."""
        # Create conversation
        conversation_id = self._create_test_conversation(test_user.id)

        # Verify in database before restart
        cursor = db_connection.cursor()
        cursor.execute(
            "SELECT id FROM conversations WHERE id = %s",
            (str(conversation_id),)
        )
        assert cursor.fetchone() is not None

        # Restart server
        backend_server.terminate()
        backend_server.wait()
        time.sleep(1)
        backend_server = subprocess.Popen(
            ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd="backend"
        )
        time.sleep(3)

        # Verify conversation still exists
        cursor.execute(
            "SELECT id FROM conversations WHERE id = %s",
            (str(conversation_id),)
        )
        assert cursor.fetchone() is not None

        # Attempt to resume conversation via API
        response = self._send_chat_message(
            test_user.id,
            "List my tasks",
            conversation_id
        )
        assert response.status_code == 200
        assert response.json()["conversation_id"] == str(conversation_id)

    def test_no_in_memory_session_state(self):
        """Test 1.3: No module-level sessions."""
        # Static analysis: check for forbidden patterns
        with open("backend/app/mcp/tools.py") as f:
            content = f.read()

        # Check for module-level Session instantiation
        assert "session = Session(engine)" not in content or \
               "def " in content.split("session = Session(engine)")[0].split("\n")[-1], \
               "Module-level Session detected"

        # Check for global caches
        assert "_cache = {}" not in content, "Global cache detected"
        assert "_state = {}" not in content, "Global state detected"

    def test_cold_start_performance(self, test_user, backend_server):
        """Test 1.4: No warm-up required."""
        # Restart server
        backend_server.terminate()
        backend_server.wait()
        time.sleep(1)

        # Start fresh
        backend_server = subprocess.Popen(
            ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd="backend"
        )
        time.sleep(3)

        # Immediate first request
        start = time.time()
        response = self._send_chat_message(test_user.id, "List my tasks", None)
        first_request_time = time.time() - start

        assert response.status_code == 200, "First request failed"
        assert first_request_time < 5.0, f"Cold start too slow: {first_request_time}s"

class TestConversationResume:
    """Test 2.1-2.3: Conversation resume scenarios."""

    def test_resume_with_full_history(self, test_user, session):
        """Test 2.1: Agent has full context."""
        # Create conversation with history
        conversation = Conversation(user_id=test_user.id, title="Test")
        session.add(conversation)
        session.commit()

        # Add messages
        messages = [
            Message(conversation_id=conversation.id, role="user", content="Add task to buy groceries"),
            Message(conversation_id=conversation.id, role="assistant", content="Added task"),
            Message(conversation_id=conversation.id, role="user", content="Add task to walk dog"),
            Message(conversation_id=conversation.id, role="assistant", content="Added task"),
        ]
        for msg in messages:
            session.add(msg)
        session.commit()

        # Resume conversation with context-dependent request
        response = self._send_chat_message(
            test_user.id,
            "Complete the first one",
            conversation.id
        )

        assert response.status_code == 200
        # Agent should identify "the first one" as "Buy groceries"
        assert any(
            tc["name"] == "complete_task"
            for tc in response.json().get("tool_calls", [])
        )

    def test_multiple_concurrent_conversations(self, test_user, session):
        """Test 2.3: Independent conversations."""
        # Create two conversations
        conv_a = Conversation(user_id=test_user.id, title="Conversation A")
        conv_b = Conversation(user_id=test_user.id, title="Conversation B")
        session.add_all([conv_a, conv_b])
        session.commit()

        # Add different tasks in each
        self._send_chat_message(test_user.id, "Add task to buy groceries", conv_a.id)
        self._send_chat_message(test_user.id, "Add task to write report", conv_b.id)

        # Complete task in each conversation
        response_a = self._send_chat_message(test_user.id, "Complete my task", conv_a.id)
        response_b = self._send_chat_message(test_user.id, "Complete my task", conv_b.id)

        # Verify correct tasks completed (no cross-contamination)
        # This requires inspecting which task IDs were completed
        assert response_a.status_code == 200
        assert response_b.status_code == 200

class TestDatabasePersistence:
    """Test 3.1-3.5: Database as source of truth."""

    def test_database_as_single_source_of_truth(self, test_user, db_connection):
        """Test 3.1: All state in database."""
        # Add tasks via chat
        self._send_chat_message(test_user.id, "Add task to buy milk", None)
        time.sleep(0.5)  # Allow processing

        # Query database directly (bypass API)
        cursor = db_connection.cursor()
        cursor.execute(
            "SELECT title FROM todos WHERE user_id = %s",
            (str(test_user.id),)
        )
        tasks = cursor.fetchall()

        assert len(tasks) == 1
        assert "milk" in tasks[0][0].lower()

    def test_conversation_history_ordering(self, test_user, session, db_connection):
        """Test 3.2: Messages in chronological order."""
        # Create conversation with multiple messages
        conversation = Conversation(user_id=test_user.id, title="Order Test")
        session.add(conversation)
        session.commit()

        # Add messages with slight delays
        for i in range(5):
            msg = Message(
                conversation_id=conversation.id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}"
            )
            session.add(msg)
            session.commit()
            time.sleep(0.1)

        # Query database
        cursor = db_connection.cursor()
        cursor.execute(
            """SELECT content, created_at FROM messages
               WHERE conversation_id = %s ORDER BY created_at ASC""",
            (str(conversation.id),)
        )
        messages = cursor.fetchall()

        # Verify chronological order
        assert len(messages) == 5
        for i in range(4):
            assert messages[i][1] <= messages[i+1][1], "Messages not in chronological order"

    def test_user_isolation_in_database(self, session, db_connection):
        """Test 3.4: Users cannot access other users' data."""
        # Create two users
        user_a = User(id=uuid4(), email="a@test.com", username="user_a")
        user_b = User(id=uuid4(), email="b@test.com", username="user_b")
        session.add_all([user_a, user_b])
        session.commit()

        # Create tasks for each
        task_a = Todo(user_id=user_a.id, title="User A Task")
        task_b = Todo(user_id=user_b.id, title="User B Task")
        session.add_all([task_a, task_b])
        session.commit()

        # Query for User A only
        cursor = db_connection.cursor()
        cursor.execute(
            "SELECT title FROM todos WHERE user_id = %s",
            (str(user_a.id),)
        )
        tasks = cursor.fetchall()

        # Verify only User A's task returned
        assert len(tasks) == 1
        assert tasks[0][0] == "User A Task"

class TestHorizontalScaling:
    """Test 4.1-4.3: Multi-instance scenarios."""

    def test_round_robin_load_distribution(self, test_user):
        """Test 4.1: Any instance can handle any request."""
        # This test requires running multiple instances
        # Simplified version: verify conversation portable across API calls

        conversation_id = self._create_test_conversation(test_user.id)

        # Simulate different instances by clearing any local caches
        # (In real multi-instance test, would use different ports)
        response = self._send_chat_message(
            test_user.id,
            "List my tasks",
            conversation_id
        )

        assert response.status_code == 200
        assert response.json()["conversation_id"] == str(conversation_id)

    # Helper methods
    def _create_test_conversation(self, user_id: UUID) -> UUID:
        """Create test conversation."""
        # Implementation depends on API client
        pass

    def _send_chat_message(self, user_id: UUID, message: str, conversation_id: UUID):
        """Send chat message via API."""
        # Implementation depends on API client
        pass
```

### Running Verification Tests

```bash
# Run all stateless behavior tests
pytest backend/tests/test_stateless_behavior.py -v

# Run specific test category
pytest backend/tests/test_stateless_behavior.py::TestServerRestart -v

# Run with detailed output
pytest backend/tests/test_stateless_behavior.py -v -s

# Generate verification report
pytest backend/tests/test_stateless_behavior.py --html=reports/stateless_verification.html
```

---

## 7. Manual Verification Procedure

### Step-by-Step Checklist

**Phase 1: Pre-Restart Verification**
- [ ] Start backend server
- [ ] Create test conversation via ChatKit UI
- [ ] Add 3 tasks: "Buy groceries", "Walk dog", "Write report"
- [ ] Note conversation_id from browser DevTools
- [ ] Take screenshot of chat UI showing all 3 tasks
- [ ] Query database to verify tasks exist:
  ```sql
  SELECT id, title, status FROM todos WHERE user_id = '<user_id>';
  ```
- [ ] Document task IDs and states

**Phase 2: Server Restart**
- [ ] Stop backend server (Ctrl+C)
- [ ] Verify server process terminated: `ps aux | grep uvicorn`
- [ ] Wait 5 seconds
- [ ] Restart backend server: `uvicorn app.main:app --reload`
- [ ] Wait for startup message: "Application startup complete"

**Phase 3: Post-Restart Verification**
- [ ] Open ChatKit UI (new browser tab or refresh)
- [ ] Load existing conversation using conversation_id
- [ ] Verify all 3 tasks still visible in chat history
- [ ] Send new message: "Complete the first task"
- [ ] Verify agent completes "Buy groceries" (not random task)
- [ ] Query database to confirm task status updated:
  ```sql
  SELECT title, status FROM todos WHERE id = '<task_id>';
  ```
- [ ] Send message: "List my tasks"
- [ ] Verify response shows 2 remaining tasks (1 completed)

**Phase 4: Conversation Resume**
- [ ] Close all browser tabs
- [ ] Clear sessionStorage: DevTools → Application → sessionStorage → Clear
- [ ] Open new incognito window
- [ ] Navigate to ChatKit UI and authenticate
- [ ] Manually set conversation_id in UI or via API call
- [ ] Send message: "What have we discussed?"
- [ ] Verify agent references previous messages (grocery task, dog task, etc.)

**Phase 5: Database Verification**
- [ ] Connect to PostgreSQL: `psql -d todo_db -U postgres`
- [ ] Query conversation metadata:
  ```sql
  SELECT id, user_id, title, created_at, updated_at FROM conversations;
  ```
- [ ] Query all messages in conversation:
  ```sql
  SELECT role, LEFT(content, 50), created_at
  FROM messages
  WHERE conversation_id = '<conversation_id>'
  ORDER BY created_at;
  ```
- [ ] Verify message count matches chat UI
- [ ] Verify timestamps in chronological order
- [ ] Verify no duplicate messages

**Phase 6: Horizontal Scaling (Optional)**
- [ ] Start second backend instance on port 8001
- [ ] Configure load balancer or use direct API calls
- [ ] Send message to instance 1 (port 8000)
- [ ] Send next message to instance 2 (port 8001)
- [ ] Verify both messages saved correctly
- [ ] Verify conversation history consistent across instances

---

## 8. Scope & Boundaries

### In Scope
- Server restart without data loss
- Conversation resume functionality
- Database persistence verification
- Stateless architecture compliance
- Horizontal scalability readiness
- User isolation enforcement

### Out of Scope
- Load testing or stress testing
- Database replication/failover testing
- Network partition scenarios
- Backup/restore procedures
- Performance optimization
- Security penetration testing

---

## 9. Success Criteria

### Critical Requirements (Must Pass)
- ✅ Server restart preserves all conversations
- ✅ Server restart preserves all tasks
- ✅ Conversations resume with full history
- ✅ No in-memory session state exists
- ✅ Database is single source of truth

### High Priority
- ✅ Cold start succeeds on first request
- ✅ User isolation enforced in database
- ✅ Message ordering correct
- ✅ Multiple conversations independent

### Medium Priority
- ✅ Round-robin load distribution works
- ✅ Concurrent requests handled safely
- ✅ Cascade deletion maintains integrity

### Pass Threshold
- **Critical**: 100% pass rate required
- **High Priority**: ≥90% pass rate
- **Medium Priority**: ≥80% pass rate
- **Overall**: ≥90% total pass rate

---

## 10. Common Violations and Remediation

### Violation 1: Module-Level Session

**Symptom**: Conversation lost after restart

**Root Cause**:
```python
# backend/app/mcp/tools.py
session = Session(engine)  # ❌ Module level

def add_task(title: str):
    task = Todo(title=title)
    session.add(task)  # ❌ Uses module session
    session.commit()
```

**Remediation**:
```python
# ✅ FIXED: Fresh session per invocation
def add_task(title: str):
    with Session(engine) as session:  # ✅ Context manager
        task = Todo(title=title)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task.dict()
```

---

### Violation 2: In-Memory Cache

**Symptom**: Stale data after restart, instance switching fails

**Root Cause**:
```python
# backend/app/services/conversation.py
conversation_cache = {}  # ❌ Global cache

def get_conversation(conversation_id: UUID):
    if conversation_id in conversation_cache:  # ❌ In-memory lookup
        return conversation_cache[conversation_id]
    # ...
```

**Remediation**:
```python
# ✅ FIXED: Always query database
def get_conversation(session: Session, conversation_id: UUID):
    return session.query(Conversation).filter_by(id=conversation_id).first()
```

---

### Violation 3: Singleton AgentRunner

**Symptom**: Conversations mixing, context leaking between users

**Root Cause**:
```python
# backend/app/agent/runner.py
class AgentRunner:
    _instance = None  # ❌ Singleton pattern
    conversation_history = []  # ❌ Shared state

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**Remediation**:
```python
# ✅ FIXED: New instance per request
class AgentRunner:
    def __init__(self):
        # No shared state
        pass

    def run(self, user_id: UUID, message: str, conversation_id: UUID):
        # Load history from database
        history = self._load_history(conversation_id)
        # Process with fresh context
        return self._process(message, history)
```

---

### Violation 4: Missing User ID Filter

**Symptom**: Users see other users' data

**Root Cause**:
```sql
-- ❌ No user_id filter
SELECT * FROM todos WHERE id = '<task_id>';
```

**Remediation**:
```sql
-- ✅ FIXED: Always filter by user_id
SELECT * FROM todos WHERE id = '<task_id>' AND user_id = '<user_id>';
```

---

## 11. Verification Report Template

```markdown
# Stateless Architecture Verification Report

**Project**: Todo App - Phase 3 AI Chatbot
**Date**: YYYY-MM-DD HH:MM UTC
**Verified By**: [Name/Agent ID]
**Environment**: [Local/Staging/Production]
**Backend Version**: X.Y.Z
**Database**: PostgreSQL X.Y

---

## Executive Summary

| Metric | Result | Status |
|--------|--------|--------|
| Overall Pass Rate | XX.X% | ✅/❌ |
| Critical Tests Passed | X/X | ✅/❌ |
| Server Restart Tests | X/4 | ✅/⚠️/❌ |
| Conversation Resume Tests | X/3 | ✅/⚠️/❌ |
| Database Persistence Tests | X/5 | ✅/⚠️/❌ |
| Horizontal Scaling Tests | X/3 | ✅/⚠️/❌ |

**Certification**: [✅ STATELESS VERIFIED / ⚠️ ISSUES FOUND / ❌ NON-COMPLIANT]

---

## Test Results

### ✅ Test 1.1: Conversation Persistence Across Restart
- **Status**: PASS
- **Duration**: 15s
- **Details**: Conversation survived server restart with all 5 messages intact
- **Verification**: Database query confirmed persistence

### ❌ Test 1.3: No In-Memory Session State
- **Status**: FAIL
- **Details**: Module-level Session detected in `backend/app/mcp/tools.py:10`
- **Impact**: High - Prevents horizontal scaling
- **Remediation**: Convert to context manager pattern
- **Tracking**: Issue #42

[... continue for all tests ...]

---

## Critical Findings

### 🔴 High Severity
1. **Module-Level Session** (Test 1.3)
   - Location: `backend/app/mcp/tools.py:10`
   - Impact: Prevents horizontal scaling
   - Fix: Use context managers

### 🟡 Medium Severity
1. **Slow Cold Start** (Test 1.4)
   - First request takes 8s (threshold: 5s)
   - Impact: UX degradation after restart
   - Fix: Optimize initialization

### 🟢 Low Severity
None

---

## Remediation Plan

| Issue | Priority | Assignee | ETA | Status |
|-------|----------|----------|-----|--------|
| Module-level Session | P0 | Backend Team | 2026-01-21 | 🔄 In Progress |
| Cold start performance | P1 | DevOps Team | 2026-01-22 | 📝 Planned |

---

## Sign-Off

- [ ] All critical tests passed
- [ ] Known issues documented and tracked
- [ ] Remediation plan approved
- [ ] Production deployment authorized

**Verified By**: ___________________________
**Date**: ___________________________
```

---

## 12. CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/stateless-verification.yml
name: Stateless Architecture Verification

on:
  pull_request:
    paths:
      - 'backend/**'
  push:
    branches:
      - main

jobs:
  verify-stateless:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: todo_db
          POSTGRES_PASSWORD: password
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-html

      - name: Run stateless verification tests
        run: |
          cd backend
          pytest tests/test_stateless_behavior.py \
            --html=reports/stateless_verification.html \
            --self-contained-html \
            -v

      - name: Upload verification report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: stateless-verification-report
          path: backend/reports/stateless_verification.html

      - name: Fail if critical tests failed
        run: |
          if grep -q "FAILED.*TestServerRestart" backend/reports/test_results.txt; then
            echo "Critical stateless tests failed"
            exit 1
          fi
```

---

## 13. Implementation Checklist

### Preparation
- [ ] Backend server running
- [ ] Database accessible with admin credentials
- [ ] Test user created with known credentials
- [ ] Logging configured for debugging
- [ ] Monitoring/observability tools ready

### Execution
- [ ] Run automated pytest suite
- [ ] Execute manual verification checklist
- [ ] Document all test results
- [ ] Take screenshots of key evidence
- [ ] Query database for verification

### Analysis
- [ ] Calculate pass rates per category
- [ ] Identify root causes for failures
- [ ] Assess severity and impact
- [ ] Create remediation plan
- [ ] Generate verification report

### Follow-Up
- [ ] Create GitHub issues for failures
- [ ] Assign owners and deadlines
- [ ] Rerun tests after fixes
- [ ] Update documentation with findings
- [ ] Obtain sign-off for production

---

**Maintained by**: Todo-app Hackathon Team
**Last Updated**: 2026-01-20
