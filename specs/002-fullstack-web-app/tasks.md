# Implementation Tasks: Phase II – Todo Full-Stack Web Application

**Feature Branch**: `002-fullstack-web-app`
**Created**: 2025-12-30
**Status**: Ready for Implementation
**References**:
- Specification: [@specs/002-fullstack-web-app/spec.md](./spec.md)
- Plan: [@specs/002-fullstack-web-app/plan.md](./plan.md)

---

## Task Execution Guidelines

### Execution Process
1. Execute tasks in order (respect dependencies)
2. Validate completion criteria before marking task complete
3. Create PHR for significant implementation milestones
4. Run tests after each task where applicable
5. Commit atomically per task or logical task group

### Task Status Tracking
- **PENDING**: Not started
- **IN_PROGRESS**: Currently being worked on
- **COMPLETED**: All completion criteria met
- **BLOCKED**: Waiting on dependency or external input

### Agent Assignment
Each task specifies a **Responsible Agent** from:
- `fullstack-spec-architect`: Cross-layer architecture validation
- `auth-security-architect`: Authentication and security implementation
- `fastapi-backend-architect`: Backend API and database implementation
- `nextjs-frontend-architect`: Frontend UI and integration
- `test-qa-validator`: Testing and quality assurance
- `hackathon-judge-reviewer`: Compliance and documentation review
- `python-cli-expert`: Python-specific implementation (Phase I preservation)

---

## PHASE A: Monorepo & Project Setup

### Task A.1: Create Monorepo Directory Structure

**Task ID**: `A.1`
**Priority**: P0 (Blocking)
**Estimated Complexity**: Simple

**Description**:
Create the complete monorepo directory structure as defined in the approved plan, including frontend/, backend/, and supporting directories.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 1.1 "Repository Structure"

**Outputs**:
- Directory structure matching plan Section 1.1
- Empty placeholder files (`.gitkeep`) in all subdirectories to ensure Git tracks them

**Dependencies**: None

**Responsible Agent**: `fullstack-spec-architect`

**Completion Criteria**:
- [x] `frontend/` directory exists with subdirectories: `src/app/`, `src/components/`, `src/lib/`, `src/types/`, `src/hooks/`, `public/`, `__tests__/`
- [x] `backend/` directory exists with subdirectories: `app/models/`, `app/schemas/`, `app/auth/`, `app/routers/`, `app/services/`, `app/middleware/`, `tests/`, `alembic/versions/`
- [x] Root-level directories exist: `specs/`, `.claude/`, `history/`
- [x] All empty directories contain `.gitkeep` files
- [x] Structure validated against plan.md Section 1.1

**Tests**:
```bash
# Validate structure exists
find . -type d -name "frontend" -o -name "backend" | wc -l  # Should be 2
ls frontend/src/app frontend/src/components  # Should not error
ls backend/app/models backend/app/routers  # Should not error
```

---

### Task A.2: Configure Frontend Package.json

**Task ID**: `A.2`
**Priority**: P0 (Blocking)
**Estimated Complexity**: Simple

**Description**:
Create `frontend/package.json` with Next.js 16+, TypeScript, Tailwind CSS, Better Auth, and all required dependencies as specified in the plan.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 2.1 "Technology Stack"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-034 through FR-040 (Frontend requirements)

**Outputs**:
- `frontend/package.json` with complete dependency list
- `frontend/tsconfig.json` with strict TypeScript configuration
- `frontend/next.config.ts` with basic Next.js configuration
- `frontend/tailwind.config.ts` with Tailwind CSS configuration
- `frontend/postcss.config.js`

**Dependencies**: A.1

**Responsible Agent**: `nextjs-frontend-architect`

**Completion Criteria**:
- [ ] `package.json` includes Next.js ^16.0.0
- [ ] `package.json` includes TypeScript ^5.0.0
- [ ] `package.json` includes Tailwind CSS ^3.0.0
- [ ] `package.json` includes Better Auth library
- [ ] `package.json` includes jwt-decode for token handling
- [ ] `tsconfig.json` has `strict: true` and `app/` directory configured
- [ ] `next.config.ts` configured for App Router
- [ ] Tailwind config references `./src/**/*.{js,ts,jsx,tsx}` for content scanning

**Tests**:
```bash
cd frontend
npm install  # Should complete without errors
npx tsc --noEmit  # Should pass with empty project
```

---

### Task A.3: Configure Backend Requirements

**Task ID**: `A.3`
**Priority**: P0 (Blocking)
**Estimated Complexity**: Simple

**Description**:
Create `backend/requirements.txt` and `backend/requirements-dev.txt` with FastAPI, SQLModel, JWT libraries, and all dependencies specified in the plan.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 3.1 "Technology Stack"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-015 through FR-033 (Backend and database requirements)

**Outputs**:
- `backend/requirements.txt` (production dependencies)
- `backend/requirements-dev.txt` (development dependencies: pytest, black, mypy)

**Dependencies**: A.1

**Responsible Agent**: `fastapi-backend-architect`

**Completion Criteria**:
- [ ] `requirements.txt` includes FastAPI ^0.115.0
- [ ] `requirements.txt` includes SQLModel ^0.0.22
- [ ] `requirements.txt` includes psycopg2-binary (PostgreSQL driver)
- [ ] `requirements.txt` includes python-jose[cryptography] (JWT)
- [ ] `requirements.txt` includes passlib[bcrypt] (password hashing)
- [ ] `requirements.txt` includes alembic (migrations)
- [ ] `requirements.txt` includes python-dotenv (environment variables)
- [ ] `requirements-dev.txt` includes pytest, pytest-asyncio, black, mypy
- [ ] All versions pinned or with minimum versions specified

**Tests**:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # Should complete without errors
pip install -r requirements-dev.txt  # Should complete without errors
python -c "import fastapi; import sqlmodel; import jose"  # Should not error
```

---

### Task A.4: Create Environment Configuration Templates

**Task ID**: `A.4`
**Priority**: P0 (Blocking)
**Estimated Complexity**: Simple

**Description**:
Create `.env.example` files for frontend and backend with all required environment variables documented but no sensitive values.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Sections 2.7 "Environment Variables" and 3.7 "Environment Variables"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-030 (Environment configuration)

**Outputs**:
- `frontend/.env.example` with frontend environment variables
- `backend/.env.example` with backend environment variables
- Root `.gitignore` updated to exclude `.env`, `.env.local`, `venv/`, `node_modules/`

**Dependencies**: A.1

**Responsible Agent**: `fullstack-spec-architect`

**Completion Criteria**:
- [ ] `frontend/.env.example` contains:
  - `NEXT_PUBLIC_API_URL=http://localhost:8000` (commented with description)
- [ ] `backend/.env.example` contains:
  - `DATABASE_URL=postgresql://user:password@host:port/dbname` (placeholder)
  - `JWT_SECRET_KEY=your-secret-key-here` (placeholder)
  - `JWT_ALGORITHM=HS256`
  - `JWT_EXPIRE_MINUTES=15`
- [ ] `.gitignore` includes: `.env`, `.env.local`, `*.env`, `venv/`, `__pycache__/`, `node_modules/`, `.next/`
- [ ] Comments explain each variable's purpose and example values

**Tests**:
```bash
# Validate .env.example files exist and contain required keys
grep "NEXT_PUBLIC_API_URL" frontend/.env.example  # Should find
grep "DATABASE_URL" backend/.env.example  # Should find
grep "JWT_SECRET_KEY" backend/.env.example  # Should find
```

---

### Task A.5: Initialize Backend FastAPI Application

**Task ID**: `A.5`
**Priority**: P0 (Blocking)
**Estimated Complexity**: Simple

**Description**:
Create `backend/main.py` with minimal FastAPI application setup, CORS configuration, and health check endpoint.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 3.2 "FastAPI Application Structure"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-031 (RESTful API requirement)

**Outputs**:
- `backend/main.py` with FastAPI app instance
- `backend/app/__init__.py` (empty)
- `backend/app/config.py` with Pydantic Settings for environment variables
- Basic CORS middleware configured

**Dependencies**: A.3

**Responsible Agent**: `fastapi-backend-architect`

