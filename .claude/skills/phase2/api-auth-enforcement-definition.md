# Skill: api-auth-enforcement-definition

## 1. Skill Name
`api-auth-enforcement-definition`

## 2. Purpose
Specify how JWT validation and authentication enforcement are applied to REST API endpoints, defining which endpoints require authentication, how middleware enforces authorization, and how unauthorized requests are handled.

## 3. Applicable Agents
- **auth-security-architect** (primary)
- **fastapi-backend-architect** (API middleware implementation)
- fullstack-spec-architect (cross-layer coordination)
- hackathon-judge-reviewer (security audit)

## 4. Inputs
- **JWT Flow Specification**: Token validation rules from `jwt-auth-flow-specification`
- **REST API Endpoints**: All backend endpoints from `rest-api-contract-definition`
- **User Identity Requirements**: Which endpoints need user context
- **Security Policy**: Authentication vs authorization requirements
- **Phase Scope**: Phase 2 boundaries (basic auth, not RBAC)

## 5. Outputs
- **Endpoint Authentication Matrix**: Which endpoints require auth, which are public
- **Middleware Specification**: How authentication is enforced at API layer
- **Authorization Rules**: User identity propagation and data access rules
- **Error Response Standards**: Consistent 401/403 response formats
- **Bypass Policies**: Endpoints that skip auth (health checks, docs)
- **Testing Requirements**: Auth enforcement verification criteria

## 6. Scope & Boundaries

### In Scope
- Classifying endpoints as public vs protected
- JWT middleware specification for FastAPI
- User identity extraction from validated tokens
- Request context enrichment with user_id
- 401 Unauthorized vs 403 Forbidden distinction
- Authentication bypass for specific routes (health, login)
- Error response standardization

### Out of Scope
- Role-based access control (RBAC) - Phase 3+
- Permission-level authorization (read/write/delete) - Phase 3+
- Rate limiting and throttling
- API key authentication (JWT only for Phase 2)
- OAuth scope enforcement (Phase 3)

## 7. Reusability Notes
- **Phase 2**: Basic authentication enforcement (logged in vs not)
- **Phase 3**: Extends to role-based rules (admin, user)
- **Phase 4**: Scales to resource-level permissions (owner, collaborator)
- **Phase 5**: AI chatbot uses same enforcement patterns
- **Cross-Project**: Middleware pattern reusable for any FastAPI + JWT app

### Reusability Mechanisms
- Decorator-based auth enforcement (e.g., `@requires_auth`)
- Middleware can be extended with additional checks
- User context injection pattern works for any identity provider
- Error response format standardized for all auth failures

## 8. Dependencies

### Upstream Dependencies
- `jwt-auth-flow-specification` (token validation rules)
- `rest-api-contract-definition` (all API endpoints)
- JWT secret management configured

### Downstream Dependencies
- `user-identity-propagation` (uses extracted user_id)
- `data-ownership-enforcement` (uses user context for queries)
- Backend implementation tasks

### Parallel Dependencies
- `security-risk-identification` (validates auth enforcement coverage)

## 9. Quality Expectations

### Security
- No protected endpoint bypasses authentication
- All auth failures return appropriate error codes
- User identity correctly extracted and propagated
- Middleware cannot be accidentally disabled

### Clarity
- Unambiguous endpoint classification (public vs protected)
- Clear middleware execution order
- Explicit error response formats

### Completeness
- Every endpoint explicitly classified
- All failure modes documented
- Testing criteria comprehensive

### Maintainability
- New protected endpoints inherit auth by default
- Explicit opt-out for public endpoints
- Centralized auth logic (no duplication)

## 10. Example Usage (Spec-Level)

### Scenario: Authentication Enforcement for Phase 2 Todo API

#### Endpoint Authentication Classification

**Public Endpoints (No Auth Required):**
```
POST   /api/auth/register      - User registration
POST   /api/auth/login         - User login (returns JWT)
GET    /api/health             - Health check
GET    /api/docs               - API documentation
```

**Protected Endpoints (JWT Required):**
```
POST   /api/auth/logout        - Logout (clears session)
GET    /api/auth/me            - Get current user info

GET    /api/todos              - List user's todos
POST   /api/todos              - Create new todo
GET    /api/todos/:id          - Get specific todo
PUT    /api/todos/:id          - Update todo
PATCH  /api/todos/:id/complete - Mark todo complete
DELETE /api/todos/:id          - Delete todo
```

#### Middleware Specification

**Middleware: JWT Authentication Middleware**

**Execution Order:**
```
1. CORS middleware (if enabled)
2. Request logging middleware
3. JWT Authentication Middleware ← Applied here
4. Route handler
5. Response middleware
6. Error handling middleware
```

**Middleware Logic:**

```
Phase 1: Request Interception
  Input: Incoming HTTP request
  Output: Request with user context OR 401 error

Phase 2: Path Checking
  If path in PUBLIC_PATHS:
    → Skip authentication, proceed to route handler
  Else:
    → Proceed to authentication

Phase 3: Token Extraction
  Extract Authorization header:
    - If missing: Return 401 "missing_token"
    - If format invalid (not "Bearer <token>"): Return 401 "invalid_format"
    - Extract token string

Phase 4: Token Validation
  Validate JWT:
    - Verify signature using JWT_SECRET_KEY
    - Check expiration (exp > now)
    - Verify issuer (iss == "todo-app-backend")
    - If any validation fails: Return 401 with specific error

Phase 5: Claims Extraction
  Extract claims from token payload:
    - user_id: UUID
    - email: string
    - Validate required claims present

Phase 6: User Context Injection
  Enrich request with user context:
    - request.user_id = claims["user_id"]
    - request.user_email = claims["email"]
  Available to all downstream handlers

Phase 7: Proceed to Route Handler
  Pass request to route handler with user context
```

