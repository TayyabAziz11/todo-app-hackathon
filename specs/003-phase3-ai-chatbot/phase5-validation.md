# Phase 5 Validation Guide: Conversational Task Querying

**Feature**: User Story 2 - Conversational Task Querying
**Status**: ✅ COMPLETE (All components implemented in previous sessions)
**Date**: 2026-01-21

## Implementation Status

All 10 tasks (T053-T062) for Phase 5 were already implemented:

### T053-T056: list_tasks MCP Tool ✅

**Location**: `backend/app/mcp/tools.py` (lines 127-201)

**Capabilities**:
- ✅ User ownership filtering (`Todo.user_id == input_data.user_id`)
- ✅ Status filtering via `completed` parameter (true/false/None)
- ✅ Title search via `search` parameter (case-insensitive ILIKE)
- ✅ Pagination via `limit` and `offset`
- ✅ Total count in response
- ✅ Comprehensive error handling

**Input Schema** (`ListTasksInput`):
```python
user_id: UUID           # Required - user authentication
completed: Optional[bool]  # None=all, True=completed, False=pending
search: Optional[str]   # Keyword search in title
limit: int = 50         # Max 100
offset: int = 0         # For pagination
```

**Output Schema** (`ListTasksOutput`):
```python
success: bool
tasks: List[TaskResult]  # Matching tasks
total: int              # Total count (before pagination)
message: str            # Human-readable summary
```

### T057: MCP Server Registration ✅

**Location**: `backend/app/mcp/tools.py` (line 404)

```python
TOOL_HANDLERS = {
    "add_task": add_task,
    "list_tasks": list_tasks,     # ✅ Registered
    "update_task": update_task,
    "complete_task": complete_task,
    "delete_task": delete_task,
}
```

### T058-T060: System Prompt ✅

**Location**: `backend/app/agent/prompts.py`

**Intent Patterns** (lines 43-56):
```text
Example triggers:
- "Show me my tasks"
- "What's on my todo list?"
- "List my incomplete tasks"
- "Do I have any tasks about groceries?"
- "Show me what I've completed"
```

**Tool Description** (lines 43-49):
```text
### 2. list_tasks
Use when: User wants to see, view, show, or check their tasks
Optional filters:
- completed=true (only completed tasks)
- completed=false (only incomplete tasks)
- search="keyword" (tasks matching a search term)
```

**Empty List Handling** (lines 120-121):
```text
list_tasks success (empty):
"You don't have any tasks yet. Would you like to add one?"
```

**Conversational Formatting** (lines 114-119):
```text
list_tasks success (with tasks):
"Here are your tasks:
1. {title} - {status}
2. {title} - {status}
..."
```

### T061: AgentRunner Tool Attachment ✅

**Location**: `backend/app/agent/runner.py` (line 128)

All MCP tools (including list_tasks) are automatically loaded:

```python
# Get tools from MCP server
tools = self.mcp_server.get_tools_for_ai()
logger.info(f"Loaded {len(tools)} MCP tools")
```

The MCP server's `get_tools_for_ai()` method returns all 5 tools in OpenAI-compatible format.

### T062: Conversational Response Rules ✅

**Location**: `backend/app/agent/prompts.py` (lines 107-142)

**Response Guidelines**:
- ✅ Friendly, human-readable language
- ✅ No raw JSON in responses
- ✅ Context-aware formatting (empty list vs. populated list)
- ✅ Helpful suggestions after actions
- ✅ Multi-turn conversation support

## Manual Validation Scenarios

### Scenario 1: List All Tasks

**Setup**: Create 5 tasks (3 pending, 2 completed)

**Request**:
```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me all my tasks"
  }'
```

**Expected Agent Behavior**:
1. Detects "show" intent → maps to list_tasks
2. Calls `list_tasks(user_id={user_id}, completed=None)`
3. Receives all 5 tasks
4. Formats conversational response:
   ```
   Here are your tasks:
   1. Buy groceries - Incomplete
   2. Call dentist - Incomplete
   3. Finish report - Incomplete
   4. Send invoice - Complete
   5. Review code - Complete
   ```

**Validation**:
- ✅ tool_calls array contains list_tasks invocation
- ✅ Response is conversational, not raw JSON
- ✅ All 5 tasks shown with correct status

### Scenario 2: List Pending Tasks Only

**Request**:
```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What tasks do I still need to do?"
  }'
```

**Expected Agent Behavior**:
1. Detects "need to do" → maps to list_tasks with pending filter
2. Calls `list_tasks(user_id={user_id}, completed=False)`
3. Receives 3 pending tasks
4. Formats response:
   ```
   You have 3 tasks to complete:
   1. Buy groceries
   2. Call dentist
   3. Finish report
   ```

