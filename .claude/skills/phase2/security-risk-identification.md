# Skill: security-risk-identification

## 1. Skill Name
`security-risk-identification`

## 2. Purpose
Identify authentication, authorization, and data exposure risks at the specification level, surfacing potential security vulnerabilities before implementation to ensure secure design from the ground up.

## 3. Applicable Agents
- **auth-security-architect** (primary)
- **hackathon-judge-reviewer** (security audit)
- fastapi-backend-architect (API security)
- fullstack-spec-architect (cross-layer security)

## 4. Inputs
- **Authentication Specifications**: JWT flow, token storage, validation
- **Authorization Rules**: Data ownership enforcement, access control
- **API Specifications**: Endpoint security, input validation
- **Database Schema**: User relationships, foreign keys, constraints
- **Frontend Specifications**: Token storage, XSS risks

## 5. Outputs
- **Security Risk Report**: Identified vulnerabilities with severity ratings
- **Threat Scenarios**: Attack vectors and exploitation paths
- **Mitigation Recommendations**: Spec-level security improvements
- **Security Checklist**: Phase 2 security requirements validation
- **Judge-Facing Security Summary**: How security is addressed

## 6. Scope & Boundaries

### In Scope
- Authentication vulnerabilities (token theft, replay attacks)
- Authorization bypasses (cross-user data access)
- Data exposure risks (information leakage)
- Input validation gaps (injection attacks)
- Insecure defaults (password policies, session expiration)
- XSS risks (token storage in localStorage)

### Out of Scope
- Infrastructure security (HTTPS, firewalls - deployment concern)
- DDoS protection (Phase 3+)
- Rate limiting (Phase 3+)
- Third-party library vulnerabilities (implementation concern)

## 7. Reusability Notes
- **Phase 2**: Basic auth/authz security analysis
- **Phase 3**: OAuth security, refresh tokens, password reset
- **Phase 4**: Multi-user permissions, shared resource security
- **Phase 5**: AI prompt injection, data privacy

## 8. Dependencies

### Upstream Dependencies
- `jwt-auth-flow-specification` (auth design)
- `data-ownership-enforcement` (authz design)
- `rest-api-contract-definition` (API attack surface)

### Downstream Dependencies
- `fullstack-spec-audit` (overall quality validation)
- Implementation tasks (secure coding practices)

## 9. Quality Expectations

### Thoroughness
- All OWASP Top 10 categories considered
- Every integration point analyzed for risks
- Edge cases and failure modes examined

### Actionability
- Clear severity ratings (Critical, High, Medium, Low)
- Specific mitigation steps (not vague advice)
- Prioritized by risk impact

### Realism
- Threats relevant to Phase 2 scope
- Feasible mitigations (not over-engineering)
- Balance security with hackathon timeline

## 10. Example Usage (Spec-Level)

### Security Risk Analysis for Phase 2

---

#### Risk Category 1: Authentication Vulnerabilities

**Risk 1.1: JWT Token Theft via XSS**
```
Severity: HIGH
Category: A7:2017 - Cross-Site Scripting (XSS)

Threat Scenario:
  1. Attacker injects malicious script into todo description field
  2. Script executes in victim's browser
  3. Script reads localStorage.getItem('access_token')
  4. Token exfiltrated to attacker's server
  5. Attacker impersonates victim using stolen token

Current Spec Weakness:
  - Token stored in localStorage (JavaScript-accessible)
  - Input sanitization not explicitly specified
  - Content Security Policy not mentioned

Mitigation Recommendations:
  1. Specify input sanitization for all user-generated content
     - Escape HTML in todo titles and descriptions
     - Use DOMPurify or similar sanitization library
  2. Document Content Security Policy (CSP) requirement
     - script-src 'self' (no inline scripts)
     - Prevents execution of injected scripts
  3. Phase 3: Consider HttpOnly cookies instead of localStorage
     - Not accessible to JavaScript
     - More secure but requires backend session management

Risk Acceptance (Phase 2):
  - localStorage acceptable with CSP mitigation
  - Short token lifetime (15min) reduces window
  - HttpOnly cookies deferred to Phase 3 (complexity vs benefit)
```

**Risk 1.2: Token Expiration Too Long**
```
Severity: MEDIUM
Category: A2:2017 - Broken Authentication

Threat Scenario:
  1. User logs in on public computer
  2. User forgets to log out
  3. Token remains valid for extended period
  4. Next person uses computer, impersonates user

Current Spec:
  - Access token: 15 minutes (GOOD)
  - No refresh token (Phase 2 simplification)
  - Session persists across browser restarts

Mitigation Recommendations:
  1. Maintain 15-minute expiration (already secure)
  2. Add explicit logout on browser close (sessionStorage option)
  3. Document user education: always log out on shared devices
  4. Phase 3: Implement refresh token with rotation

Risk Level: ACCEPTABLE (15min is industry standard)
```

