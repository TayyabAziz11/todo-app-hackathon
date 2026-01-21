---
id: 0004
title: Phase 3 Phase 0 Research Execution
stage: green
date: 2026-01-21
surface: agent
model: claude-sonnet-4-5
feature: 003-phase3-ai-chatbot
branch: 003-phase3-ai-chatbot
user: tayyab
command: /sp.implement
labels: ["phase3", "research", "implementation", "phase0", "technical-decisions"]
links:
  spec: specs/003-phase3-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-phase3-ai-chatbot/research.md
  - specs/003-phase3-ai-chatbot/tasks.md
tests:
  - N/A - Research phase only (no code implementation)
---

## Prompt

User executed `/sp.implement` command with the following scope:

**Context**:
- Phase 3 specification approved
- Phase 3 implementation plan approved
- Phase 3 task breakdown approved
- Target deployment: Hugging Face Spaces
- Architecture: Stateless FastAPI + OpenAI Agents SDK + Official MCP SDK

**Scope**: Begin Phase 0 (Research & Technical Decisions)

**Instructions**:
- Execute ONLY Phase 0 tasks (T001–T006)
- Perform research only — no code changes
- Capture findings in specs/003-phase3-ai-chatbot/research.md
- Clearly document:
  - OpenAI Agents SDK usage patterns
  - Official MCP SDK tool definitions
  - Stateless chat patterns with DB persistence
  - ChatKit integration constraints
  - Hugging Face Spaces backend deployment requirements

**Rules**:
- No implementation yet
- No assumptions without citations or reasoning
- If uncertainty exists, document it
- Stop after Phase 0 completion

## Response snapshot

Completed comprehensive Phase 0 research across all 6 technical areas, producing a detailed research.md document with implementation decisions and citations.

**Research Areas Completed**:

### T001: OpenAI Agents SDK
- **Stateless Instantiation**: Agents are stateless by default; use `Runner.run()`, `Runner.run_sync()`, or `Runner.run_streamed()`
- **Conversation History**: Manual context management via `RunResultBase.to_input_list()` recommended for full statelessness
- **Tool Attachment**: Function tools and MCP server tool calling supported
- **Error Handling**: Domain-specific exceptions (`MaxTurnsExceeded`, `ModelBehaviorError`, guardrail exceptions)
- **Decision**: Use manual context management pattern (load from DB → format → run agent → save to DB)

### T002: Official MCP SDK
- **Server Initialization**: Use `FastMCP` with decorator-based tool registration
- **Tool Registration**: `@mcp.tool()` decorator with automatic schema generation from type hints
- **Stateless Requirement**: Tools MUST use database context managers, NOT module-level sessions
- **Error Structure**: Return `{"success": bool, "data"?: any, "error"?: string}`
- **Decision**: Decorator-based registration with automatic JSON Schema generation

### T003: Hugging Face Spaces Deployment
- **Port Requirement**: 7860 (default) via `uvicorn --host 0.0.0.0 --port 7860`
- **Critical Limitation**: Only `/tmp` directory is writable; redirect all caches
- **Environment Variables**: Configure via Space settings → Variables & secrets
- **Required Vars**: `DATABASE_URL`, `OPENAI_API_KEY`, `BETTER_AUTH_SECRET`
- **Decision**: Dockerfile with cache redirects to `/tmp`, document all env vars in `.env.example`

### T004: OpenAI ChatKit Integration
- **Critical Setup**: Domain allowlist MUST be configured or widget won't render
- **Domain Allowlist**: https://platform.openai.com/settings/organization/security/domain-allowlist
- **Localhost Issue**: Cannot be added to allowlist (local development workaround needed)
- **Integration Pattern**: `useChatKit` hook with `getClientSecret` from backend
- **Decision**: Custom backend approach with POST /api/{user_id}/chat endpoint

