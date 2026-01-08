# Skill: user-identity-propagation

## 1. Skill Name
`user-identity-propagation`

## 2. Purpose
Define how authenticated user identity flows from frontend JWT token through backend API middleware to database queries, ensuring consistent user context propagation across all architectural layers without manual passing or duplication.

## 3. Applicable Agents
- **auth-security-architect** (primary)
- **fastapi-backend-architect** (backend context management)
- **fullstack-spec-architect** (cross-layer flow)
- nextjs-frontend-architect (frontend user state)

## 4. Inputs
- **JWT Claims Structure**: user_id, email, and other identity fields
- **Backend Request Context**: FastAPI request object and dependency system
- **Database Query Patterns**: SQLModel queries requiring user filtering
- **Frontend State Management**: User authentication state on client
- **API Middleware Spec**: JWT validation and claims extraction

## 5. Outputs
- **Identity Propagation Flow Diagram**: Frontend → Backend → Database
- **Context Injection Specification**: How user_id becomes available in handlers
- **Query Pattern Specification**: Automatic user_id filtering in database queries
- **Frontend State Spec**: How UI accesses current user information
- **Error Handling**: Missing user context detection and handling
- **Testing Strategy**: Verification that user context never leaks between requests

## 6. Scope & Boundaries

### In Scope
- JWT claims extraction (user_id, email)
- Backend request context enrichment
- Automatic user_id injection in database queries
- Frontend current user state management
- Cross-layer user identity consistency
- User context isolation per request

### Out of Scope
- Role/permission propagation (Phase 3+)
- User profile enrichment (lazy loading, caching)
- Multi-tenancy or organization context (Phase 4+)
- Impersonation or sudo functionality
- Audit logging of user actions (Phase 3+)

## 7. Reusability Notes
- **Phase 2**: Basic user_id propagation for data isolation
- **Phase 3**: Extends to roles, permissions, organization context
- **Phase 4**: Scales to multi-user contexts (shared resources)
- **Phase 5**: AI chatbot accesses same user context
- **Cross-Project**: Pattern applies to any authenticated multi-user system

### Reusability Mechanisms
- Dependency injection pattern (framework-agnostic concept)
- Request-scoped context (prevents cross-contamination)
- Declarative user requirements in route handlers
- Type-safe user context (prevents runtime errors)

## 8. Dependencies

### Upstream Dependencies
- `jwt-auth-flow-specification` (claims structure)
- `api-auth-enforcement-definition` (middleware extracts user_id)
- Backend request/response lifecycle defined

### Downstream Dependencies
- `data-ownership-enforcement` (uses propagated user_id)
- `relational-schema-design` (user_id foreign keys)
- All backend route handler implementations

### Parallel Dependencies
- `rest-api-contract-definition` (endpoints that need user context)

## 9. Quality Expectations

### Security
- User identity never leaks between concurrent requests
- No global variables storing user context
- User context validated on every request (not cached insecurely)
- Request isolation enforced by framework

### Consistency
- Same user_id value across frontend state, JWT claims, backend context, database queries
- No manual user_id passing through function parameters
- Single source of truth for current user

### Simplicity
- Route handlers receive user_id automatically (no boilerplate)
- Database queries automatically filter by user_id (no manual WHERE clauses)
- Frontend components access user from centralized state

### Testability
- User context mockable in tests
- Identity isolation verifiable (concurrent request tests)
- Missing user context detectable (error thrown, not silent failure)

## 10. Example Usage (Spec-Level)

### Scenario: User Identity Propagation in Todo CRUD Operations

#### Layer 1: Frontend - User State Management

**Frontend State Structure:**
```typescript
// Frontend user state (after login)
interface AuthState {
  isAuthenticated: boolean;
  user: {
    id: string;        // UUID from JWT claims
    email: string;     // Email from JWT claims
  } | null;
  accessToken: string | null;
}

// State after successful login
{
  isAuthenticated: true,
  user: {
    id: "550e8400-e29b-41d4-a716-446655440000",
    email: "user@example.com"
  },
  accessToken: "eyJhbGciOiJIUzI1NiIs..."
}
```

