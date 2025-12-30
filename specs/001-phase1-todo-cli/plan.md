# Implementation Plan: Phase 1 - In-Memory Todo CLI

**Branch**: `001-phase1-todo-cli` | **Date**: 2025-12-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phase1-todo-cli/spec.md`

## Summary

Build a command-line Todo application in Python 3.13+ with in-memory CRUD operations. Users can add todos with titles and optional descriptions, list all todos, and delete todos by ID. Phase 1 focuses on core functionality with no persistence (data lost on exit). Implementation uses Python standard library only (argparse for CLI, dict for storage) with >90% test coverage.

**Primary Requirement**: Provide a functional CLI todo manager that demonstrates Spec-Driven Development methodology and serves as foundation for future phases (persistence in Phase 2, editing in Phase 3, etc.).

**Technical Approach**: Three-module architecture (TodoManager for business logic, CLI for interface, main entry point) with clear separation of concerns, comprehensive testing, and forward compatibility for Phase 2+ enhancements.

---

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: Python standard library only (argparse, sys, typing)
**Storage**: In-memory dictionary (Dict[int, Dict[str, Any]])
**Testing**: pytest with >90% code coverage requirement
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows with Python 3.13+)
**Project Type**: Single project (CLI application)
**Performance Goals**: Add/delete < 2s, list 1000 todos < 1s, no degradation with 1000 todos
**Constraints**: No external dependencies, no persistence, single-user/single-process, CLI only
**Scale/Scope**: Support up to 10,000 todos in memory (~2.5MB), 3 core commands (add/list/delete), 4 user stories

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Principle I: Spec-First Development (NON-NEGOTIABLE)
- **Status**: PASS
- **Evidence**: Complete specification approved (spec.md) before planning began
- **Verification**: Spec includes technology-agnostic requirements, Given-When-Then acceptance criteria

### ✅ Principle II: Phase Isolation with Forward Compatibility
- **Status**: PASS
- **Evidence**: Phase 1 independently runnable, no Phase 2+ dependencies
- **Design**: In-memory dictionary structure easily serializes to JSON for Phase 2 persistence
- **Verification**: No file I/O, database, or persistence code in Phase 1 plan

### ✅ Principle III: Agentic Workflow Discipline
- **Status**: PASS
- **Evidence**: Following spec → plan → tasks → implement workflow
- **Artifacts**: spec.md (approved), plan.md (this document), tasks.md (next step)

### ✅ Principle IV: Human-in-the-Loop Governance
- **Status**: PASS
- **Evidence**: Human approval required for spec, plan, and phase transitions
- **Process**: PHR created for specification phase, will create PHR for planning phase

### ✅ Principle V: Clean Architecture and Modularity
- **Status**: PASS
- **Design**: Three-module architecture with clear separation:
  - `todo_manager.py`: Business logic and storage (single responsibility)
  - `cli.py`: CLI interface and argument parsing (single responsibility)
  - `todo.py`: Main entry point (wiring only)
- **Dependencies**: One-directional flow (main → cli → todo_manager)
- **Verification**: No circular dependencies, each module testable independently

### ✅ Principle VI: Deterministic and Observable Behavior
- **Status**: PASS
- **Design**: 
  - Pure functions where possible (list_todos returns data, doesn't print)
  - Side effects isolated (print statements in CLI layer only)
  - Clear stdout/stderr separation
  - Explicit exit codes (0=success, 1=user error, 2=system error)
- **Verification**: All operations deterministic (same input → same output)

### ✅ Principle VII: Simplicity and YAGNI
- **Status**: PASS
- **Evidence**: Simplest viable solution for Phase 1
- **Avoided**: 
  - No persistence framework (not needed for Phase 1)
  - No ORM or complex data structures (dict sufficient)
  - No external CLI libraries (argparse is stdlib)
  - No premature optimization
- **Implemented**: Only features in approved spec (FR-001 through FR-020)

**Overall Constitution Compliance**: ✅ PASS - All principles satisfied, no violations to justify

---

## Project Structure

### Documentation (this feature)

```text
specs/001-phase1-todo-cli/
├── spec.md              # Feature specification (approved)
├── plan.md              # This file (implementation plan)
├── research.md          # Technical research and decisions
├── data-model.md        # Data structures and validation rules
├── quickstart.md        # Developer quick reference
├── contracts/           # API/interface contracts
│   └── cli-interface.md # CLI command specifications
├── checklists/          # Quality checklists
│   └── requirements.md  # Spec quality validation (completed)
└── tasks.md             # (Next: /sp.tasks command output)
```

### Source Code (repository root)

```text
Todo-app/
├── todo.py                    # Main entry point
├── todo_manager.py            # Business logic and in-memory storage
├── cli.py                     # CLI interface and argument parsing
├── tests/
│   ├── __init__.py
│   ├── test_todo_manager.py   # Unit tests for TodoManager
│   ├── test_cli_integration.py # CLI integration tests (subprocess)
│   └── test_edge_cases.py     # Edge cases and performance tests
├── README.md                  # User documentation
├── CLAUDE.md                  # AI agent workflow documentation
├── requirements-dev.txt       # Development dependencies (pytest, pytest-cov)
├── .gitignore                 # Python gitignore
└── specs/                     # Specification artifacts (see above)
```

**Structure Decision**: Single project structure selected because this is a standalone CLI application. No backend/frontend split needed, no mobile components. Simple, flat structure with clear module separation aligns with Simplicity principle (VII).

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations - table not applicable**

All constitutional principles satisfied without exceptions.

---

## Module Architecture

### 1. TodoManager Module (`todo_manager.py`)

**Responsibility**: Business logic and in-memory storage

**Public Interface**:
```python
class TodoManager:
    def __init__(self) -> None:
        """Initialize with empty storage and ID counter at 1."""

    def add_todo(self, title: str, description: str | None = None) -> int:
        """Add new todo. Returns assigned ID. Raises ValueError if validation fails."""

    def list_todos(self) -> list[dict[str, Any]]:
        """Return all todos sorted by ID."""

    def delete_todo(self, todo_id: int) -> None:
        """Delete todo by ID. Raises ValueError if ID not found."""
