# Implementation Execution Plan: Phase II – Todo Full-Stack Web Application

**Feature Branch**: `002-fullstack-web-app`
**Created**: 2025-12-30
**Status**: Ready for Execution
**References**:
- Tasks: [@specs/002-fullstack-web-app/tasks.md](./tasks.md)
- Plan: [@specs/002-fullstack-web-app/plan.md](./plan.md)
- Spec: [@specs/002-fullstack-web-app/spec.md](./spec.md)

---

## Executive Summary

This document provides a **step-by-step execution guide** for implementing all 50 tasks in Phase II. Each section includes:
- Exact commands to run
- Expected outputs
- Validation checkpoints
- Rollback procedures
- Agent coordination instructions

**Estimated Total Time**: 6-8 hours with parallel execution, 15-20 hours sequential

---

## Execution Prerequisites

### Required Tools
```bash
# Verify installations
node --version        # Should be 20.x or higher
npm --version         # Should be 10.x or higher
python --version      # Should be 3.13.x
git --version         # Any recent version

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Environment Setup
```bash
# Ensure you're on the correct branch
git checkout 002-fullstack-web-app
git pull origin 002-fullstack-web-app

# Verify working directory
pwd  # Should end with /Todo-app
```

### Database Setup (Required for Phase B+)
```bash
# Option 1: Neon PostgreSQL (Recommended - serverless)
# Create account at https://neon.tech
# Create new project named "todo-app-phase2"
# Copy connection string

# Option 2: Local PostgreSQL (Development)
# Install PostgreSQL 15+
# Create database:
createdb todo_app_dev

# Get connection string format:
# postgresql://username:password@localhost:5432/todo_app_dev
```

---

## PHASE A: Monorepo & Project Setup

**Duration**: ~30 minutes
**Agent**: `fullstack-spec-architect`
**Parallelization**: Tasks A.2, A.3, A.4 can run in parallel after A.1

### Task A.1: Create Monorepo Directory Structure

**Command Sequence**:
```bash
# Create frontend directory structure
mkdir -p frontend/src/app/{register,dashboard}
mkdir -p frontend/src/components/{auth,todos,ui}
mkdir -p frontend/src/lib
mkdir -p frontend/src/types
mkdir -p frontend/src/hooks
mkdir -p frontend/public
mkdir -p frontend/__tests__/{components,pages,integration,e2e}

# Create backend directory structure
mkdir -p backend/app/{models,schemas,auth,routers,services,middleware}
mkdir -p backend/tests
mkdir -p backend/alembic/versions

# Create supporting directories
mkdir -p specs/002-fullstack-web-app/checklists
mkdir -p .claude/{agents,skills}/phase2
mkdir -p history/{adr,prompts/002-fullstack-web-app}

# Add .gitkeep to empty directories
find . -type d -empty -exec touch {}/.gitkeep \;
```

**Validation**:
```bash
# Verify structure
ls -la frontend/src
ls -la backend/app

# Expected: Should see all subdirectories created
# If any missing, re-run mkdir commands for those specific paths
```

**Status**: ☐ Task A.1 Complete

---

### Task A.2: Configure Frontend Package.json

**Command Sequence**:
```bash
cd frontend

# Initialize Next.js project with TypeScript
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias "@/*"

# When prompted:
# ✓ Would you like to use TypeScript? Yes
# ✓ Would you like to use ESLint? Yes
# ✓ Would you like to use Tailwind CSS? Yes
# ✓ Would you like to use `src/` directory? No (we already created structure)
# ✓ Would you like to use App Router? Yes
# ✓ Would you like to customize the default import alias? Yes (@/*)

# Install additional dependencies
npm install better-auth jose jwt-decode

# Install dev dependencies
npm install -D @types/node @testing-library/react @testing-library/jest-dom jest jest-environment-jsdom
```

**Manual File Creation**: `frontend/tsconfig.json`
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "jsx": "preserve",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "allowJs": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "incremental": true,
    "paths": {
      "@/*": ["./src/*"]
    },
    "plugins": [
      {
        "name": "next"
      }
    ]
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

**Manual File Creation**: `frontend/next.config.ts`
```typescript
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
};

