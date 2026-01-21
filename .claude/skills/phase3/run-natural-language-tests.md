# Skill: run-natural-language-tests

**Version**: 1.0.0
**Last Updated**: 2026-01-20
**Applicable Agents**: phase3-qa-demo

---

## 1. Purpose

Test the Phase 3 AI-powered Todo Chatbot using natural language scenarios to validate that the agent correctly interprets user intent, invokes the appropriate MCP tools, and returns accurate, helpful responses. This skill provides comprehensive test cases covering all CRUD operations, multi-step workflows, edge cases, and natural language variations.

---

## 2. Applicable Agents

**Primary Agent**: `phase3-qa-demo`
- Responsible for end-to-end QA testing and demo preparation
- Executes test scenarios and validates behavior
- Documents results and identifies issues

**Supporting Agents**:
- `mcp-compliance-validator`: Validates tool invocations are correct
- `test-qa-validator`: Validates test coverage and quality

---

## 3. Input

### Prerequisites

1. **Deployed Chatbot**:
   - Backend API running at `http://localhost:8000` or production URL
   - Frontend chat UI accessible at `http://localhost:3000` or production URL
   - MCP server initialized with all 5 tools registered
   - Database seeded with test user account

2. **Test User**:
   ```json
   {
     "user_id": "550e8400-e29b-41d4-a716-446655440000",
     "email": "test@example.com",
     "auth_token": "Bearer eyJhbGc..."
   }
   ```

3. **Test Data**:
   - Clean database state or known initial state
   - Test conversation for isolation

### Requirements

- Access to both ChatKit UI and direct API for testing
- Ability to inspect tool calls and database state
- Logging enabled for debugging failures

---

## 4. Output

### Test Suite Structure

```
backend/tests/test_natural_language.py
  ├── TestBasicCRUD
  │   ├── test_add_task_variations
  │   ├── test_list_tasks_variations
  │   ├── test_update_task_variations
  │   ├── test_complete_task_variations
  │   └── test_delete_task_variations
  ├── TestMultiStepCommands
  │   ├── test_add_and_list
  │   ├── test_list_and_complete
  │   └── test_complex_workflow
  ├── TestEdgeCases
  │   ├── test_ambiguous_input
  │   ├── test_nonexistent_task
  │   └── test_invalid_parameters
  └── TestNaturalLanguageVariations
      ├── test_informal_language
      ├── test_formal_language
      └── test_typos_and_misspellings
```

### Test Result Format

```markdown
# Natural Language Test Results

**Date**: 2026-01-20
**Tester**: phase3-qa-demo agent
**Environment**: Localhost development
**Total Tests**: 45
**Passed**: 42
**Failed**: 3

## Test Category: Basic CRUD - Add Task

### Test 1.1: Direct Add Command
- **Input**: "Add a task to buy groceries"
- **Expected**:
  - Tool: `add_task(title="Buy groceries")`
  - Response: "I've added 'Buy groceries' to your task list."
- **Actual**: ✅ PASS
  - Tool Call: `add_task(title="Buy groceries", description=None, due_date=None)`
  - Response: "I've added 'Buy groceries' to your task list. It's task #1."

### Test 1.2: Add with Details
- **Input**: "Create a task called 'Finish report' due tomorrow with high priority"
- **Expected**:
  - Tool: `add_task(title="Finish report", due_date="2026-01-21", priority="high")`
  - Response: Confirmation with due date and priority
- **Actual**: ❌ FAIL
  - Tool Call: `add_task(title="Finish report", due_date="2026-01-21")`
  - Issue: Priority parameter not extracted (schema doesn't support priority)
```

---

## 5. Comprehensive Test Cases

### 5.1 Add Task Scenarios

#### Test 1.1: Basic Add
```yaml
Input: "Add a task to buy groceries"
Expected Tool Call: add_task(title="Buy groceries")
Expected Response Pattern: "I've added 'Buy groceries'"
Validation:
  - Tool called exactly once
  - Task created in database
  - Response confirms task title
```

