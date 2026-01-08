# Skill: data-ownership-enforcement

## 1. Skill Name
`data-ownership-enforcement`

## 2. Purpose
Specify comprehensive rules and patterns ensuring users can only access, modify, or delete their own data, preventing unauthorized cross-user data access through database-level filtering, API-level validation, and error response design.

## 3. Applicable Agents
- **fastapi-backend-architect** (primary)
- **auth-security-architect** (security validation)
- fullstack-spec-architect (cross-layer enforcement)
- hackathon-judge-reviewer (security audit)

## 4. Inputs
- **User Identity Context**: user_id from JWT propagation
- **Database Schema**: Tables with user_id foreign keys
- **API Endpoints**: All CRUD operations requiring user filtering
- **Authorization Policy**: Phase 2 = owner-only access
- **Error Response Standards**: 404 vs 403 distinction

## 5. Outputs
- **Data Ownership Rules**: Explicit ownership enforcement patterns
- **Query Filtering Specification**: WHERE clauses for all user-scoped queries
- **Authorization Check Points**: Where ownership validation occurs
- **Error Response Patterns**: 404 for unauthorized access (not 403)
- **Testing Criteria**: Cross-user access prevention verification
- **Edge Case Handling**: Deleted users, orphaned data, shared resources (Phase 4+)

## 6. Scope & Boundaries

### In Scope
- User ownership validation for all CRUD operations
- Database query filtering by user_id
- Preventing cross-user data leakage
- 404 response for unauthorized access (privacy-preserving)
- Ownership checks at API layer and database layer
- Orphaned data handling (user deleted scenarios)

### Out of Scope
- Role-based access control (admin privileges) - Phase 3+
- Resource-level permissions (read/write/delete) - Phase 3+
- Multi-user collaboration (shared todos) - Phase 4
- Data export/import ownership transfer
- Audit logging of access attempts - Phase 3+

## 7. Reusability Notes
- **Phase 2**: Basic owner-only access (user owns todos)
- **Phase 3**: Extends to role-based overrides (admin can see all)
- **Phase 4**: Scales to shared resource ownership (multiple owners/collaborators)
- **Phase 5**: AI chatbot respects same ownership rules
- **Cross-Project**: Ownership patterns reusable for any multi-user system

### Reusability Mechanisms
- Ownership filter pattern (WHERE user_id = {current_user})
- Query abstraction (repository/service layer encapsulates filtering)
- Error response conventions (404 vs 403 guidance)
- Testing patterns for cross-user access prevention

## 8. Dependencies

### Upstream Dependencies
- `user-identity-propagation` (provides current_user.id)
- `relational-schema-design` (user_id foreign keys in tables)
- `rest-api-contract-definition` (endpoints requiring ownership checks)

### Downstream Dependencies
- Backend implementation tasks (implements ownership filters)
- `security-risk-identification` (validates no ownership bypasses)
- Testing tasks (cross-user access tests)

### Parallel Dependencies
- `api-auth-enforcement-definition` (authentication precedes authorization)

## 9. Quality Expectations

### Security
- Zero data leakage between users (no cross-user access possible)
- Ownership checks never bypassable (no optional filtering)
- Database constraints enforce ownership (foreign keys)
- API layer validates ownership before operations

### Consistency
- All user-scoped queries include user_id filter
- All endpoints return 404 (not 403) for unauthorized access
- Ownership validation patterns uniform across all resources

### Testability
- Every endpoint testable for cross-user access prevention
- Ownership bypass attempts detectable and blockable
- Edge cases covered (deleted users, missing user_id)

### Privacy
- 404 responses hide existence of other users' data
- Error messages never leak user_id or resource details
- Query results never include other users' data

## 10. Example Usage (Spec-Level)

### Scenario: Data Ownership Enforcement for Todo CRUD Operations

---

#### Ownership Rule 1: List User's Todos

**Specification:**
```
Endpoint: GET /api/todos
User Context: current_user.id = "user-123"

Database Query Pattern:
  SELECT * FROM todos WHERE user_id = 'user-123'

Ownership Enforcement:
  - Query MUST include WHERE user_id = {current_user.id}
  - No conditional filtering (always enforced)
  - Returns empty array if user has no todos

Response:
  200 OK: { "todos": [...] } (only user-123's todos)

Cross-User Access Prevention:
  ❌ Query: SELECT * FROM todos (returns all users' todos - WRONG)
  ✅ Query: SELECT * FROM todos WHERE user_id = 'user-123' (correct)

Testing:
  - User A calls GET /api/todos → returns only User A's todos
  - User B calls GET /api/todos → returns only User B's todos
  - User A cannot see User B's todos in any response
```

---

#### Ownership Rule 2: Get Specific Todo

