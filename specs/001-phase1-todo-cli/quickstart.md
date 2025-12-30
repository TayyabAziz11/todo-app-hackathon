# Quickstart Guide: Phase 1 - In-Memory Todo CLI

**Feature**: 001-phase1-todo-cli
**Created**: 2025-12-29
**Purpose**: Quick reference for developers implementing Phase 1

---

## 5-Minute Overview

**What**: In-memory command-line Todo application
**Tech**: Python 3.13+, argparse, no external dependencies
**Storage**: In-memory dictionary (data lost on exit)
**Commands**: add, list, delete, help

---

## Project Structure

```
Todo-app/
├── todo.py               # Main entry point
├── todo_manager.py       # Business logic and storage
├── cli.py                # CLI interface and argument parsing
├── tests/
│   ├── test_todo_manager.py      # Unit tests for business logic
│   ├── test_cli_integration.py   # CLI integration tests
│   └── test_edge_cases.py        # Edge case and performance tests
├── README.md             # User documentation
└── requirements-dev.txt  # Development dependencies (pytest, etc.)
```

---

## Quick Commands

```bash
# Add a todo
python todo.py add "Buy groceries"
python todo.py add "Call dentist" --description "Annual checkup"

# List all todos
python todo.py list

# Delete a todo
python todo.py delete 1

# Get help
python todo.py --help
python todo.py add --help
```

---

## Implementation Checklist

### Phase 0: Setup ✅
- [x] Research technical decisions (research.md)
- [x] Define data model (data-model.md)
- [x] Design CLI interface (contracts/cli-interface.md)

### Phase 1: Core Implementation
- [ ] Create `todo_manager.py` with in-memory storage
  - [ ] TodoManager class
  - [ ] add_todo(title, description) method
  - [ ] list_todos() method
  - [ ] delete_todo(id) method
  - [ ] Input validation and trimming

- [ ] Create `cli.py` with argparse
  - [ ] Argument parser configuration
  - [ ] Subcommands: add, list, delete, help
  - [ ] Error handling (stdout/stderr)
  - [ ] Exit codes (0, 1, 2)

- [ ] Create `todo.py` main entry point
  - [ ] Wire CLI to TodoManager
  - [ ] Handle exceptions
  - [ ] Main execution block

### Phase 2: Testing
- [ ] Unit tests for TodoManager (>90% coverage)
  - [ ] Test add with valid/invalid input
  - [ ] Test list empty/populated
  - [ ] Test delete existing/non-existent
  - [ ] Test ID sequencing and no-reuse
  - [ ] Test whitespace trimming

- [ ] CLI integration tests
  - [ ] Test all commands via subprocess
  - [ ] Test exit codes
  - [ ] Test stdout/stderr output
  - [ ] Test edge cases (Unicode, special chars)

- [ ] Performance tests
  - [ ] 1000 todos < 1 second (add, list, delete)

### Phase 3: Documentation
- [ ] README.md with setup instructions
- [ ] CLAUDE.md with agent workflow
- [ ] Help text in CLI
- [ ] Code documentation (docstrings)

### Phase 4: Quality Assurance
- [ ] Code review against constitution
- [ ] All tests passing
- [ ] No blocking bugs
- [ ] Phase isolation verified

---

## Module Interfaces

### TodoManager (todo_manager.py)

```python
class TodoManager:
    """Manages in-memory todo storage and operations."""

    def __init__(self):
        """Initialize with empty storage and ID counter at 1."""
        pass

    def add_todo(self, title: str, description: str | None = None) -> int:
        """
        Add a new todo.

        Args:
            title: Todo title (required, 1-200 chars after trim)
            description: Todo description (optional, trimmed)

        Returns:
            Assigned todo ID

        Raises:
            ValueError: If title is empty or > 200 characters
        """
        pass

    def list_todos(self) -> list[dict]:
        """
        List all todos sorted by ID.

        Returns:
            List of todo dictionaries with id, title, description
        """
        pass

    def delete_todo(self, todo_id: int) -> None:
        """
        Delete a todo by ID.

        Args:
            todo_id: ID of todo to delete

        Raises:
            ValueError: If todo_id not found
        """
        pass
```

### CLI (cli.py)

```python
def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    pass

def handle_add(args, manager: TodoManager) -> int:
    """Handle add command. Returns exit code."""
    pass

def handle_list(args, manager: TodoManager) -> int:
    """Handle list command. Returns exit code."""
    pass

def handle_delete(args, manager: TodoManager) -> int:
    """Handle delete command. Returns exit code."""
    pass
```

