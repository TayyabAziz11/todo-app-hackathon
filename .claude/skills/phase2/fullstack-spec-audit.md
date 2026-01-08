# Skill: fullstack-spec-audit

## 1. Skill Name
`fullstack-spec-audit`

## 2. Purpose
Validate completeness, clarity, testability, and judge-readability of Phase 2 specifications, ensuring all architectural layers are comprehensively documented and ready for implementation without ambiguity.

## 3. Applicable Agents
- **hackathon-judge-reviewer** (primary)
- fullstack-spec-architect (comprehensive review)
- spec-architect (quality validation)

## 4. Inputs
- **All Phase 2 Specifications**: Frontend, backend, auth, database specs
- **Cross-Layer Contracts**: Integration point documentation
- **Phase Boundaries**: Scope definitions and extensibility hooks
- **Hackathon Requirements**: Phase 2 deliverables checklist

## 5. Outputs
- **Audit Report**: Pass/fail with detailed findings
- **Completeness Checklist**: All required sections present
- **Clarity Assessment**: Ambiguities and unclear sections identified
- **Testability Review**: Acceptance criteria verifiable
- **Judge-Readability Score**: How well judges can understand the specs
- **Action Items**: Specific improvements needed before implementation

## 6. Scope & Boundaries

### In Scope
- Specification completeness (all layers documented)
- Clarity and precision of language
- Testability of acceptance criteria
- Cross-layer consistency
- Judge-facing readability
- Phase boundary enforcement

### Out of Scope
- Implementation code review
- Performance testing
- Security penetration testing (see `security-risk-identification`)

## 7. Reusability Notes
- **Phase 2**: Establishes spec audit methodology
- **Phase 3-5**: Same audit framework for subsequent phases
- **Cross-Project**: Audit checklist reusable for any spec-driven project

## 8. Dependencies

### Upstream Dependencies
- All Phase 2 specification skills completed
- `cross-layer-consistency-validation` (initial consistency check)

### Downstream Dependencies
- Implementation tasks (blocked until specs pass audit)
- `hackathon-requirement-verification` (final validation)

## 9. Quality Expectations

### Thoroughness
- Every specification document reviewed
- All integration points validated
- No section skipped or assumed

