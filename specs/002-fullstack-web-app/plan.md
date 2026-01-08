# Implementation Plan: Phase II – Todo Full-Stack Web Application

**Feature Branch**: `002-fullstack-web-app`
**Created**: 2025-12-30
**Status**: Planning
**References**: [@specs/002-fullstack-web-app/spec.md](./spec.md)

## Plan Overview

This implementation plan details the technical approach for building Phase II: a secure, multi-user, full-stack web todo application with persistent storage. The plan describes **HOW** the system will be implemented while remaining fully traceable to the approved Phase II specifications.

**Key Architectural Decisions**:
- Monorepo structure for unified development experience
- Next.js 16+ (App Router) for frontend SPA
- FastAPI for backend REST API
- Neon PostgreSQL with SQLModel ORM
- JWT-based stateless authentication
- User-scoped data isolation at database and API layers

---

## 1. Monorepo Architecture

### 1.1 Repository Structure

```
todo-app/
├── .env.example                    # Environment variable template
├── .env.local                      # Local development secrets (git-ignored)
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
├── docker-compose.yml              # Local development orchestration (optional)
│
├── frontend/                       # Next.js application
│   ├── .env.local                  # Frontend-specific env vars
│   ├── .gitignore
│   ├── next.config.ts              # Next.js configuration
│   ├── package.json                # Frontend dependencies
│   ├── tsconfig.json               # TypeScript configuration
│   ├── tailwind.config.ts          # Tailwind CSS configuration
│   ├── postcss.config.js
│   ├── public/                     # Static assets
│   ├── src/
│   │   ├── app/                    # Next.js App Router pages
│   │   │   ├── layout.tsx          # Root layout
│   │   │   ├── page.tsx            # Landing/login page
│   │   │   ├── register/
│   │   │   │   └── page.tsx        # Registration page
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx        # Authenticated todo dashboard
│   │   │   └── api/                # Better Auth API routes (if needed)
│   │   ├── components/             # Reusable UI components
│   │   │   ├── auth/               # Authentication components
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   ├── RegisterForm.tsx
│   │   │   │   └── LogoutButton.tsx
│   │   │   ├── todos/              # Todo components
│   │   │   │   ├── TodoList.tsx
│   │   │   │   ├── TodoItem.tsx
│   │   │   │   ├── TodoForm.tsx
│   │   │   │   └── EmptyState.tsx
│   │   │   └── ui/                 # Generic UI components
│   │   │       ├── Button.tsx
│   │   │       ├── Input.tsx
│   │   │       ├── Modal.tsx
│   │   │       └── Spinner.tsx
│   │   ├── lib/                    # Utility functions
│   │   │   ├── api.ts              # API client with auth headers
│   │   │   ├── auth.ts             # Better Auth configuration
│   │   │   └── utils.ts            # Helper functions
│   │   ├── types/                  # TypeScript type definitions
│   │   │   ├── todo.ts
│   │   │   └── user.ts
│   │   └── hooks/                  # Custom React hooks
│   │       ├── useAuth.ts          # Authentication state
│   │       └── useTodos.ts         # Todo data fetching
│   └── __tests__/                  # Frontend tests
│
├── backend/                        # FastAPI application
│   ├── .env                        # Backend-specific env vars (git-ignored)
│   ├── .gitignore
│   ├── requirements.txt            # Python dependencies
│   ├── requirements-dev.txt        # Development dependencies
│   ├── main.py                     # FastAPI application entry point
│   ├── alembic.ini                 # Database migration configuration
│   ├── alembic/                    # Migration scripts
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # Database connection setup
│   │   ├── models/                 # SQLModel database models
│   │   │   ├── __init__.py
│   │   │   ├── user.py             # User model
│   │   │   └── todo.py             # Todo model
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py             # User DTOs
│   │   │   ├── todo.py             # Todo DTOs
│   │   │   └── auth.py             # Auth DTOs
│   │   ├── auth/                   # Authentication logic
│   │   │   ├── __init__.py
│   │   │   ├── jwt.py              # JWT validation
│   │   │   └── dependencies.py     # Auth dependencies
│   │   ├── routers/                # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── auth.py             # /api/auth/* routes
│   │   │   └── todos.py            # /api/{user_id}/tasks/* routes
│   │   ├── services/               # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── user_service.py
│   │   │   └── todo_service.py
│   │   └── middleware/             # Custom middleware
│   │       ├── __init__.py
│   │       └── cors.py             # CORS configuration
│   └── tests/                      # Backend tests
│       ├── __init__.py
│       ├── conftest.py             # Pytest configuration
│       ├── test_auth.py
│       └── test_todos.py
│
├── specs/                          # Spec-Kit Plus structured specifications
│   ├── 001-phase1-todo-cli/        # Phase I specs (reference)
│   └── 002-fullstack-web-app/      # Phase II specs (current)
│       ├── spec.md
│       ├── plan.md (this file)
│       ├── tasks.md (to be generated)
│       └── checklists/
│
├── .claude/                        # Claude Code configuration
│   ├── agents/                     # Agent definitions
│   └── skills/                     # Skill library
│       ├── phase1/                 # Phase I skills (reusable)
│       └── phase2/                 # Phase II skills (current)
│
└── history/                        # Prompt History Records
    ├── adr/                        # Architecture Decision Records
    └── prompts/
        ├── 001-phase1-todo-cli/
        └── 002-fullstack-web-app/
```

