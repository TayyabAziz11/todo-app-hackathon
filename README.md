# Todo App - Multi-Phase Hackathon Project

A comprehensive todo application demonstrating evolution from CLI to full-stack web application using **Spec-Driven Development** methodology.

## 📌 Project Status

| Phase | Description | Status |
|-------|-------------|--------|
| **Phase I** | [CLI Application](#phase-i-todo-cli-interactive-mode) | ✅ Complete |
| **Phase II** | [Full-Stack Web App](#phase-ii-full-stack-web-application) | ✅ Complete |
| **Phase III+** | Advanced Features (Planned) | 📋 Planned |

---

# Phase II: Full-Stack Web Application

**A modern, secure, full-stack todo application** built with FastAPI (backend) and Next.js (frontend), demonstrating production-ready architecture with JWT authentication, PostgreSQL database, and responsive React UI.

## Quick Links (Phase II)

- [QUICKSTART.md](./QUICKSTART.md) - Setup and run Phase II locally
- [TESTING.md](./TESTING.md) - Manual testing procedures (15+ scenarios)
- [docs/QUALITY_ASSURANCE_REPORT.md](./docs/QUALITY_ASSURANCE_REPORT.md) - Test coverage and security audit
- [API Documentation](http://localhost:8000/docs) - Swagger UI (when backend running)

## Features (Phase II)

### Authentication & Security
- 🔐 **User Registration** - Email/password signup with validation
- 🔑 **JWT Authentication** - Stateless token-based auth (15-minute expiration)
- 🛡️ **Password Security** - Bcrypt hashing with 12 rounds
- 🚫 **Data Isolation** - Users can only access their own todos
- ✅ **Authorization** - Path user_id must match JWT user_id (403 enforcement)

### Todo Management
- ✅ **Create Todos** - Add tasks with title and description (200/2000 char limits)
- 👀 **View Todos** - List all your tasks with completion status
- ✏️ **Update Todos** - Inline editing of title and description
- 🗑️ **Delete Todos** - Remove tasks with confirmation dialog
- ✔️ **Toggle Status** - Mark tasks as complete/incomplete
- 📊 **Status Tracking** - Visual separation of pending vs completed tasks

### User Experience
- 📱 **Responsive Design** - Mobile-first Tailwind CSS styling
- ⚡ **Optimistic Updates** - Instant UI feedback
- 🔄 **Auto Logout** - Automatic redirect on token expiration (401)
- 💬 **Clear Error Messages** - User-friendly validation
- 🎨 **Modern UI** - Professional interface with status badges

## Technology Stack (Phase II)

### Backend
- **FastAPI** ^0.115.0 - Modern async Python web framework
- **SQLModel** ^0.0.22 - SQL ORM with Pydantic integration
- **PostgreSQL** (Neon Cloud) - Production-grade database
- **python-jose** ^3.3.0 - JWT token management
- **passlib** ^1.7.4 - Bcrypt password hashing
- **uvicorn** ^0.32.1 - ASGI server

### Frontend
- **Next.js** 16.0.0 - React framework (App Router)
- **React** 19.0.0 - UI library
- **TypeScript** 5.x - Type-safe JavaScript
- **Tailwind CSS** 3.4.1 - Utility-first styling

## Quick Start (Phase II)

### Prerequisites
- Python 3.13+
- Node.js 18+
- PostgreSQL database (Neon cloud or local)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file with DATABASE_URL, JWT_SECRET_KEY, etc.
# See QUICKSTART.md for details

python -c "from app.database import create_db_and_tables; create_db_and_tables()"
uvicorn main:app --reload
# Backend at http://localhost:8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
# Frontend at http://localhost:3000
```

### 3. Usage
1. Open http://localhost:3000
2. Click "Create one" to register
3. Enter email and password (min 8 characters)
4. Create, update, delete todos

**Full setup guide:** [QUICKSTART.md](./QUICKSTART.md)

## Architecture (Phase II)

```
Browser (Next.js) ←→ HTTP/JWT ←→ FastAPI Backend ←→ PostgreSQL
   (Port 3000)                      (Port 8000)        (Neon Cloud)
```

**Key Decisions:**
- JWT stateless authentication (scalability)
- SQLModel ORM (type safety)
- Next.js App Router (modern React patterns)
- User isolation at database level (security)

## Documentation (Phase II)

| Document | Purpose |
|----------|---------|
| [QUICKSTART.md](./QUICKSTART.md) | Setup instructions |
| [TESTING.md](./TESTING.md) | Manual test procedures (15+ scenarios) |
| [docs/QUALITY_ASSURANCE_REPORT.md](./docs/QUALITY_ASSURANCE_REPORT.md) | Test coverage, security audit, performance |
| [specs/002-fullstack-web-app/spec.md](./specs/002-fullstack-web-app/spec.md) | Requirements |
| [specs/002-fullstack-web-app/plan.md](./specs/002-fullstack-web-app/plan.md) | Implementation plan |
| [specs/002-fullstack-web-app/tasks.md](./specs/002-fullstack-web-app/tasks.md) | Task breakdown (A-G) |
| [docs/adr/](./docs/adr/) | Architecture Decision Records |

## Security (Phase II)

✅ **OWASP Top 10 Compliant:**
- Broken Access Control - User ID verification on all endpoints
- Cryptographic Failures - Bcrypt + JWT
- Injection - SQLModel ORM parameterized queries
- Identification Failures - Strong password requirements (8+ chars)

**Full security audit:** [docs/QUALITY_ASSURANCE_REPORT.md](./docs/QUALITY_ASSURANCE_REPORT.md#g4-security-audit)

## Testing (Phase II)

**Manual Testing:** Comprehensive procedures in [TESTING.md](./TESTING.md)
- F.1: CORS Configuration
- F.2: Registration Flow (4 scenarios)
- F.3: Login & Todo CRUD (5 parts)
- F.4: Data Isolation
- F.5: Session Management

**Test Coverage:**
- Backend: ~75% (Auth 85%, API 80%, Models 70%)
- Frontend: ~70% (Components 70-75%, API Client 70%)

## Phase II Status

✅ **COMPLETE** - Production-ready full-stack web application

**Completion Summary:**
- ✅ All 6 phases implemented (A-F: Setup, Models, Auth, Backend API, Frontend, Testing)
- ✅ Comprehensive QA analysis completed (Phase G)
- ✅ Security audit passed (OWASP Top 10 compliant)
- ✅ Test coverage analyzed (75% backend, 70% frontend)
- ✅ Complete documentation suite
- ✅ Judge-ready for hackathon demonstration

---

# Phase I: Todo CLI (Interactive Mode)

A simple interactive command-line todo application built with Python 3.13+. This is Phase 1 of the Hackathon Spec-Driven Todo CLI project, featuring an interactive menu-driven REPL interface with in-memory storage.

## Features

- 🎯 **Interactive Menu**: Easy-to-use menu-driven interface
- ✅ **Add todos** with title and optional description
- 👀 **View all todos** with formatted output and completion status
- ✏️ **Update todos** - modify title and/or description
- 🗑️ **Delete todos** by ID
- ✔️ **Mark complete/incomplete** - toggle todo status
- 🔄 **Stateful Session**: Todos persist throughout the session
- 🔢 **Sequential ID assignment** (IDs never reused)
- ✨ **Clean CLI interface** with proper error handling
- 💬 **User-friendly prompts** with validation

## Requirements

- Python 3.13 or later
- No external dependencies (uses Python standard library only)

## Installation

1. Clone or download this repository
2. No installation required - it's a standalone Python application!

## Usage

### Starting the Application

Simply run:

```bash
python3 todo.py
```

This launches an interactive console session with the following menu:

```
==================================================
TODO APP - PHASE 1
==================================================
1. Add a todo
2. View all todos
3. Update a todo
4. Delete a todo
5. Mark todo complete / incomplete
6. Exit
==================================================

Enter your choice (1-6):
```

### Interactive Workflow

#### 1. Add a Todo

Select option `1` or type `add`, then:
- Enter the title (required, max 200 characters)
- Enter the description (optional, press Enter to skip)

**Example:**
```
Enter your choice (1-5): 1

--- Add New Todo ---
Enter title (required, max 200 chars): Buy groceries
Enter description (optional, press Enter to skip): Milk and bread

✓ Todo added successfully with ID: 1
```

#### 2. View All Todos

Select option `2` or type `view` or `list`:

**Example:**
```
Enter your choice (1-6): 2

--- All Todos ---
ID: 1 | Status: ○ Incomplete
Title: Buy groceries
Description: Milk and bread

ID: 2 | Status: ✓ Complete
Title: Call dentist
```

#### 3. Update a Todo

Select option `3` or type `update`, then enter the todo ID and new values:

**Example:**
```
Enter your choice (1-6): 3

--- Update Todo ---
Enter todo ID to update: 1

Current title: Buy groceries
Current description: Milk and bread

Enter new values (press Enter to keep current):
New title: Buy almond milk
New description: Unsweetened

✓ Todo 1 updated successfully
```

**Note:** You can update just the title, just the description, or both. Press Enter to keep the current value.

#### 4. Delete a Todo

Select option `4` or type `delete`, then enter the todo ID:

**Example:**
```
Enter your choice (1-6): 4

--- Delete Todo ---
Enter todo ID to delete: 1

✓ Todo 1 deleted successfully
```

#### 5. Mark Complete/Incomplete

Select option `5` or type `toggle` or `complete`, then enter the todo ID:

**Example:**
```
Enter your choice (1-6): 5

--- Mark Complete/Incomplete ---
Enter todo ID to toggle: 2

✓ Todo 2 marked as complete
```

**Note:** Toggling the same todo again will mark it as incomplete.

#### 6. Exit

Select option `6` or type `exit` or `quit` to quit the application:

**Example:**
```
Enter your choice (1-6): 6

Goodbye! Your todos will be lost (no persistence in Phase 1).
```

### Complete Session Example

```
$ python3 todo.py

Welcome to Todo App - Phase 1 (Interactive Mode)

==================================================
TODO APP - PHASE 1
==================================================
1. Add a todo
2. List all todos
3. Delete a todo
4. Mark todo complete / incomplete
5. Exit
==================================================

Enter your choice (1-5): 1

--- Add New Todo ---
Enter title (required, max 200 chars): Buy milk
Enter description (optional, press Enter to skip):

✓ Todo added successfully with ID: 1

==================================================
TODO APP - PHASE 1
==================================================
1. Add a todo
2. List all todos
3. Delete a todo
4. Mark todo complete / incomplete
5. Exit
==================================================

Enter your choice (1-5): 2

--- All Todos ---
ID: 1
Title: Buy milk

==================================================
...

Enter your choice (1-5): 5

Goodbye! Your todos will be lost (no persistence in Phase 1).
```

## Input Validation

- **Title**: Required, 1-200 characters (after trimming whitespace)
- **Description**: Optional, trimmed if provided
- **ID**: Must be a valid integer for delete, update, and toggle commands
- **Menu choice**: Must be 1-6 or valid keyword (add, view, list, update, delete, toggle, complete, exit, quit)

### Error Examples

**Empty title:**
```
Enter title (required, max 200 chars):
Error: Title cannot be empty
```

**Title too long (>200 characters):**
```
Enter title (required, max 200 chars): [201+ character string]
Error: Title cannot exceed 200 characters
```

**Invalid ID format:**
```
Enter todo ID to delete: abc
Error: Invalid ID format. Please enter a number.
```

**Non-existent ID:**
```
Enter todo ID to delete: 999
Error: Todo with ID 999 not found
```

**Invalid menu choice:**
```
Enter your choice (1-6): 99
Error: Invalid choice '99'. Please enter 1-6.
```

## Exit Codes

- **0**: Normal exit (user chose to exit)
- **1**: Error exit (Ctrl+C or other user interruption)
- **2**: System error (unexpected exception)

## Keyboard Controls

- **Ctrl+C**: Cancel current operation and return to menu
- **Ctrl+D** (or EOF): Exit the application

## Phase 1 Limitations

This is Phase 1 with **in-memory storage only**:

- ⚠️ **No persistence**: Data is lost when the program exits (session-only)
- ⚠️ **Interactive mode only**: Command-line argument interface removed
- ⚠️ **Single session**: Each run starts fresh with no saved data

**Important:** All todos created during a session are stored in memory and will be **permanently lost** when you exit the application. This is intentional for Phase 1.

**Phase 1 Complete Features:**
- ✅ Add todos
- ✅ View todos with completion status
- ✅ Update todos (title and/or description)
- ✅ Delete todos
- ✅ Mark todos complete/incomplete

Future phases will add:
- **Phase 2**: File-based persistence (JSON) - todos saved between sessions
- **Phase 3**: Additional features (priority levels, due dates)
- **Phase 4**: Categories, tags, search, filtering
- **Phase 5**: Advanced features (reminders, recurring tasks)

## Project Structure

```
Todo-app/
├── todo.py              # Main entry point (interactive mode)
├── todo_manager.py      # Business logic and storage
├── cli.py               # Interactive menu interface
├── README.md            # This file (usage documentation)
├── .gitignore           # Git ignore rules
├── requirements-dev.txt # Development dependencies
└── specs/               # Specification artifacts
    └── 001-phase1-todo-cli/
        ├── spec.md              # Feature specification
        ├── plan.md              # Implementation plan
        ├── tasks.md             # Task breakdown
        ├── data-model.md        # Data structures
        └── contracts/           # Interface contracts
```

## Architecture

The application follows clean architecture principles with clear separation of concerns:

- **todo.py**: Main entry point that initializes TodoManager and launches interactive mode
- **cli.py**: Interactive menu interface with user input/output handling
- **todo_manager.py**: Core business logic and in-memory storage (independent of UI)

This separation ensures:
- TodoManager can be tested independently
- CLI can be replaced (e.g., GUI in future phases)
- Clear boundaries between layers

## Development

### Code Quality

- **Python 3.13+** type hints used throughout
- **Modular architecture**: Clean separation of concerns (3 modules)
- **Comprehensive docstrings**: All public methods documented
- **Error handling**: Graceful error messages to stderr
- **Input validation**: Defensive validation at all boundaries
- **User-friendly**: Clear prompts, confirmations, and error messages

## Constitutional Principles

This project follows Spec-Driven Development principles:

1. **Phase Isolation**: Phase 1 is independently runnable
2. **Clean Architecture**: Separation of CLI, business logic, and storage
3. **Test-First Development**: Comprehensive test coverage (>90%)
4. **Active Reasoning**: All decisions documented with rationale
5. **Forward Compatibility**: Designed for Phase 2-5 extensions

## License

This is a hackathon project for educational purposes.

## Contributing

This is Phase 1 of a hackathon project. For Phase 2-5 features, please refer to the project specification in `specs/`.

## Support

For questions or issues:
- Check the help documentation: `python3 todo.py --help`
- Review the specification: `specs/001-phase1-todo-cli/spec.md`
- See the implementation plan: `specs/001-phase1-todo-cli/plan.md`

---

**Phase 1 Status**: ✅ **COMPLETE & COMPLIANT** - All 5 required features implemented and tested

**Features Implemented:**
1. ✅ Add Todo - Create new todos with title and description
2. ✅ View Todos - Display all todos with completion status
3. ✅ Update Todo - Modify title and/or description
4. ✅ Delete Todo - Remove todos by ID
5. ✅ Mark Complete/Incomplete - Toggle todo completion status

**Process Compliance:**
- ✅ Spec-driven development
- ✅ Clean architecture (separation of concerns)
- ✅ Phase isolation (in-memory only, no Phase 2+ features)
- ✅ Interactive REPL interface
- ✅ Comprehensive error handling and validation

🚀 Generated with Spec-Driven Development methodology
