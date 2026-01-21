# Phase 9 Validation Guide: Delete Task Support

**Feature**: Delete Task Support
**Status**: ✅ COMPLETE (All components implemented in previous sessions)
**Date**: 2026-01-21

## Implementation Status

All 8 tasks (T087-T094) for Phase 9 were already implemented:

### T087-T090: delete_task MCP Tool ✅

**Location**: `backend/app/mcp/tools.py` (lines 344-395)

**Capabilities**:
- ✅ Permanently delete a task by task_id
- ✅ User ownership validation via `_get_user_task()` helper
- ✅ Task existence validation (returns TASK_NOT_FOUND if task doesn't exist)
- ✅ Permission validation (returns error if task doesn't belong to user)
- ✅ Store task summary before deletion (ID and title)
- ✅ Comprehensive error handling (database failures caught)
- ✅ Irreversible operation warning in docstring

**Input Schema** (`DeleteTaskInput`):
```python
user_id: UUID    # Required - user authentication
task_id: int     # Required - which task to delete
```

**Output Schema** (`DeleteTaskOutput`):
```python
success: bool
deleted_task: Optional[TaskSummary]  # Contains id and title of deleted task
message: str                         # "Task 'Buy groceries' has been deleted"
error: Optional[str]                 # Error code if failed
```

**Implementation Details** (lines 344-395):
```python
def delete_task(input_data: DeleteTaskInput) -> DeleteTaskOutput:
    """
    Permanently delete a task.

    This operation cannot be undone.
    """
    logger.info(f"delete_task called for task {input_data.task_id} by user {input_data.user_id}")

    try:
        engine = get_engine()
        with Session(engine) as session:
            # Get the task (with ownership check)
            todo = _get_user_task(session, input_data.user_id, input_data.task_id)

            if not todo:
                logger.warning(f"Task {input_data.task_id} not found for user {input_data.user_id}")
                return DeleteTaskOutput(
                    success=False,
                    deleted_task=None,
                    message="Task not found",
                    error=f"TASK_NOT_FOUND: Task {input_data.task_id} does not exist or does not belong to this user",
                )

            # Store task info before deletion
            deleted_summary = TaskSummary(id=todo.id, title=todo.title)

            # Delete the task
            session.delete(todo)
            session.commit()

            logger.info(f"Deleted task {deleted_summary.id} for user {input_data.user_id}")

            return DeleteTaskOutput(
                success=True,
                deleted_task=deleted_summary,
                message=f"Task '{deleted_summary.title}' has been deleted",
            )

    except Exception as e:
        logger.error(f"delete_task failed: {e}")
        return DeleteTaskOutput(
            success=False,
            deleted_task=None,
            message="Failed to delete task",
            error=f"DATABASE_ERROR: {str(e)}",
        )
```

**Error Responses**:
- `TASK_NOT_FOUND`: Task doesn't exist or doesn't belong to user
- `DATABASE_ERROR`: Database operation failed

### T091: MCP Server Registration ✅

**Location**: `backend/app/mcp/tools.py` (line 407)

```python
TOOL_HANDLERS = {
    "add_task": add_task,
    "list_tasks": list_tasks,
    "update_task": update_task,
    "complete_task": complete_task,
    "delete_task": delete_task,  # ✅ Registered
}
```

**Tool Definition Location**: `backend/app/mcp/schemas.py` (lines 413-430)

```python
MCPToolDefinition(
    name="delete_task",
    description="Permanently delete a task. Use when the user wants to remove, delete, or get rid of a task.",
    inputSchema=MCPToolInputSchema(
        properties={
            "user_id": MCPToolParameter(
                type="string",
                format="uuid",
                description="The authenticated user's unique identifier"
            ),
            "task_id": MCPToolParameter(
                type="integer",
                description="The ID of the task to delete"
            ),
        },
        required=["user_id", "task_id"]
    )
)
```

### T092: Intent Patterns for Task Deletion ✅

**Location**: `backend/app/agent/prompts.py` (lines 80-89)

**Intent Keywords**:
- "delete", "remove", "get rid of", "don't need"
- Natural variations: "erase", "discard", "throw away"

**Example Triggers**:
```text
- "Delete task 7"
- "Remove the grocery task"
- "Get rid of task 2"
- "I don't need task 4 anymore"
```

**Intent-to-Tool Mapping Table** (lines 94-100):
```text
| User Intent | Keywords/Phrases | Tool to Use |
|-------------|------------------|-------------|
| Remove task | delete, remove, get rid of, don't need | delete_task |
```

### T093: Tool Descriptions and Confirmation Strategies ✅

**Location**: `backend/app/agent/prompts.py`

**Tool Description** (lines 80-88):
```text
### 5. delete_task
**Use when**: User wants to remove, delete, or get rid of a task permanently
**Required**: task_id (which task to delete)

Example triggers:
- "Delete task 7"
- "Remove the grocery task"
- "Get rid of task 2"
- "I don't need task 4 anymore"
```

**Confirmation Strategy** (lines 129-130):
```text
**delete_task success**:
"I've deleted '{title}' from your task list."
```

**Ambiguity Resolution Example** (lines 187-194):
```text
### Example 3: Handling Ambiguity
User: "Delete the task"
Assistant: "Which task would you like me to delete? Here are your current tasks:
1. Buy milk - Incomplete
2. Finish report - Complete"

User: "The milk one"
Assistant: [Calls delete_task with task_id=1]
Assistant: "I've deleted 'Buy milk' from your task list."
```

**Key Strategy**: When task_id is not explicitly provided:
1. Agent calls `list_tasks` to get all tasks
2. Agent matches user's natural language reference to task title
3. If single match → calls `delete_task` with resolved task_id
4. If multiple matches → asks user for clarification
5. If no match → asks user to clarify or shows available tasks

### T094: AgentRunner Tool Attachment ✅

**Location**: `backend/app/agent/runner.py` (line 128)

All MCP tools (including delete_task) are automatically loaded:

```python
# Get tools from MCP server
tools = self.mcp_server.get_tools_for_ai()
logger.info(f"Loaded {len(tools)} MCP tools")
```

The MCP server's `get_tools_for_ai()` method (in `backend/app/mcp/server.py` lines 115-135) returns all 5 tools in OpenAI-compatible format, including delete_task.

## Manual Validation Scenarios

### Scenario 1: Delete Task by ID (Direct Reference)

**Setup**: Create 3 tasks

**Request**:
```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Delete task 2"
  }'
```

**Expected Agent Behavior**:
1. Detects "delete" intent → maps to delete_task
2. Extracts task_id=2 from message
3. Calls `delete_task(user_id={user_id}, task_id=2)`
4. Receives success response with deleted task summary
5. Returns conversational confirmation:
   ```
   I've deleted 'Call dentist' from your task list.
   ```

**Validation**:
- ✅ tool_calls array contains delete_task invocation with task_id=2
- ✅ Response is conversational, not raw JSON
- ✅ Task 2 permanently removed from database
- ✅ deleted_task contains id and title of removed task

### Scenario 2: Delete Task by Title (Context-Aware Resolution)

**Setup**:
- Create task "Buy groceries"
- Task ID is unknown to user

**Request**:
```json
{
  "message": "Remove the grocery task"
}
```

**Expected Agent Behavior**:
1. Detects "remove" intent → maps to delete_task
2. NO explicit task_id provided → needs resolution
3. Calls `list_tasks(user_id={user_id})` to get all tasks
4. Matches "grocery" in user message to task title "Buy groceries"
5. Finds single match → task_id=1
6. Calls `delete_task(user_id={user_id}, task_id=1)`
7. Returns confirmation:
   ```
   I've deleted 'Buy groceries' from your task list.
   ```

**Validation**:
- ✅ tool_calls array contains TWO invocations:
  1. list_tasks (to resolve task)
  2. delete_task (to delete)
- ✅ Agent correctly matched "grocery" to "Buy groceries"
- ✅ Task 1 permanently removed from database

### Scenario 3: Ambiguous Delete Request (Multiple Matches)

**Setup**:
- Create "Buy groceries at Costco"
- Create "Buy groceries at Trader Joe's"

**Request**:
```json
{
  "message": "Delete the grocery task"
}
```

**Expected Agent Behavior**:
1. Detects delete intent
2. Calls list_tasks to resolve task
3. Finds TWO matches for "grocery"
4. Returns clarification request:
   ```
   Which task would you like me to delete? Here are your current tasks:
   1. Buy groceries at Costco - Incomplete
   2. Buy groceries at Trader Joe's - Incomplete

   Which one should I delete?
   ```

**Validation**:
- ✅ Agent does NOT make assumption about which task to delete
- ✅ Agent asks for clarification
- ✅ No delete_task call made yet

**Follow-up**:
```
User: "The Costco one"
Agent: [Calls delete_task with task_id=1]
Agent: "I've deleted 'Buy groceries at Costco' from your task list."
```

### Scenario 4: Task Not Found (Invalid ID)

**Request**:
```json
{
  "message": "Delete task 99"
}
```

**Expected Agent Behavior**:
1. Detects delete intent
2. Extracts task_id=99
3. Calls `delete_task(user_id={user_id}, task_id=99)`
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
User: "Delete the first one"
Agent: [Calls delete_task with task_id=1]
Agent: "I've deleted 'Buy groceries' from your task list."
```

**Validation**:
- ✅ Agent remembers context from Turn 1
- ✅ "the first one" correctly resolved to task_id=1
- ✅ No additional list_tasks call needed (context already present)

### Scenario 6: List → Delete Chain (Search and Delete)

**Setup**: Create tasks with "meeting" in title

**Request**:
```json
{
  "message": "Show me tasks about meetings and delete them all"
}
```

**Expected Agent Behavior**:
1. Calls `list_tasks(user_id={user_id}, search="meeting")`
2. Returns:
   ```
   I found 2 tasks about meetings:
   1. Team meeting - Incomplete
   2. Client meeting - Incomplete

   Would you like me to delete both of these tasks?
   ```

**Validation**:
- ✅ Agent lists matching tasks first
- ✅ Agent asks for confirmation before deleting multiple tasks
- ✅ Safe behavior - doesn't auto-delete without explicit confirmation

**Follow-up**:
```
User: "Yes, delete both"
Agent: [Calls delete_task with task_id=1]
Agent: [Calls delete_task with task_id=2]
Agent: "I've deleted both tasks:
- Team meeting
- Client meeting"
```

### Scenario 7: Pronoun Resolution

**Turn 1**:
```
User: "Show my incomplete tasks"
Agent: [Calls list_tasks with completed=false]
Agent: "Here are your incomplete tasks:
1. Buy groceries
2. Call dentist
3. Finish report"
```

**Turn 2**:
```
User: "Delete the second one"
Agent: [Calls delete_task with task_id=2]
Agent: "I've deleted 'Call dentist' from your task list."
```

**Validation**:
- ✅ Agent resolves "second one" to task_id=2
- ✅ Context from Turn 1 preserved
- ✅ Correct task deleted

### Scenario 8: Safe Deletion (No Auto-Delete)

**Request**:
```json
{
  "message": "Delete all my tasks"
}
```

**Expected Agent Behavior**:
1. Detects delete intent but recognizes "all" scope
2. Calls list_tasks to count tasks
3. Returns confirmation request:
   ```
   I found 5 tasks in your list. Are you sure you want to delete all of them? This cannot be undone.
   ```

**Validation**:
- ✅ Agent does NOT auto-delete all tasks
- ✅ Agent asks for explicit confirmation
- ✅ Warns that operation is irreversible

**Follow-up**:
```
User: "Yes, I'm sure"
Agent: [Calls delete_task 5 times, one for each task]
Agent: "I've deleted all 5 tasks from your list."
```

## Integration Tests

### Tool Chaining: List → Delete

**Test**: Natural language deletion without explicit task_id

```python
# Conversation state: No prior context
user_message = "Remove the grocery task"

# Expected tool call sequence:
# 1. list_tasks(user_id={user_id})
#    Returns: [{"id": 1, "title": "Buy groceries", ...}]
# 2. delete_task(user_id={user_id}, task_id=1)
#    Returns: {"success": True, "deleted_task": {"id": 1, "title": "Buy groceries"}, ...}

# Expected response:
# "I've deleted 'Buy groceries' from your task list."
```

### Tool Chaining: Search → Delete

**Test**: Find and delete tasks matching search criteria

```python
user_message = "Find tasks about meetings and delete the first one"

# Expected tool call sequence:
# 1. list_tasks(user_id={user_id}, search="meeting")
#    Returns: [{"id": 3, "title": "Team meeting"}, {"id": 5, "title": "Client meeting"}]
# 2. delete_task(user_id={user_id}, task_id=3)
#    Returns: {"success": True, "deleted_task": {"id": 3, "title": "Team meeting"}, ...}

# Expected response:
# "I found 2 tasks about meetings. I've deleted 'Team meeting' from your list."
```

### Confirmation Before Batch Delete

**Test**: Agent confirms before deleting multiple tasks

```python
user_message = "Delete all completed tasks"

# Expected tool call sequence:
# 1. list_tasks(user_id={user_id}, completed=True)
#    Returns: 3 completed tasks
# Agent should ask: "I found 3 completed tasks. Are you sure you want to delete all of them?"
# Wait for user confirmation before calling delete_task
```

## Success Criteria

### Functional Requirements ✅

- ✅ **FR-001**: Agent detects delete intent (delete/remove/get rid of)
- ✅ **FR-002**: delete_task tool called with correct parameters
- ✅ **FR-003**: User ownership enforced (user_id validation)
- ✅ **FR-004**: Task existence validated before deletion
- ✅ **FR-005**: Context-aware task resolution (matches by title)
- ✅ **FR-006**: Tool chaining (list_tasks → delete_task)
- ✅ **FR-007**: Ambiguous match handling (asks for clarification)
- ✅ **FR-008**: Task not found error handling
- ✅ **FR-009**: Multi-turn context awareness
- ✅ **FR-010**: Confirmation for batch deletions

### Technical Requirements ✅

- ✅ **Stateless**: No in-memory state, fresh query per request
- ✅ **User Isolation**: Only user's own tasks can be deleted
- ✅ **Error Handling**: TASK_NOT_FOUND, DATABASE_ERROR
- ✅ **Tool Transparency**: tool_calls array populated
- ✅ **API Contract**: Matches mcp-tools.yaml specification
- ✅ **Irreversible Warning**: Docstring warns operation cannot be undone
- ✅ **Task Summary**: Returns deleted task ID and title

### User Experience ✅

- ✅ Natural language deletion ("Remove the grocery task")
- ✅ Conversational confirmation ("I've deleted 'Buy groceries'...")
- ✅ Graceful error handling with helpful suggestions
- ✅ Context awareness (pronoun resolution, multi-turn)
- ✅ Safety features (confirmation for batch deletes)
- ✅ Ambiguity resolution (asks which task if multiple matches)

## Test Commands

### Delete by ID

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Delete task 1"
  }'
```

### Delete by Title (Context-Aware)

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Remove the grocery task"
  }'
```

### List and Delete (Multi-Step)

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me tasks about meetings and delete the first one"
  }'
```

### Pronoun Resolution

```bash
# Turn 1
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show my tasks"
  }'

# Turn 2
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Delete the second one",
    "conversation_id": "{conversation_id_from_turn_1}"
  }'
```

## Agent Behavior Patterns

### Pattern 1: Direct ID Deletion
```
User: "Delete task 5"
→ delete_task(task_id=5)
```

### Pattern 2: Title-Based Deletion
```
User: "Remove the grocery task"
→ list_tasks()
→ Match "grocery" to task title
→ delete_task(task_id={resolved_id})
```

### Pattern 3: Pronoun Resolution
```
User: "Show my tasks"
→ list_tasks()
User: "Delete the first one"
→ Recall task list from context
→ delete_task(task_id={first_task_id})
```

### Pattern 4: Search and Delete
```
User: "Find tasks about meetings and delete them"
→ list_tasks(search="meeting")
→ Ask for confirmation
User: "Yes"
→ delete_task(task_id=...) for each matching task
```

### Pattern 5: Safe Batch Delete
```
User: "Delete all my tasks"
→ list_tasks()
→ Ask: "Are you sure? You have 5 tasks. This cannot be undone."
User: "Yes"
→ delete_task(task_id=...) for each task
```

### Pattern 6: Ambiguity Handling
```
User: "Delete the grocery task"
→ list_tasks()
→ Find 2 matches: "Buy groceries at Costco", "Buy groceries at Trader Joe's"
→ Ask: "Which grocery task? 1) Costco 2) Trader Joe's"
```

## Known Limitations

1. **Partial title matching**: Agent uses fuzzy matching which may match unintended tasks if titles are similar
2. **Multi-language support**: Natural language processing works best in English
3. **Complex context**: Very long conversation histories may lose context
4. **Undo not supported**: Deleted tasks cannot be recovered (by design)

These are intentional scope limitations for Phase 9. Future enhancements could add soft delete with undo functionality.

## Conclusion

**Phase 9 Status**: ✅ COMPLETE

All 8 tasks (T087-T094) implemented. The delete_task MCP tool is fully functional, registered with the MCP server, integrated with the agent via AgentRunner, and guided by comprehensive system prompt rules including:

- ✅ Intent pattern recognition
- ✅ Task matching strategies (ID, title, context)
- ✅ Tool chaining examples (list → delete, search → delete)
- ✅ Error handling guidance
- ✅ Multi-turn context awareness
- ✅ Ambiguity resolution
- ✅ Safety features (confirmation for batch deletes)

Users can now delete tasks using natural language like:
- "Delete task 3" (direct ID reference)
- "Remove the grocery task" (context-aware resolution)
- "Delete the first one" (pronoun resolution)
- "Show tasks about meetings and delete them" (search and delete chain)

The agent will intelligently resolve task references, chain list_tasks when needed, ask for confirmation on batch deletions, and provide conversational confirmations.

**Checkpoint Achieved**: All 5 MCP tools implemented and registered (add_task, list_tasks, update_task, complete_task, delete_task)

**Next Phase**: Phase 10 - Frontend ChatKit Integration (T095-T103)