export default nextConfig;
```

**Manual File Creation**: `frontend/tailwind.config.ts`
```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
      },
    },
  },
  plugins: [],
};

export default config;
```

**Manual File Creation**: `frontend/postcss.config.js`
```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

**Validation**:
```bash
cd frontend
npm install  # Should complete without errors
npx tsc --noEmit  # Should pass (may have warnings about missing files)
```

**Status**: ☐ Task A.2 Complete

---

### Task A.3: Configure Backend Requirements

**Command Sequence**:
```bash
cd backend

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlmodel==0.0.22
psycopg2-binary==2.9.10
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
alembic==1.13.3
python-dotenv==1.0.1
pydantic[email]==2.10.3
python-multipart==0.0.20
EOF

# Create requirements-dev.txt
cat > requirements-dev.txt << 'EOF'
pytest==8.3.4
pytest-asyncio==0.24.0
httpx==0.28.1
black==24.10.0
mypy==1.13.0
ruff==0.8.4
EOF
```

**Validation**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Verify imports
python -c "import fastapi; import sqlmodel; import jose; print('All imports successful')"
```

**Status**: ☐ Task A.3 Complete

---

### Task A.4: Create Environment Configuration Templates

**Command Sequence**:
```bash
# Frontend .env.example
cat > frontend/.env.example << 'EOF'
# Backend API URL
# Development: http://localhost:8000
# Production: Your deployed backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# Backend .env.example
cat > backend/.env.example << 'EOF'
# Database connection string
# Format: postgresql://user:password@host:port/database
# Neon example: postgresql://user:password@ep-example.us-east-2.aws.neon.tech/neondb?sslmode=require
DATABASE_URL=postgresql://username:password@localhost:5432/todo_app_dev

# JWT Configuration
# IMPORTANT: Generate a secure random secret for production
# Example: openssl rand -hex 32
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=15

# CORS Configuration
# Development: http://localhost:3000
# Production: Your frontend domain
FRONTEND_URL=http://localhost:3000
EOF

# Update root .gitignore
cat >> .gitignore << 'EOF'

# Environment files
.env
.env.local
*.env
!.env.example

# Python
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/

# Node
node_modules/
.next/
out/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Testing
.coverage
htmlcov/
.pytest_cache/
EOF
```

**Validation**:
```bash
# Verify .env.example files exist
cat frontend/.env.example
cat backend/.env.example

# Verify .gitignore updated
grep "\.env$" .gitignore  # Should find .env
```

**Status**: ☐ Task A.4 Complete

---

### Task A.5: Initialize Backend FastAPI Application

**Command Sequence**:
```bash
cd backend
source venv/bin/activate
```

**Manual File Creation**: `backend/app/__init__.py`
```python
# Empty file to make app a package
```

**Manual File Creation**: `backend/app/config.py`
```python
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 15
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

**Manual File Creation**: `backend/main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(
    title="Todo API",
    version="2.0.0",
    description="Phase II: Multi-user Todo Application with Authentication"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "2.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Create Backend .env** (from .env.example):
```bash
cd backend
cp .env.example .env

# Edit .env with your actual DATABASE_URL
# nano .env  # or vim, code, etc.
# Replace DATABASE_URL with your Neon or local PostgreSQL connection string
# Generate secure JWT_SECRET_KEY: openssl rand -hex 32
```

**Validation**:
```bash
cd backend
source venv/bin/activate

# Start server in background
uvicorn main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Wait for startup
sleep 3

# Test health endpoint
curl http://localhost:8000/health
# Expected: {"status":"ok","version":"2.0.0"}

# Test CORS
curl -X OPTIONS http://localhost:8000/health \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -v 2>&1 | grep "Access-Control-Allow-Origin"
# Expected: Access-Control-Allow-Origin: http://localhost:3000