### Objectivity
- Unbiased evaluation (judge's perspective)
- Evidence-based findings
- Actionable feedback

### Actionability
- Clear pass/fail criteria
- Specific line references for issues
- Prioritized action items

## 10. Example Usage (Spec-Level)

### Audit Checklist

**1. Completeness Audit**

```
Frontend Specification:
  ✅ Authentication flows documented
  ✅ Protected routes identified
  ✅ Component structure defined
  ✅ API integration patterns specified
  ❌ Error handling incomplete (missing network error scenarios)
  ❌ Loading states not fully specified

Backend Specification:
  ✅ All REST endpoints documented
  ✅ Request/response models defined
  ✅ Authentication middleware specified
  ✅ Database queries detailed
  ⚠️ Rate limiting not mentioned (Phase 3 scope, acceptable)

Authentication Specification:
  ✅ JWT flow fully documented
  ✅ Token lifecycle clear
  ✅ User identity propagation specified
  ✅ Security requirements explicit

Database Specification:
  ✅ Schema fully defined
  ✅ Constraints documented
  ✅ Indexes specified
  ✅ Migration strategy outlined
  ❌ Sample data specification missing

Cross-Layer Integration:
  ✅ Frontend-backend contracts aligned
  ✅ Backend-database mapping clear
  ⚠️ Field naming transformations need documentation
```

**2. Clarity Audit**

```
Ambiguities Detected:
  1. Token expiration behavior unclear
     Location: jwt-auth-flow-specification.md:45
     Issue: "Token expires after some time" - how long?
     Resolution: Specify exact duration (e.g., 15 minutes)

  2. User filtering not explicit
     Location: rest-api-contract-definition.md:78
     Issue: GET /api/todos mentions "user's todos" but filtering not explicit
     Resolution: Add "WHERE user_id = {current_user}" to spec

  3. Error response format inconsistent
     Location: Multiple endpoints
     Issue: Some errors include "timestamp", others don't
     Resolution: Standardize error format across all endpoints
```

**3. Testability Audit**

```
Acceptance Criteria Review:
  ✅ "User can log in with email/password" - Testable
  ✅ "User can create a todo" - Testable
  ✅ "User cannot access other users' todos" - Testable
  ❌ "App is user-friendly" - NOT testable (subjective)
  ❌ "Performance is good" - NOT testable (no metrics)

Missing Test Scenarios:
  - Concurrent user sessions (isolation testing)
  - Token expiration during active session
  - Network errors during API calls
  - Database connection failures

Recommendation: Add specific test cases for each acceptance criterion
```

**4. Judge-Readability Audit**

```
Readability Score: 7/10

Strengths:
  ✅ Clear section headings
  ✅ Visual diagrams (ERD, flow diagrams)
  ✅ Code examples provided
  ✅ Rationale documented for decisions

Weaknesses:
  ❌ Too much technical jargon (assume judges have varied backgrounds)
  ❌ No executive summary (judges need quick overview)
  ❌ Missing "Why" explanations (only "What" and "How")
  ⚠️ Lengthy sections (could use TL;DR summaries)

Recommendations:
  1. Add executive summary at top of each spec
  2. Explain architectural decisions (not just technical details)
  3. Include glossary for technical terms
  4. Add "Judge's Perspective" section highlighting key points
```

**5. Phase Boundary Audit**

```
Scope Discipline Check:
  ✅ OAuth explicitly deferred to Phase 3
  ✅ Multi-user sharing deferred to Phase 4
  ✅ AI chatbot deferred to Phase 5
  ❌ Notification system mentioned in backend spec (Phase 3 feature)
  ⚠️ "Future extensibility" sections good but could be more explicit

Extensibility Hooks:
  ✅ Database schema supports future features
  ✅ API design allows additions without breaking changes
  ✅ Authentication architecture supports OAuth (Phase 3)

Recommendation: Remove notification system from Phase 2 backend spec
```

---

### Audit Report Template

**Overall Assessment:**
```
Phase 2 Specifications: CONDITIONAL PASS

Completeness: 85% (17/20 required sections)
Clarity: 78% (minor ambiguities detected)
Testability: 82% (most criteria testable)
Judge-Readability: 70% (needs improvement)
Phase Discipline: 90% (one scope creep item)

BLOCKERS (Must Fix Before Implementation):
  1. Error response format standardization
  2. Token expiration duration specification
  3. Remove notification system from Phase 2 backend spec

NON-BLOCKERS (Improve for Judges):
  1. Add executive summaries
  2. Simplify technical language
  3. Add sample data specifications
  4. Document field naming transformations
```

---

### Action Items (Prioritized)

**Priority 1: Blockers (Fix Immediately)**
```
1. Standardize error response format
   - Create single error response template
   - Apply to all API endpoints
   - Update frontend error handling to match

2. Specify token expiration duration
   - Access token: 15 minutes
   - Document in jwt-auth-flow-specification.md

3. Remove Phase 3 features from Phase 2 spec
   - Delete notification system sections
   - Move to Phase 3 planning document
```

**Priority 2: Quality Improvements (Before Implementation)**
```
1. Add executive summaries
   - One paragraph overview at top of each spec
   - Key decisions highlighted

2. Document field naming transformations
   - snake_case (backend) → camelCase (frontend)
   - Specify transformation layer (Pydantic alias)

3. Expand test scenarios
   - Add edge cases (concurrent users, failures)
   - Document expected behaviors
```

**Priority 3: Judge-Facing Enhancements (Nice to Have)**
```
1. Add glossary of technical terms
2. Create visual architecture diagram (all layers)
3. Write "Judge's Guide to Phase 2" summary
4. Add rationale sections for key decisions
```

---

## Metadata
- **Version**: 1.0.0
- **Phase Introduced**: Phase 2
- **Last Updated**: 2025-12-30
- **Skill Type**: Validation
- **Execution Surface**: Agent (hackathon-judge-reviewer)