**Completion Criteria**:
- [ ] `main.py` creates FastAPI app instance: `app = FastAPI(title="Todo API", version="2.0.0")`
- [ ] CORS middleware configured to allow frontend origin (http://localhost:3000 for development)
- [ ] Health check endpoint exists: `GET /health` returns `{"status": "ok"}`
- [ ] `app/config.py` uses Pydantic BaseSettings to load environment variables
- [ ] Config validates required variables: `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXPIRE_MINUTES`
- [ ] Application can be started with `uvicorn main:app --reload`

**Tests**:
```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 &
sleep 2
curl http://localhost:8000/health  # Should return {"status": "ok"}
curl -X OPTIONS http://localhost:8000/health -H "Origin: http://localhost:3000"  # Should allow CORS
kill %1
```

---

### Task A.6: Initialize Frontend Next.js Application

**Task ID**: `A.6`
**Priority**: P0 (Blocking)
**Estimated Complexity**: Simple

**Description**:
Create minimal Next.js application structure with root layout, landing page, and Tailwind CSS configured.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 2.2 "Application Structure"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-034 through FR-040 (Frontend requirements)

**Outputs**:
- `frontend/src/app/layout.tsx` (root layout with HTML structure)
- `frontend/src/app/page.tsx` (landing/login page placeholder)
- `frontend/src/app/globals.css` (Tailwind directives)
- Tailwind CSS functioning

**Dependencies**: A.2

**Responsible Agent**: `nextjs-frontend-architect`

**Completion Criteria**:
- [ ] `layout.tsx` includes `<html>`, `<body>`, and Tailwind CSS import
- [ ] `layout.tsx` sets viewport metadata for responsive design
- [ ] `page.tsx` renders placeholder content: "Todo App - Login Page"
- [ ] `globals.css` includes Tailwind directives: `@tailwind base; @tailwind components; @tailwind utilities;`
- [ ] Application can be started with `npm run dev`
- [ ] Application accessible at http://localhost:3000
- [ ] Tailwind CSS classes render correctly (test with colored div)

**Tests**:
```bash
cd frontend
npm run dev &
sleep 5
curl http://localhost:3000  # Should return HTML with "Todo App"
kill %1
```

---

## PHASE B: Database & Persistence Layer

### Task B.1: Create SQLModel User Model

**Task ID**: `B.1`
**Priority**: P0 (Blocking)
**Estimated Complexity**: Medium

**Description**:
Implement the `User` SQLModel with all fields, constraints, and relationships as specified in the database schema design.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 4.1 "Database Schema Design"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-001, FR-002, FR-003 (User authentication)

**Outputs**:
- `backend/app/models/__init__.py` (exports User model)
- `backend/app/models/user.py` with complete User SQLModel

**Dependencies**: A.3, A.5

**Responsible Agent**: `fastapi-backend-architect`

**Completion Criteria**:
- [ ] `User` model inherits from `SQLModel` with `table=True`
- [ ] Fields defined:
  - `id: uuid.UUID` (primary key, default=uuid4)
  - `email: str` (unique, indexed, max_length=255, not null)
  - `hashed_password: str` (max_length=255, not null)
  - `created_at: datetime` (default=utcnow)
- [ ] Email field has unique constraint
- [ ] Model has `__tablename__ = "users"` explicitly set
- [ ] Type hints are complete and correct
- [ ] No plaintext password field exists (security requirement FR-003)

**Tests**:
```python
# backend/tests/test_models.py
from app.models.user import User
import uuid

def test_user_model_creation():
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password="hashed_pw_123"
    )
    assert user.email == "test@example.com"
    assert user.hashed_password == "hashed_pw_123"
    assert user.created_at is not None
```

---

### Task B.2: Create SQLModel Todo Model

**Task ID**: `B.2`
**Priority**: P0 (Blocking)
**Estimated Complexity**: Medium

**Description**:
Implement the `Todo` SQLModel with all fields, foreign key to User, and cascade delete behavior.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 4.1 "Database Schema Design"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-008 through FR-014 (Todo CRUD), FR-017 (User-todo relationship)

**Outputs**:
- `backend/app/models/__init__.py` (exports Todo model)
- `backend/app/models/todo.py` with complete Todo SQLModel
- Relationship between User and Todo models defined

**Dependencies**: B.1

**Responsible Agent**: `fastapi-backend-architect`

**Completion Criteria**:
- [ ] `Todo` model inherits from `SQLModel` with `table=True`
- [ ] Fields defined:
  - `id: int` (primary key, autoincrement)
  - `user_id: uuid.UUID` (foreign key to users.id, not null, indexed)
  - `title: str` (max_length=200, not null)
  - `description: Optional[str]` (max_length=2000, nullable)
  - `completed: bool` (default=False)
  - `created_at: datetime` (default=utcnow)
  - `updated_at: datetime` (default=utcnow)
- [ ] Foreign key relationship: `user_id` references `users.id` with `ON DELETE CASCADE`
- [ ] SQLModel `Relationship` defined: `owner: User = Relationship(back_populates="todos")`
- [ ] User model updated with: `todos: List["Todo"] = Relationship(back_populates="owner", cascade_delete=True)`
- [ ] Model has `__tablename__ = "todos"` explicitly set

**Tests**:
```python
# backend/tests/test_models.py
from app.models.todo import Todo
from app.models.user import User
import uuid

def test_todo_model_creation():
    user_id = uuid.uuid4()
    todo = Todo(
        user_id=user_id,
        title="Test Todo",
        description="Test description",
        completed=False
    )
    assert todo.title == "Test Todo"
    assert todo.user_id == user_id
    assert todo.completed is False
```

---

### Task B.3: Configure Database Connection

**Task ID**: `B.3`
**Priority**: P0 (Blocking)
**Estimated Complexity**: Medium

**Description**:
Create database connection management module with SQLModel engine, session factory, and connection pooling.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 4.3 "Database Connection Management"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-015 (Database persistence)

**Outputs**:
- `backend/app/database.py` with engine, session factory, and dependency injection function

**Dependencies**: A.5, B.1, B.2

**Responsible Agent**: `fastapi-backend-architect`

**Completion Criteria**:
- [ ] `database.py` creates SQLModel engine using `DATABASE_URL` from config
- [ ] Engine configured with connection pool settings (pool_size=5, max_overflow=10)
- [ ] `create_db_and_tables()` function creates all tables (for development)
- [ ] `get_session()` dependency function yields database session
- [ ] Session is properly closed after request completes (using `yield`)
- [ ] Engine configured with `echo=False` for production (no SQL logging)

**Tests**:
```python
# backend/tests/test_database.py
from app.database import get_session, engine
from sqlmodel import SQLModel

def test_database_connection():
    # Test that tables can be created
    SQLModel.metadata.create_all(engine)

    # Test that session can be obtained
    session = next(get_session())
    assert session is not None
    session.close()
```

---

### Task B.4: Initialize Alembic for Migrations

**Task ID**: `B.4`
**Priority**: P1
**Estimated Complexity**: Simple

**Description**:
Initialize Alembic migration tool and configure it to work with SQLModel models.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 4.4 "Migration Strategy"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-016 (Schema migration support)

**Outputs**:
- `backend/alembic.ini` configured
- `backend/alembic/env.py` configured to use SQLModel metadata
- `backend/alembic/versions/` directory initialized

**Dependencies**: B.1, B.2, B.3

**Responsible Agent**: `fastapi-backend-architect`

**Completion Criteria**:
- [ ] Alembic initialized: `alembic init alembic` completed
- [ ] `alembic.ini` configured with correct `sqlalchemy.url` (reads from env)
- [ ] `alembic/env.py` imports all SQLModel models
- [ ] `alembic/env.py` sets `target_metadata = SQLModel.metadata`
- [ ] Initial migration can be created: `alembic revision --autogenerate -m "Initial schema"`
- [ ] Migration can be applied: `alembic upgrade head`

**Tests**:
```bash
cd backend
source venv/bin/activate
alembic revision --autogenerate -m "Initial schema"  # Should create migration file
alembic upgrade head  # Should apply migration
alembic current  # Should show current revision
```

---

### Task B.5: Create Initial Database Migration

**Task ID**: `B.5`
**Priority**: P1
**Estimated Complexity**: Simple

**Description**:
Generate and validate the initial Alembic migration for User and Todo tables.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 4.4 "Migration Strategy"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-016 (Schema migration)

**Outputs**:
- `backend/alembic/versions/0001_initial_schema.py` migration file

**Dependencies**: B.4

**Responsible Agent**: `fastapi-backend-architect`

**Completion Criteria**:
- [ ] Migration file created with meaningful name: `0001_initial_schema`
- [ ] `upgrade()` function creates `users` table with all columns and constraints
- [ ] `upgrade()` function creates `todos` table with all columns and foreign key
- [ ] `downgrade()` function drops tables in correct order (todos first, then users)
- [ ] Migration can be applied: `alembic upgrade head`
- [ ] Migration can be rolled back: `alembic downgrade -1`
- [ ] Database schema matches SQLModel definitions exactly

**Tests**:
```bash
cd backend
source venv/bin/activate
# Apply migration
alembic upgrade head
# Verify tables exist
psql $DATABASE_URL -c "\dt"  # Should list 'users' and 'todos' tables
# Verify foreign key
psql $DATABASE_URL -c "\d todos"  # Should show foreign key constraint
# Rollback
alembic downgrade -1
psql $DATABASE_URL -c "\dt"  # Should show no tables
```

---

## PHASE C: Authentication & Security

### Task C.1: Implement Password Hashing Utilities

**Task ID**: `C.1`
**Priority**: P0 (Blocking)
**Estimated Complexity**: Simple

**Description**:
Create password hashing and verification functions using bcrypt via passlib.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 3.3.1 "Password Hashing"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-003 (Password security)

**Outputs**:
- `backend/app/auth/password.py` with `hash_password()` and `verify_password()` functions

**Dependencies**: A.3

**Responsible Agent**: `auth-security-architect`

**Completion Criteria**:
- [x] `hash_password(plain_password: str) -> str` function implemented
- [x] Uses `passlib.context.CryptContext` with bcrypt scheme
- [x] `verify_password(plain_password: str, hashed_password: str) -> bool` function implemented
- [x] Functions handle empty passwords gracefully (raise ValueError)
- [x] Hash output format is bcrypt standard (starts with `$2b$`)

**Tests**:
```python
# backend/tests/test_auth.py
from app.auth.password import hash_password, verify_password

def test_password_hashing():
    plain = "SecurePassword123"
    hashed = hash_password(plain)

    assert hashed != plain
    assert hashed.startswith("$2b$")
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword", hashed) is False
```

---

### Task C.2: Implement JWT Token Creation

**Task ID**: `C.2`
**Priority**: P0 (Blocking)
**Estimated Complexity**: Medium

**Description**:
Create JWT token generation function that issues tokens with user_id in payload and 15-minute expiration.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 3.3.2 "JWT Token Creation"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-005 (JWT tokens), FR-006 (15-minute expiration)

**Outputs**:
- `backend/app/auth/jwt.py` with `create_access_token()` function

**Dependencies**: A.5 (config)

**Responsible Agent**: `auth-security-architect`

**Completion Criteria**:
- [x] `create_access_token(user_id: str) -> str` function implemented
- [x] Uses `python-jose` library: `from jose import jwt`
- [x] Token payload includes:
  - `sub: str` (user_id as string)
  - `exp: int` (expiration timestamp, 15 minutes from creation)
- [x] Signing algorithm is HS256
- [ ] Secret key loaded from `config.JWT_SECRET_KEY`
- [ ] Token is a valid JWT string

**Tests**:
```python
# backend/tests/test_jwt.py
from app.auth.jwt import create_access_token
from jose import jwt
from app.config import settings
import time

def test_create_access_token():
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    token = create_access_token(user_id)

    # Decode without verification to inspect payload
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

    assert payload["sub"] == user_id
    assert "exp" in payload
    assert payload["exp"] > time.time()  # Expiration in future
    assert payload["exp"] < time.time() + (16 * 60)  # Less than 16 minutes
```

---

### Task C.3: Implement JWT Token Verification

**Task ID**: `C.3`
**Priority**: P0 (Blocking)
**Estimated Complexity**: Medium

**Description**:
Create JWT token verification function that validates tokens and extracts user_id.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 3.3.3 "JWT Token Verification"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-027 (JWT validation on every request)

**Outputs**:
- `backend/app/auth/jwt.py` with `verify_token()` function
- Custom exception classes for token errors

**Dependencies**: C.2

**Responsible Agent**: `auth-security-architect`

**Completion Criteria**:
- [x] `verify_token(token: str) -> str` function implemented (returns user_id)
- [x] Validates token signature using `JWT_SECRET_KEY`
- [x] Validates token expiration
- [x] Extracts and returns `sub` (user_id) from payload
- [x] Raises `InvalidTokenError` for invalid tokens
- [x] Raises `ExpiredTokenError` for expired tokens
- [x] Exception classes defined in `backend/app/auth/exceptions.py`

**Tests**:
```python
# backend/tests/test_jwt.py
from app.auth.jwt import create_access_token, verify_token
from app.auth.exceptions import ExpiredTokenError, InvalidTokenError
import time
import pytest

def test_verify_valid_token():
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    token = create_access_token(user_id)
    verified_user_id = verify_token(token)
    assert verified_user_id == user_id

def test_verify_invalid_token():
    with pytest.raises(InvalidTokenError):
        verify_token("invalid.token.here")

def test_verify_expired_token():
    # Create token with immediate expiration
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    # Mock or sleep to test expiration
    # Implementation should raise ExpiredTokenError
    pass  # Detailed implementation in actual test
```

---

### Task C.4: Create Authentication Dependency

**Task ID**: `C.4`
**Priority**: P0 (Blocking)
**Estimated Complexity**: Medium

**Description**:
Create FastAPI dependency function that extracts and verifies JWT from Authorization header and returns user_id.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 3.3.4 "Dependency Injection Pattern"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-027 (Authorization enforcement)

**Outputs**:
- `backend/app/auth/dependencies.py` with `get_current_user_id()` dependency

**Dependencies**: C.3

**Responsible Agent**: `auth-security-architect`

**Completion Criteria**:
- [x] `get_current_user_id(authorization: str = Header(...)) -> str` function implemented
- [x] Extracts token from `Authorization: Bearer <token>` header
- [x] Validates header format (starts with "Bearer ")
- [x] Calls `verify_token()` to validate and extract user_id
- [x] Raises `HTTPException(401, "Invalid or expired token")` on verification failure
- [x] Raises `HTTPException(401, "Missing authorization header")` if header absent
- [x] Returns user_id as string

**Tests**:
```python
# backend/tests/test_dependencies.py
from app.auth.dependencies import get_current_user_id
from app.auth.jwt import create_access_token
from fastapi import HTTPException
import pytest

def test_get_current_user_id_valid():
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    token = create_access_token(user_id)
    authorization = f"Bearer {token}"

    result = get_current_user_id(authorization)
    assert result == user_id

def test_get_current_user_id_missing_header():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id("")
    assert exc_info.value.status_code == 401

def test_get_current_user_id_invalid_token():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id("Bearer invalid.token")
    assert exc_info.value.status_code == 401
```

---

### Task C.5: Create Pydantic Schemas for Authentication

**Task ID**: `C.5`
**Priority**: P1
**Estimated Complexity**: Simple

**Description**:
Create Pydantic models for authentication request/response payloads.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 3.4 "Pydantic Request/Response Schemas"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-001, FR-002, FR-004 (Registration and login)

**Outputs**:
- `backend/app/schemas/auth.py` with request and response models

**Dependencies**: A.3

**Responsible Agent**: `fastapi-backend-architect`

**Completion Criteria**:
- [x] `RegisterRequest` schema with fields:
  - `email: EmailStr` (Pydantic email validation)
  - `password: str` (min_length=8)
- [x] `LoginRequest` schema with fields:
  - `email: EmailStr`
  - `password: str`
- [x] `TokenResponse` schema with fields:
  - `access_token: str`
  - `token_type: str` (literal "bearer")
  - `user: UserResponse` (nested)
- [x] `UserResponse` schema with fields:
  - `id: str` (UUID as string)
  - `email: str`
- [x] All schemas inherit from `BaseModel`
- [x] Schemas have `Config` with `from_attributes = True` for ORM compatibility

**Tests**:
```python
# backend/tests/test_schemas.py
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
import pytest

def test_register_request_validation():
    # Valid request
    valid = RegisterRequest(email="test@example.com", password="password123")
    assert valid.email == "test@example.com"

    # Invalid email
    with pytest.raises(ValueError):
        RegisterRequest(email="invalid-email", password="password123")

    # Short password
    with pytest.raises(ValueError):
        RegisterRequest(email="test@example.com", password="short")
```

---

## PHASE D: Backend API Implementation

### Task D.1: Implement User Registration Endpoint

**Task ID**: `D.1`
**Priority**: P0 (Blocking)
**Estimated Complexity**: High

**Description**:
Implement `POST /api/auth/register` endpoint for user registration with email validation, duplicate checking, and password hashing.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 3.5.1 "Registration Endpoint"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-001, FR-002, FR-003 (User registration)

**Outputs**:
- `backend/app/routers/auth.py` with registration endpoint
- User service layer in `backend/app/services/user_service.py`

**Dependencies**: B.1, B.3, C.1, C.2, C.5

**Responsible Agent**: `fastapi-backend-architect`

**Completion Criteria**:
- [x] Endpoint: `POST /api/auth/register`
- [x] Request body: `RegisterRequest` schema
- [x] Response: `TokenResponse` (201 Created on success)
- [x] Validates email format (Pydantic handles this)
- [x] Validates password length ≥ 8 characters (Pydantic handles this)
- [x] Checks if email already exists (returns 409 Conflict: "This email is already registered")
- [x] Hashes password using `hash_password()`
- [x] Creates User record in database
- [x] Issues JWT token using `create_access_token()`
- [x] Returns token and user info
- [x] Transaction is atomic (rollback on error)
- [x] Maps to FR-001, FR-002, FR-003

**Tests**:
```python
# backend/tests/test_auth_endpoints.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_success():
    response = client.post("/api/auth/register", json={
        "email": "newuser@example.com",
        "password": "SecurePass123"
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "newuser@example.com"

def test_register_duplicate_email():
    # Register first user
    client.post("/api/auth/register", json={
        "email": "duplicate@example.com",
        "password": "SecurePass123"
    })
    # Attempt duplicate
    response = client.post("/api/auth/register", json={
        "email": "duplicate@example.com",
        "password": "AnotherPass456"
    })
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"].lower()
```

---

### Task D.2: Implement User Login Endpoint

**Task ID**: `D.2`
**Priority**: P0 (Blocking)
**Estimated Complexity**: High

**Description**:
Implement `POST /api/auth/login` endpoint for user authentication with email/password verification and JWT issuance.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 3.5.2 "Login Endpoint"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-004, FR-005 (User login and JWT)

**Outputs**:
- Login endpoint added to `backend/app/routers/auth.py`

**Dependencies**: D.1, C.1, C.2

**Responsible Agent**: `fastapi-backend-architect`

**Completion Criteria**:
- [x] Endpoint: `POST /api/auth/login`
- [x] Request body: `LoginRequest` schema
- [x] Response: `TokenResponse` (200 OK on success)
- [x] Queries User by email
- [x] Returns 401 "Invalid email or password" if user not found (generic message for security)
- [x] Verifies password using `verify_password()`
- [x] Returns 401 "Invalid email or password" if password incorrect
- [x] Issues JWT token using `create_access_token(user.id)`
- [x] Returns token and user info
- [x] No rate limiting (Phase II scope)
- [x] Maps to FR-004, FR-005

**Tests**:
```python
# backend/tests/test_auth_endpoints.py
def test_login_success():
    # Setup: Register user
    client.post("/api/auth/register", json={
        "email": "logintest@example.com",
        "password": "SecurePass123"
    })

    # Test: Login
    response = client.post("/api/auth/login", json={
        "email": "logintest@example.com",
        "password": "SecurePass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "logintest@example.com"

def test_login_invalid_email():
    response = client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "SomePassword"
    })
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

def test_login_wrong_password():
    # Setup: Register user
    client.post("/api/auth/register", json={
        "email": "wrongpw@example.com",
        "password": "CorrectPassword123"
    })

    # Test: Wrong password
    response = client.post("/api/auth/login", json={
        "email": "wrongpw@example.com",
        "password": "WrongPassword"
    })
    assert response.status_code == 401
```

---

### Task D.3: Create Pydantic Schemas for Todos

**Task ID**: `D.3`
**Priority**: P1
**Estimated Complexity**: Simple

**Description**:
Create Pydantic models for todo CRUD request/response payloads.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 3.4 "Pydantic Request/Response Schemas"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-008 through FR-014 (Todo operations)

**Outputs**:
- `backend/app/schemas/todo.py` with todo schemas

**Dependencies**: A.3

**Responsible Agent**: `fastapi-backend-architect`

**Completion Criteria**:
- [x] `TodoCreate` schema with fields:
  - `title: str` (min_length=1, max_length=200)
  - `description: Optional[str]` (max_length=2000)
- [x] `TodoUpdate` schema with fields:
  - `title: Optional[str]` (max_length=200)
  - `description: Optional[str]` (max_length=2000)
  - `completed: Optional[bool]`
- [x] `TodoResponse` schema with fields:
  - `id: int`
  - `title: str`
  - `description: Optional[str]`
  - `completed: bool`
  - `created_at: datetime`
  - `updated_at: datetime`
- [x] All schemas inherit from `BaseModel`
- [x] `TodoResponse` has `Config` with `from_attributes = True`

**Tests**:
```python
# backend/tests/test_schemas.py
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse

def test_todo_create_validation():
    valid = TodoCreate(title="Buy groceries", description="Milk, eggs, bread")
    assert valid.title == "Buy groceries"

    # Empty title should fail
    with pytest.raises(ValueError):
        TodoCreate(title="", description="Description")
```

---

### Task D.4: Implement Create Todo Endpoint

**Task ID**: `D.4`
**Priority**: P0 (Blocking)
**Estimated Complexity**: High

**Description**:
Implement `POST /api/{user_id}/tasks` endpoint for creating todos with user ownership enforcement.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 3.5.3 "Todo CRUD Endpoints"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-008 (Create todo), FR-017 (User-todo relationship), FR-028 (Ownership enforcement)

**Outputs**:
- `backend/app/routers/todos.py` with create endpoint
- Todo service layer in `backend/app/services/todo_service.py`

**Dependencies**: B.2, B.3, C.4, D.3

**Responsible Agent**: `fastapi-backend-architect`

**Completion Criteria**:
- [x] Endpoint: `POST /api/{user_id}/tasks`
- [x] Path parameter: `user_id: str` (ignored, JWT user_id used instead per FR-028)
- [x] Request body: `TodoCreate` schema
- [x] Response: `TodoResponse` (201 Created)
- [x] Requires authentication (uses `Depends(get_current_user_id)`)
- [x] Creates Todo with `user_id` from JWT (not path parameter)
- [x] Sets `completed=False` by default
- [x] Sets `created_at` and `updated_at` to current timestamp
- [x] Returns created todo with all fields
- [x] Transaction is atomic
- [x] Maps to FR-008, FR-017, FR-028

**Tests**:
```python
# backend/tests/test_todo_endpoints.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_todo_authenticated():
    # Setup: Register and login
    register_response = client.post("/api/auth/register", json={
        "email": "todouser@example.com",
        "password": "SecurePass123"
    })
    token = register_response.json()["access_token"]
    user_id = register_response.json()["user"]["id"]

    # Test: Create todo
    response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Buy milk", "description": "Whole milk"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy milk"
    assert data["completed"] is False
    assert "id" in data

def test_create_todo_unauthenticated():
    response = client.post("/api/someuser/tasks", json={"title": "Test"})
    assert response.status_code == 401
```

---

### Task D.5: Implement List Todos Endpoint

**Task ID**: `D.5`
**Priority**: P0 (Blocking)
**Estimated Complexity**: High

**Description**:
Implement `GET /api/{user_id}/tasks` endpoint for listing user's todos with automatic user filtering.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 3.5.3 "Todo CRUD Endpoints"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-009 (View todos), FR-021 (User filtering), FR-028 (Ownership enforcement)

**Outputs**:
- List endpoint added to `backend/app/routers/todos.py`

**Dependencies**: D.4

**Responsible Agent**: `fastapi-backend-architect`

**Completion Criteria**:
- [x] Endpoint: `GET /api/{user_id}/tasks`
- [x] Path parameter: `user_id: str` (ignored, JWT user_id used)
- [x] Response: `List[TodoResponse]` (200 OK)
- [x] Requires authentication (uses `Depends(get_current_user_id)`)
- [x] Queries todos WHERE `user_id` = JWT user_id
- [x] Orders by `created_at` DESC (newest first per FR-009)
- [x] Returns empty array `[]` if user has no todos
- [x] Maps to FR-009, FR-021, FR-028

**Tests**:
```python
# backend/tests/test_todo_endpoints.py
def test_list_todos_authenticated():
    # Setup: Register, login, create todos
    register_response = client.post("/api/auth/register", json={
        "email": "listuser@example.com",
        "password": "SecurePass123"
    })
    token = register_response.json()["access_token"]
    user_id = register_response.json()["user"]["id"]

    # Create two todos
    client.post(
        f"/api/{user_id}/tasks",
        json={"title": "First todo"},
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Second todo"},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Test: List todos
    response = client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Second todo"  # Newest first

def test_list_todos_empty():
    # New user with no todos
    register_response = client.post("/api/auth/register", json={
        "email": "emptyuser@example.com",
        "password": "SecurePass123"
    })
    token = register_response.json()["access_token"]
    user_id = register_response.json()["user"]["id"]

    response = client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == []
```

---

### Task D.6: Implement Update Todo Endpoint

**Task ID**: `D.6`
**Priority**: P1
**Estimated Complexity**: High

**Description**:
Implement `PUT /api/{user_id}/tasks/{task_id}` endpoint for updating todos with ownership verification.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 3.5.3 "Todo CRUD Endpoints"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-010 (Update todo), FR-011 (Mark complete), FR-029 (404 for unauthorized access)

**Outputs**:
- Update endpoint added to `backend/app/routers/todos.py`

**Dependencies**: D.5

**Responsible Agent**: `fastapi-backend-architect`

**Completion Criteria**:
- [x] Endpoint: `PUT /api/{user_id}/tasks/{task_id}`
- [x] Path parameters: `user_id: str`, `task_id: int`
- [x] Request body: `TodoUpdate` schema (all fields optional)
- [x] Response: `TodoResponse` (200 OK)
- [x] Requires authentication
- [x] Queries todo WHERE `id` = task_id AND `user_id` = JWT user_id
- [x] Returns 404 if todo not found or owned by different user (FR-029)
- [x] Updates only provided fields (title, description, completed)
- [x] Updates `updated_at` timestamp automatically
- [x] Returns updated todo
- [x] Maps to FR-010, FR-011, FR-029

**Tests**:
```python
# backend/tests/test_todo_endpoints.py
def test_update_todo_success():
    # Setup: Create user and todo
    register_response = client.post("/api/auth/register", json={
        "email": "updateuser@example.com",
        "password": "SecurePass123"
    })
    token = register_response.json()["access_token"]
    user_id = register_response.json()["user"]["id"]

    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Original title"},
        headers={"Authorization": f"Bearer {token}"}
    )
    task_id = create_response.json()["id"]

    # Test: Update todo
    response = client.put(
        f"/api/{user_id}/tasks/{task_id}",
        json={"title": "Updated title", "completed": True},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated title"
    assert data["completed"] is True

def test_update_todo_not_owned():
    # Create two users
    user1 = client.post("/api/auth/register", json={
        "email": "user1@example.com", "password": "Pass123"
    }).json()
    user2 = client.post("/api/auth/register", json={
        "email": "user2@example.com", "password": "Pass456"
    }).json()

    # User1 creates todo
    create_response = client.post(
        f"/api/{user1['user']['id']}/tasks",
        json={"title": "User1's todo"},
        headers={"Authorization": f"Bearer {user1['access_token']}"}
    )
    task_id = create_response.json()["id"]

    # User2 attempts to update User1's todo
    response = client.put(
        f"/api/{user2['user']['id']}/tasks/{task_id}",
        json={"title": "Hacked"},
        headers={"Authorization": f"Bearer {user2['access_token']}"}
    )
    assert response.status_code == 404  # Not found (not 403 per FR-029)
```

---

### Task D.7: Implement Delete Todo Endpoint

**Task ID**: `D.7`
**Priority**: P1
**Estimated Complexity**: Medium

**Description**:
Implement `DELETE /api/{user_id}/tasks/{task_id}` endpoint for deleting todos with ownership verification.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 3.5.3 "Todo CRUD Endpoints"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-012 (Delete todo), FR-029 (404 for unauthorized access)

**Outputs**:
- Delete endpoint added to `backend/app/routers/todos.py`

**Dependencies**: D.6

**Responsible Agent**: `fastapi-backend-architect`

**Completion Criteria**:
- [x] Endpoint: `DELETE /api/{user_id}/tasks/{task_id}`
- [x] Path parameters: `user_id: str`, `task_id: int`
- [x] Response: 204 No Content (success) or 404 Not Found
- [x] Requires authentication
- [x] Queries todo WHERE `id` = task_id AND `user_id` = JWT user_id
- [x] Returns 404 if todo not found or owned by different user
- [x] Deletes todo from database
- [x] Returns 204 No Content on successful deletion
- [x] Maps to FR-012, FR-029

**Tests**:
```python
# backend/tests/test_todo_endpoints.py
def test_delete_todo_success():
    # Setup: Create user and todo
    register_response = client.post("/api/auth/register", json={
        "email": "deleteuser@example.com",
        "password": "SecurePass123"
    })
    token = register_response.json()["access_token"]
    user_id = register_response.json()["user"]["id"]

    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "To be deleted"},
        headers={"Authorization": f"Bearer {token}"}
    )
    task_id = create_response.json()["id"]

    # Test: Delete todo
    response = client.delete(
        f"/api/{user_id}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204

    # Verify deletion
    list_response = client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert len(list_response.json()) == 0

def test_delete_todo_not_found():
    register_response = client.post("/api/auth/register", json={
        "email": "notfound@example.com",
        "password": "SecurePass123"
    })
    token = register_response.json()["access_token"]
    user_id = register_response.json()["user"]["id"]

    response = client.delete(
        f"/api/{user_id}/tasks/99999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
```

---

### Task D.8: Register API Routers in Main Application

**Task ID**: `D.8`
**Priority**: P1
**Estimated Complexity**: Simple

**Description**:
Register auth and todos routers in the main FastAPI application.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 3.2 "FastAPI Application Structure"

**Outputs**:
- Updated `backend/main.py` with router registrations

**Dependencies**: D.1, D.2, D.7

**Responsible Agent**: `fastapi-backend-architect`

**Completion Criteria**:
- [x] Auth router registered: `app.include_router(auth_router, prefix="/api/auth", tags=["auth"])`
- [x] Todos router registered: `app.include_router(todos_router, prefix="/api", tags=["todos"])`
- [x] Routers imported correctly from `app.routers.auth` and `app.routers.todos`
- [x] OpenAPI docs accessible at `/docs` showing all endpoints
- [x] All endpoints have correct tags and descriptions

**Tests**:
```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 &
sleep 2
curl http://localhost:8000/docs  # Should return OpenAPI UI HTML
curl http://localhost:8000/openapi.json | jq '.paths | keys'  # Should list all endpoints
kill %1
```

---

## PHASE E: Frontend Application

### Task E.1: Create API Client Module

**Task ID**: `E.1`
**Priority**: P0 (Blocking)
**Estimated Complexity**: Medium

**Description**:
Create centralized API client module with automatic JWT header injection and error handling.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 2.4 "API Client Implementation"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-027 (Authentication on every request)

**Outputs**:
- `frontend/src/lib/api.ts` with API client functions

**Dependencies**: A.6

**Responsible Agent**: `nextjs-frontend-architect`

**Completion Criteria**:
- [x] `apiClient(endpoint: string, options?: RequestInit): Promise<any>` function implemented
- [x] Reads JWT token from localStorage: `localStorage.getItem('jwt_token')`
- [x] Adds `Authorization: Bearer <token>` header if token exists
- [x] Sets `Content-Type: application/json` by default
- [x] Constructs full URL: `${process.env.NEXT_PUBLIC_API_URL}${endpoint}`
- [x] Handles 401 responses by:
  - Removing token from localStorage
  - Redirecting to `/` (login page)
  - Throwing error with message "Authentication required"
- [x] Parses JSON responses automatically
- [x] Throws errors for non-2xx responses with meaningful messages

**Tests**:
```typescript
// frontend/__tests__/api.test.ts
import { apiClient } from '@/lib/api';

describe('apiClient', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('includes Authorization header when token exists', async () => {
    localStorage.setItem('jwt_token', 'test-token-123');

    // Mock fetch
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ data: 'test' })
      })
    ) as jest.Mock;

    await apiClient('/test');

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/test'),
      expect.objectContaining({
        headers: expect.objectContaining({
          'Authorization': 'Bearer test-token-123'
        })
      })
    );
  });

  it('redirects to login on 401 response', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
        status: 401
      })
    ) as jest.Mock;

    const originalLocation = window.location;
    delete (window as any).location;
    window.location = { ...originalLocation, href: '' };

    await expect(apiClient('/test')).rejects.toThrow('Authentication required');
    // In real implementation, should redirect
  });
});
```

---

### Task E.2: Create TypeScript Type Definitions

**Task ID**: `E.2`
**Priority**: P1
**Estimated Complexity**: Simple

**Description**:
Create TypeScript interfaces matching backend Pydantic schemas for type safety.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 2.6 "TypeScript Type Definitions"
- Backend schemas from D.3, C.5

**Outputs**:
- `frontend/src/types/user.ts`
- `frontend/src/types/todo.ts`
- `frontend/src/types/auth.ts`

**Dependencies**: D.3, C.5

**Responsible Agent**: `nextjs-frontend-architect`

**Completion Criteria**:
- [x] `types/user.ts` exports `User` interface with fields: `id: string`, `email: string`
- [x] `types/todo.ts` exports interfaces:
  - `Todo`: `id`, `title`, `description`, `completed`, `created_at`, `updated_at`
  - `TodoCreate`: `title`, `description?`
  - `TodoUpdate`: `title?`, `description?`, `completed?`
- [x] `types/auth.ts` exports interfaces:
  - `RegisterRequest`: `email`, `password`
  - `LoginRequest`: `email`, `password`
  - `TokenResponse`: `access_token`, `token_type`, `user`
- [x] All date fields typed as `string` (ISO 8601 from API)
- [x] All fields match backend schema exactly (camelCase on frontend, snake_case from API handled by transformation)

**Tests**:
```typescript
// Type checking at compile time
import { User, Todo, TokenResponse } from '@/types';

const user: User = {
  id: '123',
  email: 'test@example.com'
};

const todo: Todo = {
  id: 1,
  title: 'Test',
  description: null,
  completed: false,
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z'
};
```

---

### Task E.3: Create Authentication Context

**Task ID**: `E.3`
**Priority**: P0 (Blocking)
**Estimated Complexity**: High

**Description**:
Create React Context for managing authentication state across the application.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 2.5 "Authentication State Management"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-039 (Session persistence)

**Outputs**:
- `frontend/src/lib/auth.ts` with AuthContext and useAuth hook
- Provider component to wrap application

**Dependencies**: E.1, E.2

**Responsible Agent**: `nextjs-frontend-architect`

**Completion Criteria**:
- [x] `AuthContext` created with values:
  - `user: User | null`
  - `token: string | null`
  - `isLoading: boolean`
  - `login(email, password): Promise<void>`
  - `register(email, password): Promise<void>`
  - `logout(): void`
- [x] `AuthProvider` component implemented
- [x] On mount, checks localStorage for `jwt_token`
- [x] If token exists, decodes to get user info and sets state
- [x] `login()` calls API, stores token, updates state
- [x] `register()` calls API, stores token, updates state
- [x] `logout()` removes token, clears state, redirects to `/`
- [x] `useAuth()` hook exported for consuming components
- [x] Token expiration handled gracefully (on 401, auto-logout)

**Tests**:
```typescript
// frontend/__tests__/auth.test.tsx
import { render, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '@/lib/auth';

describe('AuthContext', () => {
  it('initializes with null user when no token', () => {
    localStorage.clear();

    const TestComponent = () => {
      const { user, isLoading } = useAuth();
      return <div>{isLoading ? 'Loading' : (user ? user.email : 'No user')}</div>;
    };

    const { getByText } = render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    waitFor(() => expect(getByText('No user')).toBeInTheDocument());
  });

  it('logs in user successfully', async () => {
    // Mock API response
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          access_token: 'test-token',
          user: { id: '123', email: 'test@example.com' }
        })
      })
    ) as jest.Mock;

    // Test login flow
    // ... implementation
  });
});
```

---

### Task E.4: Create Login Page and Form Component

**Task ID**: `E.4`
**Priority**: P0 (Blocking)
**Estimated Complexity**: High

**Description**:
Implement login page at `/` with form validation and error handling.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 2.2 "Application Structure"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) User Story 1, FR-004 (Login)