# Stop server
kill $SERVER_PID
```

**Status**: ☐ Task A.5 Complete

---

### Task A.6: Initialize Frontend Next.js Application

**Manual File Creation**: `frontend/src/app/layout.tsx`
```typescript
import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Todo App - Phase II',
  description: 'Multi-user todo application with authentication',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">
        {children}
      </body>
    </html>
  );
}
```

**Manual File Creation**: `frontend/src/app/page.tsx`
```typescript
export default function HomePage() {
  return (
    <main className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Todo App - Phase II
        </h1>
        <p className="text-gray-600">
          Login Page (Placeholder)
        </p>
      </div>
    </main>
  );
}
```

**Manual File Creation**: `frontend/src/app/globals.css`
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --background: #ffffff;
  --foreground: #171717;
}

body {
  color: var(--foreground);
  background: var(--background);
  font-family: Arial, Helvetica, sans-serif;
}
```

**Create Frontend .env.local**:
```bash
cd frontend
cp .env.example .env.local

# .env.local is already configured with:
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Validation**:
```bash
cd frontend

# Start dev server in background
npm run dev &
NEXT_PID=$!

# Wait for startup
sleep 5

# Test frontend
curl http://localhost:3000 | grep "Todo App"
# Expected: HTML containing "Todo App - Phase II"

# Test Tailwind (check if styles load)
curl http://localhost:3000 | grep "min-h-screen"
# Expected: HTML containing Tailwind classes

# Stop server
kill $NEXT_PID
```

**Status**: ☐ Task A.6 Complete

---

## CHECKPOINT A: Phase A Validation

**Run all validations**:
```bash
# Directory structure
ls frontend/src/app backend/app

# Frontend dependencies
cd frontend && npm list next react tailwindcss

# Backend dependencies
cd ../backend && source venv/bin/activate && pip list | grep fastapi

# Backend server starts
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 &
sleep 2 && curl http://localhost:8000/health
kill %1

# Frontend server starts
cd frontend && npm run dev &
sleep 5 && curl http://localhost:3000
kill %1
```

**Expected Results**:
- ✅ All directories exist
- ✅ All dependencies installed
- ✅ Backend health check returns {"status":"ok"}
- ✅ Frontend renders HTML with "Todo App"

**If any failures**: Review and re-execute failed tasks before proceeding.

---

## PHASE B: Database & Persistence Layer

**Duration**: ~45 minutes
**Agent**: `fastapi-backend-architect`
**Dependencies**: Requires Phase A complete
**Prerequisites**: PostgreSQL database created and DATABASE_URL configured in backend/.env

### Task B.1: Create SQLModel User Model

**Manual File Creation**: `backend/app/models/__init__.py`
```python
from .user import User
from .todo import Todo

__all__ = ["User", "Todo"]
```

**Manual File Creation**: `backend/app/models/user.py`
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid


class User(SQLModel, table=True):
    """User model for authentication and todo ownership."""

    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255, nullable=False)
    hashed_password: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to todos
    todos: List["Todo"] = Relationship(back_populates="owner", cascade_delete=True)
```

**Validation**:
```bash
cd backend
source venv/bin/activate

# Test model import
python -c "from app.models.user import User; print('User model imported successfully')"

# Test model instantiation
python << 'EOF'
from app.models.user import User
import uuid

user = User(
    id=uuid.uuid4(),
    email="test@example.com",
    hashed_password="hashed_pw_123"
)
print(f"User created: {user.email}")
assert user.email == "test@example.com"
print("✓ User model validation passed")
EOF
```

**Status**: ☐ Task B.1 Complete

---

### Task B.2: Create SQLModel Todo Model

**Manual File Creation**: `backend/app/models/todo.py`
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
import uuid


class Todo(SQLModel, table=True):
    """Todo model with user ownership."""

    __tablename__ = "todos"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user
    owner: "User" = Relationship(back_populates="todos")
```

**Update** `backend/app/models/user.py` (add import):
```python
# At the top, update import
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .todo import Todo
```

**Validation**:
```bash
cd backend
source venv/bin/activate

# Test model import
python -c "from app.models.todo import Todo; from app.models.user import User; print('Models imported successfully')"

# Test model relationships
python << 'EOF'
from app.models.todo import Todo
from app.models.user import User
import uuid

