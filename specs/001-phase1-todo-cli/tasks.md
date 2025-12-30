# Tasks: Phase 1 - In-Memory Todo CLI

**Feature**: 001-phase1-todo-cli
**Input**: Design documents from `specs/001-phase1-todo-cli/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-interface.md, quickstart.md

**Tests**: Tests are NOT explicitly requested in the specification. This task list focuses on implementation only. Testing can be added in a separate iteration if requested.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

This is a single-project Python CLI application with files at repository root:
- Core modules: `todo_manager.py`, `cli.py`, `todo.py`
- Tests (if added later): `tests/`
- Documentation: `README.md`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure per implementation plan (root-level files)
- [x] T002 Create Python project configuration files (pyproject.toml or setup.py if needed)
- [x] T003 [P] Create .gitignore for Python project (exclude __pycache__, *.pyc, .env, etc.)
- [x] T004 [P] Create requirements-dev.txt with development dependencies (pytest, coverage)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core TodoManager module that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until TodoManager is complete

- [x] T005 Implement TodoManager class skeleton in todo_manager.py with __init__ method
- [x] T006 Implement in-memory storage structure (Dict[int, Dict[str, Any]]) in todo_manager.py
- [x] T007 Implement ID counter mechanism (self._next_id) in todo_manager.py
- [x] T008 [P] Implement input validation utilities (trim whitespace, validate length) in todo_manager.py

**Checkpoint**: TodoManager foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add New Todo (Priority: P1) 🎯 MVP

**Goal**: Enable users to create new todos with title and optional description

**Independent Test**: Run `python todo.py add "Buy groceries"` and verify todo is created with ID and confirmation message

**Acceptance Criteria**: spec.md lines 18-24 (User Story 1, scenarios 1-4)

### Implementation for User Story 1

- [x] T009 [US1] Implement add_todo(title, description) method in todo_manager.py
- [x] T010 [US1] Add title validation in add_todo (empty check, length ≤200 chars) in todo_manager.py
- [x] T011 [US1] Add whitespace trimming for title and description in add_todo in todo_manager.py
- [x] T012 [US1] Implement ID assignment and increment logic in add_todo in todo_manager.py
- [x] T013 [US1] Implement todo storage in dictionary in add_todo in todo_manager.py
- [x] T014 [US1] Create CLI parser skeleton with argparse in cli.py
- [x] T015 [US1] Implement add subcommand parser in cli.py (title argument, --description option)
- [x] T016 [US1] Implement handle_add function in cli.py (calls TodoManager.add_todo)
- [x] T017 [US1] Add success output formatting in handle_add ("Todo added with ID: {id}")
- [x] T018 [US1] Add error handling for validation failures in handle_add (stderr, exit code 1)
- [x] T019 [US1] Create main entry point in todo.py
- [x] T020 [US1] Wire CLI parser to TodoManager in todo.py main function
- [x] T021 [US1] Add exception handling and exit codes in todo.py main function

**Checkpoint**: At this point, User Story 1 should be fully functional - users can add todos and receive confirmation

---

## Phase 4: User Story 2 - View All Todos (Priority: P1)

**Goal**: Enable users to view all their current todos

**Independent Test**: Add multiple todos, run `python todo.py list`, verify all todos are displayed with IDs, titles, and descriptions

**Acceptance Criteria**: spec.md lines 27-40 (User Story 2, scenarios 1-3)

### Implementation for User Story 2

- [x] T022 [P] [US2] Implement list_todos() method in todo_manager.py
- [x] T023 [US2] Add sorting by ID (ascending) in list_todos in todo_manager.py
- [x] T024 [US2] Return list of todo dictionaries from list_todos in todo_manager.py
- [x] T025 [US2] Implement list subcommand parser in cli.py (no arguments)
- [x] T026 [US2] Implement handle_list function in cli.py (calls TodoManager.list_todos)
- [x] T027 [US2] Add output formatting for todos in handle_list (ID, Title, Description format per contract)
- [x] T028 [US2] Add "No todos found" message for empty list in handle_list
- [x] T029 [US2] Handle description display logic (only show if not None) in handle_list
- [x] T030 [US2] Add UTF-8 encoding handling for special characters in handle_list

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can add and view todos

---

## Phase 5: User Story 3 - Delete Completed Todo (Priority: P2)

**Goal**: Enable users to remove todos by ID

**Independent Test**: Add todos, delete specific one by ID, verify it's removed and no longer appears in list

**Acceptance Criteria**: spec.md lines 43-57 (User Story 3, scenarios 1-4)

### Implementation for User Story 3

- [x] T031 [P] [US3] Implement delete_todo(todo_id) method in todo_manager.py
- [x] T032 [US3] Add ID existence validation in delete_todo in todo_manager.py
- [x] T033 [US3] Implement todo removal from dictionary in delete_todo in todo_manager.py
- [x] T034 [US3] Ensure deleted IDs are NOT reused (ID counter never decrements) in todo_manager.py
- [x] T035 [US3] Implement delete subcommand parser in cli.py (id argument as integer)
- [x] T036 [US3] Implement handle_delete function in cli.py (calls TodoManager.delete_todo)
- [x] T037 [US3] Add success output formatting in handle_delete ("Todo {id} deleted")
- [x] T038 [US3] Add error handling for non-existent ID in handle_delete (stderr, exit code 1)
- [x] T039 [US3] Add error handling for invalid ID format in handle_delete (stderr, exit code 1)

**Checkpoint**: All core CRUD operations (Create, Read, Delete) should now be independently functional

---

## Phase 6: User Story 4 - View Help Documentation (Priority: P3)

**Goal**: Enable users to understand available commands and usage

**Independent Test**: Run `python todo.py --help`, `python todo.py add --help`, verify comprehensive help is displayed

**Acceptance Criteria**: spec.md lines 60-73 (User Story 4, scenarios 1-3)

### Implementation for User Story 4

- [x] T040 [P] [US4] Add program description and epilog to main parser in cli.py
- [x] T041 [P] [US4] Add help text for add subcommand in cli.py (include examples)
- [x] T042 [P] [US4] Add help text for list subcommand in cli.py (include examples)
- [x] T043 [P] [US4] Add help text for delete subcommand in cli.py (include examples)
- [x] T044 [US4] Implement help subcommand parser in cli.py (shows main help)
- [x] T045 [US4] Add usage examples to main help epilog in cli.py
- [x] T046 [US4] Ensure --help and -h work for all commands in cli.py
- [x] T047 [US4] Add error message for no arguments (suggest --help) in cli.py

**Checkpoint**: All user stories should now be independently functional with comprehensive documentation

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements, documentation, and quality assurance

- [x] T048 [P] Create README.md with installation, usage, and examples
- [x] T049 [P] Add docstrings to all public methods in todo_manager.py
- [x] T050 [P] Add docstrings to all functions in cli.py
- [x] T051 [P] Add module-level docstrings to todo.py, cli.py, todo_manager.py
- [x] T052 [P] Verify error messages match contract specifications in contracts/cli-interface.md
- [x] T053 [P] Verify exit codes (0 success, 1 user error, 2 system error) across all commands
- [x] T054 [P] Test with Unicode characters in titles and descriptions (emoji, Chinese, etc.)
- [x] T055 [P] Test with special characters (quotes, newlines, backslashes)
- [x] T056 [P] Verify title length validation (reject >200 characters)
- [x] T057 [P] Verify whitespace trimming works correctly
- [x] T058 [P] Test edge cases: empty list, delete from empty list, sequential IDs after deletion
- [x] T059 Code review against constitution principles (all 7 principles)
- [x] T060 Validate against spec.md acceptance criteria (all user stories)
- [x] T061 Run quickstart.md validation checklist
- [x] T062 [P] Update CLAUDE.md with Phase 1 implementation details and workflow
- [x] T063 Final integration test: add → list → delete → list workflow

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (different files/commands)
  - Or sequentially in priority order (US1 → US2 → US3 → US4)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Add**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1) - List**: Can start after Foundational (Phase 2) - No dependencies on other stories (but integrates with US1 data)
- **User Story 3 (P2) - Delete**: Can start after Foundational (Phase 2) - No dependencies on other stories (but modifies US1 data)
- **User Story 4 (P3) - Help**: Can start after Foundational (Phase 2) - No dependencies on other stories (documents US1-3)

### Within Each User Story

- **User Story 1**: TodoManager.add_todo → CLI parser → CLI handler → main wiring
- **User Story 2**: TodoManager.list_todos → CLI parser → CLI handler → output formatting
- **User Story 3**: TodoManager.delete_todo → CLI parser → CLI handler → error handling
- **User Story 4**: All help text tasks can run in parallel [P]

### Parallel Opportunities

**Within Foundational Phase (Phase 2)**:
- T005-T007 must be sequential (class skeleton → storage → ID counter)
- T008 can run in parallel with T005-T007 (validation utilities)

**Within User Story 1 (Phase 3)**:
- T009-T013 are sequential (build add_todo method step by step)
- T014-T018 are sequential (build CLI for add command)
- T019-T021 are sequential (build main entry point)
- BUT: TodoManager work (T009-T013) can overlap with CLI work (T014-T018) if different developers

**Within User Story 2 (Phase 4)**:
- T022-T024 can be done together [P] (all in todo_manager.py list_todos)
- T025-T030 are sequential (build CLI for list command)

**Within User Story 3 (Phase 5)**:
- T031-T034 can be done together [P] (all in todo_manager.py delete_todo)
- T035-T039 are sequential (build CLI for delete command)

**Within User Story 4 (Phase 6)**:
- T040-T043 can all run in parallel [P] (different help texts)
- T044-T047 are sequential (help command implementation)

**Within Polish Phase (Phase 7)**:
- T048-T058 can all run in parallel [P] (documentation, validation, testing)
- T059-T061 should be sequential (reviews build on each other)
- T062-T063 can run in parallel [P]

**Across User Stories**:
- Once Phase 2 (Foundational) completes, ALL user stories (Phase 3-6) can start in parallel if team capacity allows
- Different developers can work on US1, US2, US3, US4 simultaneously

---

## Parallel Example: After Foundational Phase

```bash
# All these can start simultaneously after Phase 2 completes:

