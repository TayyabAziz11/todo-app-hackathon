# Skill: jwt-auth-flow-specification

## 1. Skill Name
`jwt-auth-flow-specification`

## 2. Purpose
Define the complete JWT authentication lifecycle from user login through token issuance, validation, refresh, and expiration, ensuring secure and stateless authentication across frontend and backend boundaries.

## 3. Applicable Agents
- **auth-security-architect** (primary)
- fastapi-backend-architect (backend implementation details)
- nextjs-frontend-architect (frontend token management)
- fullstack-spec-architect (integration coordination)

## 4. Inputs
- **Authentication Requirements**: Login, logout, session management needs
- **Security Constraints**: Token expiration policies, refresh requirements
- **Technology Stack**: Better Auth + JWT specification
- **User Model**: User identity fields (id, email, roles)
- **Phase Boundaries**: Phase 2 scope (basic auth) vs Phase 3+ (OAuth, MFA)

## 5. Outputs
- **JWT Flow Diagram**: Visual sequence diagram of authentication lifecycle
- **Token Structure Specification**: JWT claims, header, signature requirements
- **Endpoint Contracts**: Login, logout, verify, refresh endpoint specifications
- **Token Lifecycle Rules**: Issuance, validation, expiration, refresh policies
- **Error Scenarios**: Authentication failure modes and responses
- **Security Requirements**: Token storage, transmission, validation rules

## 6. Scope & Boundaries

### In Scope
- JWT token structure (header, payload, signature)
- Token issuance flow (login → token generation)
- Token validation flow (request → JWT verification)
- Token expiration and refresh mechanisms
- Logout and session termination
- Error handling for auth failures
- Token transmission (Authorization header)
- Claims extraction (user_id, email, roles)

### Out of Scope
- OAuth provider integration (Phase 3)
- Multi-factor authentication (Phase 3+)
- Password reset mechanisms (Phase 3)
- Email verification (Phase 3)
- Session management with Redis (optional optimization)
- Rate limiting on auth endpoints (security hardening, later phase)

## 7. Reusability Notes
- **Phase 2**: Establishes JWT-based authentication foundation
- **Phase 3**: Extends to OAuth tokens, refresh token rotation
- **Phase 4**: Scales to multi-tenant or role-based access control
- **Phase 5**: AI chatbot uses same JWT for user context
- **Cross-Project**: JWT flow pattern reusable for any authenticated web app

### Reusability Mechanisms
- Provider-agnostic JWT validation (works with Better Auth, Auth0, custom)
- Stateless design enables horizontal scaling
- Claims structure extensible (add roles, permissions later)
- Token refresh pattern supports long-lived sessions

## 8. Dependencies

### Upstream Dependencies
- User registration flow specified (user exists in database)
- Better Auth library selection confirmed
- JWT secret/key management strategy defined

### Downstream Dependencies
- `api-auth-enforcement-definition` (uses JWT validation spec)
- `user-identity-propagation` (uses claims extraction spec)
- `auth-aware-ui-flow-design` (uses token lifecycle for UI state)

### Parallel Dependencies
- `relational-schema-design` (users table schema)
- `rest-api-contract-definition` (auth endpoints)

## 9. Quality Expectations

### Security
- Token secrets never exposed in client code or logs
- JWT signature validation enforced on every protected request
- Token expiration times reasonable (15min access, 7day refresh)
- HTTPS required for token transmission

### Clarity
- Flow diagram shows all steps (login, validate, refresh, logout)
- Claims structure explicitly documented
- Error scenarios comprehensively listed

### Completeness
- All authentication states covered (logged out, logged in, expired, invalid)
- Edge cases documented (concurrent logins, token theft, clock skew)
- Rollback/recovery procedures for auth failures

### Testability
- Each flow step independently testable
- Mock token generation for testing
- Validation logic isolated and unit-testable

## 10. Example Usage (Spec-Level)

### Scenario: JWT Authentication Flow for Phase 2 Todo App

#### JWT Token Structure

**Header:**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload (Claims):**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "iat": 1735574400,
  "exp": 1735578000,
  "iss": "todo-app-backend"
}
```

**Signature:**
- Algorithm: HS256 (HMAC-SHA256)
- Secret: Environment variable `JWT_SECRET_KEY` (minimum 32 characters)
- Verification: Backend validates signature on every protected request

#### Authentication Flow Specification

**Flow 1: User Login (Token Issuance)**

```
Step 1: User submits credentials
  Frontend → POST /api/auth/login
  Body: { email: string, password: string }

Step 2: Backend validates credentials
  - Query database for user by email
  - Verify password hash using bcrypt/Better Auth
  - If invalid: Return 401 Unauthorized
  - If valid: Proceed to Step 3

