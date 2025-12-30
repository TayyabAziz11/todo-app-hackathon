# CLI Interface Contract: Phase 1 - Todo CLI

**Feature**: 001-phase1-todo-cli
**Created**: 2025-12-29
**Purpose**: Define command-line interface contracts and behaviors

---

## Command Structure

### General Format

```
python todo.py <command> [arguments] [options]
```

### Exit Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 0 | Success | Command completed successfully |
| 1 | User error | Invalid input, validation failure |
| 2 | System error | Unexpected error, crash |

### Output Streams

- **stdout**: Success messages, todo listings, help text
- **stderr**: Error messages, warnings

---

## Commands

### 1. Add Command

**Purpose**: Create a new todo with title and optional description

**Syntax**:
```bash
python todo.py add <title> [--description <text>]
python todo.py add <title> [-d <text>]
```

**Arguments**:

| Argument | Type | Required | Constraints | Description |
|----------|------|----------|-------------|-------------|
| title | string | Yes | 1-200 chars, non-empty after trim | Todo title |
| --description, -d | string | No | Trimmed if provided | Todo description |

**Success Output** (stdout):
```
Todo added with ID: {id}
```

**Error Outputs** (stderr):

| Condition | Message | Exit Code |
|-----------|---------|-----------|
| Empty title | `Error: Title cannot be empty` | 1 |
| Title too long | `Error: Title cannot exceed 200 characters` | 1 |
| Missing title | `Error: Title is required` | 1 |

**Examples**:

```bash
# Add todo with title only
$ python todo.py add "Buy groceries"
Todo added with ID: 1

# Add todo with description
$ python todo.py add "Call dentist" --description "Schedule annual checkup"
Todo added with ID: 2

# Short form
$ python todo.py add "Finish report" -d "Q4 summary"
Todo added with ID: 3

# Error: empty title
$ python todo.py add ""
Error: Title cannot be empty
$ echo $?
1

# Error: title too long
$ python todo.py add "$(python -c 'print("A" * 201)')"
Error: Title cannot exceed 200 characters
$ echo $?
1
```

**Contract Tests**:
- ✅ Add with title only → success, ID returned
- ✅ Add with title and description → success, both stored
- ✅ Add with empty title → error, exit code 1
- ✅ Add with whitespace-only title → error, exit code 1
- ✅ Add with title > 200 chars → error, exit code 1
- ✅ Whitespace trimmed from title and description

---

### 2. List Command

**Purpose**: Display all todos with their IDs, titles, and descriptions

**Syntax**:
```bash
python todo.py list
```

**Arguments**: None

**Success Output** (stdout):

**When todos exist**:
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

**When no todos exist**:
```
No todos found
```

**Error Outputs**: None (list never fails)

**Formatting Rules**:
- Todos sorted by ID (ascending)
- Each todo separated by blank line
- "ID:", "Title:", "Description:" labels
- Description only shown if provided (not None)
- UTF-8 encoding for special characters

**Examples**:

```bash
# List with multiple todos
$ python todo.py list
ID: 1
Title: Buy groceries
Description: Milk and bread

ID: 2
Title: Call mom

# List when empty
$ python todo.py list
No todos found

# List after adding todos with Unicode
$ python todo.py add "学习中文" -d "Practice writing ✏️"
Todo added with ID: 4
$ python todo.py list
ID: 1
Title: Buy groceries
Description: Milk and bread

ID: 4
Title: 学习中文
Description: Practice writing ✏️
```

**Contract Tests**:
- ✅ List empty todos → "No todos found"
- ✅ List single todo → formatted correctly
- ✅ List multiple todos → sorted by ID
- ✅ List todos with/without descriptions → formatted correctly
- ✅ Unicode characters display correctly

---

### 3. Delete Command

**Purpose**: Remove a todo by its ID

**Syntax**:
```bash
python todo.py delete <id>
```

**Arguments**:

| Argument | Type | Required | Constraints | Description |
|----------|------|----------|-------------|-------------|
| id | integer | Yes | Must exist | ID of todo to delete |

**Success Output** (stdout):
```
Todo {id} deleted
```

**Error Outputs** (stderr):

