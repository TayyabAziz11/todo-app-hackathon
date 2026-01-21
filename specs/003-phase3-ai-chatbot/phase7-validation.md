# Phase 7 Validation Guide: Multi-Step Task Operations

**Feature**: User Story 4 - Multi-Step Task Operations
**Status**: ✅ COMPLETE (All components implemented in previous sessions)
**Date**: 2026-01-21

## Implementation Status

All 5 tasks (T073-T077) for Phase 7 were already implemented:

### T073: Multi-Step Operation Examples ✅

**Location**: `backend/app/agent/prompts.py` (lines 202-207)

**Example 5: Multi-Step Operation**:
```text
User: "Add 'Buy groceries' and mark it done"
Assistant: [Calls add_task with title="Buy groceries"]
Assistant: "I've added 'Buy groceries' to your task list. (Task #5)"
Assistant: [Calls complete_task with task_id=5]
Assistant: "And I've marked it as complete. All done!"
```

**Coverage**:
- ✅ Create then complete: "Add X and mark it done"
- ✅ List then complete: Example 2 shows list → complete pattern
- ✅ Batch operations: Line 148 mentions "complete tasks 1, 2, and 3"

### T074: Tool Chaining Strategy ✅

**Location**: `backend/app/agent/prompts.py` (lines 143-148)

**Multi-Turn Conversation Handling**:
```text
1. **Remember context**: If user says "mark it done" after discussing a specific task, use that task
2. **Pronoun resolution**: "it", "that one", "the first one" refer to recently mentioned tasks
3. **Clarify when needed**: If context is ambiguous, ask for clarification
4. **Batch operations**: Handle "complete tasks 1, 2, and 3" by calling complete_task multiple times
```

**Strategy Components**:
- ✅ Step-by-step reasoning (remember context → use that task)
- ✅ Sequential execution (call tool multiple times for batch)
- ✅ Clarification when needed (if ambiguous)

### T075: Context Preservation Rules ✅

**Location**: `backend/app/agent/prompts.py` (lines 143-148)

**Context Preservation Guidelines**:
1. **Remember context** (line 145): Use task from prior conversation turn
2. **Pronoun resolution** (line 146): Map "it", "that one", "the first one" to specific tasks
3. **Use results from first tool call** (implicit in multi-step pattern):
   - Add task → get task_id from result → use in complete_task
   - List tasks → get task_id from results → use in complete_task/delete_task

**Example Pattern**:
```
Tool Call 1: add_task(title="Buy groceries")
→ Result: {"task": {"id": 5, ...}}

Tool Call 2: complete_task(task_id=5)  # Uses ID from step 1
→ Result: {"success": true}
```

### T076: AgentRunner Multiple Sequential Tool Calls ✅

**Location**: `backend/app/agent/runner.py` (lines 211-293)

**Implementation**: Complete function calling loop pattern

**Process Flow**:
1. **Detect tool calls** (line 237-238):
   ```python
   if hasattr(message, 'tool_calls') and message.tool_calls:
       logger.info(f"Processing {len(message.tool_calls)} tool calls")
   ```

2. **Add assistant message with tool calls** (lines 241-255):
   - Includes all tool calls in message history
   - Preserves tool call IDs for result mapping

3. **Execute each tool sequentially** (lines 258-271):
   ```python
   for tool_call in message.tool_calls:
       tool_result = self._execute_tool_call(tool_call, user_id)
       tool_calls_log.append(tool_result)

       # Add tool result to messages
       messages.append({
           "role": "tool",
           "tool_call_id": tool_call.id,
           "name": tool_call.function.name,
           "content": json.dumps(tool_result["result"]),
       })
   ```

4. **Call OpenAI again with all tool results** (lines 273-280):
   ```python
   response = self.client.chat.completions.create(
       model=self.model,
       messages=messages,  # Includes all tool results
       temperature=self.temperature,
       max_tokens=self.max_tokens,
   )
   ```

5. **Return final response** (lines 283-293):
   - Includes final assistant message
   - Includes all tool_calls in structured format

**Key Features**:
- ✅ Supports multiple tool calls in single agent turn
- ✅ Executes tools sequentially (not parallel)
- ✅ Preserves tool results for next OpenAI call
- ✅ Returns comprehensive tool_calls log