**Specification:**
```
Endpoint: GET /api/todos/{id}
User Context: current_user.id = "user-123"
Path Parameter: id = 456

Database Query Pattern:
  SELECT * FROM todos
  WHERE id = 456 AND user_id = 'user-123'

Ownership Enforcement:
  - Query includes both id filter AND user_id filter
  - If todo exists but user_id doesn't match: Return 404 (not 403)
  - If todo doesn't exist: Return 404

Response Scenarios:

Scenario 1: Todo owned by current user
  Query returns todo → 200 OK with todo data

Scenario 2: Todo owned by different user
  Query returns NULL → 404 Not Found
  Error: { "error": "not_found", "message": "Todo with id 456 not found" }
  Note: Does NOT reveal todo exists for another user

Scenario 3: Todo doesn't exist at all
  Query returns NULL → 404 Not Found
  Error: Same as Scenario 2 (indistinguishable for privacy)

Privacy Consideration:
  ❌ WRONG: Return 403 Forbidden "You don't have permission to access this todo"
     (Reveals todo exists for another user)
  ✅ CORRECT: Return 404 Not Found "Todo not found"
     (Does not leak existence)
```

---

#### Ownership Rule 3: Update Todo

**Specification:**
```
Endpoint: PUT /api/todos/{id}
User Context: current_user.id = "user-123"
Path Parameter: id = 456
Request Body: { "title": "Updated Title", "completed": false }

Ownership Validation Flow:

Step 1: Check ownership before update
  Query: SELECT * FROM todos WHERE id = 456 AND user_id = 'user-123'
  If NULL: Return 404 Not Found (todo doesn't exist or not owned)

Step 2: Perform update (only if ownership validated)
  Query: UPDATE todos
         SET title = 'Updated Title', completed = false, updated_at = NOW()
         WHERE id = 456 AND user_id = 'user-123'

Step 3: Return updated resource
  Query: SELECT * FROM todos WHERE id = 456 AND user_id = 'user-123'
  Response: 200 OK with updated todo

Cross-User Update Prevention:
  User B attempts: PUT /api/todos/456 (todo owned by User A)
  Query: SELECT * FROM todos WHERE id = 456 AND user_id = 'user-B'
  Result: NULL (ownership check fails)
  Response: 404 Not Found
  Database: No update performed (ownership filter prevents write)
```

---

#### Ownership Rule 4: Delete Todo

**Specification:**
```
Endpoint: DELETE /api/todos/{id}
User Context: current_user.id = "user-123"
Path Parameter: id = 456

Database Query Pattern:
  DELETE FROM todos WHERE id = 456 AND user_id = 'user-123'

Ownership Enforcement:
  - DELETE query MUST include user_id filter
  - If no rows deleted (ownership mismatch): Return 404
  - If rows deleted: Return 204 No Content

Response Scenarios:

Scenario 1: Todo owned by current user
  DELETE query affects 1 row → 204 No Content (successful deletion)

Scenario 2: Todo owned by different user
  DELETE query affects 0 rows → 404 Not Found
  Error: { "error": "not_found", "message": "Todo with id 456 not found" }

Scenario 3: Todo doesn't exist
  DELETE query affects 0 rows → 404 Not Found
  Error: Same as Scenario 2

Idempotency Consideration:
  DELETE is idempotent: multiple DELETE requests return same result
  First DELETE: 204 No Content
  Second DELETE: 404 Not Found (already deleted)
```

---

#### Ownership Rule 5: Create Todo

**Specification:**
```
Endpoint: POST /api/todos
User Context: current_user.id = "user-123"
Request Body: { "title": "New Todo", "description": "..." }

Ownership Enforcement:
  - Backend automatically sets user_id = current_user.id
  - Frontend cannot specify user_id (ignored if provided)
  - Database enforces NOT NULL constraint on user_id

Database Insert Pattern:
  INSERT INTO todos (user_id, title, description, completed, created_at, updated_at)
  VALUES ('user-123', 'New Todo', '...', false, NOW(), NOW())

Security Consideration:
  ❌ WRONG: Allow frontend to specify user_id in request body
     Risk: User could create todos for other users
  ✅ CORRECT: Backend overwrites user_id with current_user.id
     Frontend request: { "title": "...", "user_id": "user-456" }
     Backend ignores user_id, uses current_user.id = "user-123"

Response:
  201 Created: { "id": 789, "title": "New Todo", ..., "user_id": "user-123" }
  Note: Response can include user_id (current user already knows their ID)
```

---

#### Ownership Enforcement Layers