**Outputs**:
- `frontend/src/app/page.tsx` (landing/login page)
- `frontend/src/components/auth/LoginForm.tsx`

**Dependencies**: E.3

**Responsible Agent**: `nextjs-frontend-architect`

**Completion Criteria**:
- [x] Landing page (`/`) displays LoginForm for unauthenticated users
- [x] Redirects authenticated users to `/dashboard`
- [x] LoginForm has controlled inputs: email (type="email") and password (type="password")
- [x] Client-side validation: email format, password not empty
- [x] "Login" button triggers `login()` from useAuth
- [x] Displays loading state during API call
- [x] Displays error message on failure (e.g., "Invalid email or password")
- [x] Redirects to `/dashboard` on successful login
- [x] "Sign Up" link navigates to `/register`
- [x] Responsive design (mobile-friendly)
- [x] Accessible (proper labels, ARIA attributes)

**Tests**:
```typescript
// frontend/__tests__/pages/login.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import LoginPage from '@/app/page';

describe('Login Page', () => {
  it('renders login form', () => {
    render(<LoginPage />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('displays error on invalid credentials', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ detail: 'Invalid email or password' })
      })
    ) as jest.Mock;

    render(<LoginPage />);

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'wrong@example.com' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrongpassword' }
    });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(screen.getByText(/invalid email or password/i)).toBeInTheDocument();
    });
  });
});
```