user_id = uuid.uuid4()
todo = Todo(
    user_id=user_id,
    title="Test Todo",
    description="Test description",
    completed=False
)
print(f"Todo created: {todo.title}")
assert todo.title == "Test Todo"
assert todo.user_id == user_id
assert todo.completed is False
print("✓ Todo model validation passed")
EOF
```

**Status**: ☐ Task B.2 Complete

---

### Task B.3: Configure Database Connection

**Manual File Creation**: `backend/app/database.py`
```python
from sqlmodel import SQLModel, create_engine, Session
from app.config import settings
from typing import Generator

# Create engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL logging in development
    pool_size=5,
    max_overflow=10,
)


def create_db_and_tables():
    """Create all database tables. Use for development only."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency function to get database session."""
    with Session(engine) as session:
        yield session
```

**Validation**:
```bash
cd backend
source venv/bin/activate

# Test database connection
python << 'EOF'
from app.database import engine, create_db_and_tables, get_session
from sqlmodel import SQLModel

print("Testing database connection...")

# Test engine creation
print(f"✓ Engine created: {engine.url}")

# Test session creation
session = next(get_session())
print(f"✓ Session created: {type(session)}")
session.close()

# Create tables (this will actually create them in your database)
create_db_and_tables()
print("✓ Tables created successfully")

print("\n✓ Database connection validation passed")
EOF

# Verify tables exist in database
python << 'EOF'
from app.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Tables in database: {tables}")
assert "users" in tables, "users table not found"
assert "todos" in tables, "todos table not found"
print("✓ Both users and todos tables exist")
EOF
```

**Status**: ☐ Task B.3 Complete

---

### Task B.4: Initialize Alembic for Migrations

**Command Sequence**:
```bash
cd backend
source venv/bin/activate

# Initialize Alembic
alembic init alembic
```

**Edit** `backend/alembic.ini`:
```ini
# Find the line with sqlalchemy.url and replace with:
# sqlalchemy.url = driver://user:pass@localhost/dbname

# Comment it out and add:
# sqlalchemy.url =
```

**Edit** `backend/alembic/env.py`:
```python
# Replace entire file content:
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
from pathlib import Path

# Add parent directory to path to import app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from sqlmodel import SQLModel
from app.models import User, Todo  # Import all models

# this is the Alembic Config object
config = context.config

# Set sqlalchemy.url from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**Validation**:
```bash
cd backend
source venv/bin/activate

# Test alembic can connect to database
alembic current
# Expected: No error, shows current revision (empty initially)

# Test autogenerate
alembic revision --autogenerate -m "Test migration"
# Expected: Creates a migration file in alembic/versions/
# You can delete this test migration after validation

# Clean up test migration
rm alembic/versions/*_test_migration.py
```

**Status**: ☐ Task B.4 Complete

---

### Task B.5: Create Initial Database Migration

**Command Sequence**:
```bash
cd backend
source venv/bin/activate

# Drop existing tables (if created in B.3)
python << 'EOF'
from app.database import engine
from sqlmodel import SQLModel
SQLModel.metadata.drop_all(engine)
print("✓ Existing tables dropped")
EOF

# Generate initial migration
alembic revision --autogenerate -m "Initial schema: users and todos tables"

# Review the generated migration file
# It should be in alembic/versions/xxxx_initial_schema.py
ls -la alembic/versions/

# Apply migration
alembic upgrade head

# Verify current revision
alembic current
```

**Validation**:
```bash
cd backend
source venv/bin/activate

# Verify tables exist
python << 'EOF'
from app.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Tables: {tables}")

# Verify users table structure
users_columns = [col['name'] for col in inspector.get_columns('users')]
print(f"Users columns: {users_columns}")
assert 'id' in users_columns
assert 'email' in users_columns
assert 'hashed_password' in users_columns
assert 'created_at' in users_columns

# Verify todos table structure
todos_columns = [col['name'] for col in inspector.get_columns('todos')]
print(f"Todos columns: {todos_columns}")
assert 'id' in todos_columns
assert 'user_id' in todos_columns
assert 'title' in todos_columns
assert 'completed' in todos_columns

# Verify foreign key
foreign_keys = inspector.get_foreign_keys('todos')
print(f"Foreign keys: {foreign_keys}")
assert len(foreign_keys) > 0
assert foreign_keys[0]['referred_table'] == 'users'

print("\n✓ Initial migration validation passed")
EOF

# Test rollback
alembic downgrade -1
alembic current  # Should show no revision

# Re-apply migration
alembic upgrade head
alembic current  # Should show current revision
```