#### Test 1.2: Add with Natural Language
```yaml
Input: "Remind me to call mom"
Expected Tool Call: add_task(title="Call mom")
Expected Response Pattern: "I've added 'Call mom'"
Validation:
  - "Remind me to" converted to task creation
  - Response is natural and conversational
```

#### Test 1.3: Add with Due Date
```yaml
Input: "Add task to submit report by Friday"
Expected Tool Call: add_task(title="Submit report", due_date="2026-01-24")
Expected Response Pattern: "I've added 'Submit report' with due date Friday"
Validation:
  - Due date correctly parsed from natural language
  - Response mentions due date
```

#### Test 1.4: Add Multiple Tasks (Single Message)
```yaml
Input: "Add three tasks: buy milk, walk dog, and pay bills"
Expected Tool Calls:
  1. add_task(title="Buy milk")
  2. add_task(title="Walk dog")
  3. add_task(title="Pay bills")
Expected Response Pattern: "I've added 3 tasks: Buy milk, Walk dog, and Pay bills"
Validation:
  - Multiple tool calls in sequence
  - All tasks created
  - Response lists all tasks
```

#### Test 1.5: Add with Description
```yaml
Input: "Create a task to review code. Make sure to check for security issues and performance bottlenecks."
Expected Tool Call: add_task(
  title="Review code",
  description="Check for security issues and performance bottlenecks"
)
Expected Response Pattern: Confirms task with description
Validation:
  - Title extracted correctly
  - Description captured from second sentence
```

---

### 5.2 List Tasks Scenarios

#### Test 2.1: List All Tasks
```yaml
Setup: Database has 3 tasks (Task A, Task B, Task C)
Input: "Show me all my tasks"
Expected Tool Call: list_tasks(status=None)
Expected Response Pattern: Lists all 3 tasks with titles
Validation:
  - Tool called once
  - Response includes all task titles
  - Order is maintained (by creation date)
```

#### Test 2.2: List Pending Tasks
```yaml
Setup: 2 pending tasks, 1 completed task
Input: "What tasks do I still need to do?"
Expected Tool Call: list_tasks(status="pending")
Expected Response Pattern: Lists only 2 pending tasks
Validation:
  - Status filter applied
  - Completed task not shown
```

#### Test 2.3: List Completed Tasks
```yaml
Setup: 2 pending, 1 completed
Input: "Show me what I've finished"
Expected Tool Call: list_tasks(status="completed")
Expected Response Pattern: Lists only completed task
Validation:
  - Status="completed" parameter used
  - Only completed task shown
```

#### Test 2.4: Empty List
```yaml
Setup: No tasks in database
Input: "List my tasks"
Expected Tool Call: list_tasks()
Expected Response Pattern: "You don't have any tasks yet" or similar
Validation:
  - Tool called successfully
  - Empty result handled gracefully
  - Suggests adding a task
```

#### Test 2.5: List Natural Variations
```yaml
Inputs (all should call list_tasks):
  - "What's on my todo list?"
  - "Show my tasks"
  - "What do I need to do today?"
  - "Display all todos"
Validation:
  - All variations map to list_tasks
  - Responses are natural and varied
```

---

### 5.3 Update Task Scenarios

#### Test 3.1: Update Task Title
```yaml
Setup: Task #1 "Buy groceries" exists
Input: "Change task 1 to 'Buy groceries and milk'"
Expected Tool Call: update_task(task_id=1, title="Buy groceries and milk")
Expected Response Pattern: "I've updated task #1"
Validation:
  - Correct task_id identified
  - New title applied
  - Database reflects change
```

#### Test 3.2: Update by Task Name
```yaml
Setup: Task "Submit report" exists
Input: "Update the 'Submit report' task to be due tomorrow"
Expected Tool Call:
  1. list_tasks() (to find task by name)
  2. update_task(task_id=X, due_date="2026-01-21")
Expected Response Pattern: "I've updated 'Submit report' to be due tomorrow"
Validation:
  - Task found by title
  - Due date updated
```

