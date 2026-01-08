# Skill: relational-schema-design

## 1. Skill Name
`relational-schema-design`

## 2. Purpose
Define normalized, performant relational database schemas aligned with feature specifications, establishing tables, columns, data types, constraints, relationships, and indexes to support authenticated multi-user applications with data integrity.

## 3. Applicable Agents
- **fastapi-backend-architect** (primary)
- fullstack-spec-architect (cross-layer data model coordination)
- auth-security-architect (user table design, foreign keys)

## 4. Inputs
- **Feature Requirements**: User stories and data needs
- **Data Ownership Rules**: User-scoped data enforcement requirements
- **API Contracts**: Request/response models from REST API specs
- **Authentication Model**: User identity structure (id, email, password)
- **Phase Scope**: Phase 2 boundaries (no sharing, collaboration yet)

## 5. Outputs
- **Database Schema Specification**: Tables, columns, types, constraints
- **Entity Relationship Diagram (ERD)**: Visual representation of schema
- **Migration Scripts Outline**: Create table statements (Alembic/migrations)
- **Index Strategy**: Performance indexes for common queries
- **Data Integrity Rules**: Foreign keys, NOT NULL, uniqueness constraints
- **Sample Data Specification**: Test data for development and QA

## 6. Scope & Boundaries

### In Scope
- Table definitions (users, todos)
- Column specifications (names, types, constraints)
- Primary keys and foreign keys
- Uniqueness constraints (unique emails)
- NOT NULL constraints (required fields)
- Default values (timestamps, booleans)
- Indexes for query performance (user_id, email)
- ON DELETE CASCADE for referential integrity

### Out of Scope
- Denormalization strategies (Phase 3+ optimization)
- Full-text search indexes (Phase 3+)
- Database replication/sharding (Phase 4+)
- Stored procedures or triggers (prefer application logic)
- Database-specific optimizations (target PostgreSQL primarily)

## 7. Reusability Notes
- **Phase 2**: Basic users + todos schema
- **Phase 3**: Extends with notifications, OAuth providers tables
- **Phase 4**: Scales to collaboration (todos_collaborators, permissions)
- **Phase 5**: Adds AI conversation history tables
- **Cross-Project**: Normalized schema patterns reusable for any authenticated app

### Reusability Mechanisms
- Schema evolution via migrations (additive changes preferred)
- Extensibility hooks (JSON columns for flexible metadata)
- Normalized design supports future joins (no duplication)
- Consistent naming conventions (snake_case, plural tables)

## 8. Dependencies

### Upstream Dependencies
- `data-ownership-enforcement` (user_id foreign key requirements)
- `user-identity-propagation` (user identity fields needed)
- Feature specifications (data fields required)

### Downstream Dependencies
- `rest-api-contract-definition` (API models map to DB schema)
- Backend implementation (database models, queries)
- Database migration tasks (Alembic scripts)

### Parallel Dependencies
- `jwt-auth-flow-specification` (user authentication fields)

## 9. Quality Expectations

### Normalization
- Third Normal Form (3NF) as baseline
- No redundant data (DRY principle)
- Atomic columns (no comma-separated values)

### Integrity
- Foreign keys enforce relationships
- NOT NULL for required fields
- Uniqueness constraints where appropriate
- ON DELETE behaviors explicit (CASCADE, SET NULL, RESTRICT)

### Performance
- Indexes on foreign keys (user_id)
- Indexes on frequently queried columns (email)
- Balance: no over-indexing (write performance cost)

### Clarity
- Self-documenting table/column names
- Consistent naming (snake_case, singular vs plural conventions)
- Comments for non-obvious design decisions

## 10. Example Usage (Spec-Level)

### Scenario: Relational Schema for Phase 2 Authenticated Todo App

---

#### Table 1: users

**Purpose:** Store registered user accounts for authentication and ownership

**Schema:**
```sql
CREATE TABLE users (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email         VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  name          VARCHAR(100) NULL,
  created_at    TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE UNIQUE INDEX idx_users_email ON users(email);
```

**Column Specifications:**

| Column        | Type          | Constraints              | Purpose                                    |
|---------------|---------------|--------------------------|--------------------------------------------|
| id            | UUID          | PRIMARY KEY, DEFAULT     | Unique user identifier (JWT sub claim)     |
| email         | VARCHAR(255)  | NOT NULL, UNIQUE         | User login credential, must be unique      |
| password_hash | VARCHAR(255)  | NOT NULL                 | Bcrypt hashed password (never plaintext)   |
| name          | VARCHAR(100)  | NULL                     | Optional display name                      |
| created_at    | TIMESTAMP     | NOT NULL, DEFAULT NOW()  | Account creation timestamp                 |
| updated_at    | TIMESTAMP     | NOT NULL, DEFAULT NOW()  | Last profile update timestamp              |

**Design Decisions:**

1. **UUID for Primary Key:**
   - Non-sequential (security: prevents user enumeration)
   - Globally unique (supports distributed systems in future)
   - Used in JWT claims (sub: user_id)

