# Skill: validate-agent-tool-usage

**Version**: 1.0.0
**Created**: 2026-01-19
**Category**: Phase 3 - Validation

---

## 1. Purpose

Validate that the AI agent properly uses MCP tools in Phase 3 AI Chatbot, ensuring correct tool invocation, no action hallucination, proper tool chaining for complex operations, and graceful error handling. This skill provides test scenarios, validation methodology, and automated testing approaches to verify agent behavior.

Proper agent-tool interaction is critical for user trust, system reliability, and task completion accuracy.

---

## 2. Applicable Agents

**Primary Agent**: `phase3-qa-demo`
- Tests agent behavior with MCP tools
- Validates tool usage patterns
- Identifies hallucination and errors

**Supporting Agents**:
- `todo-ai-agent-designer` - Agent behavior review
- `test-qa-validator` - Test automation

---

## 3. Input

### Prerequisites
- Functional chat endpoint (`POST /api/{user_id}/chat`)
- MCP tools implemented and registered
- Agent runner with system prompt
- Test database with sample data

### Requirements
- Validate tool usage correctness
- Detect action hallucination
- Verify tool chaining
- Test error handling

---

## 4. Output

## Validation Test Scenarios

### Category 1: Correct Tool Usage

#### Test 1.1: Single Tool Invocation

**User Input**: "Add a task to buy groceries"

**Expected Behavior**:
```yaml
Agent Actions:
  - Calls: add_task
  - Arguments:
      user_id: <user_id>
      title: "Buy groceries"
      description: null

Tool Response:
  success: true
  task:
    id: 1
    title: "Buy groceries"
    completed: false

Agent Response:
  "I've added 'Buy groceries' to your task list. This is task #1."
```

**Validation Checks**:
- [ ] Agent called add_task (exactly once)
- [ ] Arguments include user_id
- [ ] Title extracted correctly from user input
- [ ] Agent confirms action in response
- [ ] No hallucinated task ID before tool call

---

#### Test 1.2: Tool with Parameters

**User Input**: "Show me completed tasks"

**Expected Behavior**:
```yaml
Agent Actions:
  - Calls: list_tasks
  - Arguments:
      user_id: <user_id>
      completed: true

Tool Response:
  success: true
  tasks:
    - {id: 3, title: "Call dentist", completed: true}
    - {id: 5, title: "Finish report", completed: true}

Agent Response:
  "You have 2 completed tasks:
   1. Call dentist (task #3)
   2. Finish report (task #5)"
```

**Validation Checks**:
- [ ] Agent called list_tasks with completed=true filter
- [ ] Agent parsed tool response correctly
- [ ] Agent presented tasks in readable format
- [ ] Agent used actual task IDs from tool response

---

#### Test 1.3: Tool with Multiple Parameters

**User Input**: "Update task 3 to say 'Buy milk and eggs'"

**Expected Behavior**:
```yaml
Agent Actions:
  - Calls: update_task
  - Arguments:
      user_id: <user_id>
      task_id: 3
      title: "Buy milk and eggs"

Tool Response:
  success: true
  task:
    id: 3
    title: "Buy milk and eggs"

Agent Response:
  "I've updated task #3 to 'Buy milk and eggs'."
```

**Validation Checks**:
- [ ] Agent extracted task_id correctly (3)
- [ ] Agent extracted new title correctly
- [ ] Agent called update_task (not add_task)
- [ ] Agent confirmed specific task updated

---

### Category 2: No Action Hallucination

#### Test 2.1: No Pretend Actions

**User Input**: "Add a task to buy groceries"

**❌ HALLUCINATION (Bad)**:
```yaml
Agent Response:
  "I've added 'Buy groceries' to your task list. It's now task #1."

Agent Actions:
  - NO TOOL CALLS  # ❌ Agent pretended to add task
```

**✅ CORRECT (Good)**:
```yaml
Agent Actions:
  - Calls: add_task  # ✅ Actually called tool

Tool Response:
  success: true
  task: {id: 1, ...}

Agent Response:
  "I've added 'Buy groceries' to your task list. It's now task #1."
```

**Validation Checks**:
- [ ] Agent MUST call tool before claiming action
- [ ] Agent MUST use tool response data (not invented data)
- [ ] Agent MUST NOT say "I've added" without add_task call
- [ ] Agent MUST NOT say "Task #X" without tool returning ID

---

#### Test 2.2: No Invented Data

**User Input**: "What tasks do I have?"