#### Test 3.3: Update Description
```yaml
Setup: Task #2 exists with title "Review code"
Input: "Add a note to task 2: focus on authentication module"
Expected Tool Call: update_task(
  task_id=2,
  description="Focus on authentication module"
)
Expected Response Pattern: Confirms description added
Validation:
  - Description field updated
  - Original title preserved
```

#### Test 3.4: Update Nonexistent Task
```yaml
Setup: Only tasks 1-3 exist
Input: "Update task 99 to be high priority"
Expected Tool Call: update_task(task_id=99, ...)
Expected Response Pattern: "Task #99 doesn't exist" or error message
Validation:
  - Tool called with correct ID
  - Error response from tool handled gracefully
  - User informed of issue
```

---

### 5.4 Complete Task Scenarios

#### Test 4.1: Complete by ID
```yaml
Setup: Task #1 "Buy groceries" is pending
Input: "Mark task 1 as complete"
Expected Tool Call: complete_task(task_id=1)
Expected Response Pattern: "I've marked task #1 'Buy groceries' as complete"
Validation:
  - Task status updated to completed
  - Response confirms completion
```

#### Test 4.2: Complete by Name
```yaml
Setup: Task "Call mom" exists
Input: "I finished calling mom"
Expected Tool Call:
  1. list_tasks() (to find task)
  2. complete_task(task_id=X)
Expected Response Pattern: "Great! I've marked 'Call mom' as complete"
Validation:
  - Task found by title matching
  - Status updated
  - Positive acknowledgment
```

#### Test 4.3: Complete Natural Language
```yaml
Setup: Task "Walk dog" exists
Input: "Done with walking the dog"
Expected Tool Call:
  1. list_tasks()
  2. complete_task(task_id=X)
Expected Response Pattern: Confirms "Walk dog" completed
Validation:
  - Intent to complete recognized
  - Task title matched (even with slight variation)
```

#### Test 4.4: Complete Already Completed
```yaml
Setup: Task #1 already has status="completed"
Input: "Mark task 1 as done"
Expected Tool Call: complete_task(task_id=1)
Expected Response Pattern: "Task #1 is already completed" or similar
Validation:
  - Tool call succeeds (idempotent)
  - User informed of current state
```

---

### 5.5 Delete Task Scenarios

#### Test 5.1: Delete by ID
```yaml
Setup: Task #2 "Review code" exists
Input: "Delete task 2"
Expected Tool Call: delete_task(task_id=2)
Expected Response Pattern: "I've deleted task #2 'Review code'"
Validation:
  - Task removed from database
  - Response confirms deletion
```

#### Test 5.2: Delete by Name
```yaml
Setup: Task "Pay bills" exists
Input: "Remove the 'Pay bills' task"
Expected Tool Call:
  1. list_tasks()
  2. delete_task(task_id=X)
Expected Response Pattern: "I've removed 'Pay bills'"
Validation:
  - Task found by name
  - Deletion executed
```

#### Test 5.3: Delete with Confirmation
```yaml
Setup: Task "Important project" exists
Input: "Delete the 'Important project' task"
Expected Tool Call:
  1. list_tasks()
  2. (Possibly ask user confirmation)
  3. delete_task(task_id=X)
Expected Response Pattern: Confirms deletion or asks for confirmation
Validation:
  - High-stakes actions may prompt confirmation
  - Deletion only after confirmation
```

#### Test 5.4: Delete Nonexistent Task
```yaml
Setup: Task #99 doesn't exist
Input: "Delete task 99"
Expected Tool Call: delete_task(task_id=99)
Expected Response Pattern: "Task #99 doesn't exist" or error message
Validation:
  - Tool returns error
  - Error handled gracefully
  - User informed clearly
```

---

### 5.6 Multi-Step Command Scenarios