**Layer 1: Database Schema (Structural Enforcement)**
```
Table: todos
Columns:
  - id: SERIAL PRIMARY KEY
  - user_id: UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
  - title: VARCHAR(200) NOT NULL
  - ...

Constraints:
  - user_id NOT NULL: Every todo must have an owner
  - FOREIGN KEY: user_id must reference valid users.id
  - ON DELETE CASCADE: If user deleted, their todos deleted automatically

Benefits:
  - Database enforces ownership at data level
  - Impossible to create ownerless todos
  - Orphaned data automatically cleaned up
```

**Layer 2: API Middleware (Authentication)**
```
Middleware: JWT Authentication
  - Extracts user_id from JWT token
  - Validates token signature and expiration
  - Injects current_user.id into request context
  - Blocks request if authentication fails (401)

Result: All protected routes have validated user_id available
```

**Layer 3: Route Handler (Ownership Filtering)**
```
Handler Pattern:
  async def get_todos(current_user: User = Depends(get_current_user)):
    user_id = current_user.id  # Validated user_id from JWT
    todos = await todo_service.get_todos_by_user(user_id)
    return { "todos": todos }

Ownership Enforcement:
  - Handler passes user_id to service/repository layer
  - No database query bypasses user_id filtering
  - Impossible for handler to access other users' data
```

**Layer 4: Service/Repository (Query Filtering)**
```
Service Method Pattern:
  async def get_todos_by_user(user_id: UUID):
    query = select(Todo).where(Todo.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().all()

Ownership Enforcement:
  - Every query includes user_id filter
  - Centralized filtering (not duplicated in handlers)
  - Type-safe (UUID parameter prevents injection)
```

---

#### Testing Requirements for Ownership Enforcement

**Test 1: User Cannot List Other Users' Todos**
```
Given: User A has todos [1, 2, 3], User B has todos [4, 5]
When: User A calls GET /api/todos
Then: Returns [1, 2, 3] only (not 4, 5)
Verify: Query includes WHERE user_id = {user_a_id}
```

**Test 2: User Cannot Get Other User's Specific Todo**
```
Given: Todo 4 owned by User B
When: User A calls GET /api/todos/4
Then: Returns 404 Not Found (not 403)
Verify: Query WHERE id = 4 AND user_id = {user_a_id} returns NULL
```

**Test 3: User Cannot Update Other User's Todo**
```
Given: Todo 4 owned by User B
When: User A calls PUT /api/todos/4 { "title": "Hacked" }
Then: Returns 404 Not Found
Verify: Database NOT updated (todo 4 title unchanged)
```

**Test 4: User Cannot Delete Other User's Todo**
```
Given: Todo 4 owned by User B
When: User A calls DELETE /api/todos/4
Then: Returns 404 Not Found
Verify: Todo 4 still exists in database
```

**Test 5: User Cannot Create Todo for Another User**
```
Given: User A authenticated (user_id = "user-a")
When: User A calls POST /api/todos { "title": "...", "user_id": "user-b" }
Then: Todo created with user_id = "user-a" (ignores "user-b")
Verify: Database todo.user_id = "user-a", NOT "user-b"
```

**Test 6: Concurrent Access Isolation**
```
Given: User A and User B both authenticated
When: Both call GET /api/todos simultaneously
Then: Each receives only their own todos
Verify: No cross-contamination of user_id in concurrent requests
```

---

#### Edge Case: Deleted User Scenarios

**Scenario: User Account Deleted**
```
Given: User A has todos [1, 2, 3]
When: User A account deleted (users table row removed)
Then: ON DELETE CASCADE removes todos [1, 2, 3]

Behavior:
  - Database enforces referential integrity
  - Orphaned todos automatically cleaned up
  - No manual cleanup required

Alternative (if ON DELETE SET NULL):
  - NOT RECOMMENDED for Phase 2
  - Would require periodic orphan cleanup jobs
```

**Scenario: JWT Valid but User Deleted**
```
Given: User A logged in with valid JWT
When: User A account deleted while JWT still valid
Then: Next API call with JWT returns 401 or 404

Option 1: Middleware checks user existence
  - Query database: SELECT id FROM users WHERE id = {jwt_user_id}
  - If NULL: Return 401 "user_not_found"
  - Trade-off: Extra DB query on every request

Option 2: Let queries return empty results
  - JWT valid, user_id extracted
  - Queries: SELECT * FROM todos WHERE user_id = {deleted_user_id}
  - Returns empty array (acceptable behavior)
  - Trade-off: JWT valid until expiration (max 15min)

Phase 2 Choice: Option 2 (simpler, acceptable for short-lived tokens)
```

---

## Metadata
- **Version**: 1.0.0
- **Phase Introduced**: Phase 2
- **Last Updated**: 2025-12-30
- **Skill Type**: Specification
- **Execution Surface**: Agent (fastapi-backend-architect)