**Status**: ☐ Task B.5 Complete

---

## CHECKPOINT B: Phase B Validation

**Run all validations**:
```bash
cd backend
source venv/bin/activate

# Verify models import
python -c "from app.models import User, Todo; print('✓ Models import')"

# Verify database connection
python -c "from app.database import engine, get_session; print('✓ Database connection')"

# Verify tables exist
python -c "from sqlalchemy import inspect; from app.database import engine; print('✓ Tables:', inspect(engine).get_table_names())"

# Verify migration system
alembic current
```

**Expected Results**:
- ✅ User and Todo models import without errors
- ✅ Database engine connects successfully
- ✅ Tables "users" and "todos" exist
- ✅ Foreign key relationship exists
- ✅ Alembic shows current migration

---

## PHASE C: Authentication & Security

**Duration**: ~60 minutes
**Agent**: `auth-security-architect`
**Dependencies**: Requires Phase A and Phase B complete

### Task C.1: Implement Password Hashing Utilities

**Manual File Creation**: `backend/app/auth/__init__.py`
```python
# Empty file to make auth a package
```

**Manual File Creation**: `backend/app/auth/password.py`
```python
from passlib.context import CryptContext

# Create password context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        plain_password: The plaintext password to hash

    Returns:
        The hashed password

    Raises:
        ValueError: If password is empty
    """
    if not plain_password:
        raise ValueError("Password cannot be empty")

    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password.

    Args:
        plain_password: The plaintext password to verify
        hashed_password: The hashed password to check against

    Returns:
        True if password matches, False otherwise
    """
    if not plain_password or not hashed_password:
        return False

    return pwd_context.verify(plain_password, hashed_password)
```

**Validation**:
```bash
cd backend
source venv/bin/activate

# Test password hashing
python << 'EOF'
from app.auth.password import hash_password, verify_password

# Test hashing
plain = "SecurePassword123"
hashed = hash_password(plain)

print(f"Plain password: {plain}")
print(f"Hashed password: {hashed[:50]}...")

# Verify hash format (bcrypt starts with $2b$)
assert hashed.startswith("$2b$"), "Hash should use bcrypt format"

# Test verification - correct password
assert verify_password(plain, hashed) is True, "Correct password should verify"

# Test verification - wrong password
assert verify_password("WrongPassword", hashed) is False, "Wrong password should not verify"

# Test empty password handling
try:
    hash_password("")
    assert False, "Should raise ValueError for empty password"
except ValueError:
    pass

print("\n✓ Password hashing validation passed")
EOF
```

**Status**: ☐ Task C.1 Complete

---

### Task C.2: Implement JWT Token Creation

**Manual File Creation**: `backend/app/auth/jwt.py`
```python
from jose import jwt
from datetime import datetime, timedelta
from app.config import settings


def create_access_token(user_id: str) -> str:
    """
    Create a JWT access token for a user.

    Args:
        user_id: User ID to encode in token (as string)

    Returns:
        JWT token string
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

    payload = {
        "sub": user_id,  # Subject (user ID)
        "exp": expire,   # Expiration time
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return token
```

**Validation**:
```bash
cd backend
source venv/bin/activate

# Test JWT token creation
python << 'EOF'
from app.auth.jwt import create_access_token
from jose import jwt
from app.config import settings
import time

user_id = "123e4567-e89b-12d3-a456-426614174000"
token = create_access_token(user_id)

print(f"User ID: {user_id}")
print(f"Token: {token[:50]}...")

# Decode token (without verification for inspection)
payload = jwt.decode(
    token,
    settings.JWT_SECRET_KEY,
    algorithms=[settings.JWT_ALGORITHM]
)

print(f"Payload: {payload}")

# Verify payload structure
assert payload["sub"] == user_id, "Token should contain user_id in 'sub'"
assert "exp" in payload, "Token should have expiration"

# Verify expiration is in future
current_time = time.time()
assert payload["exp"] > current_time, "Token should not be expired"

# Verify expiration is less than 16 minutes (15 min + buffer)
assert payload["exp"] < current_time + (16 * 60), "Token should expire within 15 minutes"

print("\n✓ JWT token creation validation passed")
EOF
```