#### Test 6.1: Add and List
```yaml
Setup: Empty task list
Input: "Add a task to buy groceries and show me all my tasks"
Expected Tool Calls:
  1. add_task(title="Buy groceries")
  2. list_tasks()
Expected Response Pattern: "I've added 'Buy groceries'. Here are all your tasks: 1. Buy groceries"
Validation:
  - Both operations executed in sequence
  - Response combines both actions
```

#### Test 6.2: List and Complete
```yaml
Setup: 3 pending tasks
Input: "Show my tasks and mark the first one as done"
Expected Tool Calls:
  1. list_tasks()
  2. complete_task(task_id=<first_task_id>)
Expected Response Pattern: Lists tasks, then confirms completion
Validation:
  - First task identified from list result
  - Completion applied correctly
```

#### Test 6.3: Add Multiple and Complete One
```yaml
Setup: Empty list
Input: "Add tasks to buy milk and walk dog, then mark 'buy milk' as complete"
Expected Tool Calls:
  1. add_task(title="Buy milk")
  2. add_task(title="Walk dog")
  3. list_tasks() (to find "buy milk")
  4. complete_task(task_id=X)
Expected Response Pattern: Confirms both additions and completion
Validation:
  - 3 distinct operations
  - Tool chaining works correctly
  - Final state matches intent
```

#### Test 6.4: Complex Workflow
```yaml
Setup: 5 tasks exist (3 pending, 2 completed)
Input: "Show me pending tasks, complete the one about groceries, then delete all completed tasks"
Expected Tool Calls:
  1. list_tasks(status="pending")
  2. complete_task(task_id=<groceries_task_id>)
  3. list_tasks(status="completed")
  4. delete_task(task_id=...) for each completed
Expected Response Pattern: Step-by-step confirmation of each action
Validation:
  - Multi-step logic executed correctly
  - Task identification by description
  - Batch operations (delete multiple)
```

#### Test 6.5: Conditional Logic
```yaml
Setup: Unknown task state
Input: "If I have any overdue tasks, show them to me"
Expected Tool Calls: list_tasks(due_date_before=today)
Expected Response Pattern: Either lists overdue tasks or says "No overdue tasks"
Validation:
  - Conditional intent recognized
  - Appropriate response for both cases
```

---

### 5.7 Edge Cases and Error Scenarios

#### Test 7.1: Ambiguous Input
```yaml
Input: "Do the thing"
Expected Behavior: Agent asks for clarification
Expected Response Pattern: "I'm not sure what you'd like me to do. Could you specify?"
Validation:
  - No tool called
  - Clarification request sent
```

#### Test 7.2: Typos and Misspellings
```yaml
Input: "Addd a taks to by grocceries"
Expected Tool Call: add_task(title="Buy groceries")
Expected Response Pattern: Task added despite typos
Validation:
  - Intent recognized despite errors
  - Task title corrected or preserved as-is
```

#### Test 7.3: Very Long Input
```yaml
Input: 500-word paragraph describing a complex project
Expected Tool Call: add_task(title="[extracted]", description="[full text]")
Expected Response Pattern: Confirms task with summary
Validation:
  - Long input handled without truncation
  - Key information extracted
```

#### Test 7.4: Special Characters
```yaml
Input: "Add task: Review PR #42 & merge it (ASAP!)"
Expected Tool Call: add_task(title="Review PR #42 & merge it (ASAP!)")
Expected Response Pattern: Confirms with exact title
Validation:
  - Special characters preserved
  - No encoding issues
```

#### Test 7.5: Out-of-Scope Request
```yaml
Input: "What's the weather today?"
Expected Behavior: Polite refusal
Expected Response Pattern: "I can only help with task management"
Validation:
  - No tool called
  - Scope boundaries enforced
  - User redirected to valid operations
```

---

## 6. Scope & Boundaries

### In Scope
- Testing all 5 MCP tool operations via natural language
- Multi-step command validation
- Natural language variation testing
- Error handling and edge cases
- Tool chaining correctness
- Response quality assessment

### Out of Scope
- Performance/load testing (use separate stress tests)
- Security penetration testing (use security audit tests)
- UI/UX evaluation (focus is on agent behavior)
- Database migration testing
- Infrastructure testing