#### Implementation Pattern (FastAPI Dependency)

**Specification (not implementation code):**

```
Pattern: Dependency Injection

Define: get_current_user() dependency
  - Extracts and validates JWT
  - Returns user_id if valid
  - Raises HTTPException(401) if invalid

Usage in route handlers:
  - Protected routes declare dependency: current_user = Depends(get_current_user)
  - Handler receives user_id automatically
  - No manual token parsing in handlers

Benefits:
  - Centralized auth logic
  - Automatic enforcement
  - Type-safe user_id
  - Easy to test (mock dependency)
```

#### Authorization Rules (Phase 2 - Basic)

**Rule 1: Authenticated User Access**
- **Requirement**: User must have valid JWT
- **Enforcement**: Middleware validates token before route handler
- **Error**: 401 Unauthorized if token missing/invalid/expired

**Rule 2: Owner-Only Data Access (Basic Ownership)**
- **Requirement**: Users can only access their own todos
- **Enforcement**: Backend queries include `WHERE user_id = {current_user_id}`
- **Error**: 404 Not Found (not 403) to avoid revealing existence of other users' data

**Rule 3: Public Endpoint Access**
- **Requirement**: No authentication required for registration, login, health
- **Enforcement**: Middleware skips these paths
- **Error**: N/A (no auth required)

#### Error Response Standards

**Error Format (Consistent across all auth failures):**
```json
{
  "error": "error_code",
  "message": "Human-readable description",
  "timestamp": "2025-12-30T12:00:00Z",
  "path": "/api/todos"
}
```

**Error Scenarios:**

**401 Unauthorized - Missing Token**
```json
{
  "error": "missing_token",
  "message": "Authentication required. Please provide a valid access token.",
  "timestamp": "2025-12-30T12:00:00Z",
  "path": "/api/todos"
}
HTTP Status: 401
```

**401 Unauthorized - Expired Token**
```json
{
  "error": "expired_token",
  "message": "Authentication token has expired. Please log in again.",
  "timestamp": "2025-12-30T12:00:00Z",
  "path": "/api/todos"
}
HTTP Status: 401
```

**401 Unauthorized - Invalid Token**
```json
{
  "error": "invalid_token",
  "message": "Token signature verification failed.",
  "timestamp": "2025-12-30T12:00:00Z",
  "path": "/api/todos"
}
HTTP Status: 401
```

**404 Not Found - Resource Owned by Different User**
```json
{
  "error": "not_found",
  "message": "Todo with id 123 not found.",
  "timestamp": "2025-12-30T12:00:00Z",
  "path": "/api/todos/123"
}
HTTP Status: 404
Note: Do NOT return 403 Forbidden (leaks information about other users' data)
```

**403 Forbidden - Reserved for Future Phases**
```
Phase 2: Not used (no permission levels)
Phase 3+: Used for role-based access (e.g., admin-only endpoints)
```

#### Bypass Policies

**Bypass 1: Health Check Endpoint**
```
Path: GET /api/health
Auth: None required
Reason: Monitoring tools need unauthenticated access
Response: { "status": "healthy" }
```

**Bypass 2: API Documentation**
```
Path: GET /api/docs (Swagger UI)
Auth: None required (Phase 2), Optional auth (Phase 3+)
Reason: Developer experience, public documentation
```

**Bypass 3: Authentication Endpoints**
```
Paths:
  - POST /api/auth/register
  - POST /api/auth/login
Auth: None required (obviously)
Reason: Cannot authenticate to create authentication
```

#### Testing Requirements

**Test 1: Protected Endpoint Rejects Unauthenticated Requests**
```
Given: No Authorization header
When: GET /api/todos
Then: Expect 401 Unauthorized
```

**Test 2: Protected Endpoint Accepts Valid Token**
```
Given: Valid JWT in Authorization header
When: GET /api/todos
Then: Expect 200 OK with user's todos
```

**Test 3: Protected Endpoint Rejects Expired Token**
```
Given: Expired JWT in Authorization header
When: GET /api/todos
Then: Expect 401 Unauthorized with "expired_token" error
```

**Test 4: Public Endpoint Accessible Without Token**
```
Given: No Authorization header
When: POST /api/auth/login
Then: Expect 200 OK (or 401 for bad credentials)
```

**Test 5: User Cannot Access Other User's Data**
```
Given: Valid JWT for User A
When: GET /api/todos/{user_b_todo_id}
Then: Expect 404 Not Found (not 403)
```

**Test 6: Middleware Execution Order**
```
Verify: JWT middleware runs before route handlers
Verify: Public endpoints skip middleware
Verify: Error middleware catches auth exceptions
```

---

## Metadata
- **Version**: 1.0.0
- **Phase Introduced**: Phase 2
- **Last Updated**: 2025-12-30
- **Skill Type**: Specification
- **Execution Surface**: Agent (auth-security-architect)
