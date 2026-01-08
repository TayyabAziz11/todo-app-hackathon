# Skill: frontend-backend-contract-alignment

## 1. Skill Name
`frontend-backend-contract-alignment`

## 2. Purpose
Ensure frontend API expectations precisely match backend API contracts, validating request/response models, field names, data types, error handling, and HTTP semantics to prevent integration failures and runtime errors.

## 3. Applicable Agents
- **fullstack-spec-architect** (primary)
- nextjs-frontend-architect (frontend requirements)
- fastapi-backend-architect (backend contracts)
- hackathon-judge-reviewer (integration validation)

## 4. Inputs
- **Backend API Specification**: REST endpoint contracts from `rest-api-contract-definition`
- **Frontend API Client Code**: TypeScript interfaces, API call implementations
- **Frontend Components**: UI components consuming API data
- **Error Handling Specs**: Frontend error response handling

## 5. Outputs
- **Contract Alignment Report**: Validation of frontend-backend consistency
- **Type Definition Alignment**: TypeScript interfaces match backend models
- **Field Mapping Documentation**: camelCase (frontend) ↔ snake_case (backend)
- **Error Handling Alignment**: Frontend handles all backend error codes
- **Integration Test Specifications**: Contract validation tests

## 6. Scope & Boundaries

### In Scope
- Request/response model alignment
- Field name and type consistency
- HTTP status code handling
- Authentication header inclusion
- Error response handling

### Out of Scope
- Performance optimization
- UI/UX design validation
- API mocking strategies (testing concern)

## 7. Reusability Notes
- **Phase 2**: Basic CRUD contract alignment
- **Phase 3**: WebSocket contract alignment
- **Phase 4**: Real-time sync contracts
- **Phase 5**: AI chatbot API contracts

## 8. Dependencies

### Upstream Dependencies
- `rest-api-contract-definition` (backend contracts)
- `cross-layer-consistency-validation` (initial validation)

### Downstream Dependencies
- Frontend implementation tasks
- Integration testing tasks

## 9. Quality Expectations

### Accuracy
- Zero type mismatches
- All required fields present
- Optional fields handled correctly

### Completeness
- All endpoints documented
- All error scenarios handled
- All success scenarios validated

## 10. Example Usage (Spec-Level)

### Contract Alignment Example: Create Todo

**Backend Contract:**
```
POST /api/todos
Request: { "title": string, "description": string | null }
Response 201: {
  "id": number,
  "title": string,
  "description": string | null,
  "completed": boolean,
  "created_at": string,
  "updated_at": string
}
```

**Frontend TypeScript Interface:**
```typescript
// Request type
interface CreateTodoRequest {
  title: string;
  description?: string; // Optional (null | undefined)
}

// Response type
interface TodoResponse {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  createdAt: string; // Note: camelCase conversion
  updatedAt: string;
}
```

**Alignment Validation:**
```
✅ Request field alignment:
   - title: string ↔ string (match)
   - description?: string ↔ string | null (compatible)

✅ Response field alignment:
   - id: number ↔ number (match)
   - title: string ↔ string (match)
   - completed: boolean ↔ boolean (match)

⚠️ Field name convention:
   - Backend: created_at (snake_case)
   - Frontend: createdAt (camelCase)
   - Resolution: Transform in API client layer

✅ HTTP semantics:
   - POST for creation (correct)
   - 201 Created status (correct)
```

### Field Name Transformation Pattern

**Backend Response (snake_case):**
```json
{
  "id": 1,
  "user_id": "550e8400-...",
  "created_at": "2025-12-30T12:00:00Z",
  "updated_at": "2025-12-30T12:00:00Z"
}
```

**Frontend Type (camelCase):**
```typescript
interface Todo {
  id: number;
  userId: string;
  createdAt: string;
  updatedAt: string;
}
```

**Transformation Specification:**
```
API Client Layer Responsibility:
  - Intercept backend responses
  - Transform snake_case → camelCase
  - Pass camelCase data to frontend components

Options:
  1. Backend serialization: Pydantic alias (created_at = Field(alias='createdAt'))
  2. Frontend transformation: Utility function transformKeys(data)
  3. Both: Backend supports both conventions

Phase 2 Recommendation: Backend transformation (Option 1)
  - Single source of transformation
  - Frontend receives ready-to-use data
  - Less error-prone
```

### Error Handling Alignment

**Backend Error Response:**
```json
{
  "error": "validation_error",
  "message": "Invalid request data",
  "details": [
    { "field": "title", "message": "Title is required" }
  ]
}
```

**Frontend Error Handling:**
```typescript
interface ApiError {
  error: string;
  message: string;
  details?: { field: string; message: string }[];
}

async function createTodo(data: CreateTodoRequest): Promise<TodoResponse> {
  try {
    const response = await fetch('/api/todos', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.message);
    }

    return await response.json();
  } catch (error) {
    // Handle network errors, parsing errors, etc.
    throw error;
  }
}
```

**Alignment Checklist:**
```
✅ Frontend expects error.message field
✅ Frontend handles error.details (validation errors)
✅ Frontend distinguishes HTTP status codes (400, 401, 500)
✅ Frontend displays user-friendly error messages
```

### Authentication Header Alignment

**Backend Requirement:**
```
Protected endpoints require:
  Authorization: Bearer <access_token>
```

**Frontend Implementation:**
```typescript
const token = localStorage.getItem('access_token');

async function apiCall(endpoint: string, options: RequestInit = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers
  };

  return fetch(endpoint, { ...options, headers });
}
```

**Alignment Validation:**
```
✅ Frontend includes Authorization header for protected routes
✅ Header format: "Bearer <token>" (not just token)
✅ Token retrieved from localStorage
✅ Header absent for public routes (login, register)
```

### Integration Test Specification

**Test 1: Create Todo Contract**
```
Given: Valid authentication token
When: Frontend calls createTodo({ title: "Test", description: "..." })
Then:
  - Request POST /api/todos
  - Headers include Authorization
  - Body contains title and description
  - Response 201 with TodoResponse shape
  - All fields present and correct types
```

**Test 2: Error Handling Contract**
```
Given: Invalid todo data (empty title)
When: Frontend calls createTodo({ title: "", description: "..." })
Then:
  - Request POST /api/todos
  - Response 400 Bad Request
  - Error body matches ApiError interface
  - error.details contains field validation errors
  - Frontend displays error message to user
```

**Test 3: Authentication Failure Contract**
```
Given: Expired token
When: Frontend calls getTodos()
Then:
  - Request GET /api/todos with expired token
  - Response 401 Unauthorized
  - Error: { error: "expired_token", message: "..." }
  - Frontend triggers re-authentication flow
```

---

## Metadata
- **Version**: 1.0.0
- **Phase Introduced**: Phase 2
- **Last Updated**: 2025-12-30
- **Skill Type**: Validation
- **Execution Surface**: Agent (fullstack-spec-architect)