### 1.2 Structure Rationale

**Monorepo Benefits**:
- **Unified Development**: Frontend and backend in one repository enables atomic commits affecting both layers
- **Shared Documentation**: Specs, ADRs, and PHRs apply to entire feature, not split across repos
- **Simplified CI/CD**: Single pipeline can build, test, and deploy both frontend and backend
- **Dependency Management**: Clear separation via subdirectories with independent `package.json` and `requirements.txt`

**Directory Organization**:
- **/frontend**: Self-contained Next.js app with its own dependencies and configuration
- **/backend**: Self-contained FastAPI app with independent Python environment
- **/specs**: Centralized specification documents accessible via `@specs/` references
- **/.claude**: Project-level agent and skill definitions
- **/history**: Cross-cutting documentation (ADRs, PHRs) for entire project

**Separation of Concerns**:
- Frontend concerns: UI components, routing, client-side state, API consumption
- Backend concerns: Business logic, data persistence, authentication, API contracts
- No direct database access from frontend (enforced architecturally)

---

## 2. Frontend Implementation Plan (Next.js + Better Auth)

### 2.1 Technology Stack

- **Framework**: Next.js 16+ with App Router
- **Language**: TypeScript 5.x
- **Authentication**: Better Auth library
- **Styling**: Tailwind CSS 3.x
- **HTTP Client**: Native `fetch` API with custom wrapper
- **State Management**: React Context API + hooks (no Redux needed for Phase II)
- **Form Handling**: React Hook Form (optional) or native controlled components

### 2.2 Application Structure

**App Router Pages**:
1. **`/` (Landing/Login)**: Public route, displays login form for unauthenticated users, redirects authenticated users to `/dashboard`
2. **`/register`**: Public route, displays registration form
3. **`/dashboard`**: Protected route, displays authenticated user's todo list

**Route Protection Strategy**:
- Create middleware (`middleware.ts`) to check for JWT token in localStorage
- Redirect unauthenticated users from `/dashboard` to `/`
- Redirect authenticated users from `/` to `/dashboard`
- Use Next.js middleware or client-side useEffect checks

### 2.3 Authentication Flow Implementation

**Registration Flow** (maps to FR-001, FR-002, FR-003):
1. User fills `<RegisterForm>` with email and password
2. Frontend validates email format and password length (min 8 chars) client-side
3. On submit, call `POST /api/auth/register` via API client
4. Backend response:
   - **Success (201)**: Auto-login or redirect to login page with success message
   - **Error (400)**: Display validation errors inline (e.g., "Invalid email format")
   - **Error (409)**: Display "This email is already registered"
5. Store JWT token in localStorage and redirect to `/dashboard`

**Login Flow** (maps to FR-004, FR-005, FR-006):
1. User fills `<LoginForm>` with email and password
2. On submit, call `POST /api/auth/login` via API client
3. Backend response:
   - **Success (200)**: Returns `{ access_token, user: { id, email } }`
   - **Error (401)**: Display "Invalid email or password"
4. Store `access_token` in localStorage under key `jwt_token`
5. Decode JWT client-side (using `jwt-decode` library) to extract `user_id` and `email` for UI display
6. Redirect to `/dashboard`

**Logout Flow** (maps to FR-007):
1. User clicks Logout button in navbar
2. Frontend removes JWT token from localStorage: `localStorage.removeItem('jwt_token')`
3. Clear any client-side user state (React Context)
4. Redirect to `/` (login page)

**Session Persistence** (maps to FR-039):
- On app initialization (root `layout.tsx`), check for `jwt_token` in localStorage
- If token exists, decode and validate expiration client-side
- If valid, populate authentication context and allow access to protected routes
- If expired, remove token and redirect to login

**Token Expiration Handling** (maps to FR-006):
- JWT tokens expire after 15 minutes (enforced server-side)
- When API call returns 401 with `expired_token` error:
  - Display modal: "Your session has expired. Please log in again."
  - Clear token from localStorage
  - Redirect to `/`

### 2.4 API Client Implementation