**Identity Propagation - Frontend:**
```
Step 1: User logs in
  POST /api/auth/login → { access_token, user_id, email }

Step 2: Frontend extracts user info
  - Decode JWT (client-side) OR use backend response
  - Store in auth state: { user: { id, email }, accessToken }
  - Store token in localStorage for persistence

Step 3: Frontend includes token in API calls
  All authenticated requests:
    Headers: { Authorization: "Bearer <accessToken>" }
  Backend extracts user_id from this token automatically

Step 4: Frontend displays user-specific data
  - UI components access auth state: useAuthContext()
  - Display user email in navbar
  - Show user-specific todos (fetched with user's token)
```

#### Layer 2: Backend - Request Context Enrichment

**Middleware Identity Extraction:**
```
Phase 1: JWT Middleware validates token
  Input: Authorization header with JWT
  Action: Validate signature, expiration
  Output: Decoded JWT claims

Phase 2: Extract user identity from claims
  Claims: { user_id: "550e8400-...", email: "user@example.com", ... }
  Extract: user_id and email

Phase 3: Inject into request context
  FastAPI dependency injection:
    - current_user: User = Depends(get_current_user)
    - Route handler receives User object automatically
    - No manual extraction in handler

Phase 4: Make available to route handler
  Handler signature:
    async def get_todos(current_user: User = Depends(get_current_user)):
      user_id = current_user.id  # Automatically available
      # Use user_id for data filtering
```

**Backend Context Pattern (Specification):**

```
Pattern: Dependency Injection

Define Dependency: get_current_user()
  Input: Request with Authorization header
  Process:
    1. Extract JWT from Authorization header
    2. Validate JWT signature and expiration
    3. Decode claims
    4. Extract user_id and email
    5. Create User object: User(id=user_id, email=email)
  Output: User object
  Error: Raise HTTPException(401) if validation fails

Usage in Route Handler:
  def create_todo(
    todo_data: CreateTodoRequest,
    current_user: User = Depends(get_current_user)  # Automatic injection
  ):
    # current_user.id is available here
    # No manual token parsing needed
    # Validated and type-safe

Benefits:
  - Automatic extraction (no boilerplate)
  - Type safety (User object, not raw dict)
  - Testable (mock dependency)
  - Centralized validation logic
```

#### Layer 3: Database - User-Filtered Queries

**Database Query Pattern (Automatic User Filtering):**

```
Specification: All user-scoped queries include user_id filter

Example 1: List User's Todos
  Naive approach (WRONG):
    SELECT * FROM todos;  # Returns ALL users' todos

  Correct approach (REQUIRED):
    SELECT * FROM todos WHERE user_id = {current_user.id};

Example 2: Get Specific Todo
  Naive approach (WRONG):
    SELECT * FROM todos WHERE id = {todo_id};  # Could return other user's todo

  Correct approach (REQUIRED):
    SELECT * FROM todos WHERE id = {todo_id} AND user_id = {current_user.id};

Example 3: Update Todo
  Query:
    UPDATE todos
    SET title = {new_title}, updated_at = NOW()
    WHERE id = {todo_id} AND user_id = {current_user.id};

  If no rows updated: Return 404 (todo doesn't exist for this user)

Example 4: Delete Todo
  Query:
    DELETE FROM todos
    WHERE id = {todo_id} AND user_id = {current_user.id};

  If no rows deleted: Return 404
```

**Database Access Pattern (SQLModel Specification):**

