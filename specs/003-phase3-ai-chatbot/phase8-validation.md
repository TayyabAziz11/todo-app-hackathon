# Phase 8 Validation Guide: Task Update and Modification

**Feature**: User Story 6 - Task Update and Modification
**Status**: ✅ COMPLETE (All components implemented in previous sessions)
**Date**: 2026-01-21

## Implementation Status

All 9 tasks (T078-T086) for Phase 8 were already implemented:

### T078-T081: update_task MCP Tool ✅

**Location**: `backend/app/mcp/tools.py` (lines 210-279)

**Capabilities**:
- ✅ Update task title and/or description
- ✅ Partial updates - only modifies provided fields
- ✅ User ownership validation via `_get_user_task()` helper
- ✅ Task existence validation (returns TASK_NOT_FOUND if task doesn't exist)
- ✅ Permission validation (returns error if task doesn't belong to user)
- ✅ Timestamp update (updated_at set to current UTC time)
- ✅ Comprehensive error handling (validation and database failures)

**Input Schema** (`UpdateTaskInput`):
```python
user_id: UUID                    # Required - user authentication
task_id: int                     # Required - which task to update
title: Optional[str] = None      # Optional - new title
description: Optional[str] = None # Optional - new description
```

**Output Schema** (`UpdateTaskOutput`):
```python
success: bool
task: Optional[TaskResult]  # Updated task with new values
message: str                # "Task {id} updated successfully"
error: Optional[str]        # Error code if failed
```

**Partial Update Logic** (lines 250-255):
```python
# Apply updates - only modify fields that are provided
if input_data.title is not None:
    todo.title = input_data.title

if input_data.description is not None:
    # Empty string clears the description
    todo.description = input_data.description if input_data.description else None
```

**Error Responses**:
- `TASK_NOT_FOUND`: Task doesn't exist or doesn't belong to user
- `VALIDATION_ERROR`: No updates provided (both title and description are None)
- `DATABASE_ERROR`: Database operation failed

### T082: MCP Server Registration ✅

**Location**: `backend/app/mcp/tools.py` (line 405)

```python
TOOL_HANDLERS = {
    "add_task": add_task,
    "list_tasks": list_tasks,
    "update_task": update_task,  # ✅ Registered
    "complete_task": complete_task,
    "delete_task": delete_task,
}
```

### T083: Intent Patterns for Task Updates ✅

**Location**: `backend/app/agent/prompts.py` (lines 57-67)

**Intent Keywords**:
- "change", "update", "edit", "modify", "rename", "fix"
- Natural variations: "revise", "alter", "adjust"

**Example Triggers**:
```text
- "Change task 5 to 'Buy organic groceries'"
- "Update the description of my first task"
- "Rename the grocery task to 'Shopping at Costco'"
- "Edit task 3"
- "Modify the title of task 1 to 'Prepare presentation'"
```

**Intent-to-Tool Mapping Table** (lines 94-100):
```text
| User Intent | Keywords/Phrases | Tool to Use |
|-------------|------------------|-------------|
| Edit task | change, update, edit, modify, rename, fix | update_task |
```

### T084: Tool Descriptions and Field Update Strategies ✅

**Location**: `backend/app/agent/prompts.py`

**Tool Description** (lines 57-67):
```text
### 3. update_task
**Use when**: User wants to change, edit, modify, or rename a task
**Required**: task_id (which task to update)
**Optional**: title (new title), description (new description)

Example triggers:
- "Change task 5 to 'Buy organic groceries'"
- "Update the description of my first task"
- "Rename the grocery task to 'Shopping at Costco'"
- "Edit task 3"
```

**Field Update Strategies** (lines 102-105):
```text
**Ambiguity Resolution**:
- If unclear between update and complete: ask "Do you want to edit the task details or mark it as done?"
- If unclear which task: use list_tasks first, then ask user to specify
- If user says "done with task" without ID: ask which task or list tasks first
```

**Key Strategy**: When task_id is not explicitly provided:
1. Agent calls `list_tasks` to get all tasks
2. Agent matches user's natural language reference to task title
3. If single match → calls `update_task` with resolved task_id
4. If multiple matches → asks user for clarification
5. If no match → asks user to clarify or shows available tasks

### T085: Task Not Found Handling ✅

**Location**: `backend/app/agent/prompts.py` (lines 134-136)

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

Same pattern applies to update_task failures.

### T086: AgentRunner Tool Attachment ✅

**Location**: `backend/app/agent/runner.py` (line 128)

All MCP tools (including update_task) are automatically loaded:

```python
# Get tools from MCP server
tools = self.mcp_server.get_tools_for_ai()
logger.info(f"Loaded {len(tools)} MCP tools")
```

The MCP server's `get_tools_for_ai()` method returns all 5 tools in OpenAI-compatible format, including update_task.

## Manual Validation Scenarios

### Scenario 1: Update Task by ID (Direct Reference)

**Setup**: Create 3 tasks

**Request**:
```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Change task 2 to Buy organic groceries"
  }'
```

**Expected Agent Behavior**:
1. Detects "change" intent → maps to update_task
2. Extracts task_id=2 from message
3. Extracts new title="Buy organic groceries"
4. Calls `update_task(user_id={user_id}, task_id=2, title="Buy organic groceries")`
5. Receives success response
6. Returns conversational confirmation:
   ```
   I've updated task 2 to "Buy organic groceries".
   ```

**Validation**:
- ✅ tool_calls array contains update_task invocation with task_id=2
- ✅ Response is conversational, not raw JSON
- ✅ Task 2 title updated in database
- ✅ Task 2 description unchanged (partial update)
- ✅ Task 2 updated_at timestamp updated

### Scenario 2: Update Task by Title (Context-Aware Resolution)

**Setup**:
- Create task "Buy groceries"
- Task ID is unknown to user

**Request**:
```json
{
  "message": "Rename the grocery task to Shopping at Costco"
}
```

**Expected Agent Behavior**:
1. Detects "rename" intent → maps to update_task
2. NO explicit task_id provided → needs resolution
3. Calls `list_tasks(user_id={user_id})` to get all tasks
4. Matches "grocery" in user message to task title "Buy groceries"
5. Finds single match → task_id=1
6. Extracts new title="Shopping at Costco"
7. Calls `update_task(user_id={user_id}, task_id=1, title="Shopping at Costco")`
8. Returns confirmation:
   ```
   I've renamed "Buy groceries" to "Shopping at Costco".
   ```

**Validation**:
- ✅ tool_calls array contains TWO invocations:
  1. list_tasks (to resolve task)
  2. update_task (to update title)
- ✅ Agent correctly matched "grocery" to "Buy groceries"
- ✅ Task 1 title updated to "Shopping at Costco" in database
- ✅ Task 1 description unchanged

### Scenario 3: Partial Update (Title Only)

**Setup**: Task 1 exists with title="Buy groceries" and description="Get items from Costco"

**Request**:
```json
{
  "message": "Change task 1 title to Buy organic vegetables"
}
```

**Expected Agent Behavior**:
1. Detects "change...title" intent → update_task with title only
2. Extracts task_id=1
3. Calls `update_task(user_id={user_id}, task_id=1, title="Buy organic vegetables")`
4. Returns confirmation:
   ```
   I've updated the title of task 1 to "Buy organic vegetables".
   ```

**Validation**:
- ✅ Task 1 title updated to "Buy organic vegetables"
- ✅ Task 1 description UNCHANGED (still "Get items from Costco")
- ✅ Partial update logic working correctly

### Scenario 4: Partial Update (Description Only)

**Setup**: Task 1 exists with title="Buy groceries" and description="Get items from Costco"

**Request**:
```json
{
  "message": "Update task 1 description to Include organic produce and dairy"
}
```

**Expected Agent Behavior**:
1. Detects "update...description" intent → update_task with description only
2. Extracts task_id=1
3. Calls `update_task(user_id={user_id}, task_id=1, description="Include organic produce and dairy")`
4. Returns confirmation:
   ```
   I've updated the description of task 1.
   ```

**Validation**:
- ✅ Task 1 title UNCHANGED (still "Buy groceries")
- ✅ Task 1 description updated to "Include organic produce and dairy"
- ✅ Partial update logic working correctly

### Scenario 5: Update Both Fields

**Request**:
```json
{
  "message": "Change task 2 title to Prepare presentation and update the description to Quarterly business review slides"
}
```

**Expected Agent Behavior**:
1. Detects update intent for both title and description
2. Extracts task_id=2
3. Calls `update_task(user_id={user_id}, task_id=2, title="Prepare presentation", description="Quarterly business review slides")`
4. Returns confirmation:
   ```
   I've updated task 2. The title is now "Prepare presentation" and I've updated the description.
   ```

**Validation**:
- ✅ Task 2 title updated to "Prepare presentation"
- ✅ Task 2 description updated to "Quarterly business review slides"
- ✅ Both fields updated in single tool call

### Scenario 6: Update + Complete Chain (Multi-Step)

**Request**:
```json
{
  "message": "Rename task 3 to Buy organic milk and mark it done"
}
```

**Expected Agent Behavior**:
1. Detects two intents: rename (update_task) + mark done (complete_task)
2. Calls `update_task(user_id={user_id}, task_id=3, title="Buy organic milk")`
3. Calls `complete_task(user_id={user_id}, task_id=3, completed=True)`
4. Returns confirmation:
   ```
   I've renamed task 3 to "Buy organic milk" and marked it as complete. All done!
   ```

**Validation**:
- ✅ tool_calls array contains TWO invocations:
  1. update_task (rename)
  2. complete_task (mark done)
- ✅ Task 3 title updated to "Buy organic milk"
- ✅ Task 3 completed set to True
- ✅ Multi-step operation executed in correct order

### Scenario 7: Task Not Found (Invalid ID)

**Request**:
```json
{
  "message": "Update task 99 to New title"
}
```

**Expected Agent Behavior**:
1. Detects update intent
2. Extracts task_id=99
3. Calls `update_task(user_id={user_id}, task_id=99, title="New title")`
4. Tool returns `TASK_NOT_FOUND` error
5. Agent responds with helpful error:
   ```
   I couldn't find task #99. Would you like me to show you your current tasks so you can pick the right one?
   ```

**Validation**:
- ✅ Error handled gracefully
- ✅ Agent offers to list tasks
- ✅ No task modified in database

### Scenario 8: No Updates Provided (Validation Error)

**Setup**: Hypothetical edge case if agent calls update_task without title or description

**Expected Agent Behavior**:
1. Agent should NOT make this mistake (system prompt prevents it)
2. If it happens, tool returns `VALIDATION_ERROR`
3. Agent should ask for clarification:
   ```
   What would you like me to update? I can change the title, description, or both.
   ```

**Validation**:
- ✅ Tool validation prevents empty updates
- ✅ Agent guidance prevents this scenario

### Scenario 9: Clear Description (Empty String)

**Setup**: Task 1 has description="Get items from Costco"

**Request**:
```json
{
  "message": "Remove the description from task 1"
}
```

**Expected Agent Behavior**:
1. Detects "remove description" intent
2. Calls `update_task(user_id={user_id}, task_id=1, description="")`
3. Tool sets description to None (empty string clears it)
4. Returns confirmation:
   ```
   I've removed the description from task 1.
   ```

**Validation**:
- ✅ Task 1 description set to None in database
- ✅ Task 1 title unchanged
- ✅ Empty string correctly clears description field

## Integration Tests

### Tool Chaining: List → Update

**Test**: Natural language update without explicit task_id

```python
# Conversation state: No prior context
user_message = "Rename the meeting task to Team standup"

# Expected tool call sequence:
# 1. list_tasks(user_id={user_id})
#    Returns: [{"id": 3, "title": "Attend team meeting", ...}]
# 2. update_task(user_id={user_id}, task_id=3, title="Team standup")
#    Returns: {"success": True, "task": {...}, "message": "..."}

# Expected response:
# "I've renamed 'Attend team meeting' to 'Team standup'."
```

### Tool Chaining: Update → Complete

**Test**: Multi-step operation with update and completion

```python
user_message = "Change task 2 to Buy milk and mark it done"

# Expected tool call sequence:
# 1. update_task(user_id={user_id}, task_id=2, title="Buy milk")
# 2. complete_task(user_id={user_id}, task_id=2, completed=True)

# Expected response:
# "I've updated task 2 to 'Buy milk' and marked it as complete."
```

### Pronoun Resolution

**Test**: Multi-turn conversation with pronoun reference

```python
# Turn 1
user_message_1 = "Show my incomplete tasks"
# Agent calls list_tasks, returns tasks 1, 2, 3

# Turn 2
user_message_2 = "Rename the second one to Call dentist appointment"
# Agent should:
# - Recall task list from Turn 1
# - Resolve "second one" to task_id=2
# - Call update_task(task_id=2, title="Call dentist appointment")
```

## Success Criteria

### Functional Requirements ✅

- ✅ **FR-001**: Agent detects update intent (change/update/edit/modify/rename)
- ✅ **FR-002**: update_task tool called with correct parameters
- ✅ **FR-003**: User ownership enforced (user_id validation)
- ✅ **FR-004**: Task existence validated before update
- ✅ **FR-005**: Partial updates supported (title only, description only, or both)
- ✅ **FR-006**: Context-aware task resolution (matches by title)
- ✅ **FR-007**: Tool chaining (list_tasks → update_task)
- ✅ **FR-008**: Task not found error handling
- ✅ **FR-009**: Multi-step operations (update + complete)

### Technical Requirements ✅

- ✅ **Stateless**: No in-memory state, fresh query per request
- ✅ **User Isolation**: Only user's own tasks can be updated
- ✅ **Error Handling**: TASK_NOT_FOUND, VALIDATION_ERROR, DATABASE_ERROR
- ✅ **Tool Transparency**: tool_calls array populated
- ✅ **API Contract**: Matches mcp-tools.yaml specification
- ✅ **Timestamp Update**: updated_at set on update
- ✅ **Partial Update Logic**: Only updates provided fields

### User Experience ✅

- ✅ Natural language updates ("Rename the grocery task to...")
- ✅ Conversational confirmation ("I've updated task 2 to...")
- ✅ Graceful error handling with helpful suggestions
- ✅ Context awareness (pronoun resolution, multi-turn)
- ✅ Multi-step support (update + complete in one message)
- ✅ Field-specific updates (title only, description only, or both)

## Test Commands

### Update by ID (Title)

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Change task 1 to Buy organic groceries"
  }'
```

### Update by Title (Context-Aware)

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Rename the grocery task to Shopping at Whole Foods"
  }'
```

### Update Description Only

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Update task 2 description to Include organic produce"
  }'