2. **Email Uniqueness:**
   - UNIQUE constraint enforces one account per email
   - Index on email for fast login lookups (SELECT WHERE email = ?)
   - Case sensitivity: Application layer normalizes to lowercase before insert

3. **Password Storage:**
   - password_hash column (never store plaintext passwords)
   - Bcrypt or Argon2 hashing (Better Auth handles this)
   - 255 characters sufficient for hash output

4. **Timestamps:**
   - created_at: Immutable, set on insert
   - updated_at: Updated on every profile modification (Phase 3+)
   - DEFAULT NOW() ensures always populated

---

#### Table 2: todos

**Purpose:** Store user-owned todo items with full CRUD support

**Schema:**
```sql
CREATE TABLE todos (
  id          SERIAL PRIMARY KEY,
  user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title       VARCHAR(200) NOT NULL,
  description TEXT NULL,
  completed   BOOLEAN NOT NULL DEFAULT FALSE,
  created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_todos_user_id ON todos(user_id);
CREATE INDEX idx_todos_user_id_completed ON todos(user_id, completed);
```

**Column Specifications:**

| Column      | Type          | Constraints                            | Purpose                                    |
|-------------|---------------|----------------------------------------|--------------------------------------------|
| id          | SERIAL        | PRIMARY KEY                            | Auto-incrementing todo identifier          |
| user_id     | UUID          | NOT NULL, FOREIGN KEY, ON DELETE CASCADE | Owner of this todo (enforces ownership)   |
| title       | VARCHAR(200)  | NOT NULL                               | Todo title (required, max 200 chars)       |
| description | TEXT          | NULL                                   | Optional detailed description              |
| completed   | BOOLEAN       | NOT NULL, DEFAULT FALSE                | Completion status (false = pending)        |
| created_at  | TIMESTAMP     | NOT NULL, DEFAULT NOW()                | Todo creation timestamp                    |
| updated_at  | TIMESTAMP     | NOT NULL, DEFAULT NOW()                | Last modification timestamp                |

**Design Decisions:**

1. **SERIAL Primary Key:**
   - Auto-incrementing integer (simple, efficient)
   - Sequential IDs acceptable for todos (no security concern)
   - Alternative: UUID (if distributed system planned)

2. **Foreign Key to users:**
   - user_id REFERENCES users(id): Enforces referential integrity
   - NOT NULL: Every todo must have an owner
   - ON DELETE CASCADE: If user deleted, their todos deleted automatically
   - Index on user_id: Fast queries (SELECT WHERE user_id = ?)

3. **Title vs Description:**
   - title: Short, required (max 200 chars) - VARCHAR for performance
   - description: Long, optional - TEXT for unlimited length

4. **Completed Boolean:**
   - Default FALSE: New todos start as incomplete
   - Simple boolean (not status enum) for Phase 2
   - Phase 3+ could extend to status ENUM('pending', 'in_progress', 'completed', 'archived')

5. **Composite Index (user_id, completed):**
   - Optimizes query: SELECT WHERE user_id = ? AND completed = ?
   - Common use case: "Show my incomplete todos"
   - Covers both filters without additional index

---

#### Entity Relationship Diagram (ERD)

**Diagram Specification:**
```
┌──────────────────────────┐
│ users                    │
├──────────────────────────┤
│ id (UUID) PK             │
│ email (VARCHAR) UNIQUE   │
│ password_hash (VARCHAR)  │
│ name (VARCHAR) NULL      │
│ created_at (TIMESTAMP)   │
│ updated_at (TIMESTAMP)   │
└──────────────────────────┘
           │
           │ 1
           │
           │ user_id (FK)
           │
           │ N
           ▼
┌──────────────────────────┐
│ todos                    │
├──────────────────────────┤
│ id (SERIAL) PK           │
│ user_id (UUID) FK        │
│ title (VARCHAR)          │
│ description (TEXT) NULL  │
│ completed (BOOLEAN)      │
│ created_at (TIMESTAMP)   │
│ updated_at (TIMESTAMP)   │
└──────────────────────────┘

Relationship: One-to-Many
- One user can have many todos
- Each todo belongs to exactly one user
- ON DELETE CASCADE: Deleting user deletes their todos
```

---

#### Index Strategy

**Index 1: users.email (Unique Index)**
```sql
CREATE UNIQUE INDEX idx_users_email ON users(email);

Purpose: Fast login lookups
Query: SELECT * FROM users WHERE email = 'user@example.com'
Benefit: O(log n) lookup instead of O(n) table scan
```

**Index 2: todos.user_id (Foreign Key Index)**
```sql
CREATE INDEX idx_todos_user_id ON todos(user_id);

Purpose: Fast user-scoped queries
Query: SELECT * FROM todos WHERE user_id = '550e8400-...'
Benefit: Supports GET /api/todos (list user's todos)
```

**Index 3: todos.(user_id, completed) (Composite Index)**
```sql
CREATE INDEX idx_todos_user_id_completed ON todos(user_id, completed);

Purpose: Fast filtered user queries
Query: SELECT * FROM todos WHERE user_id = '...' AND completed = false
Benefit: "Show my incomplete todos" query optimized
Note: Also covers user_id-only queries (leftmost prefix)
```

