---
id: 0002
title: Phase 3 Implementation Plan
stage: plan
date: 2026-01-21
surface: agent
model: claude-sonnet-4-5
feature: 003-phase3-ai-chatbot
branch: 003-phase3-ai-chatbot
user: tayyab
command: /sp.plan
labels: ["phase3", "mcp", "ai-chatbot", "planning", "architecture", "hugging-face-deployment"]
links:
  spec: specs/003-phase3-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-phase3-ai-chatbot/plan.md
tests:
  - Constitution compliance check (all 7 principles PASS)
  - Plan structure validation
---

## Prompt

User executed `/sp.plan` command with the following requirements:

**Task**: Generate a DETAILED, STEP-BY-STEP EXECUTION PLAN for Phase 3 AI Chatbot implementation.

**Important Rules**:
- Do NOT write code yet (planning phase only)
- Plan must be implementation-ready with clear dependency order
- Must assume backend deployment on **Hugging Face Spaces** (NOT Railway)
- Follow Agentic Dev Stack: spec → plan → tasks → implement
- Respect stateless server architecture throughout all phases
- Database as ONLY source of truth (no in-memory sessions)

**Required Plan Structure** (12 phases):
1. Summary and Technical Context
2. Constitution Check (validate against 7 principles)
3. Project Structure (file tree showing what to build)
4. Phase 0: Research (unknowns to investigate)
5. Phase 1: Design Artifacts (data models, API contracts)
6. Phase 2: Detailed Implementation Phases (3.1 through 3.13)
7. ADR Candidates (architecturally significant decisions)
8. Risk Analysis
9. Dependencies Graph
10. Success Metrics Alignment
11. Next Steps
12. Timeline Estimate

**Key Technical Requirements from Spec**:
- 5 MCP tools (add/list/update/complete/delete tasks) using official MCP SDK
- OpenAI Agents SDK for agent orchestration
- SQLModel + PostgreSQL for data models (Conversation, Message, Task)
- Stateless chat endpoint: POST /api/{user_id}/chat
- Frontend: OpenAI ChatKit integration with conversation_id persistence
- Deployment: Hugging Face Spaces (port 7860) + Vercel
- Conversation resume after server restarts
- Tool chaining support (multi-step operations)
- Anti-hallucination testing (ensure agent doesn't claim actions without tool calls)

## Response snapshot

Created comprehensive 1118-line implementation plan with 13 execution phases structured for dependency-ordered implementation.

**Plan Highlights**:

**Constitution Check**: All 7 principles validated
- ✅ Spec-First Development (complete spec exists)
- ✅ Phase Isolation (clear boundaries, no scope creep)
- ✅ Agentic Workflow (human approval gates before tasks)
- ✅ Human-in-Loop (approval required at each phase transition)
- ✅ Clean Architecture (MCP → Agent → API → Frontend separation)
- ✅ Deterministic Behavior (database state, no randomness)
- ✅ Simplicity (YAGNI - only required features, no extras)

**Phase 0: Research** (6 research areas identified):
1. OpenAI Agents SDK patterns and conversation history formatting
2. MCP SDK tool implementation and registration
3. Hugging Face Spaces deployment requirements (port config, env vars)
4. OpenAI ChatKit domain allowlist and integration
5. SQLModel conversation persistence patterns
6. Agent system prompt best practices for tool calling

**Phase 1: Design Artifacts**:
- Data models (Conversation, Message with SQLModel schemas)
- API contracts (POST /api/{user_id}/chat with request/response schemas)
- MCP tool specifications (5 tools with JSON schemas)
- Quickstart guide (local dev setup)
- Agent context document (system prompt, tool descriptions)

**Phase 2: Implementation Phases** (3.1 through 3.13):
- **3.1**: Database models (Conversation, Message)
- **3.2**: MCP server and 5 tools (add/list/update/complete/delete)
- **3.3**: Conversation persistence service
- **3.4**: Better Auth user_id extraction utility
- **3.5**: Agent design (system prompt ~7000 chars, AgentRunner class)
- **3.6**: Agent tool integration (attach MCP tools to OpenAI agent)
- **3.7**: Chat API endpoint (stateless POST /api/{user_id}/chat)
- **3.8**: Frontend ChatKit integration
- **3.9**: End-to-end testing (conversation flow, tool chaining)
- **3.10**: Anti-hallucination testing
- **3.11**: Stateless behavior verification (server restart tests)
- **3.12**: Hugging Face deployment setup
- **3.13**: Production validation

**Critical Path** (dependency order):
3.1 → 3.2 → 3.5 → 3.6 → 3.7 → 3.9 → 3.12 → 3.13

**ADR Candidates** (4 decisions requiring documentation):
1. Stateless Architecture with Database-Backed Conversation Persistence
2. MCP Protocol for Task Operations
3. OpenAI Agents SDK for Natural Language Understanding
4. Hugging Face Spaces for Backend Deployment

**Risk Analysis** (5 risks with mitigation):
1. OpenAI Agents SDK learning curve → early research and quickstart
2. MCP tool stateless compliance → strict code review checklist
3. Hugging Face deployment constraints → Phase 0 research
4. Agent hallucination → comprehensive anti-hallucination tests
5. Conversation_id collision → UUID generation

**Project Structure** (key files to create):
```
backend/
├── app/
│   ├── mcp/
│   │   ├── server.py              # NEW: MCP server
│   │   ├── tools.py               # NEW: 5 MCP tools
│   │   └── schemas.py             # NEW: Tool schemas
│   ├── agent/
│   │   ├── runner.py              # NEW: AgentRunner
│   │   ├── system_prompt.py       # NEW: System prompt
│   │   └── config.py              # NEW: Agent config
│   ├── services/
│   │   └── conversation.py        # NEW: Conversation service
│   ├── routes/
│   │   └── chat.py                # NEW: Chat endpoint

frontend/
├── components/
│   └── ChatInterface.tsx          # NEW: ChatKit wrapper
```

## Outcome

- ✅ Impact: Phase 3 implementation plan complete with 13 detailed phases, dependency graph, and ADR candidates. Ready for human review and approval before proceeding to `/sp.tasks`.
- 🧪 Tests: Constitution compliance validated (7/7 principles PASS), plan structure validation complete
- 📁 Files: 1 file created (plan.md - 1118 lines)
- 🔁 Next prompts: Human review plan → `/sp.tasks` to generate dependency-ordered task breakdown from this plan
- 🧠 Reflection: Plan successfully balances comprehensive detail with implementation-readiness. All phases have clear dependencies, validation criteria, and outputs. Phase 0 research questions capture genuine unknowns (OpenAI SDK patterns, MCP SDK usage, HF Spaces deployment). ADR candidates properly identify architecturally significant decisions. Risk analysis addresses both technical and architectural concerns. Plan is ready for human approval.

## Evaluation notes (flywheel)

- Failure modes observed: None. Plan creation succeeded with all required sections and proper dependency ordering.
- Graders run and results (PASS/FAIL): Constitution check - PASS (7/7 principles), Plan structure validation - PASS (all 12 required sections present)
- Prompt variant (if applicable): N/A - standard planning workflow with explicit 12-phase structure requirement
- Next experiment (smallest change to try): N/A - ready for human approval and task generation phase