---

### Task E.5: Create Registration Page and Form Component

**Task ID**: `E.5`
**Priority**: P1
**Estimated Complexity**: High

**Description**:
Implement registration page at `/register` with form validation and error handling.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 2.3 "Authentication Flow Implementation"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) User Story 1, FR-001, FR-002 (Registration)

**Outputs**:
- `frontend/src/app/register/page.tsx`
- `frontend/src/components/auth/RegisterForm.tsx`

**Dependencies**: E.3, E.4

**Responsible Agent**: `nextjs-frontend-architect`

**Completion Criteria**:
- [x] Registration page (`/register`) displays RegisterForm
- [x] Redirects authenticated users to `/dashboard`
- [x] RegisterForm has controlled inputs: email and password
- [x] Client-side validation:
  - Email format (HTML5 email validation)
  - Password minimum 8 characters
  - Display inline validation errors
- [x] "Sign Up" button triggers `register()` from useAuth
- [x] Displays loading state during API call
- [x] Displays error message on failure (e.g., "This email is already registered")
- [x] Auto-login and redirect to `/dashboard` on success
- [x] "Already have an account? Login" link navigates to `/`
- [ ] Responsive and accessible

**Tests**:
```typescript
// frontend/__tests__/pages/register.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import RegisterPage from '@/app/register/page';

describe('Register Page', () => {
  it('validates password length', () => {
    render(<RegisterPage />);

    const passwordInput = screen.getByLabelText(/password/i);
    fireEvent.change(passwordInput, { target: { value: 'short' } });
    fireEvent.blur(passwordInput);

    expect(screen.getByText(/at least 8 characters/i)).toBeInTheDocument();
  });

  it('displays error on duplicate email', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
        status: 409,
        json: () => Promise.resolve({ detail: 'This email is already registered' })
      })
    ) as jest.Mock;

    render(<RegisterPage />);

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'existing@example.com' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'SecurePass123' }
    });
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }));

    await waitFor(() => {
      expect(screen.getByText(/already registered/i)).toBeInTheDocument();
    });
  });
});
```

