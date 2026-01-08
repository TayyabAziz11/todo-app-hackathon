# Skill: rest-api-contract-definition

## 1. Skill Name
`rest-api-contract-definition`

## 2. Purpose
Define comprehensive REST API endpoint contracts including HTTP methods, request/response models, error codes, validation rules, and semantic behaviors, ensuring frontend and backend have a shared, unambiguous API specification.

## 3. Applicable Agents
- **fastapi-backend-architect** (primary)
- fullstack-spec-architect (cross-layer coordination)
- nextjs-frontend-architect (consumer perspective)
- auth-security-architect (authentication requirements)

## 4. Inputs
- **Feature Requirements**: User stories and functional specifications
- **Data Models**: Database schema from relational-schema-design
- **Authentication Rules**: Protected vs public endpoint classification
- **User Workflows**: Frontend flows requiring API support
- **REST Best Practices**: HTTP semantics, status codes, idempotency

## 5. Outputs
- **API Endpoint Specifications**: Complete contract for each endpoint
- **Request/Response Models**: JSON schemas with field types and validation
- **HTTP Status Code Matrix**: Success and error scenarios per endpoint
- **Endpoint Authentication Map**: Which endpoints require JWT
- **OpenAPI/Swagger Spec**: Machine-readable API documentation
- **Integration Examples**: Sample requests and responses for frontend

## 6. Scope & Boundaries

### In Scope
- REST endpoint paths and HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Request body, query parameters, path parameters specifications
- Response body structure with field-level documentation
- Validation rules (required fields, formats, constraints)
- HTTP status codes (2xx success, 4xx client errors, 5xx server errors)
- Authentication requirements per endpoint
- Idempotency and side-effect semantics

### Out of Scope
- GraphQL or other API paradigms
- WebSocket specifications (Phase 3)
- API versioning strategy (Phase 3+)
- Rate limiting specifications
- Caching headers and strategies
- Backend implementation details (database queries, business logic)

## 7. Reusability Notes
- **Phase 2**: CRUD operations for todos with authentication
- **Phase 3**: Extends to real-time endpoints, OAuth callbacks
- **Phase 4**: Scales to multi-user operations (sharing, collaboration)
- **Phase 5**: AI chatbot API endpoints
- **Cross-Project**: REST contract patterns reusable for any API

### Reusability Mechanisms
- OpenAPI specification exportable and reusable
- Contract-first development enables parallel frontend/backend work
- Request/response models versionable (future API versions)
- Error format standards consistent across phases

## 8. Dependencies

### Upstream Dependencies
- `relational-schema-design` (data models inform response structures)
- `api-auth-enforcement-definition` (authentication requirements)
- Feature specifications (functional requirements)

### Downstream Dependencies
- `frontend-backend-contract-alignment` (validates contract consistency)
- Backend implementation tasks (implements contracts)
- Frontend integration tasks (consumes contracts)

### Parallel Dependencies
- `data-ownership-enforcement` (user filtering in endpoints)
- `jwt-auth-flow-specification` (auth endpoints)

## 9. Quality Expectations

### Completeness
- Every endpoint documents all possible responses (success + errors)
- Request validation rules explicit (required, optional, constraints)
- Field-level documentation (purpose, format, examples)

### Clarity
- HTTP semantics correct (GET = read-only, POST = create, PUT = full replace, PATCH = partial update, DELETE = remove)
- Status codes semantically appropriate
- Error messages actionable for frontend developers

### Consistency
- Naming conventions consistent (camelCase or snake_case, not mixed)
- Response structure patterns uniform across endpoints
- Error format standardized (same fields across all errors)

### Testability
- Each endpoint contract testable in isolation
- Request/response examples valid and executable
- Error scenarios comprehensive (all 4xx/5xx cases)

## 10. Example Usage (Spec-Level)

### Scenario: REST API Contracts for Phase 2 Todo Management

---

#### Endpoint 1: User Registration

