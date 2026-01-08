# Skill: phase-safe-scope-partitioning

## 1. Skill Name
`phase-safe-scope-partitioning`

## 2. Purpose
Enforce strict phase boundaries while designing specifications that allow future extensibility, preventing scope creep in current phase while maintaining architectural runway for subsequent phases (3-5).

## 3. Applicable Agents
- **fullstack-spec-architect** (primary)
- spec-architect (coordination)
- hackathon-judge-reviewer (validation)
- phase-1-todo-delivery (Phase 1 context)

## 4. Inputs
- **Current Phase Number**: 2, 3, 4, or 5
- **Phase Definition Document**: Explicit scope for each phase
- **Feature Requirements**: User story or feature request
- **Unified Specification**: Output from orchestration skill
- **Future Phase Roadmap**: Known requirements for phases 3-5
- **Constitution**: Project principles including phase discipline

## 5. Outputs
- **Phase Scope Document**: Explicit in-scope / out-of-scope declaration
- **Extensibility Hooks**: Documented future extension points
- **Scope Creep Warnings**: Features that belong in future phases
- **Phase Boundary Map**: Visual/textual representation of phase limits
- **Acceptance Criteria**: Phase-specific success conditions
- **Rollback Plan**: How to revert to previous phase if needed

## 6. Scope & Boundaries