---

## 7. Reusability

This skill is reusable for:
- Regression testing after agent prompt updates
- Validation before production deployment
- Demo preparation for hackathon judges
- User acceptance testing (UAT)
- Continuous integration test suites
- Training data collection for agent improvements

---

## 8. Dependencies

### Phase 3 Artifacts
- MCP tools implementation (`backend/app/mcp/tools.py`)
- Agent system prompt (`backend/app/agent/system_prompt.py`)
- Intent classifier (`backend/app/agent/intent_classifier.py`)
- AgentRunner (`backend/app/agent/runner.py`)
- Chat endpoint (`backend/app/routes/chat.py`)

### Testing Infrastructure
- Pytest framework
- Database fixtures for test isolation
- Mock OpenAI API for deterministic testing
- Test user with authentication token

---

## 9. Quality Expectations

### Test Coverage
- ✅ All 5 CRUD operations covered
- ✅ At least 5 variations per operation
- ✅ Multi-step scenarios (minimum 5)
- ✅ Edge cases and errors (minimum 5)
- ✅ Total minimum: 30 test cases

### Pass Criteria
- **Critical Tests (Must Pass)**: All basic CRUD operations (Tests 1.1-5.1)
- **High Priority**: Natural language variations (Tests 1.2-5.5)
- **Medium Priority**: Multi-step commands (Tests 6.1-6.5)
- **Low Priority**: Edge cases can have known issues documented

### Documentation
- Each test must document: input, expected behavior, actual behavior
- Failed tests require root cause analysis
- Tool calls must be logged for debugging

---

## 10. Implementation Checklist

### Preparation
- [ ] Set up test environment (backend + frontend running)
- [ ] Create test user and obtain auth token
- [ ] Seed database with known test data
- [ ] Configure logging for tool calls and responses

### Test Execution
- [ ] Run all Basic CRUD tests (5.1-5.5)
- [ ] Run Multi-Step Command tests (5.6)
- [ ] Run Edge Case tests (5.7)
- [ ] Document all results in standardized format

### Validation
- [ ] Verify tool calls match expected patterns
- [ ] Check database state after each test
- [ ] Validate response quality (natural, accurate, helpful)
- [ ] Confirm no hallucinations (actions without tool calls)

### Reporting
- [ ] Generate test summary report
- [ ] Document all failures with screenshots/logs
- [ ] Create GitHub issues for bugs found
- [ ] Update test suite with new scenarios discovered

### Follow-Up
- [ ] Rerun failed tests after fixes
- [ ] Add regression tests for fixed bugs
- [ ] Update agent prompt if intent classification fails
- [ ] Document known limitations for user-facing docs

---

## 11. Automated Test Suite

### pytest Implementation

