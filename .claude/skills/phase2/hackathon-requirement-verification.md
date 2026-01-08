# Skill: hackathon-requirement-verification

## 1. Skill Name
`hackathon-requirement-verification`

## 2. Purpose
Confirm Phase 2 specifications fully satisfy hackathon requirements and evaluation criteria, ensuring all deliverables are present, phase boundaries respected, and specifications demonstrate AI-native, spec-driven development maturity.

## 3. Applicable Agents
- **hackathon-judge-reviewer** (primary)
- fullstack-spec-architect (deliverable validation)
- spec-architect (process validation)

## 4. Inputs
- **Hackathon Requirements Document**: Phase 2 deliverables checklist
- **All Phase 2 Specifications**: Complete spec suite
- **Project Artifacts**: Documentation, ADRs, PHRs, agents, skills
- **Evaluation Criteria**: Judging rubric categories
- **Phase Definition**: What's in/out of Phase 2 scope

## 5. Outputs
- **Verification Report**: Pass/fail status with evidence
- **Requirements Traceability Matrix**: Spec coverage for each requirement
- **Deliverables Checklist**: All required artifacts validated
- **Phase Discipline Validation**: Scope boundaries respected
- **Judge-Facing Summary**: What was delivered and why it matters
- **Gap Analysis**: Missing or incomplete requirements

## 6. Scope & Boundaries

### In Scope
- Verifying Phase 2 requirements met
- Validating spec-driven process followed
- Checking all artifacts present (specs, plans, tasks, docs)
- Confirming phase discipline (no scope creep)
- Assessing judge-facing clarity

### Out of Scope
- Implementation quality (code review)
- Performance testing
- Full security audit (see `security-risk-identification`)
- Phase 3+ planning validation

## 7. Reusability Notes
- **Phase 2**: Establishes verification methodology
- **Phase 3-5**: Reuse same verification framework
- **Cross-Project**: Checklist adaptable to any phased project

## 8. Dependencies

### Upstream Dependencies
- All Phase 2 specification skills completed
- `fullstack-spec-audit` (quality validation)
- `security-risk-identification` (security validation)

### Downstream Dependencies
- Implementation go/no-go decision
- Phase 3 planning initiation

## 9. Quality Expectations

### Objectivity
- Evidence-based verification (not assumptions)
- Judge's perspective (not developer's)
- Clear pass/fail criteria

### Completeness
- Every hackathon requirement checked
- All artifacts validated
- No gaps overlooked

### Actionability
- Clear list of what's missing
- Specific steps to achieve compliance
- Prioritized by importance

## 10. Example Usage (Spec-Level)

### Phase 2 Hackathon Requirements Checklist

---

#### Category 1: Functional Requirements

**Requirement 1.1: User Authentication**
```
Status: ✅ PASS

Evidence:
  - Spec: jwt-auth-flow-specification.md
  - Covers: Login, logout, JWT issuance, validation
  - Acceptance Criteria:
    ✅ User can register with email/password
    ✅ User can log in and receive JWT token
    ✅ User can log out (token cleared)
    ✅ Protected routes require valid JWT

Judge-Facing Summary:
  "Phase 2 implements JWT-based authentication with 15-minute token expiration,
   enforcing secure login/logout flows across the full stack."
```

**Requirement 1.2: Personal Todo Management**
```
Status: ✅ PASS

Evidence:
  - Spec: rest-api-contract-definition.md
  - Covers: CRUD operations for user-owned todos
  - Acceptance Criteria:
    ✅ User can create todos (title + optional description)
    ✅ User can view their todo list
    ✅ User can update todo content
    ✅ User can mark todos complete/incomplete
    ✅ User can delete todos

Judge-Facing Summary:
  "Full CRUD operations specified with user-scoped data isolation,
   ensuring each user sees only their own todos."
```

**Requirement 1.3: Data Persistence**
```
Status: ✅ PASS

Evidence:
  - Spec: relational-schema-design.md
  - Database: PostgreSQL (Neon)
  - Schema: users table + todos table with foreign keys
  - Acceptance Criteria:
    ✅ Data persists across sessions
    ✅ Database enforces referential integrity
    ✅ User ownership enforced at DB level (foreign keys)

Judge-Facing Summary:
  "PostgreSQL database with normalized schema, foreign key constraints,
   and proper indexes for performance."
```

**Requirement 1.4: User Data Isolation**
```
Status: ✅ PASS

Evidence:
  - Spec: data-ownership-enforcement.md
  - Covers: Query filtering, authorization checks, privacy
  - Acceptance Criteria:
    ✅ Users cannot access other users' todos
    ✅ All queries include WHERE user_id = {current_user}
    ✅ 404 responses prevent information leakage
    ✅ Database foreign keys enforce ownership

Judge-Facing Summary:
  "Multi-layer data isolation: database constraints, API middleware,
   and query-level filtering ensure zero cross-user data leakage."
```