```

**Internal State**:
- `_todos: Dict[int, Dict[str, Any]]` - In-memory storage
- `_next_id: int` - Sequential ID counter (starts at 1, never decrements)

**Validation Rules**:
- Title: Required, non-empty after trim, ≤ 200 characters
- Description: Optional, trimmed if provided
- ID: Must be positive integer, must exist for delete

**Skills Applied**:
- `modular-architecture-implementation`: Single responsibility, clean interfaces
- `error-handling-implementation`: Explicit validation, clear ValueError messages

---

### 2. CLI Module (`cli.py`)

**Responsibility**: Command-line interface and argument parsing

**Public Interface**:
```python
def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser with subcommands."""

def handle_add(args: argparse.Namespace, manager: TodoManager) -> int:
    """Handle add command. Returns exit code."""

def handle_list(args: argparse.Namespace, manager: TodoManager) -> int:
    """Handle list command. Returns exit code."""

def handle_delete(args: argparse.Namespace, manager: TodoManager) -> int:
    """Handle delete command. Returns exit code."""
```

**CLI Commands**:
1. `add <title> [--description <text>]` - Create new todo
2. `list` - Display all todos
3. `delete <id>` - Remove todo by ID
4. `--help` - Display usage information

**Output Conventions**:
- Success/info → stdout
- Errors → stderr
- Exit codes: 0 (success), 1 (user error), 2 (system error)

**Skills Applied**:
- `python-cli-pattern-implementation`: argparse configuration, help text, exit codes
- `cli-input-output-validation`: Input parsing, output formatting

---

### 3. Main Entry Point (`todo.py`)

**Responsibility**: Wire CLI to TodoManager and handle exceptions

**Structure**:
```python
def main() -> int:
    """Main entry point. Returns exit code."""
    # 1. Create TodoManager instance
    # 2. Create and parse CLI arguments
    # 3. Dispatch to command handlers
    # 4. Handle exceptions (ValueError → user error, Exception → system error)
    # 5. Return appropriate exit code

if __name__ == '__main__':
    sys.exit(main())
```

**Error Handling Strategy**:
- `ValueError` from TodoManager → stderr, exit 1
- `argparse` errors → stderr, exit 1 (handled by argparse)
- Unexpected exceptions → stderr, exit 2

---

## Data Model

**See**: [data-model.md](./data-model.md) for complete details

**Todo Entity**:
```python
{
    "id": int,          # Unique, sequential, > 0
    "title": str,       # Required, 1-200 chars, trimmed
    "description": str | None  # Optional, trimmed if provided
}
```

**Storage Structure**:
```python
# Dict[int, Dict[str, Any]]
{
    1: {"id": 1, "title": "Buy groceries", "description": "Milk and bread"},
    2: {"id": 2, "title": "Call mom", "description": None}
}
```

**ID Generation**: Sequential integer counter, starts at 1, never decrements (deleted IDs not reused)

---

## CLI Interface Contract

**See**: [contracts/cli-interface.md](./contracts/cli-interface.md) for complete details

### Add Command

```bash
python todo.py add "Buy groceries" --description "Milk and bread"
# Output: Todo added with ID: 1
# Exit code: 0
```

### List Command

```bash
python todo.py list
# Output:
# ID: 1
# Title: Buy groceries
# Description: Milk and bread
#
# ID: 2
# Title: Call mom
# Exit code: 0
```

### Delete Command

```bash
python todo.py delete 1
# Output: Todo 1 deleted
# Exit code: 0
```

### Error Example

```bash
python todo.py add ""
# Output (stderr): Error: Title cannot be empty
# Exit code: 1
```

---

## Testing Strategy

**Overall Target**: >90% code coverage (per acceptance criteria)

### 1. Unit Tests (`test_todo_manager.py`)

**Coverage**: TodoManager class methods

**Test Cases**:
- ✅ Add valid todo (title only)
- ✅ Add valid todo (title + description)
- ✅ Add todo rejects empty title
- ✅ Add todo rejects whitespace-only title
- ✅ Add todo rejects title > 200 characters
- ✅ Add todo trims whitespace from title/description
- ✅ Add todo assigns sequential IDs
- ✅ List todos when empty
- ✅ List todos with multiple entries (sorted by ID)
- ✅ Delete existing todo
- ✅ Delete rejects non-existent ID
- ✅ Deleted IDs not reused

**Skills Applied**: `unit-test-generation`

---

### 2. CLI Integration Tests (`test_cli_integration.py`)

**Coverage**: End-to-end CLI via subprocess

**Test Cases**:
- ✅ Add command with valid input → success message, exit 0
- ✅ Add command with empty title → error message, exit 1
- ✅ List command with todos → formatted output, exit 0
- ✅ List command when empty → "No todos found", exit 0
- ✅ Delete command with valid ID → success message, exit 0
- ✅ Delete command with invalid ID → error message, exit 1
- ✅ Help command → usage information, exit 0
- ✅ No arguments → usage hint, exit 1

**Skills Applied**: `cli-input-output-validation`

---

### 3. Edge Case & Performance Tests (`test_edge_cases.py`)

**Coverage**: Special scenarios and performance validation

**Test Cases**:
- ✅ Unicode characters in title/description (emoji, Chinese, Arabic)
- ✅ Special characters (quotes, newlines, tabs)
- ✅ Title exactly 200 characters (boundary)
- ✅ Identical titles (different IDs)
- ✅ Invalid ID format for delete (`delete abc`)
- ✅ Performance: Add 1000 todos < 1 second
- ✅ Performance: List 1000 todos < 1 second
- ✅ Performance: Delete from 1000 todos < 1 second

**Skills Applied**: `regression-detection`, performance validation

---

### Test Execution

```bash
# Run all tests with coverage
pytest tests/ -v --cov=. --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_todo_manager.py -v

# Run with detailed output
pytest tests/ -vv
```

**Coverage Target**: >90% (required by acceptance criteria)
**Expected Coverage**: ~95% (CLI and TodoManager fully covered)

---

## Agent Responsibilities

### Todo App Phase 1 Delivery Agent
**Role**: Coordinate overall Phase 1 implementation
**Tasks**:
- Orchestrate spec → plan → tasks → implement workflow
- Ensure all agents collaborate effectively
- Validate phase isolation and forward compatibility
- Coordinate final review and acceptance criteria validation

**Skills Used**: All skills from library as coordinator

---

### Python CLI Expert Agent
**Role**: Design and review CLI interface
**Tasks**:
- Design argparse configuration and command structure
- Define help text and usage documentation
- Review CLI code for UX and conventions
- Ensure proper exit codes and error messages

**Skills Used**:
- `python-cli-pattern-implementation`
- `cli-input-output-validation`

**Artifacts**:
- contracts/cli-interface.md (completed)
- cli.py (to be implemented via /sp.implement)

---

### Automated Test & QA Agent
**Role**: Generate tests and validate quality
**Tasks**:
- Generate unit tests for TodoManager
- Generate CLI integration tests
- Generate edge case and performance tests
- Validate >90% code coverage
- Run regression detection before phase completion

**Skills Used**:
- `unit-test-generation`
- `integration-test-generation`
- `cli-input-output-validation`
- `regression-detection`

**Artifacts**:
- tests/test_todo_manager.py (to be implemented)
- tests/test_cli_integration.py (to be implemented)
- tests/test_edge_cases.py (to be implemented)

---

### Documentation & Narrative Agent
**Role**: Generate user and developer documentation
**Tasks**:
- Create/update README.md with setup and usage
- Create/update CLAUDE.md with AI workflow
- Ensure help text in CLI is clear
- Document code with docstrings

**Skills Used**:
- `readme-generation`
- `judge-facing-narrative-writing`
- `phr-creation`

**Artifacts**:
- README.md (to be created)
- CLAUDE.md (to be updated)
- PHRs in history/prompts/001-phase1-todo-cli/

---

### Hackathon Review & Judge-Brain Agent
**Role**: Review against spec and constitution
**Tasks**:
- Cross-artifact consistency check (spec ↔ plan ↔ tasks ↔ code)
- Verify constitutional compliance
- Validate acceptance criteria met
- Identify risks and gaps
- Provide judge perspective feedback

**Skills Used**:
- `cross-artifact-consistency-check`
- `spec-vs-implementation-comparison`
- `risk-identification`
- `code-quality-review`

**Artifacts**:
- Quality review report (to be generated after implementation)

---

## Implementation Dependencies

### Dependency Graph

```
spec.md (approved) ✅
    ↓
plan.md (this document) ✅
    ↓
tasks.md (next: /sp.tasks)
    ↓
Implementation (/sp.implement):
    todo_manager.py → tests/test_todo_manager.py
        ↓
    cli.py → tests/test_cli_integration.py
        ↓
    todo.py (wires together)
        ↓
    tests/test_edge_cases.py
        ↓
    README.md, CLAUDE.md
        ↓
Final review and acceptance
```

### External Dependencies

**Runtime**:
- Python 3.13+ (required by FR-017)
- Python standard library (argparse, sys, typing)

**Development**:
- pytest (testing framework)
- pytest-cov (coverage reporting)

**No other dependencies** (satisfies CON-002)

---

## Risk Assessment

**See**: [research.md](./research.md) Section "Risks and Mitigations" for complete analysis

### RISK-001: Memory Limitations
- **Impact**: MEDIUM
- **Likelihood**: LOW (for Phase 1 scope)
- **Mitigation**: Document 10,000 todo limit in README; test with 1000 todos

### RISK-002: Unicode Handling
- **Impact**: MEDIUM
- **Likelihood**: LOW (Python 3.13 handles UTF-8 well)
- **Mitigation**: Comprehensive tests with Unicode characters; graceful encoding error handling

### RISK-003: CLI Parsing Edge Cases
- **Impact**: LOW
- **Likelihood**: LOW (argparse handles most cases)
- **Mitigation**: Integration tests with quotes, spaces, special characters

### RISK-004: Forward Compatibility
- **Impact**: HIGH
- **Likelihood**: LOW (design accounts for Phase 2+)
- **Mitigation**: Dictionary structure serializable to JSON; TodoManager interface swappable

---

## Phase Boundaries

### Phase 1 Scope (This Plan)

✅ **In Scope**:
- In-memory CRUD operations
- CLI with add/list/delete/help commands
- Input validation and error handling
- Sequential ID assignment
- >90% test coverage
- Documentation (README, CLAUDE.md, help text)

❌ **Out of Scope** (Deferred):
- Persistence (file, database) → Phase 2
- Edit/update todos → Phase 3
- Todo status/completion tracking → Phase 3
- Categories, tags → Phase 4
- Search, filter → Phase 4
- Due dates, reminders → Phase 5
- Multi-user support → Phase 5

### Forward Compatibility Design

**Phase 1 → Phase 2 (Persistence)**:
- Current: `Dict[int, dict]` in memory
- Phase 2: Add JSON serialization/deserialization
- Interface: TodoManager methods unchanged, add save()/load()

**Phase 1 → Phase 3 (Edit/Status)**:
- Current: Add, list, delete
- Phase 3: Add edit_todo(), update_status()
- Data model: Add "status" field to todo dict

**No breaking changes** to Phase 1 CLI or data structures anticipated

---

## Architectural Decisions

### ADR-001: Python Dictionary for In-Memory Storage

**Status**: Accepted

**Context**: Need simple, performant in-memory storage for Phase 1

**Decision**: Use Python dict with integer keys

**Alternatives Considered**:
- List with index as ID: Delete creates gaps, harder to manage
- SQLite in-memory: Over-engineering for Phase 1
- Custom class storage: Unnecessary complexity

**Consequences**:
- ✅ O(1) lookup/delete by ID
- ✅ Easy to serialize to JSON for Phase 2
- ✅ Simple to implement and test
- ❌ Not sorted by default (need to sort for list view)

**Documented in**: research.md

---

### ADR-002: argparse for CLI Parsing

**Status**: Accepted

**Context**: Need CLI argument parsing that meets CON-002 (no external deps)

**Decision**: Use Python's built-in argparse module

**Alternatives Considered**:
- click: Better API but external dependency
- typer: Modern but external dependency
- Manual sys.argv parsing: Error-prone

**Consequences**:
- ✅ Part of standard library
- ✅ Automatic help generation
- ✅ Supports subcommands
- ✅ Well-documented and mature
- ❌ More verbose than click/typer

**Documented in**: research.md

---

### ADR-003: Three-Module Architecture

**Status**: Accepted

**Context**: Need clean separation of concerns for testability and maintainability

**Decision**: Separate TodoManager (logic), CLI (interface), main (wiring)

**Alternatives Considered**:
- Single file: Simple but poor separation
- Many small files: Over-engineering for Phase 1
- Two modules (logic + CLI): Harder to test wiring logic

**Consequences**:
- ✅ Clear separation of concerns
- ✅ Each module independently testable
- ✅ Forward-compatible (can swap TodoManager in Phase 2)
- ✅ No circular dependencies
- ❌ Slightly more files than single-file approach

**Alignment**: Constitutional Principle V (Clean Architecture)

---

## Success Criteria Validation

### How Plan Satisfies Spec Requirements

| Success Criterion | Plan Implementation | Validation Method |
|-------------------|---------------------|-------------------|
| SC-001: Add < 2s | In-memory dict insert (O(1)) | Performance test |
| SC-002: List 1000 < 1s | Dict iteration + sort (O(n log n)) | Performance test |
| SC-003: Delete < 2s | Dict delete (O(1)) | Performance test |
| SC-004: 1000 todos no degradation | ~250KB memory | Performance test |
| SC-005: 100% valid ops succeed | Comprehensive unit tests | Test coverage |
| SC-006: Clear error messages | Explicit validation + error messages | Integration tests |
| SC-007: Understand in 2 min | Help text + README | Manual validation |
| SC-008: No hanging/crashing | Exception handling + tests | Integration tests |

**All success criteria addressed in plan** ✅

---

## Next Steps

### Immediate (This Session)

1. ✅ Complete Phase 0 research (research.md created)
2. ✅ Complete Phase 1 design (data-model.md, contracts/, quickstart.md created)
3. ✅ Generate implementation plan (this document)
4. ⏭️ Update agent context (next)
5. ⏭️ Create PHR for planning phase (next)

### After Plan Approval

1. **Run `/sp.tasks`**: Generate dependency-ordered task breakdown
2. **Review tasks.md**: Validate task sequence and dependencies
3. **Run `/sp.implement`**: Execute implementation following tasks
4. **Continuous testing**: Run tests after each module completion
5. **Documentation**: Update README and CLAUDE.md
6. **Final review**: Hackathon judge review and acceptance validation

---

## Artifacts Generated

### Planning Artifacts (Complete) ✅

- ✅ `research.md` - Technical decisions and rationale
- ✅ `data-model.md` - Data structures and validation rules
- ✅ `contracts/cli-interface.md` - CLI command specifications
- ✅ `quickstart.md` - Developer quick reference
- ✅ `plan.md` - This comprehensive implementation plan

### Next Artifacts (After /sp.tasks)

- ⏭️ `tasks.md` - Dependency-ordered task breakdown
- ⏭️ Implementation code (todo_manager.py, cli.py, todo.py)
- ⏭️ Test suites (test_*.py)
- ⏭️ Documentation (README.md, CLAUDE.md updates)
- ⏭️ Quality review report

---

## Conclusion

This implementation plan provides a complete, actionable blueprint for Phase 1 development:

✅ **Constitutional Compliance**: All 7 principles satisfied
✅ **Spec Alignment**: All 20 functional requirements addressed
✅ **Success Criteria**: All 8 criteria validated in design
✅ **Phase Isolation**: No Phase 2+ dependencies, independently runnable
✅ **Forward Compatibility**: Design supports Phase 2-5 evolution
✅ **Agent Coordination**: Clear responsibilities for all 5 agents
✅ **Comprehensive Testing**: >90% coverage plan with unit/integration/edge cases
✅ **Skills Integration**: All relevant skills from library applied

**Ready for `/sp.tasks` command** to generate task breakdown and proceed to implementation.
