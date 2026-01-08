# Skill: cross-layer-consistency-validation

## 1. Skill Name
`cross-layer-consistency-validation`

## 2. Purpose
Ensure specifications across UI, API, authentication, and database layers do not contradict each other, maintaining semantic consistency, data type alignment, and contract compatibility throughout the full-stack architecture.

## 3. Applicable Agents
- **fullstack-spec-architect** (primary)
- spec-architect (coordination)
- auth-security-architect (validation)
- fastapi-backend-architect (validation)
- nextjs-frontend-architect (validation)
- hackathon-judge-reviewer (audit)

## 4. Inputs
- **Frontend Specification**: UI flows, component contracts, API expectations
- **Backend Specification**: REST endpoints, request/response models, business logic rules
- **Authentication Specification**: JWT claims, token lifecycle, user identity propagation
- **Database Specification**: Schema definitions, constraints, relationships
- **Cross-Layer Contracts**: Integration point definitions from orchestration

## 5. Outputs
- **Consistency Validation Report**: Pass/fail status with detailed findings
- **Contradiction Matrix**: Specific inconsistencies identified with layer locations
- **Resolution Recommendations**: Suggested fixes for each inconsistency
- **Alignment Checklist**: Verified consistency checkpoints
- **Risk Assessment**: Impact severity of unresolved contradictions

## 6. Scope & Boundaries

### In Scope
- Data type consistency across layers (e.g., `user_id` as UUID in DB → string in API → string in UI)
- Field naming consistency (snake_case in DB, camelCase in API/UI)
- Required vs optional field alignment
- Authentication requirement consistency (protected routes match protected endpoints)
- Error code/message alignment across frontend and backend
- Business rule consistency (e.g., max todo length in UI validation matches backend validation)

### Out of Scope
- Performance optimization recommendations
- Implementation-level code validation
- UI/UX design consistency
- Detailed test case generation
- Security vulnerability scanning (covered by security-risk-identification skill)

## 7. Reusability Notes
- **Phase 2**: Establishes baseline consistency patterns for authenticated full-stack app
- **Phase 3**: Extends to real-time sync consistency (WebSocket message formats)
- **Phase 4**: Validates multi-user interaction consistency
- **Phase 5**: Ensures AI/chatbot layer aligns with existing layers
- **Cross-Project**: Checklist template reusable for any full-stack application

### Reusability Mechanisms
- Consistency rules documented as reusable checklist templates
- Automated validation patterns (e.g., type mapping rules)
- Layer-agnostic validation principles
- Progressive validation (partial validation during early phases)

## 8. Dependencies

### Upstream Dependencies
- `fullstack-requirement-orchestration` (must complete first)
- Layer-specific specifications (frontend, backend, auth, database)

### Downstream Dependencies
- `phase-safe-scope-partitioning` (uses validated specs)
- `fullstack-spec-audit` (comprehensive audit)
- Implementation tasks generation (depends on consistent specs)

### Parallel Dependencies
- Can run in parallel with other validation skills after layer specs exist

## 9. Quality Expectations

### Accuracy
- Zero false positives (no incorrect contradiction reports)
- Zero false negatives (all contradictions detected)
- Clear evidence provided for each finding

### Actionability
- Each inconsistency includes specific file/section references
- Resolution recommendations are implementable
- Severity levels guide prioritization (critical, high, medium, low)

### Completeness
- All integration points validated
- All shared data models checked
- All authentication flows verified
- All error paths consistent

### Automation-Readiness
- Validation rules expressible as code for future automation
- Checkboxes suitable for automated checklist tools
- Structured output (JSON/YAML) for tooling integration

## 10. Example Usage (Spec-Level)

### Scenario: Validate Phase 2 Todo CRUD Specification Consistency

**Input Specifications:**

**Frontend Spec:**
```
API Call: POST /todos
Body: { title: string, description?: string }
Expected Response: { id: number, title: string, description: string | null, completed: boolean, createdAt: string }
```

**Backend Spec:**
```
Endpoint: POST /api/todos
Request Model: CreateTodoRequest { title: str, description: str | None }
Response Model: TodoResponse { id: int, title: str, description: str | None, completed: bool, created_at: datetime }
```

**Database Spec:**
```
Table: todos
Columns:
  - id: SERIAL PRIMARY KEY
  - user_id: UUID NOT NULL REFERENCES users(id)
  - title: VARCHAR(200) NOT NULL
  - description: TEXT NULL
  - completed: BOOLEAN DEFAULT FALSE
  - created_at: TIMESTAMP DEFAULT NOW()
```

**Validation Output:**

#### ✅ Consistencies Detected
1. **Data Types Aligned**: `id` (number/int), `title` (string/str), `completed` (boolean/bool)
2. **Optional Fields Match**: `description` is optional in frontend, backend, and database
3. **Required Fields Match**: `title` is required across all layers

#### ❌ Inconsistencies Detected

**Inconsistency 1: Field Naming Convention Mismatch**
- **Location**: Frontend expects `createdAt` (camelCase), Backend returns `created_at` (snake_case)
- **Severity**: High (breaks API contract)
- **Impact**: Frontend will receive `undefined` for createdAt field
- **Resolution**: Backend must transform `created_at` → `createdAt` in response serialization OR frontend must accept `created_at`
- **Recommendation**: Add Pydantic alias `created_at = Field(alias='createdAt')` in backend response model

**Inconsistency 2: Missing User Context in Frontend**
- **Location**: Frontend API call does not mention authentication header
- **Severity**: Critical (feature will fail)
- **Impact**: Backend requires JWT but frontend spec silent on auth
- **Resolution**: Frontend spec must document: `Headers: { Authorization: 'Bearer <token>' }`
- **Recommendation**: Update frontend API integration contract to include authentication requirements

**Inconsistency 3: URL Path Mismatch**
- **Location**: Frontend calls `/todos`, Backend defines `/api/todos`
- **Severity**: Critical (404 errors)
- **Impact**: All API calls will fail with 404 Not Found
- **Resolution**: Align on single path convention
- **Recommendation**: Use `/api/todos` consistently, update frontend base URL configuration

**Inconsistency 4: Missing user_id Enforcement**
- **Location**: Database schema requires `user_id`, but backend spec does not mention user filtering
- **Severity**: Critical (data leak risk)
- **Impact**: Without explicit user filtering, queries could return all users' todos
- **Resolution**: Backend spec must document: "All queries filtered by authenticated user_id"
- **Recommendation**: Add explicit user ownership enforcement to backend specification

#### Consistency Validation Report
```
Total Checks: 12
Passed: 8
Failed: 4
Critical Issues: 3
High Issues: 1
Medium Issues: 0
Low Issues: 0

Status: FAILED - Critical inconsistencies must be resolved before implementation
```

---

## Metadata
- **Version**: 1.0.0
- **Phase Introduced**: Phase 2
- **Last Updated**: 2025-12-30
- **Skill Type**: Validation
- **Execution Surface**: Agent (fullstack-spec-architect)