---

#### Category 2: Technical Architecture

**Requirement 2.1: Full-Stack Implementation**
```
Status: ✅ PASS

Evidence:
  - Frontend: nextjs-frontend-architect specifications
  - Backend: fastapi-backend-architect specifications
  - Database: relational-schema-design
  - Auth: auth-security-architect specifications

Judge-Facing Summary:
  "Complete full-stack architecture: Next.js (frontend) + FastAPI (backend)
   + PostgreSQL (database) + Better Auth (authentication)."
```

**Requirement 2.2: RESTful API Design**
```
Status: ✅ PASS

Evidence:
  - Spec: rest-api-contract-definition.md
  - Endpoints: 9 total (auth + todos CRUD)
  - HTTP Semantics: GET (read), POST (create), PUT (update), DELETE (remove)
  - Status Codes: 200, 201, 400, 401, 404, 500 appropriately used

Judge-Facing Summary:
  "Industry-standard REST API with proper HTTP semantics, comprehensive
   error handling, and OpenAPI-ready contracts."
```

**Requirement 2.3: Responsive UI**
```
Status: ✅ PASS

Evidence:
  - Spec: responsive-ui-specification.md
  - Breakpoints: Mobile (320px+), Tablet (768px+), Desktop (1024px+)
  - Patterns: Mobile-first, touch-friendly (44px targets)
  - Accessibility: ARIA labels, keyboard navigation

Judge-Facing Summary:
  "Mobile-first responsive design with explicit specifications for
   all screen sizes and accessibility standards."
```

---

#### Category 3: Spec-Driven Development Process

**Requirement 3.1: Comprehensive Specifications**
```
Status: ✅ PASS

Evidence:
  - 15 Phase 2 skills created (.claude/skills/phase2/)
  - Specifications cover all layers:
    ✅ Full-stack orchestration (3 skills)
    ✅ Authentication & security (3 skills)
    ✅ Backend API & data (3 skills)
    ✅ Frontend UX & integration (3 skills)
    ✅ Review & evaluation (3 skills)

Judge-Facing Summary:
  "15 reusable, judge-auditable skills define every aspect of the
   Phase 2 architecture, from JWT flows to responsive UI patterns."
```

**Requirement 3.2: Cross-Layer Consistency**
```
Status: ✅ PASS

Evidence:
  - Skill: cross-layer-consistency-validation.md
  - Validated: Data types, field names, error formats
  - Example: user_id (UUID) consistent across DB, API, JWT

Judge-Facing Summary:
  "Explicit consistency validation ensures frontend expectations
   match backend contracts, preventing integration failures."
```

**Requirement 3.3: Phase Boundaries Enforced**
```
Status: ✅ PASS

Evidence:
  - Skill: phase-safe-scope-partitioning.md
  - In Scope: Auth, CRUD, persistence (Phase 2)
  - Out of Scope: OAuth, sharing, real-time (Phase 3+)
  - Extensibility hooks documented for future phases

Judge-Facing Summary:
  "Strict phase discipline: Phase 2 delivers foundational full-stack
   architecture with clear extensibility for Phases 3-5."
```

**Requirement 3.4: Security Considerations**
```
Status: ✅ PASS

Evidence:
  - Skill: security-risk-identification.md
  - Analyzed: OWASP Top 10 threats
  - Mitigations: SQL injection, XSS, IDOR, mass assignment
  - Known risks accepted with justification (e.g., localStorage XSS)

Judge-Facing Summary:
  "Proactive security analysis identifies risks and mitigations
   at spec level, demonstrating mature security-first design."
```

---

#### Category 4: Project Artifacts & Documentation

**Requirement 4.1: Specification Documents**
```
Status: ✅ PASS

Artifacts:
  ✅ specs/002-phase2-fullstack/spec.md (or equivalent)
  ✅ specs/002-phase2-fullstack/plan.md
  ✅ specs/002-phase2-fullstack/tasks.md
  ✅ Cross-layer specifications documented

Location: .claude/skills/phase2/ (15 skills)
```

**Requirement 4.2: Architecture Decision Records (ADRs)**
```
Status: ⚠️ PARTIAL

Expected ADRs for Phase 2:
  ✅ "ADR-001: JWT Authentication Strategy"
  ✅ "ADR-002: PostgreSQL + Neon for Database"
  ⚠️ Missing: "ADR-003: localStorage vs HttpOnly Cookies"
  ⚠️ Missing: "ADR-004: Next.js App Router vs Pages Router"

Recommendation: Create 2 additional ADRs for key decisions
```

**Requirement 4.3: Prompt History Records (PHRs)**
```
Status: ✅ PASS (Assumed)

Expected PHRs:
  ✅ Constitution definition
  ✅ Feature specification session
  ✅ Implementation planning session
  ✅ Task breakdown session

Location: history/prompts/002-phase2-fullstack/
```

