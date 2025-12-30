# Data Model: Phase 1 - In-Memory Todo CLI

**Feature**: 001-phase1-todo-cli
**Created**: 2025-12-29
**Purpose**: Define data structures and validation rules for Phase 1 implementation

---

## Entities

### Todo

**Description**: Represents a single task item with unique identifier, title, and optional description

**Fields**:

| Field | Type | Required | Constraints | Default | Description |
|-------|------|----------|-------------|---------|-------------|
| id | integer | Yes | Unique, sequential, > 0 | Auto-assigned | Unique identifier for the todo |
| title | string | Yes | 1-200 characters, trimmed | None | Short description of the task |
| description | string or None | No | Trimmed if provided | None | Optional detailed description |

**Validation Rules**:

1. **ID Validation**:
   - MUST be a positive integer (> 0)
   - MUST be unique across all todos
   - MUST be sequential (no gaps allowed during creation, but gaps okay after deletion)
   - MUST NOT be reused after deletion

2. **Title Validation**:
   - MUST NOT be empty string
   - MUST NOT be whitespace-only
   - MUST be ≤ 200 characters after trimming
   - Leading and trailing whitespace MUST be trimmed before storage
   - Internal whitespace is preserved

3. **Description Validation**:
   - MAY be None (null)
   - Leading and trailing whitespace MUST be trimmed if provided
   - No length limit (within reasonable memory constraints)
   - Internal whitespace is preserved

**Invariants**:
- Every todo MUST have a unique ID
- Every todo MUST have a non-empty title after trimming
- ID sequence MUST always increment (never decrement)

---

## Data Structures

### In-Memory Storage

**Structure**: Python dictionary with integer keys

```python
# Type: Dict[int, Dict[str, Any]]
{
    1: {
        "id": 1,
        "title": "Buy groceries",
        "description": "Milk and bread"
    },
    2: {
        "id": 2,
        "title": "Call mom",
        "description": None
    },
    3: {
        "id": 3,
        "title": "Finish report",
        "description": "Q4 summary"
    }
}
```

**Rationale**:
- O(1) lookup by ID
- Simple to iterate for list operation
- Easily serializable to JSON for Phase 2
- Minimal memory overhead

### ID Counter

**Structure**: Integer variable tracking next available ID

```python
# Type: int
next_id: int = 1  # Always increments, never decrements
```

**Behavior**:
- Initialized to 1 when application starts
- Incremented after each todo creation
- Never decremented (even after deletions)
- Lost when application exits (Phase 1 limitation)

---

## State Transitions

### Todo Lifecycle

```
[Non-existent]
     ↓
   [Create] (add command)
     ↓
 [Active] ←→ [Active] (list command - read-only)
     ↓
  [Delete] (delete command)
     ↓
[Non-existent]
```

**States**:
1. **Non-existent**: Todo does not exist in storage
2. **Active**: Todo exists in storage and can be listed/deleted
3. **Deleted**: Todo removed from storage, ID not reused

**Transitions**:
- **Create**: Non-existent → Active (add command)
- **Read**: Active → Active (list command, no state change)
- **Delete**: Active → Non-existent (delete command)

**Phase 1 Constraints**:
- No "update" transition (deferred to Phase 3)
- No "complete" status (deferred to Phase 3)
- No persistence across application restarts

---

## Validation Examples

### Valid Todos

```python
# Minimal valid todo
{
    "id": 1,
    "title": "Buy milk",
    "description": None
}

# Todo with description
{
    "id": 2,
    "title": "Call dentist",
    "description": "Schedule annual checkup"
}

# Todo with Unicode characters
{
    "id": 3,
    "title": "学习中文",  # "Learn Chinese" in Chinese
    "description": "Practice writing characters ✏️"
}

# Title at max length (200 characters)
{
    "id": 4,
    "title": "A" * 200,
    "description": None
}
```

### Invalid Todos (Validation Failures)

```python
# Empty title (INVALID)
{
    "id": 5,
    "title": "",
    "description": "This should fail"
}
# Error: "Title cannot be empty"

# Whitespace-only title (INVALID)
{
    "id": 6,
    "title": "   ",
    "description": "This should also fail"
}
# Error: "Title cannot be empty"

# Title exceeds 200 characters (INVALID)
{
    "id": 7,
    "title": "A" * 201,
    "description": None
}
# Error: "Title cannot exceed 200 characters"

# Non-integer ID (INVALID)
{
    "id": "abc",
    "title": "Invalid ID",
    "description": None
}
# Error: "Invalid ID format"
```

---

## Data Access Patterns

### Add Todo

**Input**: title (string), description (string or None)
**Process**:
1. Trim title and description
2. Validate title (not empty, ≤ 200 chars)
3. Assign next available ID
4. Increment ID counter
5. Store todo in dictionary
6. Return assigned ID

**Output**: Assigned ID (integer)

**Complexity**: O(1)

---

### List All Todos