**❌ HALLUCINATION (Bad)**:
```yaml
Agent Response:
  "You have 3 tasks:
   1. Buy groceries
   2. Call dentist
   3. Finish report"

Agent Actions:
  - NO TOOL CALLS  # ❌ Invented task list
```

**✅ CORRECT (Good)**:
```yaml
Agent Actions:
  - Calls: list_tasks  # ✅ Called tool first

Tool Response:
  tasks: [...]

Agent Response:
  "You have 3 tasks: [lists actual tasks from tool response]"
```

**Validation Checks**:
- [ ] Agent MUST call list_tasks before listing tasks
- [ ] Agent MUST list only tasks returned by tool
- [ ] Agent MUST NOT invent task titles
- [ ] Agent MUST NOT invent task counts

---

#### Test 2.3: No Assumed Success

**User Input**: "Delete task 5"

**❌ HALLUCINATION (Bad)**:
```yaml
Agent Actions:
  - Calls: delete_task
  - Arguments: {user_id: ..., task_id: 5}

Tool Response:
  success: false
  error: "Task not found"

Agent Response:
  "I've deleted task #5."  # ❌ Ignored error
```

**✅ CORRECT (Good)**:
```yaml
Agent Actions:
  - Calls: delete_task

Tool Response:
  success: false
  error: "Task not found"

Agent Response:
  "I couldn't delete task #5 because it doesn't exist. Would you like to see your current tasks?"  # ✅ Acknowledged error
```

**Validation Checks**:
- [ ] Agent MUST check tool response success field
- [ ] Agent MUST acknowledge errors (not claim success)
- [ ] Agent MUST explain what went wrong
- [ ] Agent MUST NOT proceed as if tool succeeded

---

### Category 3: Tool Chaining

#### Test 3.1: Sequential Operations

**User Input**: "Add a task to buy milk, then show me all my tasks"

**Expected Behavior**:
```yaml
Agent Actions:
  Step 1:
    - Calls: add_task
    - Arguments: {user_id: ..., title: "Buy milk"}

  Step 2:
    - Calls: list_tasks
    - Arguments: {user_id: ...}

Tool Responses:
  Step 1: {success: true, task: {id: 10, ...}}
  Step 2: {success: true, tasks: [...]}

Agent Response:
  "I've added 'Buy milk' to your list. Here are all your tasks:
   1. Buy groceries (task #1)
   2. Call dentist (task #3)
   3. Buy milk (task #10)"
```

**Validation Checks**:
- [ ] Agent chained two tool calls
- [ ] Agent called add_task BEFORE list_tasks
- [ ] Agent used results from both tools
- [ ] Agent presented cohesive response

---

#### Test 3.2: Find and Modify

**User Input**: "Mark the grocery shopping task as done"

**Expected Behavior**:
```yaml
Agent Actions:
  Step 1:
    - Calls: list_tasks
    - Arguments: {user_id: ...}
    - Rationale: Find task with "grocery" in title

  Step 2:
    - Calls: complete_task
    - Arguments: {user_id: ..., task_id: 1, completed: true}
    - Rationale: Mark found task as complete

Tool Responses:
  Step 1: {success: true, tasks: [{id: 1, title: "Buy groceries", ...}]}
  Step 2: {success: true, task: {id: 1, completed: true}}

Agent Response:
  "I found 'Buy groceries' (task #1) and marked it as complete."
```

**Validation Checks**:
- [ ] Agent chained list_tasks → complete_task
- [ ] Agent used task ID from list_tasks in complete_task
- [ ] Agent matched user intent ("grocery shopping") to task title
- [ ] Agent explained what was done

---

#### Test 3.3: Multi-Step Complex Operation

**User Input**: "Show me incomplete tasks, complete the first one, then show me what's left"

**Expected Behavior**:
```yaml
Agent Actions:
  Step 1:
    - Calls: list_tasks
    - Arguments: {user_id: ..., completed: false}

  Step 2:
    - Calls: complete_task
    - Arguments: {user_id: ..., task_id: <first_task_id>, completed: true}

  Step 3:
    - Calls: list_tasks
    - Arguments: {user_id: ..., completed: false}

Tool Responses:
  Step 1: {tasks: [{id: 1, ...}, {id: 2, ...}]}
  Step 2: {success: true, task: {id: 1, completed: true}}
  Step 3: {tasks: [{id: 2, ...}]}

Agent Response:
  "You had 2 incomplete tasks. I've completed 'Buy groceries' (task #1).
   You now have 1 remaining task: 'Call dentist' (task #2)."
```