**`lib/api.ts` Structure**:
```typescript
// Base API client with authentication
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function apiClient(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem('jwt_token');

  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // Token expired or invalid
    localStorage.removeItem('jwt_token');
    window.location.href = '/'; // Redirect to login
    throw new Error('Authentication required');
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Request failed');
  }

  return response.json();
}

// Todo API methods (maps to FR-009 through FR-016, FR-029)
export const todoApi = {
  getAll: (userId: string) => apiClient(`/api/${userId}/tasks`),
  create: (userId: string, data: { title: string; description?: string }) =>
    apiClient(`/api/${userId}/tasks`, { method: 'POST', body: JSON.stringify(data) }),
  update: (userId: string, id: number, data: Partial<Todo>) =>
    apiClient(`/api/${userId}/tasks/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (userId: string, id: number) =>
    apiClient(`/api/${userId}/tasks/${id}`, { method: 'DELETE' }),
  toggleComplete: (userId: string, id: number, completed: boolean) =>
    apiClient(`/api/${userId}/tasks/${id}/complete`, { method: 'PATCH', body: JSON.stringify({ completed }) }),
};

// Auth API methods (maps to FR-001, FR-004)
export const authApi = {
  register: (email: string, password: string) =>
    apiClient('/api/auth/register', { method: 'POST', body: JSON.stringify({ email, password }) }),
  login: (email: string, password: string) =>
    apiClient('/api/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
};
```

### 2.5 Component Hierarchy

**Todo Dashboard Component Tree**:
```
<DashboardPage>
  <AuthLayout>                      // Enforces authentication
    <Navbar>                        // User email + Logout button
    <TodoDashboard>
      <TodoForm />                  // Add new todo form
      {todos.length === 0 ? (
        <EmptyState />              // "No todos yet" message
      ) : (
        <TodoList>
          {todos.map(todo => (
            <TodoItem                // Individual todo card
              key={todo.id}
              todo={todo}
              onToggle={handleToggle}
              onUpdate={handleUpdate}
              onDelete={handleDelete}
            />
          ))}
        </TodoList>
      )}
    </TodoDashboard>
  </AuthLayout>
</DashboardPage>
```

**Component Responsibilities**:
- **TodoForm**: Input fields for title and description, validation, submit button, maps to FR-009
- **TodoList**: Container for todo items, handles loading and empty states
- **TodoItem**: Displays todo with checkbox, edit/delete buttons, handles inline editing, maps to FR-012, FR-013, FR-015
- **EmptyState**: Displays helpful message when no todos exist, maps to Edge Case
- **Navbar**: Displays authenticated user's email and logout button

### 2.6 Responsive Design Strategy (maps to FR-033)

**Breakpoints** (Tailwind CSS classes):
- **Mobile**: `< 768px` (default, mobile-first)
- **Tablet**: `md:` prefix (`>= 768px`)
- **Desktop**: `lg:` prefix (`>= 1024px`)

**Layout Patterns**:
- **Mobile (320px-767px)**:
  - Single-column layout
  - Full-width todo items
  - Stacked form fields
  - Touch-friendly buttons (min 44px height)
  - Hamburger menu for user actions

- **Tablet (768px-1023px)**:
  - Max-width container (600px) centered
  - Two-column layout for todo form (title left, description right)
  - Inline user menu

- **Desktop (1024px+)**:
  - Max-width container (800px) centered
  - Side-by-side layout for completed/incomplete todos (optional)
  - Hover states for interactive elements

**Responsive Utilities**:
- Use Tailwind responsive prefixes: `text-sm md:text-base lg:text-lg`
- Hide non-essential elements on mobile: `hidden md:block`
- Adjust padding/margins: `p-4 md:p-6 lg:p-8`

### 2.7 Error Handling (maps to FR-035, FR-036)

**Loading States**:
- Display `<Spinner />` component during API calls
- Show skeleton loaders for todo list while loading
- Disable form submit buttons during submission

**Error Display Patterns**:
- **Inline validation errors**: Below input fields in red text
- **API errors**: Toast notifications or error banners at top of page
- **Network errors**: Modal with "Retry" button
- **Authentication errors**: Automatic redirect to login with message

**Error Messages** (maps to FR-008, FR-036):
- "Invalid email or password" (login failure)
- "This email is already registered" (registration duplicate)
- "Title cannot be empty" (validation error)
- "Network error. Your todo was not saved. Please try again." (network failure)
- "Your session has expired. Please log in again." (token expiration)

---

## 3. Backend Implementation Plan (FastAPI + JWT)

### 3.1 Technology Stack

- **Framework**: FastAPI 0.100+
- **Language**: Python 3.11+
- **ORM**: SQLModel (combines SQLAlchemy + Pydantic)
- **Database**: PostgreSQL 15+ (via Neon Serverless)
- **Authentication**: PyJWT for JWT handling, passlib for password hashing
- **Migrations**: Alembic
- **ASGI Server**: Uvicorn
- **Testing**: Pytest, httpx for async testing

### 3.2 Application Initialization

**`main.py` Structure**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_db_and_tables
from app.routers import auth, todos

app = FastAPI(title="Todo API", version="1.0.0")

# CORS middleware (maps to frontend-backend communication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database initialization
@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()

# Router registration
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(todos.router, prefix="/api", tags=["todos"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### 3.3 Database Configuration

**`app/config.py`**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str  # Neon PostgreSQL connection string
    JWT_SECRET_KEY: str  # Secret for signing JWTs
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 15

    class Config:
        env_file = ".env"

settings = Settings()
```

**`app/database.py`**:
```python
from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

# Create async engine for Neon PostgreSQL
engine = create_engine(settings.DATABASE_URL, echo=True)

def create_db_and_tables():
    """Initialize database tables (development only, use Alembic for production)"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency for database sessions"""
    with Session(engine) as session:
        yield session
```

### 3.4 Database Models (SQLModel)

**`app/models/user.py`** (maps to User entity in spec):
```python
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime
import uuid

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to todos (maps to FR-018, FR-021)
    todos: List["Todo"] = Relationship(back_populates="owner", cascade_delete=True)
```

**`app/models/todo.py`** (maps to Todo entity in spec):
```python
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import datetime
import uuid

class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: int = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)  # Maps to FR-018, FR-019
    title: str = Field(max_length=200)  # Maps to FR-009
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)  # Maps to FR-013
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Maps to FR-020
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user (maps to FR-018)
    owner: User = Relationship(back_populates="todos")
```

**Database Constraints** (maps to FR-019, FR-021):
- `user_id` with `NOT NULL` constraint enforced via `nullable=False`
- Foreign key `user_id → users.id` with `ON DELETE CASCADE` via `cascade_delete=True`
- Index on `user_id` for fast query performance (maps to success criteria SC-002)

### 3.5 Authentication Implementation

**`app/auth/jwt.py`** (maps to FR-004, FR-005, FR-006, FR-027):
```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.config import settings

def create_access_token(user_id: str) -> str:
    """Generate JWT token with user_id in payload (maps to FR-005)"""
    expires_delta = timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    expire = datetime.utcnow() + expires_delta

    payload = {
        "sub": str(user_id),  # Standard JWT claim for subject (user_id)
        "exp": expire,        # Expiration time (maps to FR-006)
        "iat": datetime.utcnow(),  # Issued at time
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def verify_token(token: str) -> str:
    """Validate JWT and extract user_id (maps to FR-027, FR-028)"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise ValueError("Invalid token payload")
        return user_id
    except JWTError:
        raise ValueError("Invalid or expired token")
```

**`app/auth/dependencies.py`** (maps to FR-022, FR-023, FR-024):
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.jwt import verify_token

security = HTTPBearer()

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extract and validate JWT token from Authorization header.
    Returns authenticated user_id.
    Maps to FR-022, FR-023, FR-024, FR-028.
    """
    token = credentials.credentials
    try:
        user_id = verify_token(token)
        return user_id
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
```

**Password Hashing** (maps to FR-003):
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using bcrypt (maps to FR-003)"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)
```

### 3.6 API Router: Authentication

**`app/routers/auth.py`** (maps to FR-001, FR-002, FR-004, FR-008):
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.auth.jwt import create_access_token
from app.auth.dependencies import hash_password, verify_password
import re

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    session: Session = Depends(get_session)
):
    """
    User registration endpoint.
    Maps to FR-001, FR-002, FR-003.
    """
    # Validate email format (maps to FR-002)
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    # Validate password length (maps to FR-001)
    if len(request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )

    # Check for duplicate email
    statement = select(User).where(User.email == request.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This email is already registered"
        )

    # Create user with hashed password (maps to FR-003)
    hashed_password = hash_password(request.password)
    user = User(email=request.email, hashed_password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)

    # Auto-login: issue JWT token
    access_token = create_access_token(str(user.id))
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user={"id": str(user.id), "email": user.email}
    )

@router.post("/login")
async def login(
    request: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    User login endpoint.
    Maps to FR-004, FR-005, FR-006, FR-008.
    """
    # Find user by email
    statement = select(User).where(User.email == request.email)
    user = session.exec(statement).first()

    # Verify password (maps to FR-008: no distinction between wrong email vs wrong password)
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT token (maps to FR-004, FR-005, FR-006)
    access_token = create_access_token(str(user.id))
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user={"id": str(user.id), "email": user.email}
    )
