# Skills Library

**Project**: Todo-app Hackathon
**Version**: 1.0.0
**Created**: 2025-12-29
**Location**: `.claude/skills/`
**Purpose**: Reusable skills library for AI-native Spec-Driven Development across all phases

---

## Overview

This library defines modular, reusable skills that encapsulate domain-specific expertise and technical capabilities for the Todo-app hackathon project. Each skill supports the Spec-Driven Development workflow (spec → plan → tasks → implement) and can be invoked by appropriate agents across all development phases (Phase 1–Phase 5).

**Key Principles:**
- Skills are agent-neutral but have recommended usage contexts
- Each skill has clear input/output contracts
- Skills are composable and can be chained together
- All skills respect constitutional guarantees (human-in-loop, phase isolation, spec-first)

---

## Skill Categories

1. [Specification Skills](#1-specification-skills)
2. [Planning & Task Skills](#2-planning--task-skills)
3. [Implementation Skills](#3-implementation-skills)
4. [Testing & QA Skills](#4-testing--qa-skills)
5. [Documentation Skills](#5-documentation-skills)
6. [Review & Analysis Skills](#6-review--analysis-skills)

---

## 1. Specification Skills

### 1.1 Requirement Decomposition

**Name**: `requirement-decomposition`

**Purpose**: Break down high-level user goals into atomic, testable requirements with clear boundaries and acceptance criteria.

**Applicable Agents**:
- spec-architect (primary)
- General-purpose agents during spec refinement

**Input**:
- High-level feature description or user story
- Project constitution and phase context
- Existing specifications (for validation)

**Output**:
- List of atomic requirements (numbered, independent)
- Scope boundaries (In Scope, Out of Scope, External Dependencies)
- Dependency graph between requirements
- Rationale for decomposition choices

**Scope & Boundaries**:
- **Can**: Clarify user intent, identify missing requirements, flag ambiguities
- **Cannot**: Make technology choices, create implementation plans, write code

**Reusability Notes**: Core skill used at the start of every phase. Can be reused to refine existing specs when requirements evolve.

**Dependencies**:
- Access to `.specify/memory/constitution.md`
- Phase context (Phase 1-5 awareness)
- User clarification capability (AskUserQuestion tool)

**Quality Expectations**:
- Every requirement is independently testable
- No overlapping or duplicate requirements
- Clear rationale provided for included/excluded items
- Acceptance criteria are observable and measurable

**Example Use Case**:
```
Input: "Users should be able to manage their tasks efficiently"
Output:
  Req-1: Users can add new tasks with title and optional description
  Req-2: Users can view all existing tasks in a list format
  Req-3: Users can delete tasks by identifier
  Acceptance Criteria: Given a user provides title "Buy milk", when they add a task, then the task appears in the list with a unique ID
```

---

### 1.2 Acceptance Criteria Generation

**Name**: `acceptance-criteria-generation`

**Purpose**: Generate precise, observable, testable acceptance criteria for requirements using Given-When-Then format.

**Applicable Agents**:
- spec-architect (primary)
- test-qa-validator (validation context)

**Input**:
- Requirement statement
- User stories or feature context
- Constraints and invariants

**Output**:
- Given-When-Then formatted acceptance criteria
- Edge cases and error scenarios
- Success metrics and observables
- Validation rules

**Scope & Boundaries**:
- **Can**: Define observable behavior, specify error conditions, identify edge cases
- **Cannot**: Specify implementation details, choose data structures, design APIs

**Reusability Notes**: Used during spec creation and refinement. Can be invoked independently when validating spec completeness.

**Dependencies**:
- Requirement statement (from requirement-decomposition)
- Project constraints (from constitution)

**Quality Expectations**:
- Criteria are unambiguous and verifiable
- Both happy path and error paths covered
- Criteria map 1:1 with requirements
- No implementation assumptions embedded

**Example Use Case**:
```
Requirement: Users can add new tasks
Acceptance Criteria:
  Given: User provides task title "Buy groceries"
  When: User executes add command
  Then: System confirms task added with unique ID
        AND task appears in list view
        AND task persists across sessions (Phase 2+)

  Error Case:
  Given: User provides empty title
  When: User executes add command
  Then: System returns error "Title cannot be empty"
        AND no task is created
```

---

### 1.3 Spec Validation

**Name**: `spec-validation`

**Purpose**: Validate specifications for completeness, consistency, and compliance with project constitution before handoff to planning phase.

**Applicable Agents**:
- spec-architect (self-validation)
- hackathon-judge-reviewer (evaluation context)

**Input**:
- Draft specification document
- Project constitution
- Phase boundaries and constraints

**Output**:
- Validation report (pass/fail with details)
- List of gaps, contradictions, or ambiguities
- Compliance checklist status
- Recommendations for improvement

**Scope & Boundaries**:
- **Can**: Check completeness, identify contradictions, verify phase isolation
- **Cannot**: Rewrite specs autonomously, make scoping decisions, bypass human approval

**Reusability Notes**: Run before every spec approval gate. Can be reused during spec updates or phase transitions.

**Dependencies**:
- Spec document (spec.md)
- Constitution document
- Spec-Kit Plus template

**Quality Expectations**:
- All requirements have acceptance criteria
- No unresolved placeholders or TODOs
- Phase boundaries explicitly defined
- No implementation details leaked into spec
- Traceability to user goals maintained

**Example Use Case**:
```
Input: specs/phase-1-todo-crud/spec.md
Output:
  ✅ All requirements have acceptance criteria
  ✅ Scope boundaries clearly defined
  ⚠️  Warning: "efficient" is vague in Req-4; suggest measurable criterion
  ❌ FAIL: Out of Scope section missing
  Recommendation: Add explicit "Out of Scope" section before approval
```

---

### 1.4 Phase Boundary Definition

**Name**: `phase-boundary-definition`

**Purpose**: Define clear boundaries between development phases to ensure backward compatibility and independent runnability.

**Applicable Agents**:
- spec-architect (primary)
- Plan agents (validation during planning)

**Input**:
- Current phase number (1-5)
- Previous phase specifications
- Forward compatibility requirements

**Output**:
- Phase transition criteria
- Backward compatibility guarantees
- Feature flag strategy (if needed)
- Rollback requirements
- Phase-specific constraints

**Scope & Boundaries**:
- **Can**: Define what belongs in each phase, specify transition gates, ensure isolation
- **Cannot**: Implement phase logic, create feature flags, write migration code

**Reusability Notes**: Critical for multi-phase projects. Reusable pattern across all phase transitions.

**Dependencies**:
- Constitution principle II (Phase Isolation)
- Prior phase specs
- Hackathon evaluation criteria

**Quality Expectations**:
- Each phase is independently runnable
- Later phases extend, never break earlier phases
- Transition criteria are measurable
- Rollback strategy documented

**Example Use Case**:
```
Phase 1: In-memory CRUD (no persistence)
Phase 2: Add file-based persistence
Boundary Definition:
  - Phase 2 MUST NOT break Phase 1 in-memory functionality
  - Phase 2 adds persistence as opt-in feature (flag or command)
  - Rollback: Delete persistence file, restart in Phase 1 mode
  Transition Criteria:
  - Phase 1 acceptance criteria all pass
  - Human approval obtained
  - Phase 2 spec approved
```

---

## 2. Planning & Task Skills

### 2.1 Task Decomposition

**Name**: `task-decomposition`

**Purpose**: Break down approved specifications and implementation plans into dependency-ordered, executable tasks with clear acceptance criteria.

**Applicable Agents**:
- Plan agents (primary)
- phase-1-todo-delivery agent
- General-purpose agents during `/sp.tasks`

**Input**:
- Approved specification (spec.md)
- Implementation plan (plan.md)
- Technical research and data models

**Output**:
- Dependency-ordered task list (tasks.md)
- Exact file paths for each task
- Task-level acceptance criteria
- Estimated complexity (optional)
- Grouping by user story

**Scope & Boundaries**:
- **Can**: Identify dependencies, sequence tasks, specify file locations, define task acceptance
- **Cannot**: Implement tasks, write code, skip dependency analysis

**Reusability Notes**: Core skill for every implementation phase. Reusable template for task structure.

**Dependencies**:
- Approved spec.md
- Approved plan.md
- Codebase exploration results

**Quality Expectations**:
- Tasks are atomic and independently verifiable
- Dependencies are explicit (no circular dependencies)
- File paths are exact and concrete
- Each task maps to spec requirements
- Tasks are sequenced for optimal execution

**Example Use Case**:
```
Input: Phase 1 CRUD spec + plan
Output:
  Task 1: Create TodoManager class [todo_manager.py]
    Dependencies: None
    Acceptance: Class exists with add/list/delete methods

  Task 2: Implement add_todo method [todo_manager.py:15-30]
    Dependencies: Task 1
    Acceptance: Method accepts title, returns ID, stores in memory

  Task 3: Create CLI parser [cli.py]
    Dependencies: None
    Acceptance: argparse configured for add/list/delete commands
```

---

### 2.2 Dependency Analysis

**Name**: `dependency-analysis`

**Purpose**: Identify and document dependencies between tasks, modules, and external systems to ensure correct execution order and risk mitigation.

**Applicable Agents**:
- Plan agents (during task creation)
- Review agents (during cross-artifact analysis)

**Input**:
- Task list or implementation plan
- Codebase structure
- External system integrations

**Output**:
- Dependency graph (tasks, modules, systems)
- Critical path identification
- Circular dependency warnings
- Execution sequence recommendations
- Risk assessment for dependencies

**Scope & Boundaries**:
- **Can**: Map dependencies, identify risks, suggest execution order, flag conflicts
- **Cannot**: Resolve architectural issues, implement dependency injection, write code

**Reusability Notes**: Used during planning and review phases. Reusable pattern for any multi-task workflow.

**Dependencies**:
- Task list or module structure
- Codebase exploration capability
- Understanding of external systems

**Quality Expectations**:
- All dependencies identified and documented
- No circular dependencies
- Critical path clearly marked
- External dependencies flagged with ownership
- Execution order is deterministic

**Example Use Case**:
```
Input: 10 tasks for Phase 2 persistence feature
Output:
  Dependency Graph:
    Task 1 (Data Model) → Task 3 (Serialization)
    Task 2 (File Handler) → Task 4 (Save Operation)
    Task 3 → Task 4
    Task 4 → Task 5 (Load Operation)

  Critical Path: Task 1 → Task 3 → Task 4 → Task 5

  Warnings:
    - Task 7 and Task 8 have circular dependency (needs resolution)
    - External: File system permissions (ownership: OS/deployment)
```

---

### 2.3 Phase-Safe Planning

**Name**: `phase-safe-planning`

**Purpose**: Ensure implementation plans respect phase boundaries, maintain backward compatibility, and enable independent phase execution.

**Applicable Agents**:
- Plan agents (primary)
- spec-architect (validation)

**Input**:
- Current phase specification
- Previous phase implementations
- Future phase requirements (optional, for forward compatibility)

**Output**:
- Phase-aware implementation plan
- Compatibility checks
- Feature flag strategy (if needed)
- Migration path documentation
- Rollback procedures

**Scope & Boundaries**:
- **Can**: Design phase-aware architectures, plan feature flags, ensure compatibility
- **Cannot**: Implement features, bypass phase isolation, merge phases

**Reusability Notes**: Essential for all multi-phase projects. Pattern reusable across phases 2-5.

**Dependencies**:
- Constitution principle II (Phase Isolation)
- Prior phase code and specs
- Phase transition criteria

**Quality Expectations**:
- Each phase is independently testable
- No breaking changes to prior phases
- Clear migration/rollback documentation
- Feature flags used appropriately
- Forward compatibility considered

**Example Use Case**:
```
Input: Phase 3 plan (add task editing)
Output:
  Plan:
    - Add edit_todo method to TodoManager (extends existing class)
    - Add "edit" command to CLI (new subcommand, doesn't break existing)
    - Backward compatibility: Phase 1 & 2 commands unchanged
    - Feature flag: Not needed (edit is additive)
    - Rollback: Remove edit command, delete edit_todo method

  Validation:
    ✅ Phase 1 in-memory operations still work
    ✅ Phase 2 persistence not affected
    ✅ New functionality isolated to new methods/commands
```

---

### 2.4 Architecture Decision Identification

**Name**: `architecture-decision-identification`

**Purpose**: Identify architecturally significant decisions during planning and recommend ADR documentation.

**Applicable Agents**:
- Plan agents (primary)
- spec-architect (during planning)
- General-purpose agents (when detecting significant decisions)

**Input**:
- Implementation plan
- Alternative approaches considered
- Technical tradeoffs

**Output**:
- List of architecturally significant decisions
- ADR recommendation text for each decision
- Impact assessment (scope, reversibility, long-term consequences)
- Suggested ADR title

**Scope & Boundaries**:
- **Can**: Identify significant decisions, assess impact, recommend ADRs
- **Cannot**: Create ADRs autonomously, make architectural decisions without approval

**Reusability Notes**: Used during planning phase across all features. Pattern for detecting ADR-worthy decisions.

**Dependencies**:
- Implementation plan or design discussion
- Understanding of ADR three-part test (impact, alternatives, scope)

**Quality Expectations**:
- Only significant decisions flagged (not trivial choices)
- Clear rationale for ADR recommendation
- Alternatives documented
- Never auto-creates ADRs (waits for human consent)

**Example Use Case**:
```
Input: Planning Phase 2 persistence
Decision: Use JSON file vs SQLite vs pickle
Analysis:
  - Impact: Long-term (affects all future phases)
  - Alternatives: 3+ viable options with tradeoffs
  - Scope: Cross-cutting (affects data model, testing, portability)

Output:
  📋 Architectural decision detected: Data persistence format for todo storage
     Document reasoning and tradeoffs? Run `/sp.adr data-persistence-format`

  Rationale:
    - JSON: Human-readable, portable, but limited querying
    - SQLite: Structured, queryable, but adds dependency
    - Pickle: Simple, but Python-specific, not human-readable
```

---

## 3. Implementation Skills

### 3.1 Python CLI Pattern Implementation

**Name**: `python-cli-pattern-implementation`

**Purpose**: Implement Python command-line interfaces following best practices for parsing, validation, error handling, and user experience.

**Applicable Agents**:
- python-cli-expert (primary)
- Implementation agents during coding
- General-purpose agents with CLI tasks

**Input**:
- CLI command specification
- Argument and flag definitions
- Expected user interaction flow

**Output**:
- Python CLI code (argparse, click, or typer)
- Input validation logic
- Help text and usage documentation
- Error handling for invalid input
- Exit code management

**Scope & Boundaries**:
- **Can**: Implement CLI parsing, validation, help text, error messages
- **Cannot**: Implement business logic, data persistence, core algorithms

**Reusability Notes**: Pattern reusable for all CLI commands across phases. Template for add/list/delete/edit commands.

**Dependencies**:
- Python CLI library (argparse recommended for simplicity)
- CLI specification from spec or plan
- Business logic interface (separate module)

**Quality Expectations**:
- CLI and business logic are separated
- All error paths have specific error messages
- Help text is clear and actionable
- Exit codes follow Unix conventions (0=success, 1=error)
- Input validation prevents invalid states

**Example Use Case**:
```python
# Input: Spec requires "add" command with title and optional description
# Output: CLI implementation

import argparse
import sys
from todo_manager import TodoManager

def create_parser():
    parser = argparse.ArgumentParser(description="Todo CLI")
    subparsers = parser.add_subparsers(dest='command')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new todo')
    add_parser.add_argument('title', help='Todo title')
    add_parser.add_argument('-d', '--description', help='Todo description')

    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    manager = TodoManager()

    if args.command == 'add':
        if not args.title.strip():
            print("Error: Title cannot be empty", file=sys.stderr)
            sys.exit(1)

        todo_id = manager.add_todo(args.title, args.description)
        print(f"Todo added with ID: {todo_id}")
        sys.exit(0)
```

---

### 3.2 Modular Architecture Implementation

**Name**: `modular-architecture-implementation`

**Purpose**: Implement clean, modular code with clear separation of concerns, explicit dependencies, and single responsibility.

**Applicable Agents**:
- Implementation agents (primary)
- python-cli-expert (CLI layer)
- Review agents (validation)

**Input**:
- Implementation plan with module structure
- Specification requirements
- Architectural decisions

**Output**:
- Modular Python codebase
- Clear module boundaries
- Interface definitions
- Dependency injection patterns (if needed)
- Error handling strategy

**Scope & Boundaries**:
- **Can**: Create modules, define interfaces, separate concerns, manage dependencies
- **Cannot**: Violate spec requirements, skip error handling, introduce circular dependencies

**Reusability Notes**: Core pattern for all implementation work. Reusable module structure template.

**Dependencies**:
- Approved plan.md with module structure
- Constitution principle V (Clean Architecture)
- Python best practices

**Quality Expectations**:
- Each module has single responsibility
- Dependencies flow in one direction
- No circular dependencies
- External integrations abstracted behind interfaces
- Error handling is explicit

**Example Use Case**:
```python
# Module structure for Phase 1

# todo_manager.py (Business Logic)
class TodoManager:
    def __init__(self):
        self._todos = {}
        self._next_id = 1

    def add_todo(self, title, description=None):
        """Add a new todo. Returns todo ID."""
        todo_id = self._next_id
        self._todos[todo_id] = {
            'id': todo_id,
            'title': title,
            'description': description
        }
        self._next_id += 1
        return todo_id

# cli.py (CLI Layer - depends on todo_manager)
from todo_manager import TodoManager

def main():
    manager = TodoManager()
    # CLI parsing and command dispatch

# Dependency flow: CLI → TodoManager (one direction, no circular)
```

---

### 3.3 Error Handling Implementation

**Name**: `error-handling-implementation`

**Purpose**: Implement comprehensive, explicit error handling with actionable error messages and proper state management.

**Applicable Agents**:
- Implementation agents (primary)
- python-cli-expert (CLI error messages)
- test-qa-validator (error path testing)

**Input**:
- Specification error scenarios
- Acceptance criteria for error cases
- Error taxonomy from plan

**Output**:
- Exception handling code
- Error message definitions
- Exit code strategy
- Error logging (if applicable)
- Recovery/rollback logic

**Scope & Boundaries**:
- **Can**: Handle errors, validate input, provide clear messages, log errors
- **Cannot**: Suppress errors silently, skip validation, use generic error messages

**Reusability Notes**: Pattern reusable across all error scenarios. Template for validation errors, business rule violations, system errors.

**Dependencies**:
- Error scenarios from spec acceptance criteria
- Constitution principle VI (Deterministic Behavior)
- Python exception hierarchy

**Quality Expectations**:
- All failure modes explicitly handled
- Error messages are specific and actionable
- No silent failures
- Errors logged to stderr
- System state remains consistent after errors

**Example Use Case**:
```python
# Input: Spec defines error for empty title
# Output: Error handling implementation

def add_todo(self, title, description=None):
    # Validation
    if not title or not title.strip():
        raise ValueError("Title cannot be empty")

    if len(title) > 200:
        raise ValueError("Title cannot exceed 200 characters")

    # Business logic
    try:
        todo_id = self._next_id
        self._todos[todo_id] = {
            'id': todo_id,
            'title': title.strip(),
            'description': description
        }
        self._next_id += 1
        return todo_id
    except Exception as e:
        # Log error and re-raise with context
        logging.error(f"Failed to add todo: {e}")
        raise RuntimeError(f"Failed to add todo: {e}") from e

# CLI error handling
try:
    todo_id = manager.add_todo(args.title, args.description)
    print(f"Todo added with ID: {todo_id}")
except ValueError as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}", file=sys.stderr)
    sys.exit(2)
```

---

### 3.4 Configuration Externalization

**Name**: `configuration-externalization`

**Purpose**: Externalize configuration, secrets, and environment-specific settings to prevent hardcoding and enable flexible deployment.

**Applicable Agents**:
- Implementation agents (primary)
- Review agents (security validation)

**Input**:
- Configuration requirements
- Environment-specific settings
- Security constraints (no hardcoded secrets)

**Output**:
- Configuration file structure (.env, config.json, etc.)
- Environment variable usage
- Configuration loading logic
- Default values and validation
- Documentation for configuration options

**Scope & Boundaries**:
- **Can**: Externalize config, use environment variables, validate settings, document options
- **Cannot**: Hardcode secrets, embed environment-specific paths, skip validation

**Reusability Notes**: Pattern reusable across all phases. Essential for Phase 2+ (persistence paths, API endpoints, etc.).

**Dependencies**:
- Constitution default policy (no hardcoded secrets)
- Python-dotenv or configparser library
- Phase-specific configuration needs

**Quality Expectations**:
- No secrets or tokens in code
- Configuration validated on load
- Clear documentation for all settings
- Sensible defaults provided
- Environment variables used appropriately

**Example Use Case**:
```python
# .env file
TODO_DATA_FILE=todos.json
TODO_MAX_ITEMS=1000

# config.py
import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.data_file = os.getenv('TODO_DATA_FILE', 'todos.json')
        self.max_items = int(os.getenv('TODO_MAX_ITEMS', '1000'))
        self._validate()

    def _validate(self):
        if self.max_items < 1:
            raise ValueError("TODO_MAX_ITEMS must be positive")

# Usage
config = Config()
manager = TodoManager(data_file=config.data_file)
```

---

## 4. Testing & QA Skills

### 4.1 Unit Test Generation

**Name**: `unit-test-generation`

**Purpose**: Generate comprehensive unit tests for individual functions and methods based on acceptance criteria and edge cases.

**Applicable Agents**:
- test-qa-validator (primary)
- Implementation agents (TDD workflow)

**Input**:
- Function/method to test
- Acceptance criteria from spec
- Edge cases and error scenarios

**Output**:
- Unit test suite (pytest or unittest)
- Test cases for happy path
- Test cases for edge cases and errors
- Test fixtures and mocks (if needed)
- Coverage targets

**Scope & Boundaries**:
- **Can**: Generate tests, cover edge cases, mock dependencies, verify acceptance criteria
- **Cannot**: Modify implementation code, skip test coverage, bypass acceptance criteria

**Reusability Notes**: Core testing pattern for all implementation work. Template reusable across all phases.

**Dependencies**:
- Python testing framework (pytest recommended)
- Acceptance criteria from spec
- Implementation code to test

**Quality Expectations**:
- Tests cover happy path and edge cases
- Tests are independent (no shared state)
- Tests fail before implementation, pass after (TDD)
- Clear test names describe scenarios
- Assertions are specific and meaningful

**Example Use Case**:
```python
# Input: add_todo method with acceptance criteria
# Output: Unit test suite

import pytest
from todo_manager import TodoManager

class TestAddTodo:
    def test_add_todo_with_title_returns_id(self):
        """Given valid title, when adding todo, then return unique ID"""
        manager = TodoManager()
        todo_id = manager.add_todo("Buy milk")
        assert isinstance(todo_id, int)
        assert todo_id > 0

    def test_add_todo_with_title_and_description(self):
        """Given title and description, when adding todo, then both stored"""
        manager = TodoManager()
        todo_id = manager.add_todo("Buy milk", "From store on 5th Ave")
        todos = manager.list_todos()
        assert todos[todo_id]['title'] == "Buy milk"
        assert todos[todo_id]['description'] == "From store on 5th Ave"

    def test_add_todo_with_empty_title_raises_error(self):
        """Given empty title, when adding todo, then raise ValueError"""
        manager = TodoManager()
        with pytest.raises(ValueError, match="Title cannot be empty"):
            manager.add_todo("")

    def test_add_todo_sequential_ids(self):
        """Given multiple todos, when adding sequentially, then IDs increment"""
        manager = TodoManager()
        id1 = manager.add_todo("Task 1")
        id2 = manager.add_todo("Task 2")
        assert id2 == id1 + 1
```

---

### 4.2 Integration Test Generation

**Name**: `integration-test-generation`

**Purpose**: Generate integration tests that validate end-to-end user journeys and interactions between modules.

**Applicable Agents**:
- test-qa-validator (primary)
- Implementation agents (Phase completion testing)

**Input**:
- User stories from spec
- Acceptance criteria for user journeys
- Module interfaces

**Output**:
- Integration test suite
- End-to-end scenario tests
- Multi-module interaction tests
- CLI integration tests (for CLI apps)
- Setup/teardown logic

**Scope & Boundaries**:
- **Can**: Test user journeys, module interactions, CLI workflows, data flow
- **Cannot**: Replace unit tests, skip teardown, leave test artifacts

**Reusability Notes**: Essential for phase completion validation. Pattern reusable for all user journeys.

**Dependencies**:
- User stories and acceptance criteria
- Implemented modules
- Test environment setup

**Quality Expectations**:
- Tests validate complete user journeys
- Tests clean up after themselves
- Tests are deterministic and repeatable
- Tests verify acceptance criteria end-to-end
- Setup/teardown properly isolates tests

**Example Use Case**:
```python
# Input: User story - "User can add and view todos"
# Output: Integration test

import pytest
import tempfile
import os
from cli import main
from io import StringIO
import sys

class TestTodoWorkflow:
    def test_add_and_list_todo_workflow(self, capsys):
        """
        Given: User wants to add and view todos
        When: User adds todo and lists todos
        Then: Added todo appears in list
        """
        # Add todo
        sys.argv = ['cli.py', 'add', 'Buy groceries', '-d', 'Milk and bread']
        main()
        captured = capsys.readouterr()
        assert "Todo added with ID:" in captured.out

        # Extract ID from output
        todo_id = int(captured.out.split("ID: ")[1].strip())

        # List todos
        sys.argv = ['cli.py', 'list']
        main()
        captured = capsys.readouterr()
        assert "Buy groceries" in captured.out
        assert "Milk and bread" in captured.out

    def test_add_delete_workflow(self):
        """Complete workflow: add todo, verify exists, delete, verify gone"""
        # Implementation of add → verify → delete → verify workflow
        pass
```

---

### 4.3 CLI Input/Output Validation

**Name**: `cli-input-output-validation`

**Purpose**: Validate CLI behavior for various inputs, ensuring consistent output format, proper error messages, and correct exit codes.

**Applicable Agents**:
- test-qa-validator (primary)
- python-cli-expert (CLI design validation)

**Input**:
- CLI specification
- Command definitions
- Expected input/output behavior

**Output**:
- CLI test suite
- Input validation tests
- Output format validation tests
- Exit code verification tests
- Help text validation tests

**Scope & Boundaries**:
- **Can**: Test CLI parsing, output format, error messages, exit codes, help text
- **Cannot**: Test business logic directly (use unit tests), skip error scenarios

**Reusability Notes**: Pattern for testing all CLI commands across phases. Template for add/list/delete/edit commands.

**Dependencies**:
- CLI implementation
- Python subprocess or argparse testing utilities
- CLI specification

**Quality Expectations**:
- All CLI commands tested
- Invalid input scenarios covered
- Output format is consistent
- Exit codes follow conventions
- Help text is accurate

**Example Use Case**:
```python
# Input: CLI "add" command specification
# Output: CLI validation tests

import subprocess
import sys

class TestCLIAdd:
    def test_add_command_with_title_succeeds(self):
        """Test add command with valid title returns exit code 0"""
        result = subprocess.run(
            ['python', 'cli.py', 'add', 'Buy milk'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "Todo added with ID:" in result.stdout

    def test_add_command_with_empty_title_fails(self):
        """Test add command with empty title returns exit code 1"""
        result = subprocess.run(
            ['python', 'cli.py', 'add', ''],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert "Error: Title cannot be empty" in result.stderr

    def test_add_command_help_text(self):
        """Test add command help text is clear"""
        result = subprocess.run(
            ['python', 'cli.py', 'add', '--help'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "Add a new todo" in result.stdout
        assert "title" in result.stdout
```

---

### 4.4 Regression Detection

**Name**: `regression-detection`

**Purpose**: Detect regressions by ensuring existing functionality remains intact after code changes or new feature additions.

**Applicable Agents**:
- test-qa-validator (primary)
- Review agents (before phase transitions)

**Input**:
- Existing test suite
- New code changes
- Previous phase functionality

**Output**:
- Regression test report
- List of broken functionality (if any)
- Coverage comparison (before/after)
- Recommendations for fixes

**Scope & Boundaries**:
- **Can**: Run tests, compare results, identify regressions, report issues
- **Cannot**: Fix regressions automatically, skip tests, approve failing builds

**Reusability Notes**: Critical for phase transitions. Run before every phase advancement and code commit.

**Dependencies**:
- Existing test suite
- Test execution framework
- Previous baseline results

**Quality Expectations**:
- All existing tests pass
- No functionality broken by changes
- Test coverage maintained or improved
- Regressions reported with specific details
- Clear actionable recommendations

**Example Use Case**:
```bash
# Run regression tests before Phase 2 merge

# Phase 1 baseline: 25 tests, all passing
pytest tests/ -v

# After Phase 2 changes: 35 tests
pytest tests/ -v

# Output:
# ✅ Phase 1 tests: 25/25 passing (no regressions)
# ✅ Phase 2 tests: 10/10 passing
# ✅ Coverage: 92% (up from 88%)
# Result: PASS - Safe to merge Phase 2
```

---

## 5. Documentation Skills

### 5.1 README Generation

**Name**: `readme-generation`

**Purpose**: Create comprehensive README documentation explaining project purpose, setup, phase structure, and usage instructions.

**Applicable Agents**:
- docs-narrative-writer (primary)
- General-purpose agents during project initialization

**Input**:
- Project overview
- Phase descriptions
- Setup instructions
- Usage examples

**Output**:
- README.md file
- Project description
- Prerequisites and installation
- Phase-by-phase usage guide
- Links to additional documentation

**Scope & Boundaries**:
- **Can**: Explain project, document setup, provide usage examples, link to docs
- **Cannot**: Write technical specs, create ADRs, document internal architecture

**Reusability Notes**: Updated incrementally as phases complete. Template reusable for all projects.

**Dependencies**:
- Project specifications
- Phase implementation status
- Setup/installation procedures

**Quality Expectations**:
- Clear project purpose and context
- Complete setup instructions
- Phase-by-phase execution guide
- Links to key documentation
- Professional, concise language

**Example Use Case**:
```markdown
# Todo App - Hackathon Project

## Overview
A multi-phase CLI-based todo application demonstrating Spec-Driven Development and AI-native workflows.

## Phases

### Phase 1: In-Memory CRUD
Basic todo operations (add, list, delete) with in-memory storage.

**Run Phase 1:**
```bash
python cli.py add "Buy groceries"
python cli.py list
python cli.py delete 1
```

### Phase 2: File-Based Persistence
Extends Phase 1 with JSON file persistence.

**Run Phase 2:**
```bash
export TODO_DATA_FILE=todos.json
python cli.py add "Buy milk"
```

## Setup
1. Python 3.9+
2. `pip install -r requirements.txt`
3. Run: `python cli.py --help`
```

---

### 5.2 ADR Creation

**Name**: `adr-creation`

**Purpose**: Document architecturally significant decisions with context, alternatives, and consequences for future reference.

**Applicable Agents**:
- General-purpose agents (when human approves ADR suggestion)
- Plan agents (after identifying significant decisions)

**Input**:
- Decision title and description
- Context and problem statement
- Alternatives considered
- Decision rationale
- Consequences (positive and negative)

**Output**:
- ADR document (history/adr/NNNN-decision-title.md)
- Context section
- Decision section
- Alternatives considered section
- Consequences section
- Status (proposed, accepted, rejected, deprecated)

**Scope & Boundaries**:
- **Can**: Document decisions, record alternatives, explain rationale, note consequences
- **Cannot**: Create ADRs without human consent, make decisions independently

**Reusability Notes**: Template reusable for all significant decisions. Standard ADR format.

**Dependencies**:
- Human approval (never auto-created)
- ADR template from Spec-Kit Plus
- Understanding of decision context

**Quality Expectations**:
- Clear problem statement
- All viable alternatives documented
- Decision rationale explained
- Consequences (positive and negative) listed
- Status clearly indicated

**Example Use Case**:
```markdown
# ADR-0001: Data Persistence Format

## Status
Accepted

## Context
Phase 2 requires persistent storage for todos. We need a format that is:
- Human-readable for debugging
- Simple to implement
- Portable across systems

## Decision
Use JSON file format for todo data persistence.

## Alternatives Considered
1. **SQLite**: More structured, queryable, but adds dependency and complexity for Phase 2
2. **Pickle**: Simple, but Python-specific and not human-readable
3. **CSV**: Simple, but poor for nested data (future descriptions, tags)

## Consequences
### Positive
- Human-readable for debugging
- No external dependencies
- Simple implementation for Phase 2
- Portable across systems

### Negative
- Limited querying capability (linear search)
- May need migration to SQLite in Phase 4+ for performance
- Manual serialization logic required
```

---

### 5.3 Judge-Facing Narrative Writing

**Name**: `judge-facing-narrative-writing`

**Purpose**: Create compelling, clear documentation for hackathon judges highlighting spec-driven methodology, AI collaboration, and architectural quality.

**Applicable Agents**:
- docs-narrative-writer (primary)
- hackathon-judge-reviewer (validation)

**Input**:
- Completed phases and features
- Spec-driven workflow artifacts
- Architectural decisions
- AI collaboration approach

**Output**:
- Judge-facing documentation
- Project narrative highlighting methodology
- Workflow demonstration
- Architecture and quality showcase
- Links to key artifacts

**Scope & Boundaries**:
- **Can**: Showcase methodology, highlight quality, demonstrate workflow, explain decisions
- **Cannot**: Exaggerate capabilities, hide issues, misrepresent AI role

**Reusability Notes**: Created before final submission. Template for hackathon evaluation documentation.

**Dependencies**:
- Completed work across phases
- Spec/plan/task artifacts
- ADRs and PHRs
- Constitution and CLAUDE.md

**Quality Expectations**:
- Clear demonstration of spec-driven thinking
- Honest representation of AI collaboration
- Evidence of architectural foresight
- Professional, factual language (no marketing fluff)
- Links to concrete artifacts

**Example Use Case**:
```markdown
# Todo App: Spec-Driven Development Demonstration

## Methodology Showcase

This project demonstrates mature AI-native development:

1. **Spec-First Approach**: Every feature began with an approved specification
   - See: `specs/phase-1-todo-crud/spec.md`
   - Note: Zero code written before spec approval

2. **Workflow Discipline**: Followed spec → plan → tasks → implement
   - Artifacts: spec.md, plan.md, tasks.md for each phase
   - Evidence: Git history shows workflow adherence

3. **Architectural Foresight**: Clean phase isolation enables evolution
   - Phase 1: In-memory CRUD (independently runnable)
   - Phase 2: Added persistence without breaking Phase 1
   - See: ADR-0001 for data format decision rationale

4. **AI Collaboration**: Transparent, traceable, governed
   - PHRs capture all AI interactions: `history/prompts/`
   - ADRs document significant decisions: `history/adr/`
   - Constitution governs AI behavior: `.specify/memory/constitution.md`

## Quality Indicators
- Test coverage: 95%
- All specs have acceptance criteria
- Zero hardcoded configuration
- Full phase independence verified
```

---

### 5.4 Prompt History Record (PHR) Creation

**Name**: `phr-creation`

**Purpose**: Record every user input and AI interaction verbatim for audit, learning, and traceability.

**Applicable Agents**:
- All agents (automatically after task completion)
- General-purpose agents (when executing PHR creation)

**Input**:
- User prompt (verbatim)
- AI response (key output)
- Stage/phase context
- Files created/modified
- Tests run

**Output**:
- PHR file (history/prompts/<route>/<ID>-<slug>.<stage>.prompt.md)
- Complete YAML frontmatter
- Full prompt text (not truncated)
- Representative response text
- Metadata (date, model, feature, branch)

**Scope & Boundaries**:
- **Can**: Record prompts, capture responses, route to correct location, fill all metadata
- **Cannot**: Truncate prompts, skip PHR creation, auto-create for `/sp.phr` itself

**Reusability Notes**: Mandatory for all implementation and planning work. Automated pattern.

**Dependencies**:
- PHR template (`.specify/templates/phr-template.prompt.md`)
- Current feature context
- Git branch information

**Quality Expectations**:
- Prompt text is complete (not truncated)
- All placeholders filled
- Correct routing (constitution, feature, general)
- File paths and test info included
- Readable and traceable

**Example Use Case**:
```markdown
---
id: 0042
title: Implement Add Todo CLI Command
stage: green
date: 2025-12-29
surface: agent
model: claude-sonnet-4-5
feature: phase-1-todo-crud
branch: master
command: /sp.implement
labels: ["cli", "implementation", "phase-1"]
links:
  spec: specs/phase-1-todo-crud/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - cli.py
  - todo_manager.py
tests:
  - tests/test_cli.py::test_add_command_with_title_succeeds
  - tests/test_todo_manager.py::TestAddTodo
---

## Prompt
Implement the 'add' command for the todo CLI as specified in phase-1-todo-crud spec. The command should accept a title and optional description, validate input, and return a success message with todo ID.

## Response
Implemented add command in cli.py:15-35 and add_todo method in todo_manager.py:20-30. Added input validation for empty titles. Created unit tests covering happy path and error cases. All tests passing.
```

---

## 6. Review & Analysis Skills

### 6.1 Cross-Artifact Consistency Check

**Name**: `cross-artifact-consistency-check`

**Purpose**: Validate consistency between spec, plan, tasks, and implementation to ensure traceability and alignment.

**Applicable Agents**:
- Review agents during `/sp.analyze`
- hackathon-judge-reviewer (evaluation)

**Input**:
- spec.md
- plan.md
- tasks.md
- Implementation code

**Output**:
- Consistency report
- Alignment verification (spec ↔ plan ↔ tasks ↔ code)
- Gap identification
- Traceability matrix
- Recommendations for fixes

**Scope & Boundaries**:
- **Can**: Compare artifacts, identify gaps, verify alignment, suggest fixes
- **Cannot**: Modify artifacts autonomously, bypass human approval, skip validation

**Reusability Notes**: Run after task generation and after implementation. Critical for quality assurance.

**Dependencies**:
- All planning artifacts (spec, plan, tasks)
- Implementation code
- Acceptance criteria

**Quality Expectations**:
- All spec requirements mapped to plan
- All plan components mapped to tasks
- All tasks mapped to code
- No orphaned requirements or tasks
- Traceability maintained end-to-end

**Example Use Case**:
```
Input: Phase 1 artifacts (spec, plan, tasks, code)
Output:
  Consistency Report:

  ✅ Spec Requirement 1 "Add todo" → Plan Section 2.1 → Task 2 → cli.py:15-35
  ✅ Spec Requirement 2 "List todos" → Plan Section 2.2 → Task 4 → cli.py:40-55
  ⚠️  Spec Requirement 3 "Delete todo" → Plan Section 2.3 → Task 6 → NOT IMPLEMENTED

  Gap Analysis:
  - Delete functionality specified but not implemented
  - Recommendation: Implement Task 6 or update spec to defer to Phase 1.1

  Traceability: 66% (2/3 requirements implemented)
```

---

### 6.2 Spec vs Implementation Comparison

**Name**: `spec-vs-implementation-comparison`

**Purpose**: Compare implemented code against specification acceptance criteria to verify compliance and identify gaps.

**Applicable Agents**:
- test-qa-validator (primary)
- hackathon-judge-reviewer (evaluation)
- Review agents

**Input**:
- Specification with acceptance criteria
- Implementation code
- Test results

**Output**:
- Compliance report
- Acceptance criteria status (pass/fail)
- Gap identification
- Non-compliant code locations
- Recommendations for fixes

**Scope & Boundaries**:
- **Can**: Verify acceptance criteria, identify gaps, flag non-compliance, suggest fixes
- **Cannot**: Modify code or spec autonomously, approve non-compliant implementations

**Reusability Notes**: Run at phase completion and before phase transitions. Critical quality gate.

**Dependencies**:
- Spec with acceptance criteria
- Implementation code
- Test execution capability

**Quality Expectations**:
- All acceptance criteria verified
- Non-compliance clearly identified
- Gaps documented with code references
- Recommendations are actionable
- No false positives in compliance check

**Example Use Case**:
```
Input: Phase 1 spec + implementation
Output:
  Compliance Report:

  Acceptance Criterion 1: "Add todo returns unique ID"
    Status: ✅ PASS
    Evidence: todo_manager.py:25 returns self._next_id
    Test: tests/test_todo_manager.py::test_add_todo_with_title_returns_id PASS

  Acceptance Criterion 2: "Empty title raises error"
    Status: ✅ PASS
    Evidence: todo_manager.py:22 validates title.strip()
    Test: tests/test_todo_manager.py::test_add_todo_with_empty_title_raises_error PASS

  Acceptance Criterion 3: "Todo persists across sessions"
    Status: ❌ FAIL (Phase 1 is in-memory only)
    Evidence: No persistence implementation
    Recommendation: This is expected for Phase 1; deferred to Phase 2

  Overall Compliance: 100% for Phase 1 scope
```

---

### 6.3 Risk Identification

**Name**: `risk-identification`

**Purpose**: Identify technical, architectural, and process risks in plans, implementations, or phase transitions.

**Applicable Agents**:
- hackathon-judge-reviewer (evaluation perspective)
- Plan agents (during planning)
- Review agents (during analysis)

**Input**:
- Implementation plan or code
- Phase transition requirements
- Architectural decisions

**Output**:
- Risk assessment report
- Categorized risks (technical, process, architectural)
- Impact and likelihood assessment
- Mitigation recommendations
- Prioritized risk list

**Scope & Boundaries**:
- **Can**: Identify risks, assess impact, recommend mitigations, prioritize
- **Cannot**: Make architectural decisions, bypass human judgment, ignore risks

**Reusability Notes**: Run during planning and before phase transitions. Pattern for risk assessment.

**Dependencies**:
- Plan or implementation artifacts
- Constitution and quality standards
- Phase transition criteria

**Quality Expectations**:
- All significant risks identified
- Impact and likelihood clearly stated
- Mitigation recommendations actionable
- Risks prioritized by severity
- No false alarms (only real risks)

**Example Use Case**:
```
Input: Phase 2 persistence plan
Output:
  Risk Assessment:

  RISK-1: Data Corruption on Concurrent Access
    Category: Technical
    Impact: HIGH (data loss)
    Likelihood: MEDIUM (if multiple processes)
    Mitigation: Add file locking or document single-process constraint

  RISK-2: Breaking Phase 1 Functionality
    Category: Architectural
    Impact: HIGH (violates phase isolation)
    Likelihood: LOW (if feature flags used)
    Mitigation: Comprehensive regression testing before merge

  RISK-3: JSON File Size Growth
    Category: Performance
    Impact: MEDIUM (slow load times)
    Likelihood: LOW (for hackathon scale)
    Mitigation: Document in README as known limitation; defer to Phase 4

  Priority: RISK-1 (HIGH/MEDIUM), RISK-2 (HIGH/LOW), RISK-3 (MEDIUM/LOW)
```

---

### 6.4 Code Quality Review

**Name**: `code-quality-review`

**Purpose**: Review code for adherence to quality standards, best practices, and constitutional principles.

**Applicable Agents**:
- Review agents (code review context)
- python-cli-expert (CLI-specific review)
- hackathon-judge-reviewer (judge perspective)

**Input**:
- Implementation code
- Constitution quality standards
- Spec requirements

**Output**:
- Quality review report
- Code quality metrics
- Best practice violations
- Improvement recommendations
- Approval/rejection decision

**Scope & Boundaries**:
- **Can**: Review code, identify issues, recommend improvements, assess quality
- **Cannot**: Modify code without approval, bypass standards, approve non-compliant code

**Reusability Notes**: Run before commits and phase transitions. Pattern for all code reviews.

**Dependencies**:
- Constitution quality standards
- Python best practices
- Spec requirements

**Quality Expectations**:
- All constitutional principles verified
- Code quality metrics calculated
- Specific improvement recommendations
- No subjective or vague feedback
- Clear approval/rejection criteria

**Example Use Case**:
```
Input: Phase 1 implementation code
Output:
  Code Quality Review:

  ✅ Readability: Clear naming, well-structured (PASS)
  ✅ Modularity: CLI separated from business logic (PASS)
  ✅ Error Handling: All failure modes handled explicitly (PASS)
  ⚠️  Documentation: Missing docstrings in todo_manager.py
  ❌ Testing: Only 78% coverage (target: 90%+)

  Best Practice Violations:
  - todo_manager.py:45 - Using mutable default argument
  - cli.py:22 - Broad exception catch (use specific exceptions)

  Recommendations:
  1. Add docstrings to all public methods
  2. Fix mutable default in add_todo
  3. Add test cases for edge scenarios to reach 90% coverage
  4. Replace broad exception with specific ValueError/RuntimeError

  Decision: CONDITIONAL APPROVAL (fix critical issues, warnings acceptable)
```

---

## Appendix

### Skill Invocation Guidelines

**When to Use Skills:**
- Agents should invoke skills explicitly when task requirements match skill purpose
- Skills can be chained together (e.g., requirement-decomposition → acceptance-criteria-generation)
- Multiple skills can run in parallel if independent

**Skill Composition Examples:**
```
Workflow 1: Spec Creation
  1. requirement-decomposition
  2. acceptance-criteria-generation
  3. phase-boundary-definition
  4. spec-validation

Workflow 2: Implementation
  1. task-decomposition
  2. dependency-analysis
  3. python-cli-pattern-implementation
  4. modular-architecture-implementation
  5. error-handling-implementation
  6. unit-test-generation

Workflow 3: Phase Completion
  1. integration-test-generation
  2. regression-detection
  3. cross-artifact-consistency-check
  4. spec-vs-implementation-comparison
  5. code-quality-review
```

### Skill Evolution

As the project evolves across phases:
- **Phase 1**: Core skills (requirement-decomposition, task-decomposition, python-cli-pattern-implementation, unit-test-generation)
- **Phase 2**: Add persistence skills (configuration-externalization, data migration patterns)
- **Phase 3+**: Add advanced skills (performance optimization, security validation, API design)

New skills should follow the same 10-component structure and be added to appropriate categories.

---

**End of Skills Library**

**Maintenance Notes:**
- Update skills as new patterns emerge across phases
- Add new skills following the established template
- Version this document as skills evolve
- Link to this library from agent documentation and CLAUDE.md