# Developer A (or parallel agent):
Task T009-T021: User Story 1 - Add command implementation

# Developer B (or parallel agent):
Task T022-T030: User Story 2 - List command implementation

# Developer C (or parallel agent):
Task T031-T039: User Story 3 - Delete command implementation

# Developer D (or parallel agent):
Task T040-T047: User Story 4 - Help documentation
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

Both US1 and US2 are Priority P1 and form the minimum viable product:

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T008) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 - Add (T009-T021)
4. Complete Phase 4: User Story 2 - List (T022-T030)
5. **STOP and VALIDATE**: Test add + list workflow independently
6. Deploy/demo MVP if ready

### Incremental Delivery

1. **Foundation** (Setup + Foundational) → Core TodoManager ready
2. **MVP** (US1 + US2) → Can add and view todos → Deploy/Demo
3. **Enhanced** (+ US3) → Can delete todos → Deploy/Demo
4. **Complete** (+ US4) → Full help documentation → Deploy/Demo
5. **Polished** (Phase 7) → Production-ready → Final Deploy

### Parallel Team Strategy

With multiple developers or agents:

1. **Together**: Complete Setup (Phase 1) + Foundational (Phase 2)
2. **Once Foundational is done**, split into parallel tracks:
   - Track A: User Story 1 (Add command)
   - Track B: User Story 2 (List command)
   - Track C: User Story 3 (Delete command)
   - Track D: User Story 4 (Help documentation)