**Risk 1.3: Weak Password Policy**
```
Severity: MEDIUM
Category: A2:2017 - Broken Authentication

Threat Scenario:
  1. User chooses weak password (e.g., "password123")
  2. Attacker brute-forces or dictionary attacks login
  3. Gains unauthorized access

Current Spec Weakness:
  - Password requirements not explicitly specified
  - No mention of password hashing algorithm

Mitigation Recommendations:
  1. Specify password policy in user registration spec:
     - Minimum 8 characters
     - At least 1 uppercase, 1 lowercase, 1 digit
     - Optional: 1 special character
  2. Document password hashing:
     - Bcrypt with cost factor 12 (Better Auth default)
     - Never store plaintext passwords
  3. Phase 3: Add password strength meter, breach detection
```

---

#### Risk Category 2: Authorization Vulnerabilities

**Risk 2.1: IDOR - Insecure Direct Object Reference**
```
Severity: CRITICAL
Category: A5:2017 - Broken Access Control

Threat Scenario:
  1. User A has todo with id=123
  2. User B guesses URL: GET /api/todos/123
  3. Backend fails to validate user_id ownership
  4. User B accesses User A's todo

Current Spec Mitigation:
  ✅ GOOD: data-ownership-enforcement specifies user_id filtering
  ✅ GOOD: All queries include WHERE user_id = {current_user}
  ✅ GOOD: Returns 404 (not 403) to hide existence

Verification Required:
  - Ensure EVERY endpoint enforces user_id filtering
  - No code path bypasses ownership checks
  - Test: User A cannot access User B's todos (any operation)

Risk Level: MITIGATED (if spec followed correctly)
```

**Risk 2.2: Mass Assignment Vulnerability**
```
Severity: HIGH
Category: A5:2017 - Broken Access Control

Threat Scenario:
  1. User creates todo: POST /api/todos { "title": "...", "user_id": "other-user-id" }
  2. Backend accepts user_id from request
  3. Todo created for different user
  4. Attacker creates todos in other users' accounts

Current Spec Mitigation:
  ✅ GOOD: Spec states "Backend automatically sets user_id = current_user.id"
  ✅ GOOD: Frontend cannot specify user_id (ignored if provided)

Verification Required:
  - Backend MUST override user_id from request body
  - Validate in code review: user_id comes from JWT only, never request

Risk Level: MITIGATED (if implementation follows spec)
```

**Risk 2.3: Missing Authorization on Endpoints**
```
Severity: CRITICAL
Category: A5:2017 - Broken Access Control

Threat Scenario:
  1. Developer forgets to add authentication to new endpoint
  2. Endpoint accessible without JWT token
  3. Unauthenticated users access protected data

Current Spec Mitigation:
  ✅ GOOD: api-auth-enforcement-definition lists public vs protected
  ✅ GOOD: Middleware pattern enforces auth by default
  ⚠️ RISK: New endpoints could bypass middleware if not configured

Mitigation Recommendations:
  1. Specify "secure by default" pattern:
     - All routes protected unless explicitly marked public
     - Public routes require @public decorator or explicit opt-out
  2. Code review checklist: verify auth on all endpoints
  3. Integration test: attempt to access protected routes without token

Risk Level: MEDIUM (requires implementation discipline)
```

---

#### Risk Category 3: Data Exposure

**Risk 3.1: Sensitive Data in Error Messages**
```
Severity: MEDIUM
Category: A3:2017 - Sensitive Data Exposure

Threat Scenario:
  1. User attempts login with valid email, wrong password
  2. Error: "Password incorrect for user alice@example.com (user_id: 550e8400-...)"
  3. Attacker learns valid email addresses and user IDs

Current Spec:
  ✅ GOOD: Error messages generic ("Invalid email or password")
  ✅ GOOD: Does not distinguish "email not found" vs "wrong password"

Verification Required:
  - No user IDs in error messages
  - No stack traces in production responses
  - Generic error messages (no information leakage)
```

**Risk 3.2: User Enumeration via Registration**
```
Severity: LOW
Category: A3:2017 - Sensitive Data Exposure

Threat Scenario:
  1. Attacker attempts registration: POST /api/auth/register { "email": "target@example.com" }
  2. Response: 409 Conflict "An account with this email already exists"
  3. Attacker confirms user has an account (enumeration)

Current Spec:
  ⚠️ RISK: Spec shows 409 Conflict for duplicate email

Mitigation Options:
  1. Accept risk (common UX pattern, low severity)
  2. Alternative: Generic message "If this email is not registered, we've sent verification link"
  3. Phase 3: Add rate limiting on registration attempts

Risk Acceptance: LOW severity, common pattern, acceptable for Phase 2
```

