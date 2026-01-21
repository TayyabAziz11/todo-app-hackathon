# Phase 6 Validation Guide: Context-Aware Task Completion

**Feature**: User Story 3 - Context-Aware Task Completion
**Status**: ✅ COMPLETE (All components implemented in previous sessions)
**Date**: 2026-01-21

## Implementation Status

All 10 tasks (T063-T072) for Phase 6 were already implemented:

### T063-T066: complete_task MCP Tool ✅

**Location**: `backend/app/mcp/tools.py` (lines 286-337)

**Capabilities**:
- ✅ Mark task as completed (completed=true) or incomplete (completed=false)
- ✅ User ownership validation via `_get_user_task()` helper
- ✅ Task existence validation (returns TASK_NOT_FOUND if task doesn't exist)
- ✅ Permission validation (returns error if task doesn't belong to user)
- ✅ Timestamp update (updated_at set to current UTC time)
- ✅ Comprehensive error handling (database failures caught)

**Input Schema** (`CompleteTaskInput`):
```python
user_id: UUID           # Required - user authentication
task_id: int            # Required - which task to complete
completed: bool = True  # True=complete, False=mark incomplete
```

**Output Schema** (`CompleteTaskOutput`):
```python
success: bool
task: Optional[TaskResult]  # Updated task with new completed status
message: str                # "Task 'Buy groceries' completed"
error: Optional[str]        # Error code if failed
```

**Error Responses**:
- `TASK_NOT_FOUND`: Task doesn't exist or doesn't belong to user
- `DATABASE_ERROR`: Database operation failed

### T067: MCP Server Registration ✅

**Location**: `backend/app/mcp/tools.py` (line 406)

```python
TOOL_HANDLERS = {
    "add_task": add_task,
    "list_tasks": list_tasks,
    "update_task": update_task,
    "complete_task": complete_task,  # ✅ Registered
    "delete_task": delete_task,
}
```

### T068: Intent Patterns for Task Completion ✅

**Location**: `backend/app/agent/prompts.py` (lines 68-78)

**Intent Keywords**:
- "complete", "done", "finish", "mark", "check off"
- Natural variations: "finished", "completed", "tick"

**Example Triggers**:
```text
- "Mark task 3 as done"
- "I finished the grocery task"
- "Complete task 5"
- "Check off 'call dentist'"
- "Undo completing task 2" (use completed=false)
```

**Intent-to-Tool Mapping Table** (lines 94-100):
```text
| User Intent | Keywords/Phrases | Tool to Use |
|-------------|------------------|-------------|
| Finish task | complete, done, finish, mark, check off | complete_task |
```

### T069: Tool Descriptions and Task Matching Strategies ✅

**Location**: `backend/app/agent/prompts.py`

**Tool Description** (lines 68-78):
```text
### 4. complete_task
Use when: User wants to mark a task as done/finished/complete, or undo completion
Required: task_id (which task to complete)
Optional: completed (true to complete, false to uncomplete)
```

**Task Matching Strategies** (lines 102-105):
```text
Ambiguity Resolution:
- If unclear between update and complete: ask "Do you want to edit the task details or mark it as done?"
- If unclear which task: use list_tasks first, then ask user to specify
- If user says "done with task" without ID: ask which task or list tasks first
```

**Key Strategy**: When task_id is not explicitly provided:
1. Agent calls `list_tasks` to get all tasks
2. Agent matches user's natural language reference to task title
3. If single match → calls `complete_task` with resolved task_id
4. If multiple matches → asks user for clarification
5. If no match → asks user to clarify or shows available tasks

### T070: Task Not Found Handling ✅

**Location**: `backend/app/agent/prompts.py` (lines 134-136, 197-200)

**System Prompt Guidance**:
```text
### After Failed Tool Calls

**Task not found**:
"I couldn't find task #{id}. Would you like me to show you your current tasks?"
```

**Example Conversation** (lines 196-200):
```text
### Example 4: Error Handling
User: "Complete task 99"
Assistant: [Calls complete_task with task_id=99]
[Tool returns error: task not found]
Assistant: "I couldn't find task #99. Would you like me to show you your current tasks so you can pick the right one?"
```

### T071: AgentRunner Tool Attachment ✅

**Location**: `backend/app/agent/runner.py` (line 128)

All MCP tools (including complete_task) are automatically loaded:

```python
# Get tools from MCP server
tools = self.mcp_server.get_tools_for_ai()
logger.info(f"Loaded {len(tools)} MCP tools")
```

The MCP server's `get_tools_for_ai()` method returns all 5 tools in OpenAI-compatible format, including complete_task.

### T072: Tool Chaining Examples ✅

**Location**: `backend/app/agent/prompts.py` (lines 174-184, 143-148)

**Example: List and Complete** (lines 174-184):
```text
### Example 2: List and Complete
User: "What do I need to do?"
Assistant: [Calls list_tasks]
Assistant: "Here are your tasks:
1. Buy milk - Incomplete
2. Call dentist - Incomplete
3. Finish report - Complete"

User: "I already called the dentist"
Assistant: [Calls complete_task with task_id=2]
Assistant: "Great job! I've marked 'Call dentist' as complete."
```

**Multi-Turn Conversation Handling** (lines 143-148):
```text
1. **Remember context**: If user says "mark it done" after discussing a specific task, use that task
2. **Pronoun resolution**: "it", "that one", "the first one" refer to recently mentioned tasks
3. **Clarify when needed**: If context is ambiguous, ask for clarification
4. **Batch operations**: Handle "complete tasks 1, 2, and 3" by calling complete_task multiple times
```

**Guardrails** (line 153):
```text
DO NOT:
- Make up task IDs - always get them from list_tasks or user input
- Make assumptions about task existence - verify with list_tasks
```

## Manual Validation Scenarios

### Scenario 1: Complete Task by ID (Direct Reference)

**Setup**: Create 3 tasks

**Request**:
```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Mark task 2 as done"
  }'
```

**Expected Agent Behavior**:
1. Detects "mark...done" intent → maps to complete_task
2. Extracts task_id=2 from message
3. Calls `complete_task(user_id={user_id}, task_id=2, completed=True)`
4. Receives success response
5. Returns conversational confirmation:
   ```
   Great job! I've marked 'Call dentist' as complete.
   ```

**Validation**:
- ✅ tool_calls array contains complete_task invocation with task_id=2
- ✅ Response is conversational, not raw JSON
- ✅ Task 2 marked as completed in database

### Scenario 2: Complete Task by Title (Context-Aware Resolution)

**Setup**:
- Create task "Buy groceries"
- Task ID is unknown to user

**Request**:
```json
{
  "message": "I finished buying groceries"
}
```

**Expected Agent Behavior**:
1. Detects "finished" intent → maps to complete_task
2. NO explicit task_id provided → needs resolution
3. Calls `list_tasks(user_id={user_id}, completed=False)` to get incomplete tasks
4. Matches "groceries" in user message to task title "Buy groceries"
5. Finds single match → task_id=1
6. Calls `complete_task(user_id={user_id}, task_id=1, completed=True)`
7. Returns confirmation:
   ```
   Great job! I've marked 'Buy groceries' as complete.
   ```

**Validation**:
- ✅ tool_calls array contains TWO invocations:
  1. list_tasks (to resolve task)
  2. complete_task (to mark complete)
- ✅ Agent correctly matched "groceries" to "Buy groceries"
- ✅ Task 1 marked as completed in database

### Scenario 3: Ambiguous Match (Multiple Tasks Match)

**Setup**:
- Create "Buy groceries at Costco"
- Create "Buy groceries at Trader Joe's"

**Request**:
```json
{
  "message": "I'm done with the grocery task"
}
```

**Expected Agent Behavior**:
1. Detects completion intent
2. Calls list_tasks to resolve task
3. Finds TWO matches for "grocery"
4. Returns clarification request:
   ```
   I found 2 tasks that match "grocery":
   1. Buy groceries at Costco - Incomplete
   2. Buy groceries at Trader Joe's - Incomplete

   Which one did you finish?
   ```

**Validation**:
- ✅ Agent does NOT make assumption about which task
- ✅ Agent asks for clarification
- ✅ No complete_task call made yet

**Follow-up**:
```
User: "The Costco one"
Agent: [Calls complete_task with task_id=1]
Agent: "Great job! I've marked 'Buy groceries at Costco' as complete."
```

### Scenario 4: Task Not Found (Invalid ID)

**Request**:
```json
{
  "message": "Complete task 99"
}
```

**Expected Agent Behavior**:
1. Detects completion intent
2. Extracts task_id=99
3. Calls `complete_task(user_id={user_id}, task_id=99)`
4. Tool returns `TASK_NOT_FOUND` error
5. Agent responds with helpful error:
   ```
   I couldn't find task #99. Would you like me to show you your current tasks so you can pick the right one?
   ```

**Validation**:
- ✅ Error handled gracefully
- ✅ Agent offers to list tasks
- ✅ No task modified in database

### Scenario 5: Multi-Turn Context Awareness

**Turn 1**:
```
User: "What are my tasks?"
Agent: [Calls list_tasks]
Agent: "Here are your tasks:
1. Buy groceries - Incomplete
2. Call dentist - Incomplete
3. Finish report - Complete"
```

**Turn 2**:
```
User: "I finished the first one"
Agent: [Calls complete_task with task_id=1]
Agent: "Great job! I've marked 'Buy groceries' as complete."
```

**Validation**:
- ✅ Agent remembers context from Turn 1
- ✅ "the first one" correctly resolved to task_id=1
- ✅ No additional list_tasks call needed (context already present)

### Scenario 6: Undo Completion (Mark as Incomplete)

**Setup**: Task 1 is currently completed

**Request**:
```json
{
  "message": "Actually, I didn't finish task 1 yet"
}
```

**Expected Agent Behavior**:
1. Detects "didn't finish" → maps to complete_task with completed=False
2. Calls `complete_task(user_id={user_id}, task_id=1, completed=False)`
3. Returns confirmation:
   ```
   No problem! I've marked 'Buy groceries' as incomplete again.
   ```

**Validation**:
- ✅ Task 1 marked as incomplete (completed=False)
- ✅ Agent understands negation ("didn't finish")

## Integration Tests

### Tool Chaining: List → Complete

**Test**: Natural language completion without explicit task_id

```python
# Conversation state: No prior context
user_message = "I'm done with the meeting task"

# Expected tool call sequence:
# 1. list_tasks(user_id={user_id}, completed=False)
#    Returns: [{"id": 3, "title": "Attend team meeting", ...}]
# 2. complete_task(user_id={user_id}, task_id=3, completed=True)
#    Returns: {"success": True, "task": {...}, "message": "..."}

# Expected response:
# "Great job! I've marked 'Attend team meeting' as complete."
```

### Pronoun Resolution

**Test**: Multi-turn conversation with pronoun reference

```python
# Turn 1
user_message_1 = "Show my incomplete tasks"
# Agent calls list_tasks, returns tasks 1, 2, 3

# Turn 2
user_message_2 = "Mark the second one as done"
# Agent should:
# - Recall task list from Turn 1
# - Resolve "second one" to task_id=2
# - Call complete_task(task_id=2)
```

## Success Criteria

### Functional Requirements ✅

- ✅ **FR-001**: Agent detects completion intent (done/finished/complete)
- ✅ **FR-002**: complete_task tool called with correct parameters
- ✅ **FR-003**: User ownership enforced (user_id validation)
- ✅ **FR-004**: Task existence validated before completion
- ✅ **FR-005**: Context-aware task resolution (matches by title)
- ✅ **FR-006**: Tool chaining (list_tasks → complete_task)
- ✅ **FR-007**: Ambiguous match handling (asks for clarification)
- ✅ **FR-008**: Task not found error handling
- ✅ **FR-009**: Multi-turn context awareness
- ✅ **FR-010**: Undo completion (completed=False)

### Technical Requirements ✅

- ✅ **Stateless**: No in-memory state, fresh query per request
- ✅ **User Isolation**: Only user's own tasks can be completed
- ✅ **Error Handling**: TASK_NOT_FOUND, DATABASE_ERROR
- ✅ **Tool Transparency**: tool_calls array populated
- ✅ **API Contract**: Matches mcp-tools.yaml specification
- ✅ **Timestamp Update**: updated_at set on completion

### User Experience ✅

- ✅ Natural language completion ("I finished buying groceries")
- ✅ Conversational confirmation ("Great job! I've marked...")
- ✅ Graceful error handling with helpful suggestions
- ✅ Context awareness (pronoun resolution, multi-turn)
- ✅ Clarification requests for ambiguous matches
- ✅ Undo support (mark as incomplete)

## Test Commands

### Create Test Task

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}'
```

### Complete by ID

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Mark task 1 as done"}'
```

### Complete by Title (Context-Aware)

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "I finished buying groceries"}'
```

### Undo Completion

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Actually I didnt finish task 1 yet"}'
```

