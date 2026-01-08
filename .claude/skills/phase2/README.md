# Phase 2 Skills Library

**Hackathon Todo Application - Full-Stack Web Development**

## Overview

This directory contains 15 reusable, judge-auditable skills for Phase 2 of the Hackathon Todo Application. Phase 2 introduces full-stack web architecture with authentication, REST APIs, database persistence, and responsive UI—transitioning from Phase 1's in-memory console app to a production-ready authenticated web application.

## Phase 2 Technology Stack

- **Frontend**: Next.js (React) with TypeScript
- **Backend**: FastAPI (Python) with SQLModel
- **Database**: PostgreSQL (Neon serverless)
- **Authentication**: Better Auth + JWT
- **Deployment**: Vercel (frontend) + Render/Railway (backend)

## Skills by Category

### Category 1: Full-Stack Specification Skills (3)

Coordinate requirements across frontend, backend, authentication, and database layers.

1. **fullstack-requirement-orchestration**
   - Coordinate frontend, backend, auth, and database requirements into unified spec
   - Applicable Agents: fullstack-spec-architect, spec-architect

2. **cross-layer-consistency-validation**
   - Ensure specifications across all layers do not contradict each other
   - Applicable Agents: fullstack-spec-architect, hackathon-judge-reviewer

3. **phase-safe-scope-partitioning**
   - Enforce strict Phase 2 boundaries while designing for future extensibility
   - Applicable Agents: fullstack-spec-architect, hackathon-judge-reviewer

### Category 2: Authentication & Security Skills (3)

Define secure authentication flows and user identity management.

4. **jwt-auth-flow-specification**
   - Define JWT authentication lifecycle: login → token issuance → validation → refresh → logout
   - Applicable Agents: auth-security-architect, fastapi-backend-architect

5. **api-auth-enforcement-definition**
   - Specify how JWT validation is applied to REST endpoints (middleware, guards)
   - Applicable Agents: auth-security-architect, fastapi-backend-architect

6. **user-identity-propagation**
   - Define how authenticated user identity flows from JWT → backend → database
   - Applicable Agents: auth-security-architect, fastapi-backend-architect

### Category 3: Backend API & Data Skills (3)

Specify REST APIs, database schemas, and data ownership rules.

7. **rest-api-contract-definition**
   - Define REST endpoints, HTTP semantics, request/response models, error codes
   - Applicable Agents: fastapi-backend-architect, fullstack-spec-architect

8. **data-ownership-enforcement**
   - Specify rules ensuring users only access their own data (query filtering, 404 responses)
   - Applicable Agents: fastapi-backend-architect, auth-security-architect

9. **relational-schema-design**
   - Define normalized database schemas (tables, columns, constraints, indexes, foreign keys)
   - Applicable Agents: fastapi-backend-architect, fullstack-spec-architect

### Category 4: Frontend UX & Integration Skills (3)

Design responsive, accessible UI with authentication awareness.

10. **auth-aware-ui-flow-design**
    - Specify UI behavior based on authentication state (logged-in, logged-out, expired)
    - Applicable Agents: nextjs-frontend-architect, fullstack-spec-architect

11. **frontend-backend-contract-alignment**
    - Ensure frontend API expectations match backend contracts (types, fields, errors)
    - Applicable Agents: fullstack-spec-architect, nextjs-frontend-architect

12. **responsive-ui-specification**
    - Define responsive behavior across mobile, tablet, desktop without implementation details
    - Applicable Agents: nextjs-frontend-architect, fullstack-spec-architect

### Category 5: Review & Hackathon Evaluation Skills (3)

Validate specifications for completeness, security, and hackathon readiness.

13. **fullstack-spec-audit**
    - Validate completeness, clarity, testability, and judge-readability of Phase 2 specs
    - Applicable Agents: hackathon-judge-reviewer, fullstack-spec-architect

14. **security-risk-identification**
    - Identify auth/authz/data exposure risks at spec level (OWASP Top 10 analysis)
    - Applicable Agents: auth-security-architect, hackathon-judge-reviewer

15. **hackathon-requirement-verification**
    - Confirm Phase 2 specs satisfy hackathon requirements and evaluation criteria
    - Applicable Agents: hackathon-judge-reviewer, fullstack-spec-architect

## Key Design Principles

### 1. Spec-Driven, Not Implementation-Driven
- Skills define **what** must be specified, not **how** to implement
- No code in skill definitions (only specification patterns)
- Technology-agnostic where possible (e.g., "JWT validation" not "FastAPI dependency injection code")

### 2. Judge-Auditable
- Clear, professional language
- Rationale documented for architectural decisions
- Examples demonstrate spec application, not code
- Security considerations transparent

### 3. Reusable Across Phases
- Phase 2 skills extend for Phase 3 (real-time, OAuth)
- Phase 4 (multi-user collaboration)
- Phase 5 (AI chatbot integration)
- Metadata includes reusability notes

### 4. Agent-Aligned
- Each skill lists applicable agents
- Primary agent (main responsibility) + supporting agents (coordination)
- Enables parallel agent execution

## Usage Guidelines

### For Agents

When executing Phase 2 specification work:

1. **Identify Required Skills**: Match task to skill category (orchestration, auth, backend, frontend, review)
2. **Read Skill Definition**: Understand purpose, inputs, outputs, scope
3. **Apply Skill Pattern**: Follow examples, adapt to specific feature context
4. **Document Outputs**: Create artifacts matching skill outputs (specs, diagrams, checklists)
5. **Cross-Reference**: Use upstream/downstream dependencies to sequence work

### For Humans (Judges, Developers, Reviewers)

When evaluating Phase 2 work:

1. **Start with Category 5 Skills** (fullstack-spec-audit, security-risk-identification, hackathon-requirement-verification)
   - These provide comprehensive evaluation frameworks
2. **Trace Requirements**: Use skills as validation checklists
3. **Assess Completeness**: Ensure all 15 skills have corresponding artifacts
4. **Review Examples**: Skills include spec-level examples for reference

## Skill Execution Flow (Recommended Sequence)

### Step 1: Orchestration (Skills 1-3)
```
fullstack-requirement-orchestration
  → Coordinate requirements across all layers

cross-layer-consistency-validation
  → Ensure no contradictions

phase-safe-scope-partitioning
  → Define Phase 2 boundaries
```

### Step 2: Layer-Specific Specification (Skills 4-12)

**Authentication & Security (Skills 4-6)**
```
jwt-auth-flow-specification
  → Define token lifecycle

api-auth-enforcement-definition
  → Define middleware enforcement

user-identity-propagation
  → Define identity flow across layers
```

**Backend API & Data (Skills 7-9)**
```
relational-schema-design
  → Define database schema

rest-api-contract-definition
  → Define API endpoints

data-ownership-enforcement
  → Define user filtering rules
```

**Frontend UX (Skills 10-12)**
```
auth-aware-ui-flow-design
  → Define authentication-based UI behavior

frontend-backend-contract-alignment
  → Validate API contract consistency

responsive-ui-specification
  → Define responsive patterns
```

### Step 3: Validation & Review (Skills 13-15)
```
security-risk-identification
  → Analyze security risks

fullstack-spec-audit
  → Validate spec quality

hackathon-requirement-verification
  → Confirm hackathon compliance
```

## Quality Standards

All Phase 2 skills meet these standards:

- **Completeness**: All 10 required sections present (Name, Purpose, Agents, Inputs, Outputs, Scope, Reusability, Dependencies, Quality, Examples)
- **Clarity**: Professional language, no ambiguity
- **Testability**: Acceptance criteria verifiable
- **Reusability**: Extensible to Phase 3-5
- **Judge-Readability**: Accessible to non-technical evaluators

## Integration with Phase 1 Skills

Phase 2 skills **extend** (not replace) Phase 1 skills:

- **Phase 1**: In-memory console app, basic CRUD, specification foundations
- **Phase 2**: Full-stack web app, authentication, persistence, multi-layer architecture

Phase 1 skills remain relevant:
- Specification workflow (sp.specify, sp.plan, sp.tasks)
- Implementation practices (test-driven, iterative)
- Documentation (ADRs, PHRs)

Phase 2 adds:
- Cross-layer orchestration
- Authentication/authorization patterns
- API design and data persistence
- Responsive UI and frontend integration

## Future Phases

**Phase 3 Extensions:**
- Real-time sync (WebSocket specifications)
- OAuth provider integration
- Notifications and alerts
- Password reset flows

**Phase 4 Extensions:**
- Multi-user collaboration (todo sharing)
- Permissions and access control
- Team/workspace features

**Phase 5 Extensions:**
- AI chatbot interface
- Conversational todo management
- LLM integration patterns

## Metadata

- **Version**: 1.0.0
- **Phase**: Phase 2
- **Skills Count**: 15
- **Created**: 2025-12-30
- **Compatible Agents**: fullstack-spec-architect, auth-security-architect, fastapi-backend-architect, nextjs-frontend-architect, hackathon-judge-reviewer
- **Hackathon**: Hackathon II - Spec-Driven AI-Native Development

---

## Quick Reference

| # | Skill Name | Category | Primary Agent |
|---|------------|----------|---------------|
| 1 | fullstack-requirement-orchestration | Orchestration | fullstack-spec-architect |
| 2 | cross-layer-consistency-validation | Orchestration | fullstack-spec-architect |
| 3 | phase-safe-scope-partitioning | Orchestration | fullstack-spec-architect |
| 4 | jwt-auth-flow-specification | Auth & Security | auth-security-architect |
| 5 | api-auth-enforcement-definition | Auth & Security | auth-security-architect |
| 6 | user-identity-propagation | Auth & Security | auth-security-architect |
| 7 | rest-api-contract-definition | Backend & Data | fastapi-backend-architect |
| 8 | data-ownership-enforcement | Backend & Data | fastapi-backend-architect |
| 9 | relational-schema-design | Backend & Data | fastapi-backend-architect |
| 10 | auth-aware-ui-flow-design | Frontend & UX | nextjs-frontend-architect |
| 11 | frontend-backend-contract-alignment | Frontend & UX | fullstack-spec-architect |
| 12 | responsive-ui-specification | Frontend & UX | nextjs-frontend-architect |
| 13 | fullstack-spec-audit | Review & Evaluation | hackathon-judge-reviewer |
| 14 | security-risk-identification | Review & Evaluation | auth-security-architect |
| 15 | hackathon-requirement-verification | Review & Evaluation | hackathon-judge-reviewer |

---

**For detailed information on each skill, see individual markdown files in this directory.**