**Contract:**
```
POST /api/auth/register
Content-Type: application/json
Authentication: None (public endpoint)

Request Body:
{
  "email": string (required, format: email, max 255 chars),
  "password": string (required, min 8 chars, max 128 chars),
  "name": string (optional, max 100 chars)
}

Validation Rules:
- email: Must be valid email format, unique in database
- password: Minimum 8 characters, at least 1 uppercase, 1 lowercase, 1 digit
- name: Optional display name

Response 201 Created:
{
  "id": string (UUID),
  "email": string,
  "name": string | null,
  "created_at": string (ISO 8601 datetime)
}

Response 400 Bad Request (Validation Error):
{
  "error": "validation_error",
  "message": "Invalid request data",
  "details": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}

Response 409 Conflict (Duplicate Email):
{
  "error": "duplicate_email",
  "message": "An account with this email already exists"
}

Response 500 Internal Server Error:
{
  "error": "internal_error",
  "message": "An unexpected error occurred"
}

Idempotency: Non-idempotent (duplicate registrations return 409)
Side Effects: Creates user in database, hashes password
```

---

#### Endpoint 2: User Login

**Contract:**
```
POST /api/auth/login
Content-Type: application/json
Authentication: None (public endpoint)

Request Body:
{
  "email": string (required, format: email),
  "password": string (required)
}

Response 200 OK:
{
  "access_token": string (JWT),
  "token_type": "Bearer",
  "expires_in": number (seconds, e.g., 900),
  "user": {
    "id": string (UUID),
    "email": string,
    "name": string | null
  }
}

Response 401 Unauthorized (Invalid Credentials):
{
  "error": "invalid_credentials",
  "message": "Email or password is incorrect"
}

Response 429 Too Many Requests (Rate Limiting, Phase 3):
{
  "error": "rate_limit_exceeded",
  "message": "Too many login attempts. Try again in 5 minutes."
}

Idempotency: Non-idempotent (multiple logins generate different tokens)
Side Effects: None (stateless JWT, no session in database)
```

---

#### Endpoint 3: Get Current User

**Contract:**
```
GET /api/auth/me
Authentication: Required (JWT in Authorization header)

Request Headers:
Authorization: Bearer <access_token>

Response 200 OK:
{
  "id": string (UUID),
  "email": string,
  "name": string | null,
  "created_at": string (ISO 8601)
}

Response 401 Unauthorized:
{
  "error": "expired_token" | "invalid_token" | "missing_token",
  "message": string
}

Idempotency: Idempotent (multiple calls return same data)
Side Effects: None (read-only)
```

---

#### Endpoint 4: List User's Todos

**Contract:**
```
GET /api/todos
Authentication: Required (JWT in Authorization header)

Request Headers:
Authorization: Bearer <access_token>

Query Parameters:
- completed: boolean (optional, filter by completion status)
- limit: number (optional, default 50, max 100)
- offset: number (optional, default 0, for pagination)

Example: GET /api/todos?completed=false&limit=20&offset=0

Response 200 OK:
{
  "todos": [
    {
      "id": number,
      "title": string,
      "description": string | null,
      "completed": boolean,
      "created_at": string (ISO 8601),
      "updated_at": string (ISO 8601)
    }
  ],
  "total": number (total count matching filters),
  "limit": number,
  "offset": number
}

Response 401 Unauthorized: (See auth errors above)

Response 400 Bad Request (Invalid Query Params):
{
  "error": "invalid_parameter",
  "message": "limit must be between 1 and 100"
}

Idempotency: Idempotent (same query returns same results)
Side Effects: None (read-only)
User Filtering: Automatic (only returns current user's todos)
```

---

#### Endpoint 5: Create Todo

**Contract:**
```
POST /api/todos
Content-Type: application/json
Authentication: Required (JWT in Authorization header)

Request Headers:
Authorization: Bearer <access_token>

Request Body:
{
  "title": string (required, min 1 char, max 200 chars),
  "description": string (optional, max 2000 chars)
}

Response 201 Created:
{
  "id": number,
  "title": string,
  "description": string | null,
  "completed": boolean (always false for new todos),
  "created_at": string (ISO 8601),
  "updated_at": string (ISO 8601)
}

Response 400 Bad Request (Validation Error):
{
  "error": "validation_error",
  "message": "Invalid request data",
  "details": [
    {
      "field": "title",
      "message": "Title is required and cannot be empty"
    }
  ]
}

Response 401 Unauthorized: (See auth errors above)

Idempotency: Non-idempotent (multiple POSTs create multiple todos)
Side Effects: Creates new todo in database with current user's user_id
User Filtering: Automatic (user_id from JWT)
```

---

#### Endpoint 6: Get Specific Todo

