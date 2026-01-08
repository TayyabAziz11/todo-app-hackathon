# ADR 001: JWT Stateless Authentication

## Status
Accepted

## Context
Phase II requires user authentication for the full-stack web application. Users must be able to register, login, and access only their own todo data. We need to choose an authentication strategy that:

1. **Scales horizontally** - No server-side session storage
2. **Works across services** - Backend API and future microservices
3. **Supports stateless architecture** - No shared session state
4. **Simple to implement** - Hackathon timeline constraints
5. **Industry standard** - Well-documented and secure

### Options Considered

#### Option 1: Session-Based Authentication (Cookies)
**Pros:**
- Immediate server-side session invalidation
- Familiar pattern for traditional web apps
- Browser handles cookie storage automatically

**Cons:**
- Requires server-side session storage (Redis, database)
- Harder to scale horizontally (sticky sessions or shared storage)
- CSRF protection complexity
- Not ideal for API-first architecture

#### Option 2: JWT (JSON Web Tokens)
**Pros:**
- **Stateless** - No server-side storage required
- **Scalable** - Works across distributed services
- **Standard** - RFC 7519, well-supported libraries
- **Self-contained** - Token includes user identity and claims
- **API-friendly** - Works with mobile apps, SPAs, and microservices

**Cons:**
- Cannot invalidate tokens before expiration (mitigation: short TTL)
- Token size larger than session ID
- Secret key management required

#### Option 3: OAuth 2.0 / OpenID Connect
**Pros:**
- Industry standard for third-party authentication
- Supports social login (Google, GitHub)
- Comprehensive security features

**Cons:**
- **Overkill for this use case** - We don't need third-party login
- Complex implementation (authorization server, token endpoints)
- Not suitable for hackathon timeline

## Decision
We will use **JWT (JSON Web Tokens) with HS256 algorithm** for stateless authentication.

### Implementation Details
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Token Expiration**: 15 minutes (configurable via JWT_EXPIRE_MINUTES)
- **Claims**: `sub` (user_id), `email`, `exp` (expiration), `iat` (issued at)
- **Storage**: Client-side localStorage (frontend)
- **Transport**: Authorization header (`Authorization: Bearer <token>`)
- **Secret Key**: Environment variable (JWT_SECRET_KEY) - 256-bit random string

### Security Measures
1. **Short TTL (15 minutes)** - Limits exposure window if token is stolen
2. **HTTPS only (production)** - Prevents token interception
3. **Strong secret key** - 32-byte random string from secrets.token_urlsafe(32)
4. **No sensitive data in payload** - Only user_id and email
5. **Logout clears token** - Client-side removal from localStorage
6. **Automatic expiration** - Backend rejects expired tokens (401)

## Consequences

### Positive
✅ **Horizontal scalability** - No shared session state, add more backend instances easily
✅ **Simple architecture** - No Redis or session database required
✅ **API-first design** - Works seamlessly with REST API endpoints
✅ **Fast implementation** - python-jose library handles JWT operations
✅ **Stateless** - Each request is self-contained, no server-side lookup

### Negative
⚠️ **No immediate revocation** - Cannot invalidate token before expiration
  - **Mitigation**: Short 15-minute TTL reduces risk window
  - **Future**: Implement token blacklist or refresh tokens if needed

⚠️ **Client-side storage** - localStorage vulnerable to XSS attacks
  - **Mitigation**: React auto-escapes output (XSS protection)
  - **Future**: Consider httpOnly cookies for production

⚠️ **Secret key management** - Single point of failure if key is compromised
  - **Mitigation**: Environment variable, never committed to git
  - **Future**: Key rotation mechanism

### Trade-offs
- **Chose simplicity over revocation** - 15-minute window acceptable for hackathon
- **Chose scalability over immediate control** - Stateless > session management
- **Chose API-first over traditional sessions** - Supports future mobile/microservices

## Related Decisions
- **ADR 002**: SQLModel for database ORM
- **ADR 003**: FastAPI for backend framework
- **ADR 004**: Monorepo structure

## References
- [RFC 7519 - JSON Web Token (JWT)](https://datatracker.ietf.org/doc/html/rfc7519)
- [OWASP JWT Security Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- [python-jose documentation](https://python-jose.readthedocs.io/)

## Date
2025-12-31

## Authors
Phase II Implementation Team (Spec-Driven Development)
