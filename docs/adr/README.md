# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for Phase II of the Todo App project.

## What are ADRs?

Architecture Decision Records document significant architectural decisions made during the project. Each ADR captures:
- **Context**: Why we needed to make a decision
- **Options Considered**: Alternative approaches we evaluated
- **Decision**: What we chose and why
- **Consequences**: Trade-offs and impacts

## ADR Index

| ID | Title | Status | Date |
|----|-------|--------|------|
| [001](./001-jwt-stateless-authentication.md) | JWT Stateless Authentication | Accepted | 2025-12-31 |
| [002](./002-sqlmodel-orm.md) | SQLModel for Database ORM | Accepted | 2025-12-31 |
| [003](./003-monorepo-structure.md) | Monorepo Structure for Full-Stack Application | Accepted | 2025-12-31 |

## Key Decisions Summary

### 001: JWT Stateless Authentication
**Decision:** Use JWT tokens with HS256 algorithm for authentication
**Rationale:** Horizontal scalability, stateless architecture, API-first design
**Trade-off:** No immediate token revocation (mitigated by 15-minute TTL)

### 002: SQLModel for Database ORM
**Decision:** Use SQLModel instead of SQLAlchemy or Django ORM
**Rationale:** Type safety, single source of truth (DB model = API schema), FastAPI integration
**Trade-off:** Younger library (mitigated by stable SQLAlchemy foundation)

### 003: Monorepo Structure
**Decision:** Use monorepo without npm workspaces
**Rationale:** Unified Spec-Driven Development artifacts, atomic commits, simple setup
**Trade-off:** Larger repo size (mitigated by .gitignore)

## Reading Recommendations

For new team members or contributors:
1. Start with **ADR 003** (Monorepo Structure) to understand project organization
2. Read **ADR 001** (JWT Authentication) to understand security model
3. Review **ADR 002** (SQLModel ORM) to understand data layer

## ADR Template

When creating new ADRs, use this structure:
```markdown
# ADR NNN: [Title]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
[What is the issue that we're seeing that is motivating this decision or change?]

## Options Considered
### Option 1: [Name]
**Pros:** ...
**Cons:** ...

### Option 2: [Name]
**Pros:** ...
**Cons:** ...

## Decision
[What is the change that we're proposing and/or doing?]

## Consequences
### Positive
✅ ...

### Negative
⚠️ ...

### Trade-offs
- ...

## Related Decisions
- ADR XXX: ...

## References
- [Link]()

## Date
YYYY-MM-DD

## Authors
[Name or Team]
```

## References

- [Architecture Decision Records (ADR) - Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [ADR GitHub Organization](https://adr.github.io/)