```

### 3.7 API Router: Todos

**`app/routers/todos.py`** (maps to FR-009 through FR-016, FR-029, FR-025, FR-026):
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.database import get_session
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from app.auth.dependencies import get_current_user_id
import uuid

router = APIRouter()

@router.get("/{user_id}/tasks", response_model=List[TodoResponse])
async def list_todos(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    List all todos for authenticated user.
    Maps to FR-010, FR-011, FR-024, FR-025, FR-028.
    """
    # Enforce user ownership: ignore user_id from URL, use JWT user_id (maps to FR-028)
    statement = select(Todo).where(Todo.user_id == uuid.UUID(current_user_id)).order_by(Todo.created_at.desc())
    todos = session.exec(statement).all()
    return todos

@router.post("/{user_id}/tasks", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    user_id: str,
    todo_data: TodoCreate,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Create new todo for authenticated user.
    Maps to FR-009, FR-024, FR-028.
    """
    # Ignore user_id from URL, use JWT user_id (maps to FR-028)
    todo = Todo(**todo_data.dict(), user_id=uuid.UUID(current_user_id))
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@router.get("/{user_id}/tasks/{task_id}", response_model=TodoResponse)
async def get_todo(
    user_id: str,
    task_id: int,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Get specific todo (must belong to authenticated user).
    Maps to FR-025, FR-026.
    """
    statement = select(Todo).where(
        Todo.id == task_id,
        Todo.user_id == uuid.UUID(current_user_id)
    )
    todo = session.exec(statement).first()

    # Return 404 (not 403) to avoid information leakage (maps to FR-026)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    return todo

@router.put("/{user_id}/tasks/{task_id}", response_model=TodoResponse)
async def update_todo(
    user_id: str,
    task_id: int,
    todo_data: TodoUpdate,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Update todo (must belong to authenticated user).
    Maps to FR-012, FR-025.
    """
    statement = select(Todo).where(
        Todo.id == task_id,
        Todo.user_id == uuid.UUID(current_user_id)
    )
    todo = session.exec(statement).first()

    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    # Update fields
    for key, value in todo_data.dict(exclude_unset=True).items():
        setattr(todo, key, value)

    todo.updated_at = datetime.utcnow()
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TodoResponse)
async def toggle_complete(
    user_id: str,
    task_id: int,
    completed: bool,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Toggle todo completion status.
    Maps to FR-013, FR-014, FR-025.
    """
    statement = select(Todo).where(
        Todo.id == task_id,
        Todo.user_id == uuid.UUID(current_user_id)
    )
    todo = session.exec(statement).first()

    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    todo.completed = completed
    todo.updated_at = datetime.utcnow()
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user_id: str,
    task_id: int,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Delete todo (must belong to authenticated user).
    Maps to FR-015, FR-016, FR-025.
    """
    statement = select(Todo).where(
        Todo.id == task_id,
        Todo.user_id == uuid.UUID(current_user_id)
    )
    todo = session.exec(statement).first()

    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    session.delete(todo)
    session.commit()
    return None
```