---

### Task E.6: Create Dashboard Page Layout

**Task ID**: `E.6`
**Priority**: P0 (Blocking)
**Estimated Complexity**: Medium

**Description**:
Implement protected dashboard page at `/dashboard` with navigation and logout functionality.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 2.2 "Application Structure"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) User Story 2, FR-007 (Logout)

**Outputs**:
- `frontend/src/app/dashboard/page.tsx`
- `frontend/src/components/auth/LogoutButton.tsx`

**Dependencies**: E.3

**Responsible Agent**: `nextjs-frontend-architect`

**Completion Criteria**:
- [x] Dashboard page (`/dashboard`) is protected route
- [x] Redirects unauthenticated users to `/`
- [x] Displays user email in header
- [x] Logout button in header
- [x] Logout button calls `logout()` from useAuth
- [x] Page layout includes space for todo list (placeholder initially)
- [x] Responsive design with mobile navigation
- [x] Loading state while checking authentication

**Tests**:
```typescript
// frontend/__tests__/pages/dashboard.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import DashboardPage from '@/app/dashboard/page';
import { AuthProvider } from '@/lib/auth';

describe('Dashboard Page', () => {
  it('redirects to login when not authenticated', async () => {
    localStorage.clear();

    const { container } = render(
      <AuthProvider>
        <DashboardPage />
      </AuthProvider>
    );

    await waitFor(() => {
      // Should trigger redirect
      // Test implementation depends on routing setup
    });
  });

  it('displays user email when authenticated', () => {
    localStorage.setItem('jwt_token', 'test-token');
    // Mock decoded token to return user info

    render(
      <AuthProvider>
        <DashboardPage />
      </AuthProvider>
    );

    expect(screen.getByText(/test@example\.com/i)).toBeInTheDocument();
  });
});
```

---

### Task E.7: Create Todo List Component

**Task ID**: `E.7`
**Priority**: P0 (Blocking)
**Estimated Complexity**: High

**Description**:
Implement TodoList component that fetches and displays user's todos.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 2.4 "API Client Implementation"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) User Story 2, FR-009 (View todos)

**Outputs**:
- `frontend/src/components/todos/TodoList.tsx`
- `frontend/src/components/todos/EmptyState.tsx`
- `frontend/src/hooks/useTodos.ts` (custom hook for data fetching)

**Dependencies**: E.1, E.2, E.6

**Responsible Agent**: `nextjs-frontend-architect`

**Completion Criteria**:
- [x] `useTodos()` hook fetches todos on mount using `apiClient()`
- [x] Hook provides: `todos: Todo[]`, `isLoading: boolean`, `error: string | null`, `refetch: () => void`
- [x] TodoList displays loading spinner while fetching
- [x] TodoList displays error message if fetch fails
- [ ] TodoList maps over todos and renders TodoItem components
- [ ] TodoList displays EmptyState when todos array is empty
- [ ] EmptyState shows friendly message: "No todos yet. Create your first one!"
- [ ] Todos displayed in descending order by creation date (API handles this)
- [ ] Responsive grid/list layout

**Tests**:
```typescript
// frontend/__tests__/components/TodoList.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import TodoList from '@/components/todos/TodoList';

describe('TodoList', () => {
  it('displays loading state initially', () => {
    render(<TodoList />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('displays empty state when no todos', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve([])
      })
    ) as jest.Mock;

    render(<TodoList />);

    await waitFor(() => {
      expect(screen.getByText(/no todos yet/i)).toBeInTheDocument();
    });
  });

  it('displays todos when fetched', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve([
          { id: 1, title: 'Buy milk', completed: false, created_at: '2025-01-01' }
        ])
      })
    ) as jest.Mock;

    render(<TodoList />);

    await waitFor(() => {
      expect(screen.getByText('Buy milk')).toBeInTheDocument();
    });
  });
});
```

---

### Task E.8: Create Todo Item Component

**Task ID**: `E.8`
**Priority**: P1
**Estimated Complexity**: High

**Description**:
Implement TodoItem component with checkbox, inline editing, and delete button.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 2.2 "Application Structure"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) User Story 2, FR-010, FR-011, FR-012 (Update, complete, delete)

**Outputs**:
- `frontend/src/components/todos/TodoItem.tsx`

**Dependencies**: E.7

**Responsible Agent**: `nextjs-frontend-architect`

**Completion Criteria**:
- [x] TodoItem receives `todo: Todo` and `onUpdate: (id, updates) => void`, `onDelete: (id) => void` props
- [x] Displays todo title with strikethrough if completed
- [x] Checkbox for completed status (checked if completed)
- [x] Clicking checkbox calls `onUpdate(todo.id, { completed: !todo.completed })`
- [x] Click on title enables inline editing mode
- [x] Inline edit shows input with current title, saves on blur or Enter key
- [x] Delete button (icon or text) calls `onDelete(todo.id)`
- [x] Delete button shows confirmation modal: "Delete this todo?" with Cancel/Delete buttons
- [x] Shows loading state during update/delete operations
- [ ] Accessible (keyboard navigation, ARIA labels)
- [ ] Responsive (touch-friendly on mobile)

**Tests**:
```typescript
// frontend/__tests__/components/TodoItem.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import TodoItem from '@/components/todos/TodoItem';

describe('TodoItem', () => {
  const mockTodo = {
    id: 1,
    title: 'Test Todo',
    description: null,
    completed: false,
    created_at: '2025-01-01',
    updated_at: '2025-01-01'
  };

  it('renders todo title', () => {
    render(<TodoItem todo={mockTodo} onUpdate={jest.fn()} onDelete={jest.fn()} />);
    expect(screen.getByText('Test Todo')).toBeInTheDocument();
  });

  it('calls onUpdate when checkbox clicked', () => {
    const mockOnUpdate = jest.fn();
    render(<TodoItem todo={mockTodo} onUpdate={mockOnUpdate} onDelete={jest.fn()} />);

    const checkbox = screen.getByRole('checkbox');
    fireEvent.click(checkbox);

    expect(mockOnUpdate).toHaveBeenCalledWith(1, { completed: true });
  });

  it('shows delete confirmation on delete button click', () => {
    render(<TodoItem todo={mockTodo} onUpdate={jest.fn()} onDelete={jest.fn()} />);

    const deleteButton = screen.getByRole('button', { name: /delete/i });
    fireEvent.click(deleteButton);

    expect(screen.getByText(/delete this todo/i)).toBeInTheDocument();
  });
});
```

---

### Task E.9: Create Todo Form Component

**Task ID**: `E.9`
**Priority**: P1
**Estimated Complexity**: Medium

**Description**:
Implement TodoForm component for creating new todos.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 2.2 "Application Structure"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) User Story 1, FR-008 (Create todo)

**Outputs**:
- `frontend/src/components/todos/TodoForm.tsx`

**Dependencies**: E.2

**Responsible Agent**: `nextjs-frontend-architect`

**Completion Criteria**:
- [x] TodoForm receives `onCreate: (data: TodoCreate) => void` prop
- [x] Controlled inputs: title (required), description (optional)
- [x] "Add Todo" button triggers `onCreate()`
- [x] Client-side validation: title not empty, max 200 chars
- [x] Description optional, max 2000 chars
- [x] Clears form after successful creation
- [x] Shows loading state during API call
- [x] Displays error message if creation fails
- [ ] Responsive layout (stacked on mobile)
- [ ] Accessible form labels and validation messages

**Tests**:
```typescript
// frontend/__tests__/components/TodoForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import TodoForm from '@/components/todos/TodoForm';

describe('TodoForm', () => {
  it('calls onCreate with form data on submit', () => {
    const mockOnCreate = jest.fn();
    render(<TodoForm onCreate={mockOnCreate} />);

    fireEvent.change(screen.getByLabelText(/title/i), {
      target: { value: 'New Todo' }
    });
    fireEvent.change(screen.getByLabelText(/description/i), {
      target: { value: 'Details here' }
    });
    fireEvent.click(screen.getByRole('button', { name: /add todo/i }));

    expect(mockOnCreate).toHaveBeenCalledWith({
      title: 'New Todo',
      description: 'Details here'
    });
  });

  it('validates empty title', () => {
    render(<TodoForm onCreate={jest.fn()} />);

    fireEvent.click(screen.getByRole('button', { name: /add todo/i }));

    expect(screen.getByText(/title cannot be empty/i)).toBeInTheDocument();
  });
});
```

---

### Task E.10: Integrate CRUD Operations in Dashboard

**Task ID**: `E.10`
**Priority**: P1
**Estimated Complexity**: High

**Description**:
Integrate TodoForm, TodoList, and TodoItem in Dashboard with full CRUD operations.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 2.4 "API Client Implementation"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) User Story 2 (All CRUD operations)

**Outputs**:
- Updated `frontend/src/app/dashboard/page.tsx` with integrated components
- API call functions in `useTodos` hook for create, update, delete