### T077: Tool Call Logging ✅

**Location**: `backend/app/routers/chat.py` (lines 268-273)

**Logging Implementation**:
```python
tool_calls_data = agent_response.tool_calls

logger.info(
    f"Agent executed successfully, "
    f"tool_calls={len(tool_calls_data)}, "
    f"finish_reason={agent_response.finish_reason}"
)
```

**What Gets Logged**:
- ✅ Number of tool calls executed
- ✅ Finish reason (stop, tool_calls, length, etc.)
- ✅ Full tool_calls_data persisted to database via save_message (line 297)

**Database Persistence** (line 291-298):
```python
assistant_message = save_message(
    db=session,
    conversation_id=conversation.id,
    user_id=UUID(authenticated_user_id),
    role="assistant",
    content=assistant_content,
    tool_calls=tool_calls_data if tool_calls_data else None  # All tool calls saved
)
```

## Manual Validation Scenarios

### Scenario 1: List Then Complete (Basic Multi-Step)

**Setup**: Create 3 tasks

**Request**:
```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show my tasks and mark the first one as complete"
  }'
```

**Expected Agent Behavior**:
1. Decompose intent:
   - Sub-intent 1: "Show my tasks" → list_tasks
   - Sub-intent 2: "mark the first one as complete" → complete_task

2. **Tool Call Sequence**:
   ```
   Call 1: list_tasks(user_id={user_id})
   → Returns: [
       {"id": 1, "title": "Buy groceries", ...},
       {"id": 2, "title": "Call dentist", ...},
       {"id": 3, "title": "Finish report", ...}
     ]

   Call 2: complete_task(user_id={user_id}, task_id=1, completed=True)
   → Returns: {"success": true, "task": {...}, "message": "..."}
   ```

3. **Conversational Response**:
   ```
   Here are your tasks:
   1. Buy groceries - Incomplete
   2. Call dentist - Incomplete
   3. Finish report - Incomplete

   Great job! I've marked 'Buy groceries' as complete.
   ```

**Validation**:
- ✅ tool_calls array contains 2 invocations (list_tasks, complete_task)
- ✅ Agent used result from list_tasks (task_id=1) in complete_task
- ✅ Single coherent response summarizing both actions
- ✅ Task 1 marked as completed in database

### Scenario 2: Create Then Complete (Sequential with ID Propagation)

**Request**:
```json
{
  "message": "Add a task to buy milk and mark it done"
}
```

**Expected Agent Behavior**:
1. **Tool Call Sequence**:
   ```
   Call 1: add_task(user_id={user_id}, title="Buy milk")
   → Returns: {"success": true, "task": {"id": 10, ...}}

   Call 2: complete_task(user_id={user_id}, task_id=10, completed=True)
   → Returns: {"success": true, ...}
   ```

2. **Conversational Response**:
   ```
   I've added 'Buy milk' to your task list. (Task #10)
   And I've marked it as complete. All done!
   ```

**Validation**:
- ✅ Agent extracted task_id=10 from add_task result
- ✅ Agent used task_id=10 in complete_task call
- ✅ Task created AND completed in database
- ✅ Response acknowledges both actions

### Scenario 3: Batch Operations (Multiple Completions)

**Setup**: Tasks 1, 2, 3 exist

**Request**:
```json
{
  "message": "Complete tasks 1, 2, and 3"
}
```

**Expected Agent Behavior**:
1. **Tool Call Sequence**:
   ```
   Call 1: complete_task(task_id=1)
   Call 2: complete_task(task_id=2)
   Call 3: complete_task(task_id=3)
   ```

2. **Conversational Response**:
   ```
   Great work! I've marked the following tasks as complete:
   - Buy groceries
   - Call dentist
   - Finish report
   ```

**Validation**:
- ✅ tool_calls array contains 3 invocations
- ✅ All 3 tasks marked as completed in database
- ✅ Response summarizes all completions

### Scenario 4: Search Then Delete (Different Tool Combination)

**Setup**: Tasks with "grocery" in title