```

### Update Both Fields

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Change task 3 to Prepare slides and update description to Q4 business review"
  }'
```

### Update + Complete Chain

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Rename task 1 to Buy milk and mark it done"
  }'
```

### Clear Description

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Remove the description from task 2"
  }'
```

## Agent Behavior Patterns

### Pattern 1: Direct ID + Title Update
```
User: "Change task 5 to Buy organic groceries"
→ update_task(task_id=5, title="Buy organic groceries")
```

### Pattern 2: Title-Based Resolution + Update
```
User: "Rename the grocery task to Shopping at Costco"
→ list_tasks()
→ Match "grocery" to task title
→ update_task(task_id={resolved_id}, title="Shopping at Costco")
```

### Pattern 3: Field-Specific Update
```
User: "Update task 3 description to Include dairy products"
→ update_task(task_id=3, description="Include dairy products")
# Note: title is NOT updated (partial update)
```

### Pattern 4: Multi-Field Update
```
User: "Change task 2 title to Prepare presentation and description to Q4 review slides"
→ update_task(task_id=2, title="Prepare presentation", description="Q4 review slides")
```

### Pattern 5: Update + Complete Chain
```
User: "Rename task 1 to Buy milk and mark it done"
→ update_task(task_id=1, title="Buy milk")
→ complete_task(task_id=1, completed=True)
```