### T005: Stateless Conversation Management
- **Recommended Pattern**: External database (PostgreSQL) with stateless servers
- **Architecture**: Load history from DB → format for agent → run → save response → no retained state
- **Database Schema**: Conversation (id, user_id, title, timestamps), Message (id, conversation_id, role, content, tool_calls, created_at)
- **Critical Index**: Composite index on `(conversation_id, created_at)` for chronological retrieval
- **Connection Pooling**: FastAPI lifespan for pool, dependency injection for request-scoped sessions
- **Decision**: conversation_id as ONLY state token, order messages by `created_at ASC`

### T006: Better Auth JWT Integration
- **Validation Pattern**: Use `python-jose` for JWT decoding with `HTTPBearer` security
- **User ID Extraction**: Extract from `sub` claim in JWT payload
- **Path Parameter Verification**: MUST verify `{user_id}` path param matches token user_id
- **Error Codes**: 401 for invalid token, 403 for user_id mismatch
- **Decision**: Standard JWT validation with path parameter verification to prevent unauthorized access

**Key Architecture Decisions Documented**:

| Area | Decision | Rationale |
|------|----------|-----------|
| Agent Pattern | Manual context management with stateless instantiation | Full control, database as source of truth |
| MCP Tools | Decorator-based with automatic schema generation | Simplifies definition, ensures compliance |
| Conversation Storage | PostgreSQL with pooling and request-scoped sessions | Scalable, durable, horizontal scaling |
| Deployment | Hugging Face Spaces on port 7860 with `/tmp` redirects | Required by spec, free tier |
| Frontend UI | ChatKit with custom backend | Control over logic, leverage ChatKit UX |
| Authentication | JWT validation with user_id path verification | Industry standard, Better Auth compatible |
| Session Management | conversation_id only, persisted in sessionStorage | True statelessness, restart resume |

**Critical Constraints Identified**:

1. Hugging Face Spaces: Only `/tmp` writable
2. ChatKit: Domain allowlist required before deployment
3. Stateless: No module-level sessions or in-memory caches
4. User Isolation: All MCP tools validate user ownership
5. Connection Pooling: FastAPI lifespan for pool management

**Unknown Areas** (to validate during implementation):
- OpenAI Agents SDK + MCP SDK exact integration pattern
- ChatKit custom backend API contract details
- Hugging Face Spaces exact resource limits

**Research Sources**: 26 citations included with markdown hyperlinks across all research areas.

## Outcome

- ✅ Impact: Phase 0 research complete with comprehensive research.md document (6 research areas, 26+ citations, architecture decisions table, constraint documentation). Ready for Phase 1 (Design Artifacts). Tasks T001-T006 marked complete in tasks.md.
- 🧪 Tests: N/A - Research phase only (no code to test)
- 📁 Files: 2 files modified (research.md created, tasks.md updated with completed checkboxes)
- 🔁 Next prompts: Continue with Phase 1 (Design Artifacts) via `/sp.implement` with Phase 1 scope, or review research.md before proceeding
- 🧠 Reflection: Research successfully identified all critical patterns and constraints. Manual context management for stateless agents confirmed. MCP decorator pattern simplifies tool registration. Hugging Face `/tmp` limitation documented. ChatKit domain allowlist is critical blocker (must configure before deploy). PostgreSQL stateless pattern with connection pooling is solid foundation. JWT validation pattern compatible with Better Auth. Three unknown areas flagged for validation during implementation but don't block Phase 1 design work. Research quality high with direct citations from official docs.

## Evaluation notes (flywheel)

- Failure modes observed: None. All research tasks completed successfully with authoritative sources.
- Graders run and results (PASS/FAIL): Research completeness - PASS (all 6 areas covered), Citation quality - PASS (26+ sources with markdown links), Decision clarity - PASS (architecture decisions table with rationale), Constraint documentation - PASS (5 critical constraints identified)
- Prompt variant (if applicable): N/A - standard research workflow with web search and documentation review
- Next experiment (smallest change to try): N/A - proceeding to Phase 1 design artifacts