3. **Merge and integrate**: Each story is independently testable
4. **Together**: Complete Polish phase (Phase 7)

---

## Agent Assignments

Based on `.claude/skills/skills_library.md` and agent responsibilities from `plan.md`:

### Phase 1 & 2: Setup & Foundational
- **Primary**: Todo App Phase 1 Delivery Agent (coordination)
- **Support**: Python CLI Expert Agent (architecture review)
- **Skills**: `modular-architecture-implementation`, `python-cli-pattern-implementation`

### Phase 3-6: User Story Implementation
- **Primary**: Python CLI Expert Agent (CLI design and implementation)
- **Support**: Todo App Phase 1 Delivery Agent (coordination)
- **Skills**: `python-cli-pattern-implementation`, `error-handling-implementation`, `cli-input-output-validation`

### Phase 7: Polish & QA
- **Documentation**: Documentation & Narrative Agent (T048, T062)
  - **Skills**: `readme-generation`, `end-user-documentation-creation`
- **Testing**: Automated Test & QA Agent (T052-T058)
  - **Skills**: `cli-input-output-validation`, `edge-case-testing`
- **Review**: Hackathon Review & Judge-Brain Agent (T059-T061)
  - **Skills**: `cross-artifact-consistency-check`, `spec-alignment-validation`
- **Coordination**: Todo App Phase 1 Delivery Agent (overall)

---

## Notes

- **[P] tasks** = different files or independent sections, no dependencies, can run in parallel
- **[Story] label** maps task to specific user story for traceability (US1, US2, US3, US4)
- Each user story should be independently completable and testable
- Tests are NOT included in this task list (not requested in spec)
- If tests are needed later, add them BEFORE implementation tasks for each story
- Commit after each task or logical group of tasks
- Stop at any checkpoint to validate story independently
- **Constitutional Compliance**: All tasks align with 7 constitutional principles
- **Phase Isolation**: No Phase 2+ dependencies (persistence, editing, status tracking)
- **Skill References**: Each phase references applicable skills from skills_library.md

---

## Task Summary

- **Total Tasks**: 63 tasks
- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 4 tasks
- **Phase 3 (US1 - Add)**: 13 tasks
- **Phase 4 (US2 - List)**: 9 tasks
- **Phase 5 (US3 - Delete)**: 9 tasks
- **Phase 6 (US4 - Help)**: 8 tasks
- **Phase 7 (Polish)**: 16 tasks

**Parallel Opportunities**: 25 tasks marked [P] can run in parallel with other tasks in their phase

**MVP Scope** (Recommended first milestone):
- Phase 1 (Setup): T001-T004
- Phase 2 (Foundational): T005-T008
- Phase 3 (US1): T009-T021
- Phase 4 (US2): T022-T030
- **Total MVP**: 34 tasks

**Independent Test Criteria**:
- US1: `python todo.py add "Test"` → Verify ID assigned and confirmation shown
- US2: Add 3 todos → `python todo.py list` → Verify all 3 displayed
- US3: Add 3 todos → `python todo.py delete 2` → Verify todo 2 removed
- US4: `python todo.py --help` → Verify comprehensive help displayed

Ready for `/sp.implement` execution!
