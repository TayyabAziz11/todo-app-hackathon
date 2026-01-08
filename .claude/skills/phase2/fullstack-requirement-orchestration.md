# Skill: fullstack-requirement-orchestration

## 1. Skill Name
`fullstack-requirement-orchestration`

## 2. Purpose
Coordinate frontend, backend, authentication, and database requirements into a unified, cohesive specification that ensures all architectural layers work together harmoniously while maintaining clear boundaries and responsibilities.

## 3. Applicable Agents
- **fullstack-spec-architect** (primary)
- spec-architect (supporting)
- auth-security-architect (coordination)
- fastapi-backend-architect (coordination)
- nextjs-frontend-architect (coordination)

## 4. Inputs
- **User Requirements**: Natural language feature description
- **Phase Context**: Current phase number (2-5) and phase boundaries
- **Technology Stack**: Confirmed technologies (Next.js, FastAPI, Better Auth, SQLModel, PostgreSQL)
- **Phase 1 Context**: Existing in-memory implementation and patterns
- **Constitution**: Project principles and architectural constraints

## 5. Outputs
- **Unified Specification Document**: Single source of truth spanning all layers
- **Layer Responsibility Matrix**: Clear ownership of concerns (UI, API, Auth, Data)
- **Integration Points Map**: Documented interfaces between layers
- **Cross-Layer Dependencies**: Explicit dependency graph
- **Phase Scope Boundaries**: What's in/out for current phase with future extensibility hooks

## 6. Scope & Boundaries

### In Scope
- Requirement decomposition across frontend, backend, auth, and database layers
- Identification of cross-layer contracts and integration points
- Alignment of user stories with technical capabilities at each layer
- Phase-specific feature scoping with extensibility markers
- Conflict detection between layer requirements

### Out of Scope
- Implementation details or code generation
- Technology selection (stack is predetermined)
- Performance benchmarking or optimization strategies
- Detailed UI wireframes or API endpoint implementations
- Test case generation (handled by other skills)

## 7. Reusability Notes
- **Phase 2**: Establishes initial full-stack orchestration patterns
- **Phase 3**: Extends to real-time features (WebSocket coordination)
- **Phase 4**: Scales to multi-user scenarios and shared data
- **Phase 5**: Incorporates AI/chatbot layer coordination
- **Cross-Project**: Template applies to any full-stack web application

### Reusability Mechanisms
- Layer abstraction allows technology swaps
- Phase markers enable progressive elaboration
- Contract-first approach supports parallel agent execution
- Dependency tracking prevents circular references

## 8. Dependencies

### Upstream Dependencies (Must Exist Before This Skill)
- Project constitution established
- Phase boundaries defined
- Technology stack confirmed

### Downstream Dependencies (Skills That Need This Output)
- `cross-layer-consistency-validation`
- `phase-safe-scope-partitioning`
- All layer-specific specification skills

### Parallel Dependencies (Can Execute Concurrently)
- None (this is typically a first step)

## 9. Quality Expectations

### Completeness
- All four layers (UI, API, Auth, DB) explicitly addressed
- No implicit assumptions about "obvious" requirements
- Future extensibility explicitly documented

### Clarity
- Non-technical stakeholders can understand layer boundaries
- Technical agents can derive actionable sub-specifications
- Integration points use consistent terminology

### Testability
- Each layer's responsibilities can be independently verified
- Integration contracts include success/failure scenarios
- Acceptance criteria span multiple layers where appropriate

### Maintainability
- Changes isolated to specific layers without cascade effects
- Version compatibility explicitly stated
- Deprecation paths for future phases documented

## 10. Example Usage (Spec-Level)

### Scenario: Phase 2 - User Authentication and Todo Management

**Input:**
```
User Story: As a registered user, I want to log in and manage my personal todo list so that my data is private and persistent.
Phase: 2
Stack: Next.js + FastAPI + Better Auth + SQLModel + Neon PostgreSQL
```

**Orchestration Output:**

#### Layer Responsibility Breakdown

**Frontend (Next.js)**
- Login form with email/password fields
- Session management using Better Auth client SDK
- Display authenticated user's todos only
- Logout functionality
- Protected routes requiring authentication

**Backend (FastAPI)**
- `/auth/login` endpoint (delegates to Better Auth)
- `/auth/verify` endpoint for JWT validation
- `/todos` CRUD endpoints with JWT middleware
- User identity extraction from JWT claims
- Error responses for unauthenticated requests

**Authentication (Better Auth + JWT)**
- User registration flow
- JWT token issuance on successful login
- Token refresh mechanism
- Token validation on every protected API call
- User session lifecycle management

**Database (SQLModel + PostgreSQL)**
- `users` table with email, hashed_password, created_at
- `todos` table with user_id foreign key
- Row-level user_id filtering in queries
- Database indexes on user_id for performance

#### Integration Contracts

**Frontend ↔ Backend**
- Frontend sends JWT in `Authorization: Bearer <token>` header
- Backend returns 401 if token invalid/expired
- Backend returns user-specific data in JSON format

**Backend ↔ Auth**
- Backend validates JWT signature using Better Auth public key
- Backend extracts `user_id` from JWT claims
- Backend enforces auth on all `/todos/*` routes

**Backend ↔ Database**
- All queries include `WHERE user_id = {authenticated_user_id}`
- Database enforces NOT NULL constraint on user_id
- No cross-user data leakage possible at query level

#### Phase 2 Boundaries
- **In Scope**: Login, logout, per-user todos
- **Out of Scope**: OAuth providers, password reset, email verification (Phase 3+)
- **Extensibility Hook**: Auth provider abstraction allows OAuth in Phase 3

---

## Metadata
- **Version**: 1.0.0
- **Phase Introduced**: Phase 2
- **Last Updated**: 2025-12-30
- **Skill Type**: Orchestration
- **Execution Surface**: Agent (fullstack-spec-architect)