**Status**: ☐ Task C.2 Complete

---

### Task C.3: Implement JWT Token Verification

**Manual File Creation**: `backend/app/auth/exceptions.py`
```python
class InvalidTokenError(Exception):
    """Raised when JWT token is invalid."""
    pass


class ExpiredTokenError(Exception):
    """Raised when JWT token has expired."""
    pass
```

**Update** `backend/app/auth/jwt.py` (add verification function):
```python
# Add these imports at the top
from jose import jwt, JWTError, ExpiredSignatureError
from app.auth.exceptions import InvalidTokenError, ExpiredTokenError

# Add this function after create_access_token
def verify_token(token: str) -> str:
    """
    Verify a JWT token and extract user_id.

    Args:
        token: JWT token string to verify

    Returns:
        User ID (as string)

    Raises:
        InvalidTokenError: If token is invalid
        ExpiredTokenError: If token has expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        user_id: str = payload.get("sub")
        if user_id is None:
            raise InvalidTokenError("Token payload missing 'sub' field")

        return user_id

    except ExpiredSignatureError:
        raise ExpiredTokenError("Token has expired")
    except JWTError as e:
        raise InvalidTokenError(f"Invalid token: {str(e)}")
```

**Validation**:
```bash
cd backend
source venv/bin/activate

# Test JWT token verification
python << 'EOF'
from app.auth.jwt import create_access_token, verify_token
from app.auth.exceptions import InvalidTokenError, ExpiredTokenError

user_id = "123e4567-e89b-12d3-a456-426614174000"

# Test 1: Valid token
token = create_access_token(user_id)
verified_user_id = verify_token(token)
assert verified_user_id == user_id, "Should extract correct user_id"
print("✓ Valid token verification passed")

# Test 2: Invalid token
try:
    verify_token("invalid.token.here")
    assert False, "Should raise InvalidTokenError"
except InvalidTokenError:
    print("✓ Invalid token raises InvalidTokenError")

# Test 3: Malformed token
try:
    verify_token("not-a-jwt")
    assert False, "Should raise InvalidTokenError"
except InvalidTokenError:
    print("✓ Malformed token raises InvalidTokenError")

# Note: Testing expired tokens requires time manipulation or waiting
# For now, we verify the exception type exists
print("✓ ExpiredTokenError exception defined")

print("\n✓ JWT token verification validation passed")
EOF
```

**Status**: ☐ Task C.3 Complete

---

### Task C.4: Create Authentication Dependency

**Manual File Creation**: `backend/app/auth/dependencies.py`
```python
from fastapi import Header, HTTPException, status
from app.auth.jwt import verify_token
from app.auth.exceptions import InvalidTokenError, ExpiredTokenError


def get_current_user_id(authorization: str = Header(...)) -> str:
    """
    FastAPI dependency to extract and verify user_id from JWT token.

    Args:
        authorization: Authorization header (format: "Bearer <token>")

    Returns:
        User ID as string

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )

    # Extract token from "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Bearer <token>"
        )

    token = parts[1]

    try:
        user_id = verify_token(token)
        return user_id
    except ExpiredTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again."
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
```