**Input**: None
**Process**:
1. Retrieve all todos from dictionary
2. Sort by ID (ascending)
3. Format for display

**Output**: List of all todos sorted by ID

**Complexity**: O(n log n) for sorting, where n = number of todos

**Optimization Note**: For Phase 1 with ≤ 1000 todos, sorting overhead is negligible

---

### Delete Todo

**Input**: ID (integer)
**Process**:
1. Validate ID is integer
2. Check if ID exists in storage
3. Remove todo from dictionary
4. Return confirmation

**Output**: Confirmation message

**Complexity**: O(1)

**Note**: ID is never reused even after deletion

---

## Memory Footprint

### Estimation

**Per Todo**:
- ID: ~28 bytes (Python int object)
- Title: ~50-250 bytes (average ~100 bytes)
- Description: ~0-1000 bytes (average ~100 bytes if provided)
- Dictionary overhead: ~48 bytes per entry

**Total per todo**: ~250 bytes average

**For 1000 todos**: ~250 KB
**For 10,000 todos**: ~2.5 MB

**Conclusion**: Memory is not a concern for Phase 1 (target ≤ 1000 todos per SC-004)

---

## Forward Compatibility (Phase 2+)

### JSON Serialization

Current structure easily converts to JSON:

```json
{
    "next_id": 4,
    "todos": {
        "1": {
            "id": 1,
            "title": "Buy groceries",
            "description": "Milk and bread"
        },
        "2": {
            "id": 2,
            "title": "Call mom",
            "description": null
        },
        "3": {
            "id": 3,
            "title": "Finish report",
            "description": "Q4 summary"
        }
    }
}
```

### Database Schema (Phase 3+)

```sql
CREATE TABLE todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Migration Path**: Current in-memory structure maps directly to database columns

---

## Constraints Summary

### Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-001 | Todo IDs must be unique | Check before insert (guaranteed by dict key) |
| BR-002 | Todo IDs must be sequential during creation | Increment-only counter |
| BR-003 | Deleted IDs are never reused | Counter never decrements |
| BR-004 | Title must be non-empty after trimming | Validation before insert |
| BR-005 | Title must be ≤ 200 characters | Validation before insert |
| BR-006 | Whitespace must be trimmed | Automatic trim on input |

### Technical Constraints

| Constraint | Description | Phase 1 Implementation |
|------------|-------------|------------------------|
| TC-001 | In-memory storage only | Python dictionary |
| TC-002 | Single-user, single-process | No concurrency control needed |
| TC-003 | No persistence across restarts | Acceptable for Phase 1 |
| TC-004 | Maximum ~10,000 todos | Memory limit, not enforced |
| TC-005 | UTF-8 character encoding | Python 3.13 default |

---

## Error Handling

### Validation Errors

| Error Code | Condition | User Message | Exit Code |
|------------|-----------|--------------|-----------|
| VAL-001 | Empty title | "Title cannot be empty" | 1 |
| VAL-002 | Title too long | "Title cannot exceed 200 characters" | 1 |
| VAL-003 | Invalid ID format | "Invalid ID format. Please provide a number." | 1 |
| VAL-004 | ID not found | "Todo with ID {id} not found" | 1 |

### System Errors

| Error Code | Condition | User Message | Exit Code |
|------------|-----------|--------------|-----------|
| SYS-001 | Unexpected exception | "An unexpected error occurred: {error}" | 2 |
| SYS-002 | Memory exhausted | "System out of memory" | 2 |

---

## Testing Implications

### Unit Test Coverage

**TodoManager Tests**:
- ✅ Add valid todo
- ✅ Add todo with description
- ✅ Add todo without description
- ✅ Reject empty title
- ✅ Reject whitespace-only title
- ✅ Reject title > 200 characters
- ✅ Trim whitespace from title
- ✅ Trim whitespace from description
- ✅ Assign sequential IDs
- ✅ List todos (empty)
- ✅ List todos (multiple)
- ✅ Delete todo by ID
- ✅ Reject delete of non-existent ID
- ✅ Never reuse deleted IDs

### Performance Tests

- ✅ Add 1000 todos < 1 second
- ✅ List 1000 todos < 1 second
- ✅ Delete from 1000 todos < 1 second

### Edge Case Tests

- ✅ Unicode characters in title/description
- ✅ Special characters (quotes, newlines, etc.)
- ✅ Maximum length title (exactly 200 characters)
- ✅ Identical titles (should be allowed, different IDs)

---

## Conclusion

This data model:
- ✅ Satisfies all functional requirements (FR-001 through FR-020)
- ✅ Supports all user stories and acceptance scenarios
- ✅ Meets performance requirements (SC-001 through SC-004)
- ✅ Maintains phase isolation (no Phase 2+ dependencies)
- ✅ Provides forward compatibility for future phases
- ✅ Enables comprehensive testing

Ready for implementation in `/sp.tasks` and `/sp.implement`.