```
Pattern: User-Scoped Repository/Service

Specification:
  All database operations receive current_user.id as parameter
  No database operation bypasses user filtering

Example Service Method:
  async def get_user_todos(user_id: UUID):
    # user_id propagated from JWT → middleware → handler → service
    return db.query(Todo).filter(Todo.user_id == user_id).all()

  async def get_todo_by_id(todo_id: int, user_id: UUID):
    # Both filters required
    todo = db.query(Todo).filter(
      Todo.id == todo_id,
      Todo.user_id == user_id
    ).first()
    if not todo:
      raise HTTPException(404, "Todo not found")
    return todo
```

#### Full Identity Propagation Flow

**End-to-End Example: GET /api/todos**

```
Step 1: Frontend initiates request
  User clicks "My Todos" in UI
  Frontend state: { user: { id: "550e8400-...", email: "..." }, token: "..." }
  Frontend sends:
    GET /api/todos
    Headers: { Authorization: "Bearer eyJhbGciOi..." }

Step 2: Request reaches backend
  FastAPI receives request
  Routing: Match to get_todos() handler

Step 3: Middleware extracts user identity
  JWT middleware:
    - Extract token from Authorization header
    - Validate signature
    - Decode claims: { user_id: "550e8400-...", email: "user@example.com" }
    - Create User object: User(id="550e8400-...", email="...")

Step 4: Dependency injection
  FastAPI dependency system:
    - get_current_user() dependency executes
    - Returns User object
    - Injected as current_user parameter in handler

Step 5: Route handler receives user context
  Handler: async def get_todos(current_user: User = Depends(...))
  Handler has: current_user.id = "550e8400-..."
  NO manual extraction needed

Step 6: Handler calls service/repository
  todos = await todo_service.get_user_todos(user_id=current_user.id)
  user_id propagated to service layer

Step 7: Service queries database
  Query: SELECT * FROM todos WHERE user_id = '550e8400-...'
  Database returns only this user's todos
  No cross-user data leakage possible

Step 8: Response sent to frontend
  Backend returns: { todos: [...] }
  Frontend receives only current user's todos
  UI displays todos specific to logged-in user
```

#### Error Handling - Missing User Context

**Scenario 1: Missing Authorization Header**
```
Request: GET /api/todos (no Authorization header)
Middleware: Raises HTTPException(401, "missing_token")
Response: 401 Unauthorized
Handler: Never executed (middleware blocks)
```

**Scenario 2: Invalid/Expired Token**
```
Request: GET /api/todos (expired token)
Middleware: Raises HTTPException(401, "expired_token")
Response: 401 Unauthorized
Handler: Never executed
```

**Scenario 3: User Not Found (Edge Case)**
```
Scenario: JWT valid but user deleted from database
Middleware: Token valid, extracts user_id
Handler: Executes with user_id
Database Query: Returns 0 todos (user has none)
Response: 200 OK with empty array (acceptable)

Alternative: Check user existence in middleware (stricter)
  - Query database for user by user_id
  - If not found: Return 401 "user_not_found"
  - Trade-off: Extra database query on every request
```

#### Testing Strategy

**Test 1: User Isolation**
```
Given: User A and User B both authenticated
When: User A requests GET /api/todos
Then: Returns only User A's todos, not User B's
Verify: Query includes WHERE user_id = {user_a_id}
```

**Test 2: Concurrent Request Isolation**
```
Given: User A and User B send requests simultaneously
Then: Each request has isolated user context
Verify: No cross-contamination of user_id values
Verify: No shared global state
```

**Test 3: User Context Availability**
```
Given: Protected route handler
Then: current_user parameter automatically populated
Verify: Handler can access current_user.id without errors
```

**Test 4: Missing Token Blocks Access**
```
Given: Request without Authorization header
Then: Middleware blocks request before handler
Verify: Handler never executes
Verify: 401 response returned
```

---

## Metadata
- **Version**: 1.0.0
- **Phase Introduced**: Phase 2
- **Last Updated**: 2025-12-30
- **Skill Type**: Specification
- **Execution Surface**: Agent (auth-security-architect)