**Validation**:
```bash
cd backend
source venv/bin/activate

# Test authentication dependency
python << 'EOF'
from app.auth.dependencies import get_current_user_id
from app.auth.jwt import create_access_token
from fastapi import HTTPException

user_id = "123e4567-e89b-12d3-a456-426614174000"
token = create_access_token(user_id)
authorization_header = f"Bearer {token}"

# Test 1: Valid authorization header
result = get_current_user_id(authorization_header)
assert result == user_id, "Should extract correct user_id"
print("✓ Valid authorization header accepted")

# Test 2: Missing header
try:
    get_current_user_id("")
    assert False, "Should raise HTTPException for missing header"
except HTTPException as e:
    assert e.status_code == 401
    print("✓ Missing header raises 401")

# Test 3: Invalid format (no "Bearer")
try:
    get_current_user_id(token)  # Just token without "Bearer"
    assert False, "Should raise HTTPException for invalid format"
except HTTPException as e:
    assert e.status_code == 401
    print("✓ Invalid format raises 401")

# Test 4: Invalid token
try:
    get_current_user_id("Bearer invalid.token")
    assert False, "Should raise HTTPException for invalid token"
except HTTPException as e:
    assert e.status_code == 401
    print("✓ Invalid token raises 401")

print("\n✓ Authentication dependency validation passed")
EOF
```

**Status**: ☐ Task C.4 Complete

---

### Task C.5: Create Pydantic Schemas for Authentication

**Manual File Creation**: `backend/app/schemas/__init__.py`
```python
# Empty file to make schemas a package
```

**Manual File Creation**: `backend/app/schemas/auth.py`
```python
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request schema for user registration."""
    email: EmailStr
    password: str = Field(min_length=8, description="Password must be at least 8 characters")


class LoginRequest(BaseModel):
    """Request schema for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User information in responses."""
    id: str
    email: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Response schema for authentication endpoints."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
```

**Validation**:
```bash
cd backend
source venv/bin/activate

# Test schemas
python << 'EOF'
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from pydantic import ValidationError

# Test 1: Valid registration request
valid_register = RegisterRequest(
    email="test@example.com",
    password="password123"
)
assert valid_register.email == "test@example.com"
print("✓ Valid RegisterRequest accepted")

# Test 2: Invalid email
try:
    RegisterRequest(email="invalid-email", password="password123")
    assert False, "Should raise ValidationError for invalid email"
except ValidationError:
    print("✓ Invalid email rejected")

# Test 3: Short password
try:
    RegisterRequest(email="test@example.com", password="short")
    assert False, "Should raise ValidationError for short password"
except ValidationError:
    print("✓ Short password rejected")

# Test 4: Valid login request
valid_login = LoginRequest(
    email="test@example.com",
    password="anypassword"
)
assert valid_login.email == "test@example.com"
print("✓ Valid LoginRequest accepted")

# Test 5: TokenResponse structure
user = UserResponse(id="123", email="test@example.com")
token_response = TokenResponse(
    access_token="token123",
    user=user
)
assert token_response.token_type == "bearer"
print("✓ TokenResponse structure valid")

print("\n✓ Authentication schemas validation passed")
EOF
```

**Status**: ☐ Task C.5 Complete

---

## CHECKPOINT C: Phase C Validation

**Run all validations**:
```bash
cd backend
source venv/bin/activate

# Verify password utilities
python -c "from app.auth.password import hash_password, verify_password; h = hash_password('test'); assert verify_password('test', h); print('✓ Password utilities')"

# Verify JWT utilities
python -c "from app.auth.jwt import create_access_token, verify_token; t = create_access_token('123'); assert verify_token(t) == '123'; print('✓ JWT utilities')"

# Verify dependencies
python -c "from app.auth.dependencies import get_current_user_id; print('✓ Auth dependencies')"

# Verify schemas
python -c "from app.schemas.auth import RegisterRequest, LoginRequest; print('✓ Auth schemas')"
```

**Expected Results**:
- ✅ Password hashing and verification works
- ✅ JWT creation and verification works
- ✅ Authentication dependency imports successfully
- ✅ Schemas validate input correctly

---

## Continue to Phase D...

Due to length constraints, I'll create a summary of the remaining phases. The pattern continues similarly for:

- **Phase D**: Backend API Implementation (8 tasks)
- **Phase E**: Frontend Application (11 tasks)
- **Phase F**: Integration & E2E Flow (5 tasks)
- **Phase G**: QA, Validation & Documentation (10 tasks)

Would you like me to:
1. Continue with Phase D in detail?
2. Create abbreviated execution guides for Phases D-G?
3. Generate shell scripts to automate task execution?