### 3.8 Request/Response Schemas

**`app/schemas/auth.py`**:
```python
from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict
```

**`app/schemas/todo.py`**:
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TodoCreate(BaseModel):
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None

class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

---

## 4. Database Schema & Migration Plan

### 4.1 PostgreSQL Schema (Neon)

**Table: `users`** (maps to User entity):
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_users_email ON users(email);
```

**Table: `todos`** (maps to Todo entity):
```sql
CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_todos_user_id ON todos(user_id);
CREATE INDEX idx_todos_user_id_completed ON todos(user_id, completed);
```

**Constraints**:
- `users.email` UNIQUE constraint (maps to FR-001)
- `todos.user_id` NOT NULL constraint (maps to FR-019)
- Foreign key `todos.user_id → users.id` ON DELETE CASCADE (maps to FR-021)

**Indexes** (maps to success criteria SC-002):
- `idx_users_email`: Fast login lookups
- `idx_todos_user_id`: Fast user-scoped queries
- `idx_todos_user_id_completed`: Optimized filtered queries (e.g., "show my incomplete todos")

### 4.2 Alembic Migration Strategy

**Initial Migration** (create tables):
```bash
# Initialize Alembic
alembic init alembic

# Generate initial migration
alembic revision --autogenerate -m "Initial schema: users and todos tables"