```python
# backend/tests/test_natural_language.py

import pytest
from uuid import uuid4
from app.agent.runner import AgentRunner
from app.models.user import User
from app.models.todo import Todo
from app.database import Session, engine

@pytest.fixture
def test_user(session):
    """Create test user."""
    user = User(
        id=uuid4(),
        email="test@example.com",
        username="testuser"
    )
    session.add(user)
    session.commit()
    return user

@pytest.fixture
def clean_tasks(session, test_user):
    """Ensure clean task state."""
    session.query(Todo).filter_by(user_id=test_user.id).delete()
    session.commit()
    yield
    session.query(Todo).filter_by(user_id=test_user.id).delete()
    session.commit()

@pytest.fixture
def agent_runner():
    """Initialize AgentRunner."""
    return AgentRunner()

class TestBasicCRUD:
    """Test basic CRUD operations via natural language."""

    def test_add_task_direct(self, agent_runner, test_user, clean_tasks):
        """Test 1.1: Direct add command."""
        response = agent_runner.run(
            user_id=test_user.id,
            user_message="Add a task to buy groceries"
        )

        # Verify tool call
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].name == "add_task"
        assert "buy groceries" in response.tool_calls[0].parameters["title"].lower()

        # Verify response
        assert "added" in response.message.lower()
        assert "groceries" in response.message.lower()

        # Verify database
        with Session(engine) as session:
            tasks = session.query(Todo).filter_by(user_id=test_user.id).all()
            assert len(tasks) == 1
            assert "groceries" in tasks[0].title.lower()

    def test_add_task_natural_language(self, agent_runner, test_user, clean_tasks):
        """Test 1.2: Natural language variation."""
        response = agent_runner.run(
            user_id=test_user.id,
            user_message="Remind me to call mom"
        )

        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].name == "add_task"
        assert "call mom" in response.tool_calls[0].parameters["title"].lower()

    def test_list_tasks_all(self, agent_runner, test_user, session):
        """Test 2.1: List all tasks."""
        # Seed tasks
        for title in ["Task A", "Task B", "Task C"]:
            task = Todo(user_id=test_user.id, title=title)
            session.add(task)
        session.commit()

        response = agent_runner.run(
            user_id=test_user.id,
            user_message="Show me all my tasks"
        )

        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].name == "list_tasks"

        # Response should mention all 3 tasks
        assert "Task A" in response.message or "task a" in response.message.lower()
        assert "Task B" in response.message or "task b" in response.message.lower()
        assert "Task C" in response.message or "task c" in response.message.lower()

    def test_complete_task_by_id(self, agent_runner, test_user, session):
        """Test 4.1: Complete by ID."""
        # Seed task
        task = Todo(user_id=test_user.id, title="Buy groceries", status="pending")
        session.add(task)
        session.commit()
        task_id = task.id

        response = agent_runner.run(
            user_id=test_user.id,
            user_message=f"Mark task {task_id} as complete"
        )

        assert any(tc.name == "complete_task" for tc in response.tool_calls)

        # Verify database
        session.refresh(task)
        assert task.status == "completed"

    def test_delete_task_by_id(self, agent_runner, test_user, session):
        """Test 5.1: Delete by ID."""
        task = Todo(user_id=test_user.id, title="Review code")
        session.add(task)
        session.commit()
        task_id = task.id

        response = agent_runner.run(
            user_id=test_user.id,
            user_message=f"Delete task {task_id}"
        )

        assert any(tc.name == "delete_task" for tc in response.tool_calls)

        # Verify deletion
        deleted_task = session.query(Todo).filter_by(id=task_id).first()
        assert deleted_task is None

class TestMultiStepCommands:
    """Test multi-step command handling."""

    def test_add_and_list(self, agent_runner, test_user, clean_tasks):
        """Test 6.1: Add then list."""
        response = agent_runner.run(
            user_id=test_user.id,
            user_message="Add a task to buy groceries and show me all my tasks"
        )

        # Should have both tool calls
        tool_names = [tc.name for tc in response.tool_calls]
        assert "add_task" in tool_names
        assert "list_tasks" in tool_names

        # Response should mention both actions
        assert "added" in response.message.lower() or "created" in response.message.lower()
        assert "groceries" in response.message.lower()

    def test_list_and_complete(self, agent_runner, test_user, session):
        """Test 6.2: List then complete first."""
        # Seed tasks
        for i, title in enumerate(["Task A", "Task B", "Task C"], 1):
            task = Todo(user_id=test_user.id, title=title, status="pending")
            session.add(task)
        session.commit()

        response = agent_runner.run(
            user_id=test_user.id,
            user_message="Show my tasks and mark the first one as done"
        )

        tool_names = [tc.name for tc in response.tool_calls]
        assert "list_tasks" in tool_names
        assert "complete_task" in tool_names

        # First task should be completed
        first_task = session.query(Todo).filter_by(user_id=test_user.id).order_by(Todo.created_at).first()
        assert first_task.status == "completed"

class TestEdgeCases:
    """Test error handling and edge cases."""

    def test_empty_list(self, agent_runner, test_user, clean_tasks):
        """Test 2.4: Empty task list."""
        response = agent_runner.run(
            user_id=test_user.id,
            user_message="List my tasks"
        )

        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].name == "list_tasks"

        # Should handle empty gracefully
        assert "don't have" in response.message.lower() or "no tasks" in response.message.lower()

    def test_nonexistent_task(self, agent_runner, test_user, clean_tasks):
        """Test 3.4: Update nonexistent task."""
        response = agent_runner.run(
            user_id=test_user.id,
            user_message="Update task 99999 to be high priority"
        )

        # Should attempt update
        assert any(tc.name == "update_task" for tc in response.tool_calls)

        # Should communicate error
        assert "doesn't exist" in response.message.lower() or "not found" in response.message.lower()

    def test_ambiguous_input(self, agent_runner, test_user, clean_tasks):
        """Test 7.1: Ambiguous request."""
        response = agent_runner.run(
            user_id=test_user.id,
            user_message="Do the thing"
        )

        # Should not call tools without clarity
        # OR should ask for clarification
        if len(response.tool_calls) == 0:
            assert "not sure" in response.message.lower() or "clarify" in response.message.lower()

class TestNaturalLanguageVariations:
    """Test various phrasings map to correct operations."""

    @pytest.mark.parametrize("user_input", [
        "What's on my todo list?",
        "Show my tasks",
        "What do I need to do today?",
        "Display all todos"
    ])
    def test_list_variations(self, agent_runner, test_user, clean_tasks, user_input):
        """Test 2.5: List task variations."""
        response = agent_runner.run(
            user_id=test_user.id,
            user_message=user_input
        )

        assert len(response.tool_calls) >= 1
        assert response.tool_calls[0].name == "list_tasks"
```