## Agent Behavior Patterns

### Pattern 1: Direct ID Reference
```
User: "Complete task 5"
→ complete_task(task_id=5)
```

### Pattern 2: Title-Based Resolution
```
User: "I finished the grocery task"
→ list_tasks(completed=False)
→ Match "grocery" to task title
→ complete_task(task_id={resolved_id})
```

### Pattern 3: Pronoun Resolution
```
User: "Show my tasks"
→ list_tasks()
User: "Mark the first one done"
→ Recall task list from context
→ complete_task(task_id={first_task_id})
```

### Pattern 4: Ambiguity Handling
```
User: "Complete the meeting task"
→ list_tasks()
→ Find 2 matches: "Team meeting", "Client meeting"
→ Ask: "Which meeting task? 1) Team meeting 2) Client meeting"
```

## Known Limitations

1. **Partial title matching**: Agent uses fuzzy matching which may match unintended tasks if titles are similar
2. **Multi-language support**: Natural language processing works best in English
3. **Complex context**: Very long conversation histories may lose context
4. **Batch completion**: "Complete all my tasks" requires explicit implementation

These are intentional scope limitations for Phase 6. Future enhancements can improve matching algorithms and add batch operations.

## Conclusion

**Phase 6 Status**: ✅ COMPLETE

All 10 tasks (T063-T072) implemented. The complete_task MCP tool is fully functional, registered with the MCP server, integrated with the agent via AgentRunner, and guided by comprehensive system prompt rules including:

- ✅ Intent pattern recognition
- ✅ Task matching strategies (ID, title, context)
- ✅ Tool chaining examples (list → complete)
- ✅ Error handling guidance
- ✅ Multi-turn context awareness
- ✅ Ambiguity resolution

Users can now complete tasks using natural language like:
- "I finished buying groceries" (context-aware resolution)
- "Mark task 3 as done" (direct ID reference)
- "Complete the first one" (pronoun resolution)
- "Actually I didn't finish that" (undo completion)

The agent will intelligently resolve task references, chain list_tasks when needed, and provide conversational confirmations.

**Next Phase**: Phase 7 - User Story 4: Multi-Step Task Operations (T073-T077)
