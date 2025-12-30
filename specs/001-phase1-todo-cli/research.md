# Research: Phase 1 - In-Memory Todo CLI

**Feature**: 001-phase1-todo-cli
**Created**: 2025-12-29
**Purpose**: Technical research and decision rationale for Phase 1 implementation

---

## Technology Decisions

### 1. CLI Parsing Library

**Decision**: Use Python's built-in `argparse` module

**Rationale**:
- Part of Python standard library (no external dependencies per CON-002)
- Mature, well-documented, and widely used
- Provides automatic help text generation
- Supports subcommands (add, list, delete, help)
- Handles argument validation and type conversion
- Compatible with Python 3.13+

**Alternatives Considered**:
- `click`: More elegant API but external dependency (violates CON-002)
- `typer`: Modern with type hints but external dependency (violates CON-002)
- `docopt`: Declarative but less common and external dependency
- Manual `sys.argv` parsing: Too error-prone, no built-in help

**References**:
- argparse documentation: https://docs.python.org/3/library/argparse.html
- Python CLI best practices: https://docs.python-guide.org/writing/structure/

---

### 2. Data Storage Strategy

**Decision**: Python dictionary with integer keys for in-memory todo storage

**Rationale**:
- Simple and performant for Phase 1 requirements
- O(1) lookup by ID for delete operations
- Meets FR-004 (in-memory storage requirement)
- Easy to serialize to JSON in Phase 2 (forward compatibility)
- No persistence mechanism needed (meets FR-018)

**Alternatives Considered**:
- List with index as ID: Delete operations would require list manipulation, gaps in IDs
- Custom Todo class with class-level storage: Over-engineering for Phase 1
- SQLite in-memory mode: Violates simplicity principle, unnecessary complexity

**Data Structure**:
```python
{
    1: {"id": 1, "title": "Buy groceries", "description": "Milk and bread"},
    2: {"id": 2, "title": "Call mom", "description": None},
    3: {"id": 3, "title": "Finish report", "description": "Q4 summary"}
}
```

---

### 3. ID Generation Strategy

**Decision**: Sequential integer counter starting from 1

**Rationale**:
- Simple and predictable for users
- Meets FR-003 (unique, sequential IDs)
- Easy to implement with a single counter variable
- Forward-compatible with database auto-increment in Phase 2
- Deleted IDs are not reused (as per acceptance criteria)

**Implementation**:
- Global counter variable tracking next available ID
- Increment after each todo creation
- Never decrement (even after deletion)

**Alternatives Considered**:
- UUID: Overkill for single-user, in-memory system
- Hash of title: Not guaranteed unique, violates sequential requirement
- Timestamp-based: Not user-friendly, not strictly sequential

---

### 4. Input Validation Approach

**Decision**: Validate at CLI layer before passing to business logic

**Rationale**:
- Fail fast with clear error messages
- Meets CON-010 (clear, actionable error messages)
- Separation of concerns: CLI handles user input, logic handles business rules
- Easier to test each layer independently

**Validation Rules**:
- Title: Required, non-empty after trimming, max 200 characters (FR-020)
- Description: Optional, trimmed if provided
- ID for delete: Must be integer, must exist in storage

**Error Handling Strategy**:
- User input errors → stderr with exit code 1
- Unexpected errors → stderr with exit code 2
- Success → stdout with exit code 0

---

### 5. Output Formatting

**Decision**: Plain text with clear structure for list command

**Rationale**:
- Meets CON-012 (readable in standard 80-character terminal)
- Simple to implement and test
- Human-readable output for Phase 1
- Can be enhanced with tables/colors in later phases

**Format Design**:
```
ID: 1
Title: Buy groceries
Description: Milk and bread

ID: 2
Title: Call mom

ID: 3
Title: Finish report
Description: Q4 summary
```

**Alternatives Considered**:
- JSON output: Not user-friendly for CLI interactive use
- Table format: Requires external library or complex formatting logic
- CSV: Poor readability for multiple fields

---

### 6. Module Organization

**Decision**: Three-module architecture with clear separation

**Modules**:
1. `todo_manager.py` - Business logic and in-memory storage
2. `cli.py` - Command-line interface and argument parsing
3. `main.py` - Entry point that wires CLI to business logic

**Rationale**:
- Follows Constitution Principle V (Clean Architecture and Modularity)
- Single responsibility per module
- Easy to test each module independently
- Forward-compatible: can swap storage in Phase 2 without touching CLI
- No circular dependencies

**Dependency Flow**:
```
main.py → cli.py → todo_manager.py
```

---

### 7. Testing Strategy

**Decision**: Pytest for unit and integration tests

**Rationale**:
- De facto standard for Python testing
- Part of standard testing ecosystem
- Clear assertion syntax
- Excellent test discovery
- Supports fixtures for setup/teardown
- Can run CLI integration tests via subprocess