**Validation Checks**:
- [ ] Agent chained 3 tool calls in correct order
- [ ] Agent used data from Step 1 in Step 2
- [ ] Agent explained complete workflow
- [ ] Agent presented before/after state

---

### Category 4: Error Handling

#### Test 4.1: Tool Failure

**User Input**: "Complete task 999"

**Expected Behavior**:
```yaml
Agent Actions:
  - Calls: complete_task
  - Arguments: {user_id: ..., task_id: 999, completed: true}

Tool Response:
  success: false
  error: "Task not found"

Agent Response:
  "I couldn't find task #999. It may have been deleted or the ID is incorrect.
   Would you like me to show your current tasks?"
```

**Validation Checks**:
- [ ] Agent acknowledged failure (not success)
- [ ] Agent explained error clearly
- [ ] Agent offered helpful next step
- [ ] Agent DID NOT retry without user input

---

#### Test 4.2: Graceful Degradation

**User Input**: "Update task 5 to 'New title'"

**Expected Behavior** (if task doesn't exist):
```yaml
Agent Actions:
  - Calls: update_task
  - Arguments: {user_id: ..., task_id: 5, title: "New title"}

Tool Response:
  success: false
  error: "Task not found"

Agent Response:
  "I couldn't update task #5 because it doesn't exist.
   Would you like me to:
   1. Show your existing tasks
   2. Create a new task with 'New title'"
```

**Validation Checks**:
- [ ] Agent didn't crash or give unhelpful error
- [ ] Agent provided actionable alternatives
- [ ] Agent maintained conversation flow
- [ ] Agent asked clarifying question

---

#### Test 4.3: Partial Failure Recovery

**User Input**: "Complete tasks 3, 5, and 999"

**Expected Behavior**:
```yaml
Agent Actions:
  - Calls: complete_task (task_id=3)
  - Calls: complete_task (task_id=5)
  - Calls: complete_task (task_id=999)

Tool Responses:
  Task 3: {success: true}
  Task 5: {success: true}
  Task 999: {success: false, error: "Task not found"}

Agent Response:
  "I've completed tasks #3 and #5 successfully.
   However, task #999 doesn't exist - it may have been deleted."
```

**Validation Checks**:
- [ ] Agent attempted all operations
- [ ] Agent reported both successes and failures
- [ ] Agent didn't stop at first failure
- [ ] Agent gave clear success/failure breakdown

---

## 5. Automated Validation Script

**File**: `backend/tests/test_agent_tool_usage.py`

```python
"""
Agent Tool Usage Validation Tests.

Tests that AI agent uses MCP tools correctly without hallucination.
"""

import pytest
from uuid import uuid4
from unittest.mock import Mock, patch

from app.agent.runner import create_agent_runner, AgentResponse
from app.models.user import User
from app.models.todo import Todo


class TestCorrectToolUsage:
    """Test agent calls tools correctly."""

    @patch('app.agent.runner.OpenAI')
    def test_add_task_calls_tool(self, mock_openai, test_db, test_user):
        """Agent must call add_task tool when user requests."""
        # Setup mock OpenAI response
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message = Mock()
        mock_completion.choices[0].message.tool_calls = [
            Mock(
                id="call_1",
                function=Mock(
                    name="add_task",
                    arguments='{"user_id": "' + str(test_user.id) + '", "title": "Buy groceries"}'
                )
            )
        ]
        mock_openai.return_value.chat.completions.create.return_value = mock_completion

        # Run agent
        runner = create_agent_runner(openai_api_key="test-key")
        response = runner.run(
            user_id=test_user.id,
            user_message="Add a task to buy groceries"
        )

        # Verify tool was called
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0]["tool_name"] == "add_task"
        assert "Buy groceries" in response.tool_calls[0]["arguments"]["title"]

    @patch('app.agent.runner.OpenAI')
    def test_list_tasks_with_filter(self, mock_openai, test_db, test_user):
        """Agent must call list_tasks with correct filter."""
        mock_completion = Mock()
        mock_completion.choices[0].message.tool_calls = [
            Mock(
                id="call_1",
                function=Mock(
                    name="list_tasks",
                    arguments='{"user_id": "' + str(test_user.id) + '", "completed": true}'
                )
            )
        ]
        mock_openai.return_value.chat.completions.create.return_value = mock_completion

        runner = create_agent_runner(openai_api_key="test-key")
        response = runner.run(
            user_id=test_user.id,
            user_message="Show me completed tasks"
        )

        # Verify filter applied
        assert response.tool_calls[0]["arguments"]["completed"] == True


class TestNoHallucination:
    """Test agent doesn't hallucinate actions."""

    @patch('app.agent.runner.OpenAI')
    def test_no_tool_call_no_claim(self, mock_openai, test_user):
        """Agent must not claim action without tool call."""
        # Mock: Agent responds without calling tools
        mock_completion = Mock()
        mock_completion.choices[0].message.tool_calls = None  # No tools called
        mock_completion.choices[0].message.content = "I've added the task"  # ❌ Hallucination
        mock_openai.return_value.chat.completions.create.return_value = mock_completion

        runner = create_agent_runner(openai_api_key="test-key")
        response = runner.run(
            user_id=test_user.id,
            user_message="Add task to buy milk"
        )

        # THIS IS A HALLUCINATION - should be caught by system prompt
        if len(response.tool_calls) == 0 and "added" in response.message.lower():
            pytest.fail("Agent hallucinated action without calling tool")

    def test_agent_uses_actual_task_ids(self, test_db, test_user):
        """Agent must use task IDs from tool response."""
        # Create actual task
        from sqlmodel import Session
        from app.database import get_engine

        engine = get_engine()
        with Session(engine) as session:
            todo = Todo(user_id=test_user.id, title="Test task", completed=False)
            session.add(todo)
            session.commit()
            session.refresh(todo)
            actual_task_id = todo.id

        # Now test agent retrieves correct ID
        runner = create_agent_runner(openai_api_key="test-key")
        response = runner.run(
            user_id=test_user.id,
            user_message="What tasks do I have?"
        )

        # Agent's response should mention actual task ID
        assert str(actual_task_id) in response.message


class TestToolChaining:
    """Test agent chains tools correctly."""

    @patch('app.agent.runner.OpenAI')
    def test_find_and_modify_chain(self, mock_openai, test_db, test_user):
        """Agent should chain list_tasks → complete_task."""
        # Setup: Two tool calls
        mock_completion_1 = Mock()
        mock_completion_1.choices[0].message.tool_calls = [
            Mock(function=Mock(name="list_tasks", arguments='{"user_id": "..."}'))
        ]

        mock_completion_2 = Mock()
        mock_completion_2.choices[0].message.tool_calls = [
            Mock(function=Mock(name="complete_task", arguments='{"user_id": "...", "task_id": 1}'))
        ]

        mock_openai.return_value.chat.completions.create.side_effect = [
            mock_completion_1,
            mock_completion_2
        ]

        runner = create_agent_runner(openai_api_key="test-key")
        response = runner.run(
            user_id=test_user.id,
            user_message="Mark the grocery task as done"
        )

        # Verify both tools called
        tool_names = [tc["tool_name"] for tc in response.tool_calls]
        assert "list_tasks" in tool_names
        assert "complete_task" in tool_names

    def test_sequential_operations(self, test_db, test_user):
        """Agent should execute operations in sequence."""
        runner = create_agent_runner(openai_api_key="test-key")
        response = runner.run(
            user_id=test_user.id,
            user_message="Add task 'Test', then show all tasks"
        )

        # Verify order
        if len(response.tool_calls) >= 2:
            assert response.tool_calls[0]["tool_name"] == "add_task"
            assert response.tool_calls[1]["tool_name"] == "list_tasks"


class TestErrorHandling:
    """Test agent handles tool errors gracefully."""

    def test_acknowledges_tool_failure(self, test_user):
        """Agent must acknowledge when tool fails."""
        runner = create_agent_runner(openai_api_key="test-key")
        response = runner.run(
            user_id=test_user.id,
            user_message="Delete task 999"  # Doesn't exist
        )

        # Tool should fail
        assert any(not tc["success"] for tc in response.tool_calls)

        # Agent response should acknowledge failure
        assert "couldn't" in response.message.lower() or \
               "not found" in response.message.lower() or \
               "doesn't exist" in response.message.lower()

    def test_offers_alternative_on_failure(self, test_user):
        """Agent should offer helpful alternative when tool fails."""
        runner = create_agent_runner(openai_api_key="test-key")
        response = runner.run(
            user_id=test_user.id,
            user_message="Update task 999 to 'New title'"
        )

        # Response should offer alternative
        assert "would you like" in response.message.lower() or \
               "you can" in response.message.lower() or \
               "try" in response.message.lower()


def test_run_agent_validation_suite():
    """Run complete agent tool usage validation."""
    pytest.main([__file__, "-v", "--tb=short"])
```

---

## 6. Manual Validation Protocol

### Validation Session Template

**File**: `tests/manual/agent_validation_session.md`

```markdown
# Agent Tool Usage Validation Session

**Date**: _______________
**Tester**: _______________
**Agent Version**: _______________

## Test Results

### 1. Correct Tool Usage

| Test | Input | Expected Tool | Actual Tool | Pass/Fail |
|------|-------|---------------|-------------|-----------|
| 1.1  | "Add task to buy milk" | add_task | _______ | ☐ Pass ☐ Fail |
| 1.2  | "Show completed tasks" | list_tasks (completed=true) | _______ | ☐ Pass ☐ Fail |
| 1.3  | "Update task 3 to 'New'" | update_task (id=3) | _______ | ☐ Pass ☐ Fail |

**Notes**: _______________________________________________

---

### 2. No Hallucination

| Test | Input | Hallucination Check | Pass/Fail |
|------|-------|---------------------|-----------|
| 2.1  | "Add task" | Agent called tool before claiming success? | ☐ Pass ☐ Fail |
| 2.2  | "List tasks" | Agent used actual task data (not invented)? | ☐ Pass ☐ Fail |
| 2.3  | "Delete task 999" | Agent acknowledged error (not claimed success)? | ☐ Pass ☐ Fail |

**Hallucination Examples Found**: _______________________________________________

---

### 3. Tool Chaining

| Test | Input | Expected Chain | Actual Chain | Pass/Fail |
|------|-------|----------------|--------------|-----------|
| 3.1  | "Add task, then list" | add_task → list_tasks | _______ | ☐ Pass ☐ Fail |
| 3.2  | "Mark grocery task done" | list_tasks → complete_task | _______ | ☐ Pass ☐ Fail |
| 3.3  | "Complete first incomplete task" | list_tasks → complete_task → list_tasks | _______ | ☐ Pass ☐ Fail |

**Chaining Issues**: _______________________________________________

---

### 4. Error Handling

| Test | Input | Error Scenario | Agent Response | Pass/Fail |
|------|-------|----------------|----------------|-----------|
| 4.1  | "Complete task 999" | Task not found | Acknowledged error? | ☐ Pass ☐ Fail |
| 4.2  | "Update task 5" | Task not found | Offered alternative? | ☐ Pass ☐ Fail |
| 4.3  | "Complete tasks 1, 2, 999" | Partial failure | Reported successes & failures? | ☐ Pass ☐ Fail |

**Error Handling Issues**: _______________________________________________

---

## Summary

**Total Tests**: ___ / ___
**Pass Rate**: ___%

**Critical Issues**:
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

**Recommendations**:
1. _______________________________________________
2. _______________________________________________

**Approved for Production**: ☐ Yes ☐ No (pending fixes)

**Signature**: _______________
```

---

## 7. Validation Report Format

### Standard Validation Report

```markdown
# Agent Tool Usage Validation Report

**Project**: Todo AI Chatbot - Phase 3
**Date**: 2026-01-19
**Validator**: QA Team
**Agent Version**: 1.0.0

---

## Executive Summary

**Overall Status**: ✅ PASS / ⚠️ PASS WITH WARNINGS / ❌ FAIL

**Test Results**:
- Correct Tool Usage: 3/3 ✅
- No Hallucination: 3/3 ✅
- Tool Chaining: 3/3 ✅
- Error Handling: 2/3 ⚠️

**Critical Issues**: 1
**Non-Critical Issues**: 2

---

## Detailed Results

### 1. Correct Tool Usage ✅

**Status**: PASS (3/3)

| Test ID | Test Case | Result | Notes |
|---------|-----------|--------|-------|
| 1.1 | Single tool invocation | ✅ PASS | Agent correctly called add_task |
| 1.2 | Tool with parameters | ✅ PASS | Filters applied correctly |
| 1.3 | Multiple parameters | ✅ PASS | Task ID and title extracted properly |

**No issues found in this category.**

---

### 2. No Hallucination ✅

**Status**: PASS (3/3)

| Test ID | Test Case | Result | Notes |
|---------|-----------|--------|-------|
| 2.1 | No pretend actions | ✅ PASS | Agent always called tools before claiming actions |
| 2.2 | No invented data | ✅ PASS | Agent used actual task data from tool responses |
| 2.3 | No assumed success | ✅ PASS | Agent acknowledged errors, didn't claim success |

**No hallucination detected.**

---

### 3. Tool Chaining ✅

**Status**: PASS (3/3)

| Test ID | Test Case | Result | Notes |
|---------|-----------|--------|-------|
| 3.1 | Sequential operations | ✅ PASS | Agent chained add → list correctly |
| 3.2 | Find and modify | ✅ PASS | Agent listed tasks before completing |
| 3.3 | Complex 3-step chain | ✅ PASS | All steps executed in correct order |

**Tool chaining works as expected.**

---

### 4. Error Handling ⚠️

**Status**: PASS WITH WARNINGS (2/3)

| Test ID | Test Case | Result | Notes |
|---------|-----------|--------|-------|
| 4.1 | Tool failure | ✅ PASS | Agent acknowledged error clearly |
| 4.2 | Graceful degradation | ✅ PASS | Agent offered alternatives |
| 4.3 | Partial failure recovery | ⚠️ WARNING | Agent didn't explain which tasks succeeded |

**Issue ID 001**: Partial failure reporting unclear
- **Severity**: Medium
- **Description**: When completing tasks 3, 5, and 999 (where 999 doesn't exist), agent said "I completed some tasks" without specifying which succeeded.
- **Expected**: "I've completed tasks #3 and #5. Task #999 doesn't exist."
- **Recommendation**: Update system prompt to require explicit success/failure breakdown.

---

## Issues Summary

### Critical Issues: 0

*None*

---

### Non-Critical Issues: 1

**Issue ID 001**: Partial failure reporting unclear
- **Category**: Error Handling
- **Severity**: Medium
- **Status**: Open
- **Assigned**: Agent Prompt Team

---

## Recommendations

1. **System Prompt Enhancement**: Add explicit instruction to list successes and failures separately in partial failure scenarios.

2. **Additional Test Coverage**: Add edge case tests for:
   - Empty task lists
   - Very long task titles
   - Special characters in task descriptions

3. **Production Monitoring**: Implement logging to track:
   - Tool call success rates
   - Hallucination incidents (if any)
   - Error handling quality

---

## Conclusion

The agent demonstrates **strong tool usage** with correct invocation, no hallucination, and proper chaining. Error handling is generally good but could be improved for partial failure scenarios.

**Recommendation**: ✅ **APPROVE for Production** with minor system prompt enhancement.

---

**Report Generated**: 2026-01-19
**Next Review**: After system prompt update
```

---

## 8. Continuous Validation

### Production Monitoring

**File**: `backend/app/api/middleware/agent_monitoring.py`

```python
"""
Agent tool usage monitoring middleware.

Logs agent behavior for continuous validation.
```python
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def log_agent_interaction(
    user_message: str,
    agent_response: str,
    tool_calls: List[Dict[str, Any]],
    user_id: str
):
    """
    Log agent interaction for analysis.

    Helps detect:
    - Hallucination patterns
    - Tool usage errors
    - Chaining failures
    """
    log_entry = {
        "user_id": user_id,
        "user_message": user_message,
        "tools_called": [tc["tool_name"] for tc in tool_calls],
        "tool_count": len(tool_calls),
        "response_length": len(agent_response),
        "all_tools_succeeded": all(tc.get("success", False) for tc in tool_calls),
    }

    # Check for potential hallucination
    action_verbs = ["added", "deleted", "completed", "updated", "created"]
    claimed_action = any(verb in agent_response.lower() for verb in action_verbs)
    actually_called_tool = len(tool_calls) > 0

    if claimed_action and not actually_called_tool:
        logger.warning(f"POTENTIAL HALLUCINATION: {log_entry}")

    logger.info(f"Agent interaction: {log_entry}")
```

---

## Implementation Checklist

- [ ] Create automated test suite: `tests/test_agent_tool_usage.py`
- [ ] Run correct tool usage tests
- [ ] Run hallucination detection tests
- [ ] Run tool chaining tests
- [ ] Run error handling tests
- [ ] Create manual validation protocol
- [ ] Conduct first manual validation session
- [ ] Document any issues found
- [ ] Generate validation report
- [ ] Set up production monitoring
- [ ] Configure hallucination alerts
- [ ] Train team on validation process
- [ ] Schedule recurring validation sessions

---

**Skill Version**: 1.0.0
**Last Updated**: 2026-01-19
**Status**: Ready for Implementation