**Risk 3.3: Database Information Leakage**
```
Severity: MEDIUM
Category: A3:2017 - Sensitive Data Exposure

Threat Scenario:
  1. Database error occurs (e.g., constraint violation)
  2. Full error message returned: "psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint 'users_email_key'"
  3. Attacker learns database structure, table names, column names

Current Spec Weakness:
  - Error handling not explicitly specified
  - No mention of sanitizing database errors

Mitigation Recommendations:
  1. Specify error handling:
     - Catch database exceptions
     - Return generic 500 error: "Internal server error"
     - Log full error server-side (not client-facing)
  2. Never expose stack traces or SQL queries
```

---

#### Risk Category 4: Input Validation

**Risk 4.1: SQL Injection**
```
Severity: CRITICAL (if vulnerable)
Category: A1:2017 - Injection

Threat Scenario:
  1. User creates todo: { "title": "'; DROP TABLE todos; --" }
  2. Backend concatenates SQL: "INSERT INTO todos (title) VALUES ('" + title + "')"
  3. Malicious SQL executes, drops todos table

Current Spec Mitigation:
  ✅ GOOD: SQLModel ORM specified (parameterized queries)
  ✅ GOOD: No raw SQL mentioned in specs

Verification Required:
  - Confirm: ALL queries use ORM (no string concatenation)
  - Code review: ban raw SQL queries
  - Test: attempt SQL injection in all input fields

Risk Level: LOW (ORMs prevent SQL injection by design)
```

**Risk 4.2: XSS via Todo Content**
```
Severity: HIGH
Category: A7:2017 - Cross-Site Scripting

Threat Scenario:
  1. User creates todo: { "title": "<script>alert('XSS')</script>" }
  2. Todo stored in database as-is
  3. Another user views todos
  4. Script executes in victim's browser

Current Spec Weakness:
  - No input sanitization specified
  - No output encoding specified

Mitigation Recommendations:
  1. Input validation:
     - Strip HTML tags from title and description
     - Or: Escape HTML entities before storage
  2. Output encoding:
     - Frontend must render as text (not HTML)
     - React/Next.js does this by default (document in spec)
  3. Content Security Policy (CSP):
     - script-src 'self' (no inline scripts)

Risk Level: MEDIUM (React mitigates by default, but spec should document)
```

---

### Security Checklist for Phase 2

```
Authentication:
  ✅ JWT tokens signed with strong secret (min 32 chars)
  ✅ Token expiration set (15 minutes)
  ✅ Password hashing specified (Bcrypt)
  ✅ HTTPS required (production deployment)
  ⚠️ Token storage (localStorage) - XSS risk mitigated by CSP

Authorization:
  ✅ User ownership enforced at database level (foreign keys)
  ✅ User ownership enforced at API level (WHERE user_id filter)
  ✅ Mass assignment prevented (user_id from JWT only)
  ✅ 404 responses (not 403) prevent information leakage
  ⚠️ New endpoints require explicit auth check

Data Protection:
  ✅ Passwords hashed (never plaintext)
  ✅ Sensitive data not in error messages
  ✅ Database errors sanitized
  ⚠️ User enumeration possible (low risk, acceptable)

Input Validation:
  ✅ SQL injection prevented (ORM used)
  ⚠️ XSS mitigation needs explicit documentation
  ✅ Input length limits specified (title 200 chars, description 2000 chars)
  ⚠️ Content Security Policy needs documentation

Session Management:
  ✅ Short-lived tokens (15 minutes)
  ✅ Logout clears token
  ⚠️ No refresh token (Phase 2 simplification acceptable)
```

---

### Judge-Facing Security Summary

**Security Posture for Phase 2:**
```
Phase 2 security focuses on:
  1. Secure authentication (JWT with proper validation)
  2. Strict authorization (user data isolation)
  3. Protection against common attacks (SQL injection, XSS)

Key Security Features:
  - JWT-based authentication with 15-minute expiration
  - Database-enforced user ownership (foreign keys)
  - API-enforced user filtering (every query includes user_id)
  - Password hashing (Bcrypt, never plaintext)
  - Input validation (length limits, type checking)

Known Limitations (Phase 2 Scope):
  - localStorage token storage (XSS risk, mitigated by CSP)
  - No refresh tokens (user must re-login after 15min)
  - No rate limiting (Phase 3)
  - No OAuth (Phase 3)

Security vs Usability Trade-offs:
  - Short token lifetime (secure) vs frequent re-login (UX cost)
  - Accepted for Phase 2 demo context
  - Phase 3 will add refresh tokens for better UX
```

---

## Metadata
- **Version**: 1.0.0
- **Phase Introduced**: Phase 2
- **Last Updated**: 2025-12-30
- **Skill Type**: Security Analysis
- **Execution Surface**: Agent (auth-security-architect)