| Condition | Message | Exit Code |
|-----------|---------|-----------|
| ID not found | `Error: Todo with ID {id} not found` | 1 |
| Invalid ID format | `Error: Invalid ID format. Please provide a number.` | 1 |
| Missing ID | `Error: Todo ID required` | 1 |

**Examples**:

```bash
# Successful deletion
$ python todo.py delete 2
Todo 2 deleted

# Error: ID not found
$ python todo.py delete 999
Error: Todo with ID 999 not found
$ echo $?
1

# Error: invalid ID format
$ python todo.py delete abc
Error: Invalid ID format. Please provide a number.
$ echo $?
1

# Error: missing ID
$ python todo.py delete
Error: Todo ID required
$ echo $?
1
```

**Behavior Notes**:
- Deleted IDs are never reused
- ID counter continues to increment
- Deleting non-existent ID is an error (idempotency not required for Phase 1)

**Contract Tests**:
- ✅ Delete existing todo → success, confirmation message
- ✅ Delete non-existent ID → error, exit code 1
- ✅ Delete with invalid ID format → error, exit code 1
- ✅ Delete without ID → error, exit code 1
- ✅ Deleted IDs not reused in subsequent adds

---

### 4. Help Command

**Purpose**: Display usage information and command documentation

**Syntax**:
```bash
python todo.py --help
python todo.py -h
python todo.py help
python todo.py <command> --help
```

**Arguments**: Optional command name for command-specific help

**Success Output** (stdout):

**Main help**:
```
usage: todo.py [-h] {add,list,delete,help} ...

Todo CLI - Manage your todos from the command line

positional arguments:
  {add,list,delete,help}
    add                 Add a new todo
    list                List all todos
    delete              Delete a todo by ID
    help                Show this help message

options:
  -h, --help            show this help message and exit

Examples:
  python todo.py add "Buy groceries"
  python todo.py add "Call dentist" --description "Annual checkup"
  python todo.py list
  python todo.py delete 1
```

**Command-specific help** (e.g., `python todo.py add --help`):
```
usage: todo.py add [-h] [-d DESCRIPTION] title

Add a new todo

positional arguments:
  title                 Todo title (required, max 200 characters)

options:
  -h, --help            show this help message and exit
  -d DESCRIPTION, --description DESCRIPTION
                        Todo description (optional)

Examples:
  python todo.py add "Buy groceries"
  python todo.py add "Call dentist" -d "Annual checkup"
```

**Error Outputs**: None (help never fails)

**Contract Tests**:
- ✅ Main help displays all commands
- ✅ Command-specific help displays arguments and options
- ✅ Help includes examples
- ✅ --help and -h both work
- ✅ Help exits with code 0

---

### 5. No Arguments / Invalid Command

**Purpose**: Handle cases where user runs CLI without arguments or with invalid command

**Syntax**:
```bash
python todo.py
python todo.py invalid-command
```

**Output** (stdout):
```
usage: todo.py [-h] {add,list,delete,help} ...
todo.py: error: invalid choice: 'invalid-command' (choose from 'add', 'list', 'delete', 'help')

Use 'python todo.py --help' for usage information.
```

**Exit Code**: 1 (user error)

**Examples**:

```bash
# No arguments
$ python todo.py
usage: todo.py [-h] {add,list,delete,help} ...
Use 'python todo.py --help' for usage information.
$ echo $?
1

# Invalid command
$ python todo.py invalid
todo.py: error: invalid choice: 'invalid' (choose from 'add', 'list', 'delete', 'help')
$ echo $?
1
```

---

## Data Flow

### Add Command Flow

```
User Input → CLI Parser → Validation → TodoManager.add() → Success Message
                              ↓
                           Error Message (if validation fails)
```

### List Command Flow

```
User Input → CLI Parser → TodoManager.list() → Format Output → Display
```

### Delete Command Flow

```
User Input → CLI Parser → Validation → TodoManager.delete() → Success Message
                              ↓                    ↓
                         Error Message      Error Message (if ID not found)
```

---

## Error Handling Strategy

### Validation Layer (CLI)

**Responsibilities**:
- Parse arguments
- Validate argument types
- Validate argument formats
- Provide clear error messages