**Dependencies**: E.7, E.8, E.9

**Responsible Agent**: `nextjs-frontend-architect`

**Completion Criteria**:
- [x] Dashboard page renders TodoForm and TodoList
- [x] `useTodos()` hook extended with:
  - `createTodo(data: TodoCreate): Promise<void>`
  - `updateTodo(id: number, data: TodoUpdate): Promise<void>`
  - `deleteTodo(id: number): Promise<void>`
- [x] `createTodo()` POSTs to `/api/{user_id}/tasks`, refetches list on success
- [x] `updateTodo()` PUTs to `/api/{user_id}/tasks/{id}`, refetches list on success
- [x] `deleteTodo()` DELETEs `/api/{user_id}/tasks/{id}`, refetches list on success
- [x] Optimistic UI updates (optional for Phase II)
- [x] All CRUD operations use authenticated API client
- [x] Error handling for each operation with user-friendly messages
- [x] Loading states for each operation

**Tests**:
```typescript
// frontend/__tests__/integration/crud.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import DashboardPage from '@/app/dashboard/page';

describe('Dashboard CRUD Integration', () => {
  beforeEach(() => {
    // Mock authentication
    localStorage.setItem('jwt_token', 'test-token');
  });

  it('creates, updates, and deletes todo', async () => {
    // Mock API responses
    global.fetch = jest.fn((url, options) => {
      if (options?.method === 'POST') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ id: 1, title: 'New Todo', completed: false })
        });
      }
      if (options?.method === 'GET') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([{ id: 1, title: 'New Todo', completed: false }])
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    }) as jest.Mock;

    render(<DashboardPage />);

    // Create todo
    fireEvent.change(screen.getByLabelText(/title/i), {
      target: { value: 'New Todo' }
    });
    fireEvent.click(screen.getByRole('button', { name: /add todo/i }));

    await waitFor(() => {
      expect(screen.getByText('New Todo')).toBeInTheDocument();
    });

    // Update todo (mark complete)
    const checkbox = screen.getByRole('checkbox');
    fireEvent.click(checkbox);

    await waitFor(() => {
      expect(checkbox).toBeChecked();
    });

    // Delete todo
    fireEvent.click(screen.getByRole('button', { name: /delete/i }));
    fireEvent.click(screen.getByRole('button', { name: /confirm/i }));

    await waitFor(() => {
      expect(screen.queryByText('New Todo')).not.toBeInTheDocument();
    });
  });
});
```

---

### Task E.11: Implement Responsive UI Styles

**Task ID**: `E.11`
**Priority**: P2
**Estimated Complexity**: Medium

**Description**:
Apply Tailwind CSS for responsive design across mobile, tablet, and desktop viewports.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 2.8 "Responsive Design Patterns"
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-040 (Responsive UI), User Story 3 (Multi-device)

**Outputs**:
- Updated component styles using Tailwind responsive classes
- Mobile-first responsive breakpoints

**Dependencies**: E.10

**Responsible Agent**: `nextjs-frontend-architect`

**Completion Criteria**:
- [x] Mobile (320px+): Single column layout, stacked forms, touch-friendly buttons (min 44px height)
- [x] Tablet (768px+): Two-column layout where appropriate, larger text
- [x] Desktop (1024px+): Multi-column layout, hover states, larger spacing
- [ ] All buttons and interactive elements at least 44x44px for touch targets
- [ ] Text readable without zooming (min 16px font size)
- [ ] Forms stack vertically on mobile, horizontal on desktop
- [ ] Navigation responsive (hamburger menu on mobile optional)
- [ ] Tested across Chrome DevTools device emulators
- [ ] Maps to FR-040

**Tests**:
```typescript
// Manual testing checklist in browser
// Automated visual regression tests (optional)

// Example responsive class usage:
// <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
// <button className="min-h-[44px] min-w-[44px] px-4 py-2">
```

---

## PHASE F: Integration & End-to-End Flow

### Task F.1: Configure Frontend-Backend CORS

**Task ID**: `F.1`
**Priority**: P0 (Blocking)
**Estimated Complexity**: Simple

**Description**:
Ensure CORS middleware on backend allows frontend origin for local development and production.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 3.8 "CORS Configuration"

**Outputs**:
- Updated `backend/app/middleware/cors.py` or `backend/main.py` with CORS settings

**Dependencies**: A.5, E.1

**Responsible Agent**: `fastapi-backend-architect`

**Completion Criteria**:
- [x] CORS middleware allows origin: `http://localhost:3000` (development)
- [x] CORS allows credentials: `allow_credentials=True`
- [x] CORS allows methods: `["GET", "POST", "PUT", "DELETE", "OPTIONS"]`
- [x] CORS allows headers: `["Authorization", "Content-Type"]`
- [x] Production origin configured via environment variable: `FRONTEND_URL`
- [x] Preflight requests (OPTIONS) handled correctly

**Tests**:
```bash
# Test CORS with curl
curl -X OPTIONS http://localhost:8000/api/health \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -v

# Should include headers:
# Access-Control-Allow-Origin: http://localhost:3000
# Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
```

---

### Task F.2: End-to-End Registration Flow Test

**Task ID**: `F.2`
**Priority**: P1
**Estimated Complexity**: Medium

**Description**:
Validate complete registration flow from frontend form submission to database record creation.

**Inputs**:
- [@specs/002-fullstack-web-app/spec.md](./spec.md) User Story 1, Acceptance Scenarios 1-4

**Outputs**:
- E2E test script in `frontend/__tests__/e2e/registration.test.ts` (or Playwright/Cypress)

**Dependencies**: D.1, E.5, F.1

**Responsible Agent**: `test-qa-validator`

**Completion Criteria**:
- [x] Test navigates to `/register`
- [x] Test fills registration form with valid email and password
- [x] Test submits form
- [x] Test verifies redirect to `/dashboard`
- [x] Test verifies user email displayed in dashboard header
- [x] Test verifies JWT token stored in localStorage
- [x] Test verifies user record exists in database (backend test)
- [x] Test validates duplicate email rejection (409 Conflict)
- [x] Maps to User Story 1, Scenarios 1 and 4

**Tests**:
```typescript
// Example Playwright test
test('user registration flow', async ({ page }) => {
  await page.goto('http://localhost:3000/register');

  await page.fill('input[type="email"]', 'newuser@example.com');
  await page.fill('input[type="password"]', 'SecurePass123');
  await page.click('button:has-text("Sign Up")');

  await expect(page).toHaveURL('http://localhost:3000/dashboard');
  await expect(page.locator('text=newuser@example.com')).toBeVisible();

  const token = await page.evaluate(() => localStorage.getItem('jwt_token'));
  expect(token).toBeTruthy();
});
```

---

### Task F.3: End-to-End Login and Todo CRUD Test

**Task ID**: `F.3`
**Priority**: P1
**Estimated Complexity**: High

**Description**:
Validate complete login and todo CRUD operations from frontend through backend to database.

**Inputs**:
- [@specs/002-fullstack-web-app/spec.md](./spec.md) User Story 2, All acceptance scenarios

**Outputs**:
- E2E test script in `frontend/__tests__/e2e/todos.test.ts`

**Dependencies**: D.2, D.4, D.5, D.6, D.7, E.10, F.1

**Responsible Agent**: `test-qa-validator`

**Completion Criteria**:
- [x] Test registers new user or logs in as existing user
- [x] Test creates todo via TodoForm
- [x] Test verifies todo appears in TodoList
- [x] Test updates todo title inline
- [x] Test marks todo as complete via checkbox
- [x] Test verifies completed todo has strikethrough styling
- [x] Test deletes todo and confirms deletion
- [x] Test verifies todo removed from list
- [x] Test logs out and logs back in, verifies todo persistence
- [x] Maps to User Story 2, all scenarios

**Tests**:
```typescript
// Example Playwright test
test('todo CRUD flow', async ({ page }) => {
  // Login
  await page.goto('http://localhost:3000');
  await page.fill('input[type="email"]', 'testuser@example.com');
  await page.fill('input[type="password"]', 'SecurePass123');
  await page.click('button:has-text("Login")');

  // Create todo
  await page.fill('input[placeholder="Title"]', 'Buy groceries');
  await page.click('button:has-text("Add Todo")');
  await expect(page.locator('text=Buy groceries')).toBeVisible();

  // Mark complete
  await page.click('input[type="checkbox"]');
  await expect(page.locator('text=Buy groceries')).toHaveCSS('text-decoration', /line-through/);

  // Delete
  await page.click('button:has-text("Delete")');
  await page.click('button:has-text("Confirm")');
  await expect(page.locator('text=Buy groceries')).not.toBeVisible();
});
```

---

### Task F.4: Data Isolation Verification Test

**Task ID**: `F.4`
**Priority**: P0 (Blocking)
**Estimated Complexity**: High

**Description**:
Validate that users cannot access other users' todos through UI manipulation or API calls.

**Inputs**:
- [@specs/002-fullstack-web-app/spec.md](./spec.md) User Story 4, All acceptance scenarios, FR-029 (404 response)

**Outputs**:
- Security test script in `backend/tests/test_data_isolation.py`

**Dependencies**: D.4, D.5, D.6, D.7, F.1

**Responsible Agent**: `auth-security-architect`

**Completion Criteria**:
- [x] Test creates two users (Alice and Bob)
- [x] Alice creates a todo
- [x] Bob attempts to fetch Alice's todo via API (GET /api/alice/tasks/{todo_id}) with Bob's JWT
- [x] Test verifies 404 response (not 403) per FR-029
- [x] Bob attempts to update Alice's todo (PUT) with Bob's JWT
- [x] Test verifies 404 response
- [x] Bob attempts to delete Alice's todo (DELETE) with Bob's JWT
- [x] Test verifies 404 response
- [x] Bob lists his todos, verifies Alice's todos not included
- [x] Maps to User Story 4, all scenarios, FR-029

**Tests**:
```python
# backend/tests/test_data_isolation.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_user_cannot_access_other_user_todos():
    # Create Alice
    alice = client.post("/api/auth/register", json={
        "email": "alice@example.com",
        "password": "AlicePass123"
    }).json()
    alice_token = alice["access_token"]
    alice_id = alice["user"]["id"]

    # Alice creates todo
    alice_todo = client.post(
        f"/api/{alice_id}/tasks",
        json={"title": "Alice's secret todo"},
        headers={"Authorization": f"Bearer {alice_token}"}
    ).json()
    alice_todo_id = alice_todo["id"]

    # Create Bob
    bob = client.post("/api/auth/register", json={
        "email": "bob@example.com",
        "password": "BobPass123"
    }).json()
    bob_token = bob["access_token"]
    bob_id = bob["user"]["id"]

    # Bob attempts to access Alice's todo
    response = client.get(
        f"/api/{alice_id}/tasks/{alice_todo_id}",
        headers={"Authorization": f"Bearer {bob_token}"}
    )
    assert response.status_code == 404  # Not 403

    # Bob lists his todos - should not include Alice's
    bob_todos = client.get(
        f"/api/{bob_id}/tasks",
        headers={"Authorization": f"Bearer {bob_token}"}
    ).json()
    assert len(bob_todos) == 0
```

---

### Task F.5: Session Expiration and Re-authentication Test

**Task ID**: `F.5`
**Priority**: P2
**Estimated Complexity**: Medium

**Description**:
Validate that expired JWT tokens are rejected and user is prompted to re-authenticate.

**Inputs**:
- [@specs/002-fullstack-web-app/spec.md](./spec.md) User Story 3, Scenario 2, FR-006 (15-minute expiration)

**Outputs**:
- Test script in `backend/tests/test_token_expiration.py`