**Requirement 4.4: Reusable Agents**
```
Status: ✅ PASS

Agents Created:
  ✅ fullstack-spec-architect
  ✅ auth-security-architect
  ✅ fastapi-backend-architect
  ✅ nextjs-frontend-architect

Location: .claude/agents/
```

**Requirement 4.5: Skills Library**
```
Status: ✅ PASS

Skills Created: 15 (Phase 2)
Categories:
  ✅ Full-Stack Specification (3)
  ✅ Authentication & Security (3)
  ✅ Backend API & Data (3)
  ✅ Frontend UX & Integration (3)
  ✅ Review & Hackathon Evaluation (3)

Location: .claude/skills/phase2/
```

**Requirement 4.6: README Documentation**
```
Status: ⚠️ NEEDS UPDATE

Expected:
  ✅ README.md exists
  ⚠️ Update: Include Phase 2 overview
  ⚠️ Update: Architecture diagram
  ⚠️ Update: Setup instructions

Recommendation: Update README with Phase 2 context
```

---

#### Category 5: AI-Native Development Demonstration

**Requirement 5.1: Agent-Driven Workflow**
```
Status: ✅ PASS

Evidence:
  - 4 agents defined for Phase 2 (fullstack, auth, backend, frontend)
  - Skills reference applicable agents
  - Orchestration patterns documented

Judge-Facing Summary:
  "Specialized agents coordinate specification work, each with
   defined responsibilities and tool access."
```

**Requirement 5.2: Reusable Skill Library**
```
Status: ✅ PASS

Evidence:
  - 15 skills created (reusable across phases)
  - Phase 1 skills preserved (6 skills)
  - Phase 2 skills extend Phase 1 patterns
  - Metadata includes reusability notes

Judge-Facing Summary:
  "Growing library of 21 skills (6 Phase 1 + 15 Phase 2) demonstrates
   systematic knowledge capture and reuse."
```

**Requirement 5.3: Spec-First Methodology**
```
Status: ✅ PASS

Evidence:
  - Specifications created BEFORE implementation
  - Skills define "what" not "how" (no code in skills)
  - Cross-layer validation performed
  - Judge-readable documentation

Judge-Facing Summary:
  "Phase 2 follows rigorous spec-first approach: define requirements,
   validate consistency, then implement—not code-first."
```

---

### Requirements Traceability Matrix

| Requirement | Status | Evidence Document | Notes |
|-------------|--------|-------------------|-------|
| User Registration | ✅ PASS | jwt-auth-flow-specification.md | Email/password |
| User Login | ✅ PASS | jwt-auth-flow-specification.md | JWT issued |
| User Logout | ✅ PASS | auth-aware-ui-flow-design.md | Token cleared |
| Create Todo | ✅ PASS | rest-api-contract-definition.md | POST /api/todos |
| Read Todos | ✅ PASS | rest-api-contract-definition.md | GET /api/todos |
| Update Todo | ✅ PASS | rest-api-contract-definition.md | PUT /api/todos/:id |
| Delete Todo | ✅ PASS | rest-api-contract-definition.md | DELETE /api/todos/:id |
| Data Persistence | ✅ PASS | relational-schema-design.md | PostgreSQL |
| User Isolation | ✅ PASS | data-ownership-enforcement.md | user_id filtering |
| Responsive UI | ✅ PASS | responsive-ui-specification.md | Mobile-first |
| RESTful API | ✅ PASS | rest-api-contract-definition.md | 9 endpoints |
| Authentication | ✅ PASS | api-auth-enforcement-definition.md | JWT middleware |
| Security Analysis | ✅ PASS | security-risk-identification.md | OWASP Top 10 |
| Phase Boundaries | ✅ PASS | phase-safe-scope-partitioning.md | Scope enforced |
| ADRs | ⚠️ PARTIAL | history/adr/ | 2 of 4 recommended |

---

### Overall Verification Result

```
PHASE 2 REQUIREMENTS: PASS WITH MINOR ITEMS

Functional Requirements: 100% (4/4)
Technical Architecture: 100% (3/3)
Spec-Driven Process: 100% (4/4)
Project Artifacts: 83% (5/6 complete, 1 partial)
AI-Native Development: 100% (3/3)

OVERALL SCORE: 96%

BLOCKERS: None

NICE-TO-HAVES (Before Implementation):
  1. Create 2 additional ADRs for key architectural decisions
  2. Update README.md with Phase 2 overview and architecture diagram

RECOMMENDATION: PROCEED TO IMPLEMENTATION
```

---

## Metadata
- **Version**: 1.0.0
- **Phase Introduced**: Phase 2
- **Last Updated**: 2025-12-30
- **Skill Type**: Verification
- **Execution Surface**: Agent (hackathon-judge-reviewer)