# Apply migration
alembic upgrade head
```

**Migration File Structure** (`alembic/versions/001_initial_schema.py`):
```python
def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)

    # Create todos table
    op.create_table(
        'todos',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('completed', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_todos_user_id', 'todos', ['user_id'])
    op.create_index('idx_todos_user_id_completed', 'todos', ['user_id', 'completed'])

def downgrade():
    op.drop_table('todos')
    op.drop_table('users')
```

**Environment Configuration** (Neon Connection):
- Store Neon PostgreSQL connection string in `.env` file:
  ```
  DATABASE_URL=postgresql://username:password@ep-xyz.us-east-2.aws.neon.tech/todo_db?sslmode=require
  ```
- Use environment variable in `app/database.py` via `settings.DATABASE_URL`

---

## 5. Component Interactions & Data Flow

### 5.1 Architecture Diagram (Text Representation)

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ LoginForm    │  │ RegisterForm │  │ TodoDashboard│          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                  │
│                            │                                     │
│                   ┌────────▼────────┐                            │
│                   │   API Client    │ (lib/api.ts)               │
│                   │ + JWT Storage   │                            │
│                   └────────┬────────┘                            │
│                            │ Authorization: Bearer <JWT>         │
└────────────────────────────┼─────────────────────────────────────┘
                             │ HTTPS
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                       BACKEND (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   CORS Middleware                        │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│                         │                                        │
│  ┌──────────────────────▼───────────────────────────────────┐   │
│  │  JWT Verification Middleware (auth/dependencies.py)      │   │
│  │  • Extract Authorization header                          │   │
│  │  • Validate JWT signature                                │   │
│  │  • Extract user_id from payload                          │   │
│  │  • Inject into request context                           │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│                         │                                        │
│      ┌──────────────────┼──────────────────┐                    │
│      │                  │                  │                    │
│  ┌───▼────────┐   ┌─────▼──────┐   ┌──────▼─────┐              │
│  │ Auth Router│   │Todo Router │   │Health Check│              │
│  │/api/auth/* │   │/api/{user}/│   │  /health   │              │
│  └───┬────────┘   └─────┬──────┘   └────────────┘              │
│      │                  │                                        │
│  ┌───▼──────────────────▼───┐                                   │
│  │   Services Layer         │ (Business Logic)                  │
│  │ • user_service.py        │                                   │
│  │ • todo_service.py        │                                   │
│  └───┬──────────────────────┘                                   │
│      │                                                           │
│  ┌───▼──────────────────────┐                                   │
│  │  Database Session        │ (SQLModel)                        │
│  │  • User model            │                                   │
│  │  • Todo model            │                                   │
│  └───┬──────────────────────┘                                   │
│      │ SQL Queries (user-filtered)                              │
└──────┼───────────────────────────────────────────────────────────┘
       │
┌──────▼───────────────────────────────────────────────────────────┐
│              DATABASE (Neon PostgreSQL)                          │
│  ┌─────────────────┐          ┌─────────────────┐               │
│  │  users table    │          │  todos table    │               │
│  │ • id (PK, UUID) │◄─────────│ • id (PK, int)  │               │
│  │ • email (unique)│  FK      │ • user_id (FK)  │               │
│  │ • hashed_pass   │          │ • title         │               │
│  │ • created_at    │          │ • description   │               │
│  └─────────────────┘          │ • completed     │               │
│                               │ • created_at    │               │
│                               │ • updated_at    │               │
│                               └─────────────────┘               │
└──────────────────────────────────────────────────────────────────┘
```

### 5.2 Request Flow Example: Create Todo

**Step-by-Step Flow** (maps to User Story 1, FR-009, FR-024, FR-028):

1. **User Action**: User fills todo form and clicks "Add Todo"
2. **Frontend Validation**: Client-side checks title is not empty
3. **API Call**: `todoApi.create(userId, { title: "Buy groceries", description: "Milk, eggs" })`
4. **HTTP Request**:
   ```
   POST /api/alice-uuid/tasks
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   Content-Type: application/json

   { "title": "Buy groceries", "description": "Milk, eggs" }
   ```
5. **Backend CORS Check**: CORS middleware verifies origin
6. **JWT Verification**:
   - Extract token from Authorization header
   - Validate signature using JWT_SECRET_KEY
   - Decode payload: `{ "sub": "alice-uuid", "exp": 1640000000 }`
   - Check expiration: `exp > current_time`
   - Inject `current_user_id = "alice-uuid"` into request context
7. **Router Handler** (`create_todo`):
   - Ignore `user_id` from URL path (`/api/alice-uuid/tasks`)
   - Use `current_user_id` from JWT validation (maps to FR-028)
   - Create Todo object: `Todo(user_id=current_user_id, title="Buy groceries", ...)`
8. **Database Insert**:
   ```sql
   INSERT INTO todos (user_id, title, description, completed, created_at, updated_at)
   VALUES ('alice-uuid', 'Buy groceries', 'Milk, eggs', false, NOW(), NOW())
   RETURNING *;
   ```
9. **Response**:
   ```json
   HTTP 201 Created
   {
     "id": 123,
     "title": "Buy groceries",
     "description": "Milk, eggs",
     "completed": false,
     "created_at": "2025-12-30T12:00:00Z",
     "updated_at": "2025-12-30T12:00:00Z"
   }
   ```
10. **Frontend Update**: Add new todo to local state, re-render `<TodoList>`

---

## 6. Deployment & Environment Configuration

### 6.1 Environment Variables

**Frontend (`.env.local`)**:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend (`.env`)**:
```
DATABASE_URL=postgresql://username:password@ep-xyz.us-east-2.aws.neon.tech/todo_db?sslmode=require
JWT_SECRET_KEY=your-secret-key-minimum-32-characters-long
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=15
```

**Security Note**: Never commit `.env` files. Use `.env.example` as template.

### 6.2 Local Development Setup

**Prerequisites**:
- Node.js 18+ (frontend)
- Python 3.11+ (backend)
- Neon PostgreSQL account (or local PostgreSQL)

**Frontend Setup**:
```bash
cd frontend
npm install
npm run dev  # Runs on http://localhost:3000
```

**Backend Setup**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head  # Run migrations
uvicorn main:app --reload  # Runs on http://localhost:8000
```

### 6.3 Production Deployment (Optional for Phase II)

**Frontend (Vercel)**:
- Deploy Next.js app to Vercel
- Set environment variable: `NEXT_PUBLIC_API_URL=https://api.yourdomain.com`

**Backend (Render/Railway)**:
- Deploy FastAPI app to Render or Railway
- Set environment variables: `DATABASE_URL`, `JWT_SECRET_KEY`
- Run migrations: `alembic upgrade head`

**Database (Neon)**:
- Use Neon-provided connection string
- Enable SSL mode (`sslmode=require`)

---

## 7. Testing Strategy

### 7.1 Backend Tests (Pytest)

**Test Coverage**:
- Authentication flows (register, login, token validation)
- CRUD operations (create, read, update, delete todos)
- Authorization checks (user cannot access other users' todos)
- Edge cases (invalid tokens, missing fields, duplicate emails)

**Example Test** (`tests/test_todos.py`):
```python
def test_create_todo_requires_authentication(client):
    """Test that creating a todo without JWT returns 401"""
    response = client.post("/api/user-id/tasks", json={"title": "Test"})
    assert response.status_code == 401

def test_user_cannot_access_other_users_todos(client, auth_headers_alice, auth_headers_bob):
    """Test data isolation (maps to FR-025, FR-026)"""
    # Alice creates a todo
    response = client.post("/api/alice/tasks", headers=auth_headers_alice, json={"title": "Alice's todo"})
    alice_todo_id = response.json()["id"]

    # Bob tries to access Alice's todo
    response = client.get(f"/api/bob/tasks/{alice_todo_id}", headers=auth_headers_bob)
    assert response.status_code == 404  # Not 403 (maps to FR-026)
```

### 7.2 Frontend Tests (Jest + React Testing Library)

**Test Coverage**:
- Component rendering (forms, todo items, empty states)
- User interactions (form submission, todo toggle, delete)
- API integration (mocked API calls)
- Routing and navigation

**Example Test** (`__tests__/TodoForm.test.tsx`):
```typescript
test('displays validation error for empty title', () => {
  render(<TodoForm onSubmit={jest.fn()} />);

  const submitButton = screen.getByText('Add Todo');
  fireEvent.click(submitButton);

  expect(screen.getByText('Title cannot be empty')).toBeInTheDocument();
});
```

---

## 8. Key Design Decisions & Rationale

### Decision 1: Monorepo Structure
**Rationale**: Simplifies coordination between frontend and backend, enables atomic commits, centralizes documentation. Alternative (separate repos) would require complex orchestration for feature development.

### Decision 2: Next.js App Router
**Rationale**: Modern Next.js pattern with built-in routing, layouts, and server components. More scalable than Pages Router for future phases (SSR, API routes).

### Decision 3: JWT in localStorage
**Rationale**: Simple implementation for Phase II. Trade-off: XSS risk mitigated by Content Security Policy. Phase III will migrate to HttpOnly cookies for enhanced security.

### Decision 4: UUID for User IDs
**Rationale**: Non-sequential, prevents user enumeration, globally unique. Better security than auto-increment integers. Trade-off: Slightly larger storage footprint.

### Decision 5: user_id in URL but ignored
**Rationale**: RESTful API convention (`/api/{user_id}/tasks`), but actual user_id comes from JWT for security. Frontend consistency with REST principles.

### Decision 6: 404 instead of 403 for unauthorized access
**Rationale**: Prevents information leakage about resource existence (maps to FR-026). Attacker cannot enumerate valid todo IDs.

### Decision 7: SQLModel (not pure SQLAlchemy)
**Rationale**: Combines SQLAlchemy ORM with Pydantic validation, reducing boilerplate. Single model definition for database and API schemas.

### Decision 8: Neon PostgreSQL (not local PostgreSQL)
**Rationale**: Serverless, easy setup, free tier sufficient for Phase II. Alternative (local PostgreSQL) requires manual setup and maintenance.

---

## 9. Phase Boundaries & Future Extensibility

### What Phase II Delivers
- Authenticated multi-user web application
- Full CRUD todo operations
- Persistent PostgreSQL storage
- JWT-based stateless authentication
- Responsive UI (mobile, tablet, desktop)
- User data isolation (zero cross-user access)

### Extensibility Hooks for Phase III+
- **OAuth Integration**: Better Auth supports OAuth providers (Google, GitHub) via configuration, no architectural changes needed
- **WebSocket Support**: FastAPI supports WebSocket endpoints alongside REST endpoints, can add `/ws` routes for real-time sync
- **Email Service**: Add email service layer for password reset and verification emails
- **Token Refresh**: Extend JWT flow with refresh tokens (separate table or Redis cache)

### What Changes in Phase III
- **Authentication**: Add OAuth providers, password reset, email verification
- **Real-time**: Add WebSocket endpoints for live todo sync
- **Notifications**: Add push notifications table and service

### What Stays the Same
- Monorepo structure
- Core REST API endpoints
- Database schema (additive changes only)
- Frontend component architecture

---

## 10. Implementation Checklist

### Backend Implementation
- [ ] Setup FastAPI project structure
- [ ] Configure environment variables and settings
- [ ] Create SQLModel models (User, Todo)
- [ ] Implement JWT authentication (create, verify tokens)
- [ ] Create authentication router (/api/auth/*)
- [ ] Create todo router (/api/{user_id}/tasks/*)
- [ ] Add CORS middleware
- [ ] Setup Neon PostgreSQL connection
- [ ] Create Alembic migrations
- [ ] Add request/response schema validation
- [ ] Implement error handling
- [ ] Write backend tests (pytest)

### Frontend Implementation
- [ ] Setup Next.js project with App Router
- [ ] Configure Tailwind CSS
- [ ] Create authentication pages (login, register)
- [ ] Implement Better Auth integration
- [ ] Create API client with JWT headers
- [ ] Build todo dashboard page
- [ ] Create todo components (form, list, item)
- [ ] Implement responsive layouts
- [ ] Add loading and error states
- [ ] Implement route protection
- [ ] Handle token expiration
- [ ] Write frontend tests (Jest)

### Integration & Testing
- [ ] Test full registration → login → create todo flow
- [ ] Verify user data isolation (cross-user access blocked)
- [ ] Test responsive design on mobile/tablet/desktop
- [ ] Verify token expiration handling
- [ ] Test error scenarios (network failures, validation errors)
- [ ] Confirm data persists across logout/login
- [ ] Performance test (100 concurrent users)
- [ ] Security audit (JWT validation, SQL injection, XSS)

### Documentation
- [ ] Update README with setup instructions
- [ ] Document API endpoints (OpenAPI/Swagger)
- [ ] Create deployment guide
- [ ] Document environment variables
- [ ] Add troubleshooting guide

---

## 11. Success Criteria Verification

**Traceability to Spec** (maps to Success Criteria SC-001 through SC-010):

| Success Criterion | Implementation Evidence |
|-------------------|-------------------------|
| SC-001: Registration + login + first todo < 3 minutes | Minimal UI with inline validation, auto-login after registration, one-click todo creation |
| SC-002: 100 concurrent users, <300ms response | Database indexes on user_id, stateless JWT (no server-side sessions), async FastAPI |
| SC-003: Zero cross-user data leakage | User ownership enforced at JWT validation layer, database foreign keys, 404 responses |
| SC-004: 95% first-attempt success rate | Inline validation, clear error messages, intuitive UI |
| SC-005: Mobile-functional (320px viewport) | Tailwind responsive classes, touch-friendly buttons (44px), mobile-first design |
| SC-006: Multi-device data consistency <1s | Database persistence, API fetches on page load, no client-side caching issues |
| SC-007: 99% uptime | Neon PostgreSQL reliability, FastAPI error handling, graceful degradation |
| SC-008: Clear error messages | Custom error responses with actionable messages (no generic "error" strings) |
| SC-009: Data persists across sessions | PostgreSQL storage, JWT token in localStorage for session persistence |
| SC-010: Loading states prevent confusion | Spinners during API calls, skeleton loaders, disabled buttons during submission |

---

## 12. Next Steps

**After Plan Approval**:
1. Run `/sp.tasks` to generate implementation tasks from this plan
2. Implement backend (FastAPI + database) first (dependency for frontend)
3. Implement frontend (Next.js) with API mocking if backend not ready
4. Integration testing with both layers running
5. Security audit and performance testing
6. Documentation and deployment

**Dependencies for Implementation**:
- Neon PostgreSQL account setup
- Environment variable configuration
- Node.js and Python environments installed

**Estimated Implementation Timeline**:
- Backend: ~15-20 tasks
- Frontend: ~15-20 tasks
- Integration & Testing: ~5-10 tasks
- **Total**: ~35-50 tasks (exact breakdown in `/sp.tasks`)

---

**Plan Status**: Ready for task generation via `/sp.tasks`
**References**: [@specs/002-fullstack-web-app/spec.md](./spec.md)
**Next Command**: `/sp.tasks` to convert this plan into actionable implementation tasks