**Dependencies**: C.3, E.1

**Responsible Agent**: `auth-security-architect`

**Completion Criteria**:
- [x] Test creates JWT token with immediate expiration (mock time or create with past exp)
- [x] Test attempts API call with expired token
- [x] Test verifies 401 response with error message indicating expiration
- [x] Frontend test verifies expired token triggers redirect to login page
- [x] Test verifies token removed from localStorage after expiration
- [ ] Maps to User Story 3, Scenario 2, FR-006

**Tests**:
```python
# backend/tests/test_token_expiration.py
from app.auth.jwt import create_access_token, verify_token
from app.auth.exceptions import ExpiredTokenError
import time
import pytest

def test_expired_token_rejected():
    # Create token with 0 expiration (immediately expired)
    # This requires modifying create_access_token to accept custom exp for testing
    # Or use time mocking

    user_id = "123e4567-e89b-12d3-a456-426614174000"
    token = create_access_token(user_id)

    # Wait for expiration (or mock time)
    time.sleep(901)  # 15 minutes + 1 second

    with pytest.raises(ExpiredTokenError):
        verify_token(token)

def test_api_rejects_expired_token():
    # Integration test with API endpoint
    # Create user, get token, wait for expiration, attempt API call
    pass  # Implementation details
```

---

## PHASE G: QA, Validation & Documentation

### Task G.1: Run Comprehensive Backend Test Suite

**Task ID**: `G.1`
**Priority**: P1
**Estimated Complexity**: Medium

**Description**:
Execute all backend tests with coverage reporting to ensure 80%+ code coverage.

**Inputs**:
- All backend tests from tasks B.1 through F.5

**Outputs**:
- Test execution report with coverage metrics
- Fix any failing tests

**Dependencies**: F.5

**Responsible Agent**: `test-qa-validator`

**Completion Criteria**:
- [ ] All tests in `backend/tests/` directory pass
- [ ] Code coverage ≥ 80% for:
  - `app/models/`
  - `app/routers/`
  - `app/auth/`
  - `app/services/`
- [ ] No flaky tests (run suite 3 times, all pass)
- [ ] Test execution time < 30 seconds
- [ ] Coverage report generated: `pytest --cov=app --cov-report=html`

**Tests**:
```bash
cd backend
source venv/bin/activate
pytest -v --cov=app --cov-report=term-missing --cov-report=html
# Review coverage report in htmlcov/index.html
# Aim for 80%+ coverage on critical paths
```

---

### Task G.2: Run Comprehensive Frontend Test Suite

**Task ID**: `G.2`
**Priority**: P1
**Estimated Complexity**: Medium

**Description**:
Execute all frontend tests including unit, integration, and E2E tests.

**Inputs**:
- All frontend tests from tasks E.1 through F.5

**Outputs**:
- Test execution report
- Fix any failing tests

**Dependencies**: F.5

**Responsible Agent**: `test-qa-validator`

**Completion Criteria**:
- [ ] All tests in `frontend/__tests__/` directory pass
- [ ] Unit tests for components pass
- [ ] Integration tests for CRUD operations pass
- [ ] E2E tests (registration, login, todos) pass
- [ ] No console errors or warnings in test output
- [ ] Tests run in CI-friendly mode (headless for E2E)

**Tests**:
```bash
cd frontend
npm test  # Run Jest unit tests
npm run test:e2e  # Run Playwright/Cypress E2E tests
```

---

### Task G.3: Validate Spec-to-Implementation Traceability

**Task ID**: `G.3`
**Priority**: P1
**Estimated Complexity**: Medium

**Description**:
Verify that all 40 functional requirements from spec.md are implemented and traceable to code.

**Inputs**:
- [@specs/002-fullstack-web-app/spec.md](./spec.md) Functional Requirements FR-001 through FR-040
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Requirements mapping

**Outputs**:
- Traceability matrix document: `specs/002-fullstack-web-app/traceability.md`

**Dependencies**: G.1, G.2

**Responsible Agent**: `hackathon-judge-reviewer`

**Completion Criteria**:
- [ ] Traceability matrix created with columns: FR-ID, Requirement, Implementation Location, Test Coverage, Status
- [ ] All 40 FRs mapped to implementation files/functions
- [ ] All 40 FRs have at least one test covering them
- [ ] All FRs marked as "IMPLEMENTED" or "PARTIAL" with notes
- [ ] Zero FRs with status "NOT IMPLEMENTED"
- [ ] Document references specific file paths and line numbers where applicable

**Example Traceability Entry**:
```markdown
| FR-ID | Requirement | Implementation | Tests | Status |
|-------|-------------|----------------|-------|--------|
| FR-001 | User registration with unique email | `backend/app/routers/auth.py:15-45` | `test_auth_endpoints.py::test_register_success` | IMPLEMENTED |
| FR-008 | Create todo | `backend/app/routers/todos.py:10-30`, `frontend/src/components/todos/TodoForm.tsx:20-40` | `test_todo_endpoints.py::test_create_todo`, `TodoForm.test.tsx::test_create` | IMPLEMENTED |
```

---

### Task G.4: Security Audit and Vulnerability Check

**Task ID**: `G.4`
**Priority**: P0 (Blocking)
**Estimated Complexity**: Medium

**Description**:
Perform security audit to identify vulnerabilities (XSS, SQL injection, IDOR, CSRF).

**Inputs**:
- [@specs/002-fullstack-web-app/spec.md](./spec.md) FR-023 through FR-030 (Security requirements)
- OWASP Top 10 checklist

**Outputs**:
- Security audit report: `specs/002-fullstack-web-app/security-audit.md`

**Dependencies**: G.1, G.2, G.3

**Responsible Agent**: `auth-security-architect`

**Completion Criteria**:
- [ ] SQL injection: Verified ORM (SQLModel) prevents injection (no raw SQL queries)
- [ ] XSS: Verified React auto-escapes user input (no `dangerouslySetInnerHTML` used)
- [ ] IDOR: Verified user ownership checks on all endpoints (tested in F.4)
- [ ] Password security: Verified bcrypt hashing, no plaintext passwords
- [ ] JWT security: Verified HS256 signing, secret key from environment, 15-minute expiration
- [ ] CORS: Verified proper origin configuration
- [ ] HTTPS: Noted as production deployment requirement (out of Phase II scope)
- [ ] Rate limiting: Noted as Phase III+ requirement
- [ ] Sensitive data: Verified no secrets in code or git history
- [ ] Audit report documents findings and mitigations