**Errors Handled**:
- Missing required arguments
- Invalid argument types
- Invalid argument formats

### Business Logic Layer (TodoManager)

**Responsibilities**:
- Validate business rules
- Perform operations
- Return results or raise exceptions

**Errors Handled**:
- Empty/whitespace title
- Title too long
- ID not found

### Error Message Format

```
Error: {what went wrong}
{optional context or suggestion}
```

**Consistency**: All error messages start with "Error:" for easy parsing/testing

---

## Performance Requirements

| Operation | Max Time | Measured Against |
|-----------|----------|------------------|
| Add | < 2 seconds | SC-001 |
| List (1000 todos) | < 1 second | SC-002 |
| Delete | < 2 seconds | SC-003 |

**Note**: All operations are O(1) or O(n) with small n, trivially meeting requirements

---

## Character Encoding

### Input

- Accept UTF-8 encoded arguments
- Handle Unicode characters in titles/descriptions
- Preserve special characters (except whitespace trimming)

### Output

- Display UTF-8 encoded text
- Handle encoding errors gracefully (replace with '?' if terminal doesn't support)

### Edge Cases

```bash
# Emoji
$ python todo.py add "Buy 🥛 and 🍞"
Todo added with ID: 1

# Chinese characters
$ python todo.py add "学习中文"
Todo added with ID: 2

# Arabic text (RTL)
$ python todo.py add "مرحبا بك"
Todo added with ID: 3

# All work in list view
$ python todo.py list
ID: 1
Title: Buy 🥛 and 🍞

ID: 2
Title: 学习中文

ID: 3
Title: مرحبا بك
```

---

## Backward Compatibility

### Phase 1 → Phase 2

When adding persistence in Phase 2:
- All Phase 1 commands remain unchanged
- CLI interface stays the same
- Only internal storage mechanism changes

**No breaking changes to CLI contract**

---

## Testing Contract

### CLI Integration Tests

**Required Test Cases**:

1. **Add Command**:
   - ✅ Add with title only
   - ✅ Add with title and description
   - ✅ Add with empty title (error)
   - ✅ Add with long title (error)
   - ✅ Add with Unicode characters

2. **List Command**:
   - ✅ List empty
   - ✅ List single todo
   - ✅ List multiple todos (sorted by ID)
   - ✅ List with/without descriptions

3. **Delete Command**:
   - ✅ Delete existing todo
   - ✅ Delete non-existent ID (error)
   - ✅ Delete with invalid ID format (error)

4. **Help Command**:
   - ✅ Main help
   - ✅ Command-specific help
   - ✅ --help and -h variants

5. **Edge Cases**:
   - ✅ No arguments
   - ✅ Invalid command
   - ✅ Special characters
   - ✅ Rapid sequential operations

### Test Execution

```bash
# Run all CLI integration tests
pytest tests/test_cli_integration.py -v

# Run with coverage
pytest tests/test_cli_integration.py --cov=todo --cov-report=html
```

---

## Implementation Notes

### Argument Parser Configuration

```python
import argparse

parser = argparse.ArgumentParser(
    prog='todo.py',
    description='Todo CLI - Manage your todos from the command line'
)

subparsers = parser.add_subparsers(dest='command', required=True)

# Add command
add_parser = subparsers.add_parser('add', help='Add a new todo')
add_parser.add_argument('title', help='Todo title (required, max 200 characters)')
add_parser.add_argument('-d', '--description', help='Todo description (optional)')

# List command
list_parser = subparsers.add_parser('list', help='List all todos')

# Delete command
delete_parser = subparsers.add_parser('delete', help='Delete a todo by ID')
delete_parser.add_argument('id', type=int, help='ID of todo to delete')

# Help command
help_parser = subparsers.add_parser('help', help='Show this help message')
```

---

## Conclusion

This CLI interface contract:
- ✅ Satisfies all functional requirements
- ✅ Provides clear, consistent user experience
- ✅ Handles all error cases gracefully
- ✅ Supports comprehensive testing
- ✅ Maintains forward compatibility with Phase 2+

Ready for implementation in `/sp.tasks` and `/sp.implement`.