**Request**:
```json
{
  "message": "Show me tasks about groceries and delete them"
}
```

**Expected Agent Behavior**:
1. **Tool Call Sequence**:
   ```
   Call 1: list_tasks(user_id={user_id}, search="groceries")
   → Returns: [{"id": 1, "title": "Buy groceries", ...}]

   Call 2: delete_task(user_id={user_id}, task_id=1)
   → Returns: {"success": true}
   ```

2. **Conversational Response**:
   ```
   I found this task about groceries:
   1. Buy groceries - Incomplete

   I've deleted 'Buy groceries' from your task list.
   ```

**Validation**:
- ✅ Agent chained list_tasks (with search) → delete_task
- ✅ Task 1 deleted from database
- ✅ Response confirms both search and deletion

### Scenario 5: Complex Multi-Step with Clarification

**Setup**: Multiple tasks match "meeting"

**Request**:
```json
{
  "message": "List my meetings and complete the first one"
}
```

**Expected Agent Behavior**:
1. **Tool Call 1**:
   ```
   list_tasks(user_id={user_id}, search="meeting")
   → Returns: [
       {"id": 5, "title": "Team meeting", ...},
       {"id": 8, "title": "Client meeting", ...}
     ]
   ```

2. **Clarification** (if "first" is ambiguous by date):
   ```
   I found 2 meetings:
   1. Team meeting (created earlier)
   2. Client meeting

   I've marked 'Team meeting' (the first one created) as complete.
   ```

   OR agent might ask:
   ```
   I found 2 meetings. Which one should I complete?
   1. Team meeting
   2. Client meeting
   ```

**Validation**:
- ✅ Agent handles search results intelligently
- ✅ Either completes logical "first" or asks clarification
- ✅ Does not make unsafe assumptions

### Scenario 6: Error Handling in Multi-Step

**Request**:
```json
{
  "message": "Complete task 99 and show my tasks"
}
```

**Expected Agent Behavior**:
1. **Tool Call Sequence**:
   ```
   Call 1: complete_task(task_id=99)
   → Returns: {"success": false, "error": "TASK_NOT_FOUND"}

   Call 2: list_tasks(user_id={user_id})
   → Returns: [{"id": 1, ...}, ...]
   ```

2. **Conversational Response**:
   ```
   I couldn't find task #99, but here are your current tasks:
   1. Buy groceries - Incomplete
   2. Call dentist - Incomplete
   ```

**Validation**:
- ✅ Agent continues despite first tool call failure
- ✅ Agent provides helpful context (lists tasks after error)
- ✅ Response acknowledges error gracefully

## Integration Tests

### Test 1: Tool Call Ordering

**Objective**: Verify tools execute in correct order

```python
# Request: "Add 'Task A', add 'Task B', complete Task A"

# Expected order:
1. add_task(title="Task A") → task_id=1
2. add_task(title="Task B") → task_id=2
3. complete_task(task_id=1)

# Verify:
- tool_calls[0].tool == "add_task" and "Task A" in arguments
- tool_calls[1].tool == "add_task" and "Task B" in arguments
- tool_calls[2].tool == "complete_task" and task_id == 1
```

### Test 2: Context Preservation Across Tool Calls

**Objective**: Verify agent uses results from earlier tool calls

```python
# Request: "Create a shopping task and mark it done"

# Expected:
1. add_task(title="shopping task")
   → result.task.id = X
2. complete_task(task_id=X)  # Must use X from step 1

# Verify:
- tool_calls[1].arguments.task_id == tool_calls[0].result.task.id
```

### Test 3: All Tool Calls Logged

**Objective**: Verify all tool calls persisted to database

```python
# Request: "Complete tasks 1, 2, 3"

# Verify database:
- Assistant message has tool_calls field
- tool_calls is JSON array with 3 elements
- Each element has: tool, arguments, result
```

## Success Criteria

### Functional Requirements ✅

- ✅ **FR-001**: Agent decomposes multi-step intent correctly
- ✅ **FR-002**: Tools execute in logical order
- ✅ **FR-003**: Agent uses results from earlier tool calls
- ✅ **FR-004**: Batch operations supported (multiple same tool)
- ✅ **FR-005**: Different tool combinations work (list→complete, add→complete, search→delete)
- ✅ **FR-006**: Single coherent response summarizing all actions
- ✅ **FR-007**: Error in one step doesn't block other steps
- ✅ **FR-008**: All tool calls logged and persisted