**Audit Report Template**:
```markdown
# Security Audit Report - Phase II

## Vulnerability Assessment

### SQL Injection
**Status**: MITIGATED
**Mitigation**: SQLModel ORM used exclusively. No raw SQL queries found.
**Evidence**: Grepped codebase for `execute(`, `raw_sql` - zero matches.

### XSS (Cross-Site Scripting)
**Status**: MITIGATED
**Mitigation**: React's JSX auto-escapes all user input.
**Evidence**: No `dangerouslySetInnerHTML` usage found.

### IDOR (Insecure Direct Object Reference)
**Status**: MITIGATED
**Mitigation**: User ownership enforced at database query level.
**Evidence**: Test F.4 validates cross-user access returns 404.

... (continue for all OWASP Top 10 risks)
```

---

### Task G.5: Performance Benchmarking

**Task ID**: `G.5`
**Priority**: P2
**Estimated Complexity**: Medium

**Description**:
Benchmark API response times to validate < 300ms requirement.

**Inputs**:
- [@specs/002-fullstack-web-app/spec.md](./spec.md) Non-functional Requirements (Performance: < 300ms)

**Outputs**:
- Performance report: `specs/002-fullstack-web-app/performance-report.md`

**Dependencies**: G.1

**Responsible Agent**: `test-qa-validator`

**Completion Criteria**:
- [ ] Benchmark registration endpoint (POST /api/auth/register): p95 < 300ms
- [ ] Benchmark login endpoint (POST /api/auth/login): p95 < 300ms
- [ ] Benchmark list todos endpoint (GET /api/{user_id}/tasks): p95 < 300ms
- [ ] Benchmark create todo endpoint (POST /api/{user_id}/tasks): p95 < 300ms
- [ ] Run with 10 concurrent users, 100 requests per endpoint
- [ ] Use tools: `ab` (Apache Bench), `wrk`, or `locust`
- [ ] Document results with p50, p95, p99 latencies
- [ ] Identify any endpoints exceeding 300ms threshold

**Benchmark Commands**:
```bash
# Example using Apache Bench
ab -n 100 -c 10 -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/$USER_ID/tasks

# Example using wrk
wrk -t4 -c10 -d30s --latency http://localhost:8000/api/health
```

---

### Task G.6: Update Root README for Phase II

**Task ID**: `G.6`
**Priority**: P1
**Estimated Complexity**: Simple

**Description**:
Update root README.md to document Phase II features, setup instructions, and architecture.

**Inputs**:
- [@specs/002-fullstack-web-app/spec.md](./spec.md) Executive Summary
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Architecture Overview

**Outputs**:
- Updated `README.md` at repository root

**Dependencies**: G.3

**Responsible Agent**: `hackathon-judge-reviewer`

**Completion Criteria**:
- [ ] README includes Phase II overview
- [ ] README documents technology stack (Next.js, FastAPI, PostgreSQL)
- [ ] README includes setup instructions:
  - Prerequisites (Node 20+, Python 3.13+, PostgreSQL)
  - Backend setup (venv, install deps, run migrations, start server)
  - Frontend setup (install deps, configure env vars, start dev server)
- [ ] README includes API documentation link (OpenAPI docs at /docs)
- [ ] README includes architecture diagram (optional but recommended)
- [ ] README includes Phase I vs Phase II comparison
- [ ] README includes hackathon submission information
- [ ] Markdown formatting is correct and renders properly on GitHub

**README Structure**:
```markdown
# Todo Application - Hackathon II

## Phase II: Full-Stack Web Application

Multi-user, secure, persistent todo application with authentication.

### Features
- User registration and login
- JWT-based authentication
- Personal todo lists (CRUD operations)
- Data persistence (PostgreSQL)
- Responsive web UI (mobile, tablet, desktop)
- User data isolation

### Technology Stack
- **Frontend**: Next.js 16+, TypeScript, Tailwind CSS
- **Backend**: FastAPI, SQLModel, PostgreSQL
- **Authentication**: JWT (HS256), bcrypt password hashing

### Quick Start
[Detailed setup instructions...]

### API Documentation
OpenAPI docs: http://localhost:8000/docs

### Testing
[Test execution instructions...]

### Architecture
[Architecture overview or diagram...]
```

---

### Task G.7: Create Architectural Decision Records

**Task ID**: `G.7`
**Priority**: P1
**Estimated Complexity**: Medium

**Description**:
Document significant architectural decisions made during Phase II implementation.

**Inputs**:
- [@specs/002-fullstack-web-app/plan.md](./plan.md) Section 8 "Key Architectural Decisions"

**Outputs**:
- ADR files in `history/adr/`:
  - `0001-monorepo-structure.md`
  - `0002-jwt-storage-localstorage.md`
  - `0003-user-ownership-enforcement.md`
  - `0004-neon-postgresql-serverless.md`
  - `0005-404-unauthorized-access.md`

**Dependencies**: G.6

**Responsible Agent**: `fullstack-spec-architect`

**Completion Criteria**:
- [ ] Each ADR follows template: Title, Status, Context, Decision, Consequences, Alternatives Considered
- [ ] ADR 0001: Monorepo structure (chosen over microrepo for unified development)
- [ ] ADR 0002: JWT in localStorage (chosen over httpOnly cookies for simplicity)
- [ ] ADR 0003: Multi-layer user ownership enforcement (DB + middleware + route handler)
- [ ] ADR 0004: Neon PostgreSQL (chosen over self-hosted for zero maintenance)
- [ ] ADR 0005: 404 for unauthorized access (chosen over 403 to prevent info leakage)
- [ ] Each ADR includes date, status (Accepted), and links to related specs

**ADR Template Example**:
```markdown
# ADR 0001: Monorepo Structure for Frontend and Backend

## Status
Accepted (2025-12-30)

## Context
Phase II requires both frontend (Next.js) and backend (FastAPI) components. We needed to decide between:
1. Separate repositories (microrepo)
2. Unified repository (monorepo)

## Decision
Use monorepo structure with separate `frontend/` and `backend/` directories.

## Consequences
**Positive:**
- Atomic commits affecting both layers
- Simplified CI/CD (single pipeline)
- Shared specs and documentation
- Easier onboarding for new developers

**Negative:**
- Larger repository size
- Requires clear directory boundaries
- CI must handle both Node and Python environments

## Alternatives Considered
- Separate repositories: Rejected due to complexity in syncing changes across repos and managing version compatibility.
```

---

### Task G.8: Hackathon Requirements Compliance Verification

**Task ID**: `G.8`
**Priority**: P0 (Blocking)
**Estimated Complexity**: Medium

**Description**:
Verify Phase II implementation meets all hackathon evaluation criteria.

**Inputs**:
- Hackathon evaluation rubric (if provided)
- [@specs/002-fullstack-web-app/spec.md](./spec.md) Success Criteria SC-001 through SC-010

**Outputs**:
- Compliance report: `specs/002-fullstack-web-app/hackathon-compliance.md`

**Dependencies**: G.7

**Responsible Agent**: `hackathon-judge-reviewer`

**Completion Criteria**:
- [ ] All 10 success criteria (SC-001 through SC-010) validated:
  - SC-001: Registration/login/first todo < 3 minutes ✓
  - SC-002: Users can register, create, update, complete, delete todos ✓
  - SC-003: Zero cross-user data leakage ✓
  - SC-004: All operations < 300ms (see performance report) ✓
  - SC-005: 100 concurrent users supported (load test) ✓
  - SC-006: Responsive UI (mobile/tablet/desktop) ✓
  - SC-007: Data persists across sessions ✓
  - SC-008: Phase I CLI still functional ✓
  - SC-009: Authentication enforced on all endpoints ✓
  - SC-010: User-friendly error messages ✓
- [ ] Spec-driven development process documented (PHRs created)
- [ ] All user stories tested and validated
- [ ] Architecture is judge-readable (README, ADRs, diagrams)
- [ ] No Phase III+ features implemented (phase discipline maintained)

**Compliance Report Template**:
```markdown
# Hackathon Compliance Report - Phase II

## Success Criteria Validation

### SC-001: User Onboarding Time
**Target**: < 3 minutes for registration, login, first todo
**Result**: PASS - Average 2 minutes 15 seconds (tested with 5 users)
**Evidence**: Manual testing video, E2E test timing logs

### SC-002: Complete CRUD Operations
**Target**: All todo operations functional
**Result**: PASS
**Evidence**: Tests F.2, F.3 validate all CRUD operations

... (continue for all 10 success criteria)

## Phase Discipline
✅ No Phase III+ features implemented
✅ OAuth deferred to Phase III
✅ Real-time sync deferred to Phase III
✅ Notifications deferred to Phase IV

## Spec-Driven Development Process
✅ Specification created (`spec.md`)
✅ Plan created (`plan.md`)
✅ Tasks created (`tasks.md` - this document)
✅ PHRs documented in `history/prompts/002-fullstack-web-app/`
✅ ADRs documented in `history/adr/`

## Judge-Facing Documentation
✅ README.md comprehensive and clear
✅ Architecture diagrams included
✅ API documentation at /docs
✅ Security audit report available
✅ Traceability matrix complete
```

---

### Task G.9: Create Final Prompt History Record

**Task ID**: `G.9`
**Priority**: P1
**Estimated Complexity**: Simple

**Description**:
Create PHR documenting the `/sp.tasks` task generation process.

**Inputs**:
- This tasks.md document
- User's `/sp.tasks` prompt

**Outputs**:
- `history/prompts/002-fullstack-web-app/0003-phase-2-task-generation.tasks.prompt.md`

**Dependencies**: G.8

**Responsible Agent**: `fullstack-spec-architect`

**Completion Criteria**:
- [ ] PHR follows template from `.specify/templates/phr-template.prompt.md`
- [ ] PHR includes complete user prompt (all task requirements)
- [ ] PHR includes response summary (number of tasks, phases, dependencies)
- [ ] PHR metadata: id=0003, stage=tasks, feature=002-fullstack-web-app
- [ ] PHR links to spec.md and plan.md
- [ ] PHR documents outcomes: 7 phases (A-G), 70+ atomic tasks, dependency graph complete
- [ ] PHR includes reflection on task breakdown approach

**PHR Content Highlights**:
- Prompt: User's `/sp.tasks` command with all requirements
- Response: Generated 72 atomic tasks across 7 phases (A: Setup, B: Database, C: Auth, D: Backend, E: Frontend, F: Integration, G: QA)
- Outcome: Complete task list ready for `/sp.implement`
- Reflection: Tasks ordered by dependency, all traceable to specs, Phase II boundaries maintained

---

### Task G.10: Final Code Review and Cleanup

**Task ID**: `G.10`
**Priority**: P1
**Estimated Complexity**: Medium

**Description**:
Perform final code review to ensure code quality, consistency, and documentation.

**Inputs**:
- All implemented code from Phase II

**Outputs**:
- Code review report with any necessary fixes applied

**Dependencies**: G.9

**Responsible Agent**: `hackathon-judge-reviewer`

**Completion Criteria**:
- [ ] No commented-out code blocks (remove or explain)
- [ ] No console.log or print statements in production code
- [ ] No hardcoded credentials or secrets
- [ ] All functions have docstrings/comments explaining purpose
- [ ] Code follows consistent style (Black for Python, Prettier for TypeScript)
- [ ] No unused imports or variables
- [ ] All TODO comments resolved or tracked as issues
- [ ] Git history is clean (no "WIP" or "temp" commits in main branch)
- [ ] All files have appropriate copyright/license headers (if required)

**Review Checklist**:
```bash
# Python code style check
cd backend
black . --check
mypy app/

# TypeScript code style check
cd frontend
npm run lint
npm run typecheck

# Search for common issues
grep -r "console.log" frontend/src/
grep -r "print(" backend/app/
grep -r "TODO" . | grep -v "node_modules" | grep -v "venv"
```

---

## Task Summary and Dependency Graph

### Task Count by Phase
- **Phase A (Setup)**: 6 tasks (A.1 - A.6)
- **Phase B (Database)**: 5 tasks (B.1 - B.5)
- **Phase C (Auth)**: 5 tasks (C.1 - C.5)
- **Phase D (Backend)**: 8 tasks (D.1 - D.8)
- **Phase E (Frontend)**: 11 tasks (E.1 - E.11)
- **Phase F (Integration)**: 5 tasks (F.1 - F.5)
- **Phase G (QA)**: 10 tasks (G.1 - G.10)

**Total**: 50 atomic, testable, traceable tasks

### Critical Path (Blocking Tasks)
```
A.1 → A.2 → A.6 (Frontend init)
A.1 → A.3 → A.5 → B.1 → B.2 → B.3 → B.4 → B.5 (Database layer)
B.3 → C.1 → C.2 → C.3 → C.4 → D.1 → D.2 (Auth flow)
D.2 → D.4 → D.5 → D.6 → D.7 (Backend CRUD)
A.6 → E.1 → E.3 → E.4 → E.6 → E.7 → E.10 (Frontend CRUD)
E.10 + D.7 → F.1 → F.2 → F.3 → F.4 (Integration)
F.4 → G.1 → G.3 → G.4 → G.8 (Validation)
```

### Parallel Execution Opportunities
- **Phase A**: A.2, A.3, A.4 can run in parallel after A.1
- **Phase C**: C.1, C.5 can run in parallel
- **Phase D**: D.3 can run in parallel with C tasks
- **Phase E**: E.2 can run anytime after dependencies
- **Phase G**: G.1, G.2 can run in parallel; G.6, G.7 can run in parallel

### Agent Workload Distribution
- `fastapi-backend-architect`: 18 tasks (B.1-B.5, C.5, D.1-D.8, F.1)
- `nextjs-frontend-architect`: 13 tasks (E.1-E.11, A.2, A.6)
- `auth-security-architect`: 7 tasks (C.1-C.4, F.4, F.5, G.4)
- `test-qa-validator`: 6 tasks (F.2, F.3, G.1, G.2, G.5)
- `hackathon-judge-reviewer`: 4 tasks (G.3, G.6, G.8, G.10)
- `fullstack-spec-architect`: 2 tasks (A.1, A.4, G.7, G.9)

---

## Execution Commands

### Phase-by-Phase Execution
```bash
# Execute all Phase A tasks (setup)
/sp.implement --phase A

# Execute all Phase B tasks (database)
/sp.implement --phase B

# Continue through phases...
```

### Single Task Execution
```bash
# Execute specific task by ID
/sp.implement --task A.1
/sp.implement --task B.1
```

### Parallel Execution (Advanced)
```bash
# Execute independent tasks in parallel
/sp.implement --tasks A.2,A.3,A.4 --parallel
```

---

## Success Metrics

### Definition of Done for Phase II
- [ ] All 50 tasks completed with status COMPLETED
- [ ] All completion criteria validated for each task
- [ ] All 40 functional requirements (FR-001 through FR-040) implemented
- [ ] All 10 success criteria (SC-001 through SC-010) validated
- [ ] All 5 user stories tested and passing
- [ ] Backend test coverage ≥ 80%
- [ ] Frontend test coverage ≥ 70%
- [ ] E2E tests passing for registration, login, and CRUD flows
- [ ] Security audit completed with no critical vulnerabilities
- [ ] Performance benchmarks < 300ms for all critical endpoints
- [ ] Documentation complete (README, ADRs, PHRs)
- [ ] Hackathon compliance report completed
- [ ] Zero Phase III+ features implemented (phase discipline maintained)

---

## Notes for Implementation

### Order of Execution Recommendation
1. **Start with Phase A** (foundation): Critical for all subsequent work
2. **Then Phase B and C in parallel** (database and auth can be developed independently)
3. **Then Phase D** (backend APIs depend on B and C)
4. **Then Phase E** (frontend depends on D for API contracts)
5. **Then Phase F** (integration depends on D and E)
6. **Finally Phase G** (validation depends on complete implementation)

### Testing Strategy
- **Unit tests**: Write alongside implementation (TDD approach)
- **Integration tests**: Write after completing each subsystem (auth, CRUD)
- **E2E tests**: Write after frontend-backend integration (Phase F)
- **Run test suites continuously**: After each task completion

### Risk Mitigation
- **Database connection issues**: Validate B.3 early with real PostgreSQL instance
- **CORS problems**: Test F.1 immediately after backend and frontend are running
- **Token expiration testing**: May require time mocking (document approach in C.3)
- **Performance bottlenecks**: Run G.5 early to identify issues before final validation

---

**Plan Status**: Ready for implementation via `/sp.implement`
**References**:
- Specification: [@specs/002-fullstack-web-app/spec.md](./spec.md)
- Implementation Plan: [@specs/002-fullstack-web-app/plan.md](./plan.md)
**Next Command**: `/sp.implement` to begin task execution
**Last Updated**: 2025-12-30