### Running Tests

```bash
# Run all natural language tests
pytest backend/tests/test_natural_language.py -v

# Run specific test class
pytest backend/tests/test_natural_language.py::TestBasicCRUD -v

# Run with coverage
pytest backend/tests/test_natural_language.py --cov=app.agent --cov-report=html

# Run in verbose mode with output
pytest backend/tests/test_natural_language.py -v -s
```

---

## 12. Manual Testing Protocol

### ChatKit UI Testing

1. **Setup**:
   - Open ChatKit UI at `http://localhost:3000/chat`
   - Ensure authenticated as test user
   - Open browser DevTools to inspect network requests

2. **Execute Test Cases**:
   - Input each test scenario from Section 5
   - Observe agent response in UI
   - Check browser network tab for tool calls
   - Verify database state with admin query

3. **Document Results**:
   - Screenshot any unexpected behavior
   - Copy tool call JSON from network inspector
   - Note response time for each operation
   - Record user experience observations

### Direct API Testing (Postman/curl)

```bash
# Test add task
curl -X POST http://localhost:8000/api/$USER_ID/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries",
    "conversation_id": null
  }'

# Inspect response JSON
# Expected: { "message": "...", "tool_calls": [...], "conversation_id": "..." }
```

---

## 13. Example Test Results Report