**Contract:**
```
GET /api/todos/{id}
Authentication: Required (JWT in Authorization header)

Path Parameters:
- id: number (todo ID)

Request Headers:
Authorization: Bearer <access_token>

Response 200 OK:
{
  "id": number,
  "title": string,
  "description": string | null,
  "completed": boolean,
  "created_at": string (ISO 8601),
  "updated_at": string (ISO 8601)
}

Response 404 Not Found (Todo Doesn't Exist or Not Owned by User):
{
  "error": "not_found",
  "message": "Todo with id {id} not found"
}
Note: Returns 404 (not 403) to avoid leaking existence of other users' todos

Response 401 Unauthorized: (See auth errors above)

Idempotency: Idempotent
Side Effects: None (read-only)
User Filtering: Enforced (WHERE user_id = current_user)
```

---

#### Endpoint 7: Update Todo

**Contract:**
```
PUT /api/todos/{id}
Content-Type: application/json
Authentication: Required (JWT in Authorization header)

Path Parameters:
- id: number (todo ID)

Request Headers:
Authorization: Bearer <access_token>

Request Body (Full Replacement):
{
  "title": string (required, min 1 char, max 200 chars),
  "description": string | null (optional),
  "completed": boolean (optional, default false)
}

Response 200 OK:
{
  "id": number,
  "title": string,
  "description": string | null,
  "completed": boolean,
  "created_at": string (ISO 8601),
  "updated_at": string (ISO 8601, updated to current time)
}

Response 404 Not Found: (See GET /api/todos/{id})
Response 400 Bad Request: (Validation errors)
Response 401 Unauthorized: (Auth errors)

Idempotency: Idempotent (multiple PUTs with same data produce same result)
Side Effects: Updates todo in database, sets updated_at to current timestamp
User Filtering: Enforced (cannot update other users' todos)
```

---

#### Endpoint 8: Mark Todo Complete/Incomplete

**Contract:**
```
PATCH /api/todos/{id}/complete
Content-Type: application/json
Authentication: Required (JWT in Authorization header)

Path Parameters:
- id: number (todo ID)

Request Headers:
Authorization: Bearer <access_token>

Request Body:
{
  "completed": boolean (required, true = complete, false = reopen)
}

Response 200 OK:
{
  "id": number,
  "title": string,
  "description": string | null,
  "completed": boolean (updated value),
  "created_at": string (ISO 8601),
  "updated_at": string (ISO 8601)
}

Response 404 Not Found: (See GET /api/todos/{id})
Response 401 Unauthorized: (Auth errors)

Idempotency: Idempotent (multiple PATCHes with same completed value have no effect)
Side Effects: Updates completed field and updated_at timestamp
User Filtering: Enforced
```

---

#### Endpoint 9: Delete Todo

**Contract:**
```
DELETE /api/todos/{id}
Authentication: Required (JWT in Authorization header)

Path Parameters:
- id: number (todo ID)

Request Headers:
Authorization: Bearer <access_token>

Response 204 No Content:
(Empty body, successful deletion)

Response 404 Not Found:
{
  "error": "not_found",
  "message": "Todo with id {id} not found"
}

Response 401 Unauthorized: (Auth errors)

Idempotency: Idempotent (deleting already-deleted todo returns 404)
Side Effects: Permanently removes todo from database
User Filtering: Enforced (cannot delete other users' todos)
```

---

#### Error Response Standard (All Endpoints)

**Format:**
```json
{
  "error": string (machine-readable error code),
  "message": string (human-readable description),
  "details": array (optional, for validation errors),
  "timestamp": string (ISO 8601, optional),
  "path": string (requested endpoint, optional)
}
```

**Common Error Codes:**
- `validation_error`: Request data invalid (400)
- `invalid_credentials`: Login failed (401)
- `missing_token`: No Authorization header (401)
- `expired_token`: JWT expired (401)
- `invalid_token`: JWT signature invalid (401)
- `not_found`: Resource doesn't exist or not accessible (404)
- `duplicate_email`: Email already registered (409)
- `internal_error`: Unexpected server error (500)

---

## Metadata
- **Version**: 1.0.0
- **Phase Introduced**: Phase 2
- **Last Updated**: 2025-12-30
- **Skill Type**: Specification
- **Execution Surface**: Agent (fastapi-backend-architect)