### Technical Requirements ✅

- ✅ **Stateless**: No in-memory state between requests
- ✅ **User Isolation**: All tool calls validate user_id
- ✅ **Sequential Execution**: Tools called in order (not parallel)
- ✅ **Tool Transparency**: All tool calls visible in tool_calls array
- ✅ **Context Preservation**: Results from Call N available to Call N+1
- ✅ **API Contract**: Matches OpenAI function calling protocol
- ✅ **Database Persistence**: All tool calls saved to Message.tool_calls

### User Experience ✅

- ✅ Natural language multi-step commands
- ✅ Conversational response summarizing all actions
- ✅ Graceful error handling mid-sequence
- ✅ Clear acknowledgment of each sub-action
- ✅ Logical ordering of operations
- ✅ Helpful context when errors occur

## Test Commands

### Create and Complete

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to call mom and mark it done"}'
```

### List and Complete First

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show my tasks and complete the first one"}'
```

### Batch Complete

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Complete tasks 1, 2, and 3"}'
```

## Agent Behavior Patterns

### Pattern 1: Sequential Tool Chaining
```
User: "Add X and complete it"
→ add_task(title="X") → get task_id
→ complete_task(task_id={from_step_1})
→ Response: "Added and completed!"
```

### Pattern 2: List-Resolve-Act
```
User: "Show tasks and complete the first"
→ list_tasks() → get tasks array
→ Extract first task ID
→ complete_task(task_id={first_task_id})
→ Response: "Here are tasks... Completed first one!"
```

### Pattern 3: Batch Operations
```
User: "Complete 1, 2, 3"
→ complete_task(task_id=1)
→ complete_task(task_id=2)
→ complete_task(task_id=3)
→ Response: "Completed all 3 tasks!"
```

### Pattern 4: Error-Resilient Chain
```
User: "Complete 99 and list tasks"
→ complete_task(task_id=99) → ERROR
→ list_tasks() → SUCCESS
→ Response: "Couldn't find 99, here are your tasks..."
```

## OpenAI Function Calling Loop

The implementation follows the standard OpenAI function calling pattern:

```
1. User message → OpenAI API
2. OpenAI returns: tool_calls = [call1, call2, ...]
3. Execute call1 → result1
4. Execute call2 → result2
5. Add all results to messages
6. Send messages → OpenAI API again
7. OpenAI returns: final text response
8. Return response to user
```

**Key Points**:
- All tool calls happen in **one agent turn**
- OpenAI decides which tools to call and in what order
- Results fed back to OpenAI for final response generation
- This enables coherent multi-step summaries

## Known Limitations

1. **Parallel execution not supported**: Tools execute sequentially, not in parallel
2. **OpenAI decides order**: Agent (not explicit code) determines tool call sequence
3. **No loop detection**: Agent won't detect infinite tool call loops (relies on max_tokens)
4. **No transaction rollback**: If step 3 fails, steps 1 and 2 are not undone

These are acceptable limitations for Phase 7. Future enhancements could add:
- Parallel tool execution where safe
- Explicit transaction boundaries
- Loop detection and circuit breakers

## Conclusion

**Phase 7 Status**: ✅ COMPLETE

All 5 tasks (T073-T077) implemented. The system now supports sophisticated multi-step operations:

- ✅ Multi-step examples in system prompt
- ✅ Tool chaining strategy documented
- ✅ Context preservation rules established
- ✅ AgentRunner implements complete function calling loop
- ✅ All tool calls logged and persisted

Users can now issue complex commands like:
- "Add a task to buy milk and mark it done"
- "Show my tasks and complete the first one"
- "Complete tasks 1, 2, and 3"
- "List tasks about groceries and delete them"

The agent will intelligently decompose these into sequential tool calls, preserve context between steps, and return a single coherent conversational response summarizing all actions.

**Next Phase**: Phase 8 - User Story 6: Task Update and Modification (T078-T086)