```markdown
# Phase 3 Natural Language Test Results

**Test Date**: 2026-01-20 15:30 UTC
**Tester**: phase3-qa-demo agent
**Environment**: Local development (backend v1.0.0, frontend v1.0.0)
**Test Duration**: 45 minutes
**Agent Model**: gpt-4-turbo

## Summary

| Category | Total | Passed | Failed | Skipped |
|----------|-------|--------|--------|---------|
| Basic CRUD | 15 | 14 | 1 | 0 |
| Multi-Step | 10 | 9 | 1 | 0 |
| Edge Cases | 10 | 8 | 2 | 0 |
| NL Variations | 10 | 10 | 0 | 0 |
| **TOTAL** | **45** | **41** | **4** | **0** |

**Pass Rate**: 91.1%

## Failed Tests

### FAIL: Test 1.2 - Add with Details
- **Input**: "Create a task called 'Finish report' due tomorrow with high priority"
- **Expected**: Task with priority field set
- **Actual**: Task created but priority ignored
- **Root Cause**: Todo model doesn't have priority field yet
- **Resolution**: Add priority field in Phase 3.1 enhancement OR document as known limitation
- **Severity**: Low (feature not in MVP scope)

### FAIL: Test 6.3 - Add Multiple and Complete One
- **Input**: "Add tasks to buy milk and walk dog, then mark 'buy milk' as complete"
- **Expected**: 2 adds + 1 complete
- **Actual**: Only first task added, second task ignored
- **Root Cause**: Agent stopped after first tool call, didn't continue parsing
- **Resolution**: Fix intent classifier to detect multiple commands
- **Severity**: High (multi-step commands are core feature)

### FAIL: Test 7.2 - Typos and Misspellings
- **Input**: "Addd a taks to by grocceries"
- **Expected**: Task created despite typos
- **Actual**: No tool called, agent asked for clarification
- **Root Cause**: LLM too strict on parsing malformed input
- **Resolution**: Update system prompt to be more tolerant of typos
- **Severity**: Medium (UX impact)

### FAIL: Test 3.4 - Update Nonexistent Task
- **Input**: "Update task 99999 to be high priority"
- **Expected**: Error message "Task doesn't exist"
- **Actual**: Internal server error 500
- **Root Cause**: update_task tool doesn't validate task existence before attempting update
- **Resolution**: Add validation in MCP tool implementation
- **Severity**: Medium (error handling)

## Recommendations

1. **Immediate Fixes** (before demo):
   - Fix multi-step command parsing (Test 6.3)
   - Add task existence validation in update_task (Test 3.4)

2. **Short-Term Improvements**:
   - Improve typo tolerance in agent prompt (Test 7.2)
   - Add priority field to Todo model (Test 1.2) OR remove from test suite

3. **Long-Term Enhancements**:
   - Add confidence scoring for ambiguous inputs
   - Implement conversational memory for follow-up commands
   - Add support for bulk operations ("delete all completed tasks")

## Test Logs

Full test logs available at: `backend/tests/logs/natural_language_test_2026-01-20.log`
Database snapshot: `backend/tests/fixtures/db_snapshot_20260120.sql`
```

---

## 14. Demo Scenarios

### Recommended Demo Flow for Judges

**Scenario 1: Quick Task Management** (2 minutes)
```
User: "Add a task to prepare hackathon presentation"
Agent: ✅ Adds task

User: "Add another one: practice demo"
Agent: ✅ Adds second task

User: "Show me what I need to do"
Agent: ✅ Lists both tasks

User: "I finished the presentation, mark it as done"
Agent: ✅ Completes task by name match
```

**Scenario 2: Natural Language Power** (2 minutes)
```
User: "Remind me to email the judges tomorrow"
Agent: ✅ Creates task with due date

User: "What's on my plate today?"
Agent: ✅ Lists tasks (demonstrates NL variation)

User: "Actually, change that email task to 'email judges and sponsors'"
Agent: ✅ Updates task title

User: "Done with that"
Agent: ✅ Completes task (demonstrates context awareness)
```

**Scenario 3: Multi-Step Intelligence** (2 minutes)
```
User: "Add three tasks: review code, write tests, deploy to production"
Agent: ✅ Creates all three tasks

User: "Show pending tasks and complete the one about tests"
Agent: ✅ Lists tasks, then completes matching task

User: "Delete all completed tasks"
Agent: ✅ Removes completed tasks (demonstrates batch operation)
```

---

## 15. Success Metrics

### Quantitative Metrics
- **Pass Rate**: ≥90% of tests passing
- **Tool Call Accuracy**: ≥95% correct tool selection
- **Response Time**: <2s average for single-step commands
- **Error Rate**: <5% of requests return errors

### Qualitative Metrics
- **Natural Language Understanding**: Users can phrase requests in various ways
- **Response Quality**: Responses are conversational, accurate, and helpful
- **Error Handling**: Failures produce clear, actionable error messages
- **Multi-Step Coherence**: Complex commands execute logically in sequence

---

**Maintained by**: Todo-app Hackathon Team
**Last Updated**: 2026-01-20