**Validation**:
- ✅ Only incomplete tasks shown (3 tasks)
- ✅ Agent correctly inferred completed=False from "need to do"

### Scenario 3: List Completed Tasks

**Request**:
```json
{
  "message": "Show me what I've finished"
}
```

**Expected Agent Behavior**:
1. Calls `list_tasks(user_id={user_id}, completed=True)`
2. Receives 2 completed tasks
3. Response:
   ```
   Great work! Here's what you've completed:
   1. Send invoice
   2. Review code
   ```

### Scenario 4: Search for Specific Tasks

**Request**:
```json
{
  "message": "Do I have any tasks about groceries?"
}
```

**Expected Agent Behavior**:
1. Detects search intent
2. Calls `list_tasks(user_id={user_id}, search="groceries")`
3. Returns matching task
4. Response:
   ```
   Yes! I found this task:
   1. Buy groceries - Incomplete
   ```

### Scenario 5: Empty Task List

**Setup**: Delete all tasks

**Request**:
```json
{
  "message": "What's on my plate today?"
}
```

**Expected Agent Behavior**:
1. Calls `list_tasks(user_id={user_id})`
2. Receives empty list
3. Response follows empty list guideline:
   ```
   You don't have any tasks yet. Would you like to add one?
   ```

**Validation**:
- ✅ Friendly empty state message
- ✅ Helpful suggestion to add tasks

## Integration Tests

### Multi-Turn Conversation

**Turn 1**:
```
User: "Show my tasks"
Agent: [calls list_tasks] "Here are your 3 tasks: ..."
```

**Turn 2**:
```
User: "Just the incomplete ones"
Agent: [calls list_tasks with completed=False] "You have 2 incomplete tasks: ..."
```

**Validation**:
- ✅ Agent understands context from previous query
- ✅ Correctly interprets "incomplete ones" as filter refinement

### Tool Chaining (Future Enhancement)

**Request**: "Show my tasks and add 'Buy milk' to the list"

**Expected**:
1. Calls list_tasks first
2. Then calls add_task
3. Confirms both actions in single response

## Test Commands

### Create Test Data

```bash
# Create 5 tasks via add_task tool
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}'

# Repeat for 4 more tasks...
```

### Complete Some Tasks

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Mark task 1 as done"}'
```

### Query Tasks

```bash
# All tasks
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me all my tasks"}'

# Pending only
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "What do I still need to do?"}'

# Completed only
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "What have I finished?"}'
```

## Success Criteria

### Functional Requirements ✅

- ✅ **FR-001**: Agent detects list/show/view intents
- ✅ **FR-002**: list_tasks tool called with correct parameters
- ✅ **FR-003**: Status filter works (all/pending/completed)
- ✅ **FR-004**: Search filter works (case-insensitive)
- ✅ **FR-005**: User isolation enforced (user_id filtering)
- ✅ **FR-006**: Conversational response formatting
- ✅ **FR-007**: Empty list handled gracefully
- ✅ **FR-008**: Tool calls visible in response

### Technical Requirements ✅

- ✅ **Stateless**: No in-memory state, fresh query per request
- ✅ **User Isolation**: Only user's own tasks returned
- ✅ **Error Handling**: Database errors caught and reported
- ✅ **Tool Transparency**: tool_calls array populated
- ✅ **API Contract**: Matches mcp-tools.yaml specification

### User Experience ✅

- ✅ Natural language query processing
- ✅ Conversational response format
- ✅ Helpful empty state messaging
- ✅ Context awareness in multi-turn conversations
- ✅ Clear task status indicators

## Known Limitations

1. **No sorting options**: Tasks always sorted by created_at DESC
2. **No date filtering**: Cannot query "tasks from last week"
3. **Search is title-only**: Description not searched
4. **No task grouping**: Cannot group by status, priority, etc.

These are intentional scope limitations for Phase 5. Future enhancements can add these features.

## Conclusion

**Phase 5 Status**: ✅ COMPLETE

All 10 tasks (T053-T062) implemented. The list_tasks MCP tool is fully functional, registered with the MCP server, integrated with the agent via AgentRunner, and guided by comprehensive system prompt rules.

Users can now query their tasks using natural language like:
- "Show me my tasks"
- "What's pending?"
- "What have I completed?"
- "Do I have any tasks about groceries?"

The agent will call list_tasks with appropriate filters and return conversational summaries.

**Next Phase**: Phase 6 - User Story 3: Context-Aware Task Completion (T063-T072)