Step 3: Backend generates JWT
  - Create payload with user_id, email
  - Set iat (issued at) to current timestamp
  - Set exp (expiration) to iat + 15 minutes
  - Sign token using JWT_SECRET_KEY
  - Return token to frontend

Step 4: Frontend stores token
  Response: { access_token: string, token_type: "Bearer", expires_in: 900 }
  Storage: localStorage or sessionStorage (trade-off: XSS risk vs convenience)
  State: Update app state to "authenticated"

Step 5: Frontend includes token in subsequent requests
  All API calls: Header "Authorization: Bearer <access_token>"
```

**Flow 2: Protected Request (Token Validation)**

```
Step 1: Frontend sends authenticated request
  GET /api/todos
  Headers: { Authorization: "Bearer <access_token>" }

Step 2: Backend extracts token
  - Parse Authorization header
  - Extract token (remove "Bearer " prefix)
  - If missing: Return 401 Unauthorized

Step 3: Backend validates token
  - Verify JWT signature using JWT_SECRET_KEY
  - Check token expiration (exp > current time)
  - Extract claims (user_id, email)
  - If validation fails: Return 401 Unauthorized with error detail
    - Errors: "invalid_token", "expired_token", "signature_mismatch"

Step 4: Backend extracts user identity
  - user_id from claims stored in request context
  - Available to all downstream handlers
  - Used for data filtering (e.g., WHERE user_id = ...)

Step 5: Backend processes request
  - Execute business logic with user context
  - Return user-specific data
```

**Flow 3: Token Expiration and Refresh**

```
Phase 2 Approach: Short-lived tokens, re-login on expiration
  - Access token: 15 minutes
  - No refresh token (simplified for Phase 2)
  - On expiration: Frontend redirects to login

Phase 3+ Approach: Refresh token pattern
  - Access token: 15 minutes
  - Refresh token: 7 days (stored securely)
  - Endpoint: POST /api/auth/refresh
  - Body: { refresh_token: string }
  - Response: New access_token

Phase 2 Justification:
  - Simpler implementation
  - Lower security risk (no long-lived tokens)
  - Acceptable UX for demo (15min session sufficient)
```

**Flow 4: User Logout (Token Invalidation)**

```
Step 1: Frontend initiates logout
  POST /api/auth/logout (optional endpoint)
  Headers: { Authorization: "Bearer <access_token>" }

Step 2: Frontend clears token
  - Remove token from localStorage/sessionStorage
  - Clear app authentication state
  - Redirect to login page

Step 3: Backend response
  - 200 OK (no server-side action needed with stateless JWT)
  - Phase 3+: Could add token blacklist for immediate revocation

Note: Stateless JWT means token remains valid until expiration
      even after logout. This is acceptable for Phase 2.
```

#### Error Scenarios and Responses

**Error 1: Invalid Credentials**
```
Request: POST /api/auth/login
Body: { email: "user@example.com", password: "wrong" }

Response: 401 Unauthorized
Body: {
  "error": "invalid_credentials",
  "message": "Email or password is incorrect"
}
```

**Error 2: Expired Token**
```
Request: GET /api/todos
Headers: { Authorization: "Bearer <expired_token>" }

Response: 401 Unauthorized
Body: {
  "error": "expired_token",
  "message": "Authentication token has expired. Please log in again."
}
```

**Error 3: Invalid Token Signature**
```
Request: GET /api/todos
Headers: { Authorization: "Bearer <tampered_token>" }

Response: 401 Unauthorized
Body: {
  "error": "invalid_token",
  "message": "Token signature verification failed"
}
```

**Error 4: Missing Token**
```
Request: GET /api/todos
Headers: {} (no Authorization header)

Response: 401 Unauthorized
Body: {
  "error": "missing_token",
  "message": "Authentication required. Please provide a valid access token."
}
```

#### Security Requirements

**Requirement 1: Secret Management**
- JWT_SECRET_KEY stored in environment variable, never in code
- Minimum 32 characters, cryptographically random
- Rotated periodically (manual process Phase 2, automated Phase 3+)

**Requirement 2: Token Transmission**
- HTTPS required for all auth endpoints (enforced in production)
- Authorization header preferred over query params (no token logging)
- Never expose token in URL or client-side logs

**Requirement 3: Token Storage (Frontend)**
- localStorage: Survives page refresh (Phase 2 choice)
- XSS Risk: Mitigated by Content Security Policy
- Phase 3+ Alternative: HttpOnly cookies (more secure)

**Requirement 4: Validation Strictness**
- Signature verification mandatory (no skip option)
- Expiration check mandatory (no grace period)
- Issuer claim validation (iss = "todo-app-backend")

---

## Metadata
- **Version**: 1.0.0
- **Phase Introduced**: Phase 2
- **Last Updated**: 2025-12-30
- **Skill Type**: Specification
- **Execution Surface**: Agent (auth-security-architect)