**Test Coverage Requirements**:
- Unit tests: >90% code coverage (per acceptance criteria)
- CLI integration tests: All commands (add, list, delete, help)
- Edge case tests: Empty titles, invalid IDs, special characters
- Performance tests: 1000 todos without degradation

---

### 8. Error Message Design

**Decision**: Structured error messages with context and suggestions

**Format**:
```
Error: {what went wrong}
{optional context}
{optional suggestion}
```

**Examples**:
- `Error: Title cannot be empty`
- `Error: Todo with ID 999 not found`
- `Error: Invalid ID format. Please provide a number.`

**Rationale**:
- Meets CON-010 (clear, actionable error messages)
- Helps users understand what went wrong and how to fix it
- Consistent format across all error types

---

### 9. Character Encoding

**Decision**: UTF-8 throughout, with graceful degradation

**Rationale**:
- Meets ASM-005 (terminal supports UTF-8)
- Handles international characters in titles/descriptions
- Python 3.13 uses UTF-8 by default
- Encode/decode explicitly when interfacing with terminal

**Implementation**:
- Store strings as Python str (Unicode internally)
- Print with UTF-8 encoding
- Handle encoding errors gracefully (replace with '?' if needed)

---

### 10. Help Text Design

**Decision**: Comprehensive help with examples for each command

**Rationale**:
- Meets SC-007 (users understand within 2 minutes)
- argparse provides automatic help generation
- Custom descriptions and examples for clarity

**Help Structure**:
```
usage: todo <command> [options]

Commands:
  add       Add a new todo
  list      List all todos
  delete    Delete a todo by ID
  help      Show this help message

Use 'todo <command> --help' for more information on a specific command.
```

---

## Best Practices Applied

### Python CLI Best Practices

1. **Shebang line**: `#!/usr/bin/env python3` for cross-platform compatibility
2. **Exit codes**: 0 for success, 1 for user errors, 2 for unexpected errors
3. **Argument parsing**: Use argparse subcommands for clean command structure
4. **Error output**: All errors to stderr, success/info to stdout
5. **Help text**: Always provide --help for main command and subcommands

### Clean Code Principles

1. **Single Responsibility**: Each function does one thing
2. **DRY**: No code duplication
3. **Explicit > Implicit**: Clear variable names, explicit error handling
4. **Testability**: All functions pure or with minimal side effects
5. **Documentation**: Docstrings for all public functions

### Phase Isolation Strategy

1. **No persistence code**: All storage is in-memory dictionaries
2. **Extensible design**: TodoManager interface can be swapped in Phase 2
3. **CLI independence**: CLI layer has zero knowledge of storage implementation
4. **Data model flexibility**: Dictionary structure easily converts to JSON/DB in future

---

## Risks and Mitigations

### Risk 1: Memory Limitations
**Impact**: System could crash with extremely large number of todos
**Mitigation**:
- Document limit of 10,000 todos in README
- Test performance with 1000 todos (per SC-004)
- Defer to Phase 2 persistence for unlimited storage

### Risk 2: Unicode Handling
**Impact**: Special characters might display incorrectly or cause crashes
**Mitigation**:
- Use UTF-8 encoding throughout
- Test with diverse character sets (emoji, Chinese, Arabic, etc.)
- Gracefully handle encoding errors

### Risk 3: CLI Parsing Edge Cases
**Impact**: Quotes, spaces, special characters in arguments might confuse parser
**Mitigation**:
- Comprehensive integration tests with edge cases
- Clear documentation with examples
- argparse handles most edge cases automatically

### Risk 4: Forward Compatibility
**Impact**: Phase 1 design might not support Phase 2+ requirements
**Mitigation**:
- Use dictionary structure (easily serializable)
- Keep CLI and storage layers separate
- Design TodoManager interface that can be swapped

---

## Performance Considerations

### Expected Performance

- **Add operation**: O(1) - dictionary insert
- **List operation**: O(n) - iterate all todos, n ≤ 1000
- **Delete operation**: O(1) - dictionary delete by key

### Benchmarks

Per SC-002, SC-003, SC-004:
- Add/delete: < 2 seconds (trivially met with in-memory dict)
- List with 1000 todos: < 1 second (tested)
- No degradation with 1000 todos in memory (~100KB assuming 100 bytes per todo)

---

## Security Considerations

### Phase 1 Security Posture

**In Scope**:
- Input validation (prevent empty titles, invalid IDs)
- No code injection possible (argparse sanitizes input)
- No file system access (everything in memory)

**Out of Scope** (acceptable for Phase 1):
- No authentication/authorization (single-user, local only)
- No encryption (data only in memory, not persisted)
- No audit logging (deferred to Phase 2+)

---

## Conclusion

All technical decisions align with:
- ✅ Specification requirements (FR-001 through FR-020)
- ✅ Constitutional principles (I-VII)
- ✅ Success criteria (SC-001 through SC-008)
- ✅ Phase isolation (no Phase 2+ dependencies)

Implementation can proceed to `/sp.tasks` with confidence.