**Index Trade-offs:**
- Indexes speed up reads but slow down writes
- Phase 2: Read-heavy workload (listing todos more common than creating)
- 3 indexes acceptable (not over-indexed)
- Phase 3+ could add indexes on created_at for sorting

---

#### Data Integrity Constraints

**Constraint 1: User Email Uniqueness**
```sql
email VARCHAR(255) NOT NULL UNIQUE

Enforcement: Database prevents duplicate emails
Error: INSERT with duplicate email raises UNIQUE constraint violation
API Behavior: Catch exception, return 409 Conflict
```

**Constraint 2: Todo Ownership (Foreign Key)**
```sql
user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE

Enforcement:
  - Cannot insert todo with non-existent user_id (FK violation)
  - Cannot set user_id to NULL (NOT NULL)
  - Deleting user cascades to delete their todos (ON DELETE CASCADE)

Benefits:
  - Referential integrity guaranteed
  - No orphaned todos
  - Automatic cleanup
```

**Constraint 3: Required Fields**
```sql
users.email NOT NULL
users.password_hash NOT NULL
todos.user_id NOT NULL
todos.title NOT NULL
todos.completed NOT NULL

Enforcement: Database rejects NULL values for these columns
API Behavior: Validation at API layer before database insert
```

**Constraint 4: Default Values**
```sql
todos.completed DEFAULT FALSE
users.created_at DEFAULT NOW()
users.updated_at DEFAULT NOW()
todos.created_at DEFAULT NOW()
todos.updated_at DEFAULT NOW()

Benefit: Fields populated automatically if not specified
```

---

#### Migration Strategy (Alembic/SQLAlchemy)

**Migration 001: Initial Schema**
```
Operation: Create tables users and todos
File: migrations/001_initial_schema.py

Up Migration:
  1. CREATE TABLE users
  2. CREATE UNIQUE INDEX idx_users_email
  3. CREATE TABLE todos
  4. CREATE INDEX idx_todos_user_id
  5. CREATE INDEX idx_todos_user_id_completed

Down Migration (Rollback):
  1. DROP TABLE todos (CASCADE)
  2. DROP TABLE users (CASCADE)
```

**Future Migrations (Phase 3+):**
```
Migration 002: Add OAuth provider column
  ALTER TABLE users ADD COLUMN auth_provider VARCHAR(50) DEFAULT 'email'

Migration 003: Add notifications table
  CREATE TABLE notifications (...)

Migration 004: Add todos_collaborators table (Phase 4)
  CREATE TABLE todos_collaborators (todo_id, user_id, permission_level)
```

---

#### Sample Data for Development

**Sample Users:**
```sql
INSERT INTO users (email, password_hash, name) VALUES
  ('alice@example.com', '$2b$12$...hash...', 'Alice'),
  ('bob@example.com', '$2b$12$...hash...', 'Bob'),
  ('charlie@example.com', '$2b$12$...hash...', NULL);
```

**Sample Todos (Alice's):**
```sql
INSERT INTO todos (user_id, title, description, completed) VALUES
  ('alice-uuid', 'Buy groceries', 'Milk, eggs, bread', false),
  ('alice-uuid', 'Finish Phase 2', 'Complete full-stack todo app', false),
  ('alice-uuid', 'Review PRs', NULL, true);
```

**Sample Todos (Bob's):**
```sql
INSERT INTO todos (user_id, title, description, completed) VALUES
  ('bob-uuid', 'Prepare presentation', 'Hackathon demo slides', false),
  ('bob-uuid', 'Test authentication', 'Verify JWT flow end-to-end', true);
```

---

#### Database Technology: PostgreSQL (Neon)

**Choice Justification:**
- PostgreSQL: Industry-standard, mature, feature-rich
- Neon: Serverless PostgreSQL, easy setup, free tier
- SQLModel: Python ORM for type-safe queries
- Alembic: Migration tool for schema versioning

**Connection String Format:**
```
postgresql://user:password@host:port/database
Example (Neon):
postgresql://user:pass@ep-cool-name-123456.us-east-2.aws.neon.tech/todo_db?sslmode=require
```

**Environment Variable:**
```
DATABASE_URL=postgresql://...
```

---

#### Schema Evolution (Future Phases)

**Phase 3 Extensions:**
- users.auth_provider: VARCHAR(50) for OAuth providers
- notifications table: User notifications/alerts
- user_sessions table (optional): Token refresh management

**Phase 4 Extensions:**
- todos_collaborators: Multi-user todo sharing
- permissions: Granular access control (read, write, delete)

**Phase 5 Extensions:**
- ai_conversations: Chatbot interaction history
- ai_context: User preferences for AI assistant

**Design Principle: Additive Changes**
- Prefer ALTER TABLE ADD COLUMN (not DROP COLUMN)
- Use NULL for new optional columns (no default required)
- Maintain backward compatibility where possible

---

## Metadata
- **Version**: 1.0.0
- **Phase Introduced**: Phase 2
- **Last Updated**: 2025-12-30
- **Skill Type**: Specification
- **Execution Surface**: Agent (fastapi-backend-architect)