### In Scope
- Explicit phase boundary enforcement
- Identification of features belonging to future phases
- Documentation of extensibility hooks for future work
- Prevention of "while we're at it" scope expansion
- Alignment of spec complexity with phase maturity
- Trade-off documentation (what's deferred and why)

### Out of Scope
- Implementation timeline estimation
- Resource allocation or sprint planning
- Detailed Phase 3-5 specifications (only high-level hooks)
- Technology migration planning
- Performance benchmarking across phases

## 7. Reusability Notes
- **Phase 2**: Establishes phase partitioning methodology
- **Phase 3**: Reuses partitioning rules for real-time features
- **Phase 4**: Scales partitioning to multi-user scenarios
- **Phase 5**: Extends to AI/chatbot integration boundaries
- **Cross-Project**: Phase discipline framework applicable to any phased project

### Reusability Mechanisms
- Phase boundary decision tree (reusable template)
- Scope creep detection checklist
- Extensibility hook documentation patterns
- Phase upgrade path templates

## 8. Dependencies

### Upstream Dependencies
- `fullstack-requirement-orchestration` (defines overall scope)
- `cross-layer-consistency-validation` (ensures validated specs)
- Phase definition document (hackathon requirements)

### Downstream Dependencies
- All layer-specific specification skills (use phase boundaries)
- `hackathon-requirement-verification` (validates phase completion)
- Implementation task generation (scoped to phase)

### Parallel Dependencies
- Can inform `security-risk-identification` (phase-specific risks)

## 9. Quality Expectations

### Strictness
- Zero tolerance for out-of-phase features sneaking into specs
- Every feature explicitly marked as in-phase or deferred
- Clear justification for any phase boundary exceptions

### Clarity
- Non-negotiable phase boundaries clearly stated
- Deferred features explicitly listed with target phase
- Extensibility hooks documented with future use cases

### Pragmatism
- Phase boundaries balance hackathon goals with technical feasibility
- Extensibility hooks prevent architectural rework
- Deferred features preserve motivation and forward momentum

### Auditability
- Judges can verify phase discipline from documentation
- Clear evidence that scope was actively managed
- Traceable decisions for why features were included/excluded

## 10. Example Usage (Spec-Level)

### Scenario: Phase 2 Scope Partitioning for Todo Application

**Input Requirements:**
```
Feature Request: "Users should be able to log in, manage their personal todos, and optionally share todos with other users for collaboration."

Phase Context: Phase 2
Known Future Phases:
  - Phase 3: Real-time sync, notifications
  - Phase 4: Multi-user collaboration, sharing
  - Phase 5: AI-powered chatbot interface
```

**Phase Partitioning Analysis:**

#### Phase 2: In Scope (Core Authentication + Personal Todos)
- ✅ User registration and login
- ✅ JWT-based authentication
- ✅ Personal todo CRUD operations
- ✅ User-specific data isolation
- ✅ Database persistence (PostgreSQL)
- ✅ Protected API endpoints
- ✅ Authenticated frontend routes

**Justification**: These features establish the foundational authenticated full-stack architecture required for subsequent phases.

#### Phase 2: Out of Scope (Deferred to Future Phases)
- ❌ **Todo sharing/collaboration** → Phase 4
  - **Reason**: Requires multi-user permissions, access control, and shared data models
  - **Complexity**: High (new database relationships, permission system)
  - **Dependency**: Phase 3 real-time sync should exist first

- ❌ **Real-time notifications** → Phase 3
  - **Reason**: Requires WebSocket infrastructure
  - **Complexity**: Medium (new communication protocol)
  - **Dependency**: Basic CRUD must be solid first

- ❌ **OAuth providers (Google, GitHub)** → Phase 3
  - **Reason**: Email/password auth sufficient for Phase 2 validation
  - **Complexity**: Medium (third-party integration)
  - **Extensibility**: Better Auth supports OAuth, easy to add later

- ❌ **Password reset via email** → Phase 3
  - **Reason**: Requires email service integration
  - **Complexity**: Low-medium (SMTP, email templates)
  - **Workaround**: Admin can reset passwords in Phase 2 if needed

- ❌ **AI chatbot interface** → Phase 5
  - **Reason**: Separate UI paradigm
  - **Complexity**: High (LLM integration, conversational design)
  - **Dependency**: All core features must exist first

#### Extensibility Hooks for Future Phases

**Hook 1: Multi-User Collaboration (Phase 4)**
```
Database Design Extensibility:
- todos.user_id: Keep as owner_id in future
- Create todos_collaborators table in Phase 4 with:
  - todo_id (FK)
  - user_id (FK)
  - permission_level (read, write, admin)

API Design Extensibility:
- Current: GET /api/todos (returns user's todos)
- Phase 4: GET /api/todos?include=shared (includes shared todos)
- Phase 4: POST /api/todos/:id/share (share todo with user)

No Phase 2 code changes required; architecture supports extension.
```

**Hook 2: Real-Time Sync (Phase 3)**
```
Backend Architecture Extensibility:
- Phase 2: REST endpoints only
- Phase 3: Add WebSocket endpoint at /ws
- Database: Add todos.updated_at for sync detection
- Frontend: Add WebSocket client alongside REST client

No Phase 2 refactoring required; additive only.
```

**Hook 3: OAuth Providers (Phase 3)**
```
Authentication Extensibility:
- Phase 2: Better Auth with email/password strategy
- Phase 3: Enable Better Auth OAuth strategies (config change)
- Database: users.auth_provider column (default 'email')
- API: Same JWT validation, provider-agnostic

Better Auth designed for this; minimal changes needed.
```

#### Scope Creep Warning Triggers

**Warning 1: "While we're building login, let's add social auth"**
- **Response**: Deferred to Phase 3. Email/password sufficient for Phase 2 validation.
- **Action**: Document as extensibility hook, do not implement now.

**Warning 2: "Let's make todos shareable between users"**
- **Response**: Phase 4 feature. Focus on per-user isolation first.
- **Action**: Ensure database schema doesn't prevent sharing (user_id as FK, not embedded data).

**Warning 3: "Can we add password reset emails?"**
- **Response**: Phase 3 feature. Requires SMTP integration.
- **Action**: Document as nice-to-have, not blocking for Phase 2 demo.

#### Phase 2 Acceptance Criteria (Strict)
- [ ] User can register with email and password
- [ ] User can log in and receive JWT token
- [ ] User can create, read, update, delete their own todos
- [ ] User cannot access other users' todos (enforced at DB and API)
- [ ] Frontend displays only authenticated user's todos
- [ ] User can log out and session expires
- [ ] All data persists in PostgreSQL database
- [ ] Zero scope creep: no Phase 3+ features implemented

#### Phase Boundary Commitment
```
WE WILL NOT:
- Implement real-time sync (Phase 3)
- Implement todo sharing (Phase 4)
- Implement OAuth providers (Phase 3)
- Implement AI chatbot (Phase 5)
- Implement email notifications (Phase 3)

WE WILL:
- Maintain architecture that supports these features in future phases
- Document extensibility hooks
- Focus exclusively on authenticated personal todo management
- Demonstrate phase discipline to hackathon judges
```

---

## Metadata
- **Version**: 1.0.0
- **Phase Introduced**: Phase 2
- **Last Updated**: 2025-12-30
- **Skill Type**: Governance
- **Execution Surface**: Agent (fullstack-spec-architect)