### Pattern 6: Clear Description
```
User: "Remove the description from task 4"
→ update_task(task_id=4, description="")
# Tool sets description to None
```

## Known Limitations

1. **Partial title matching**: Agent uses fuzzy matching which may match unintended tasks if titles are similar
2. **Multi-language support**: Natural language processing works best in English
3. **Complex context**: Very long conversation histories may lose context
4. **Batch updates**: "Update all my grocery tasks" requires explicit implementation

These are intentional scope limitations for Phase 8. Future enhancements can improve matching algorithms and add batch operations.

## Conclusion

**Phase 8 Status**: ✅ COMPLETE

All 9 tasks (T078-T086) implemented. The update_task MCP tool is fully functional, registered with the MCP server, integrated with the agent via AgentRunner, and guided by comprehensive system prompt rules including:

- ✅ Intent pattern recognition
- ✅ Task matching strategies (ID, title, context)
- ✅ Partial update logic (only updates provided fields)
- ✅ Tool chaining examples (list → update, update → complete)
- ✅ Error handling guidance
- ✅ Field-specific update strategies

Users can now update tasks using natural language like:
- "Change task 3 to Buy organic groceries" (direct ID reference)
- "Rename the grocery task to Shopping at Costco" (context-aware resolution)
- "Update task 2 description to Include dairy" (partial update - description only)
- "Change task 1 to Buy milk and mark it done" (multi-step: update + complete)

The agent will intelligently resolve task references, support partial updates, chain list_tasks when needed, and provide conversational confirmations.

**Next Phase**: Phase 9 - Delete Task Support (T087-T094)