### Main (todo.py)

```python
def main() -> int:
    """Main entry point. Returns exit code."""
    pass

if __name__ == '__main__':
    sys.exit(main())
```

---

## Key Implementation Rules

### 1. Validation
- **Where**: CLI layer validates format, TodoManager validates business rules
- **Title**: Required, non-empty after trim, ≤ 200 chars
- **Description**: Optional, trimmed if provided
- **ID**: Integer, must exist for delete

### 2. Error Handling
- **User errors** → stderr, exit code 1
- **System errors** → stderr, exit code 2
- **Success** → stdout, exit code 0

### 3. Output Format
```
# Success messages to stdout
Todo added with ID: {id}
Todo {id} deleted

# Error messages to stderr (start with "Error:")
Error: Title cannot be empty
Error: Todo with ID {id} not found
```

### 4. Data Storage
```python
# In-memory structure
self._todos = {}  # Dict[int, Dict[str, Any]]
self._next_id = 1  # Always increments

# Example
{
    1: {"id": 1, "title": "Buy milk", "description": None},
    2: {"id": 2, "title": "Call mom", "description": "Ask about dinner"}
}
```

---

## Testing Quick Reference

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_todo_manager.py -v

# Run specific test
pytest tests/test_todo_manager.py::TestAddTodo::test_add_valid_todo -v

# Run integration tests only
pytest tests/test_cli_integration.py -v
```

---

## Common Pitfalls to Avoid

1. ❌ **Don't** implement persistence (Phase 2)
2. ❌ **Don't** add edit/update functionality (Phase 3)
3. ❌ **Don't** add status tracking (Phase 3)
4. ❌ **Don't** use external libraries beyond stdlib
5. ❌ **Don't** reuse deleted IDs
6. ✅ **Do** trim whitespace from title/description
7. ✅ **Do** validate title length ≤ 200 chars
8. ✅ **Do** handle Unicode characters correctly
9. ✅ **Do** use proper exit codes
10. ✅ **Do** write tests for all functionality

---

## Skills to Apply

From `.claude/skills/skills_library.md`:

1. **python-cli-pattern-implementation**: CLI design and argparse usage
2. **modular-architecture-implementation**: TodoManager/CLI separation
3. **error-handling-implementation**: Validation and error messages
4. **unit-test-generation**: Comprehensive test coverage
5. **cli-input-output-validation**: Integration testing

---

## Agent Responsibilities

- **Todo App Phase 1 Delivery Agent**: Coordinate overall implementation
- **Python CLI Expert Agent**: Design CLI interface, review CLI code
- **Automated Test & QA Agent**: Generate tests, validate coverage
- **Documentation & Narrative Agent**: README, CLAUDE.md, help text
- **Hackathon Review Agent**: Final review against spec and constitution

---

## Success Criteria Checklist

- [ ] SC-001: Add operation < 2 seconds ✅ (trivially met)
- [ ] SC-002: List 1000 todos < 1 second ✅ (tested)
- [ ] SC-003: Delete operation < 2 seconds ✅ (trivially met)
- [ ] SC-004: 1000 todos no degradation ✅ (tested)
- [ ] SC-005: 100% valid operations succeed ✅ (tested)
- [ ] SC-006: Clear error messages ✅ (validated)
- [ ] SC-007: Understand commands in 2 min ✅ (help text)
- [ ] SC-008: No hanging/crashing ✅ (tested)

---

## Next Steps

1. **Review** research.md, data-model.md, contracts/cli-interface.md
2. **Run** `/sp.tasks` to generate task breakdown
3. **Implement** following task order (dependencies resolved)
4. **Test** after each module completion
5. **Review** against spec and constitution
6. **Document** in README and CLAUDE.md
7. **Validate** all acceptance criteria pass

---

## Quick Reference Links

- **Specification**: `specs/001-phase1-todo-cli/spec.md`
- **Research**: `specs/001-phase1-todo-cli/research.md`
- **Data Model**: `specs/001-phase1-todo-cli/data-model.md`
- **CLI Contract**: `specs/001-phase1-todo-cli/contracts/cli-interface.md`
- **Constitution**: `.specify/memory/constitution.md`
- **Skills Library**: `.claude/skills/skills_library.md`

---

## Estimated Timeline

- **Setup**: Already complete ✅
- **Core Implementation**: 2-3 hours
- **Testing**: 1-2 hours
- **Documentation**: 1 hour
- **Review & Polish**: 1 hour

**Total**: ~5-7 hours for complete Phase 1

---

**Ready to implement!** 🚀
