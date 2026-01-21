# Implementation Plan: AI-Powered Todo Chatbot (Phase 3)

**Branch**: `003-phase3-ai-chatbot` | **Date**: 2026-01-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-phase3-ai-chatbot/spec.md`

## Summary

Phase 3 transforms the Todo application into an AI-powered conversational interface using the Model Context Protocol (MCP) and OpenAI Agents SDK. Users will manage tasks through natural language commands like "Add a task to buy groceries" or "Show my pending tasks". The system implements true stateless architecture where all conversation and task state persists in PostgreSQL, enabling horizontal scalability and seamless server restarts. The backend deploys to Hugging Face Spaces, and the frontend uses OpenAI ChatKit on Vercel.

**Core Technical Approach**:
1. MCP server exposes 5 stateless tools (add/list/update/complete/delete) that operate only on database
2. OpenAI agent orchestrates tool calls based on natural language intent classification
3. FastAPI chat endpoint loads conversation history from DB, runs agent, persists results, returns response
4. No in-memory session state - conversation_id is the only state token passed between client and server

---

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5+ (frontend)

**Primary Dependencies**:
- **Backend**: FastAPI 0.104+, OpenAI Agents SDK (latest), Official MCP SDK (latest), SQLModel 0.14+, Pydantic 2.5+
- **Frontend**: Next.js 15+, OpenAI ChatKit (latest), Better Auth SDK

**Storage**: Neon Serverless PostgreSQL (primary database), sessionStorage (frontend conversation_id persistence only)

**Testing**: pytest (backend unit/integration), Jest (frontend), playwright (E2E)

**Target Platform**: Hugging Face Spaces (backend), Vercel (frontend)

**Project Type**: Web application (fullstack)

**Performance Goals**:
- Chat endpoint response time: <3 seconds p95 (including OpenAI API call)
- Conversation history load: <200ms for 50 messages
- Database throughput: 1000 queries/minute minimum
- Concurrent users: 100 without >10% degradation

**Constraints**:
- Stateless architecture: NO in-memory sessions, caches, or global state
- MCP compliance: All task operations through MCP tools only
- Database as single source of truth
- Hugging Face Spaces port/env compatibility
- OpenAI ChatKit domain allowlist requirements

**Scale/Scope**:
- User conversations: Support 1000+ messages per conversation
- Concurrent conversations per user: Unlimited (independent contexts)
- MCP tools: Exactly 5 (no more, no less per spec)
- Agent prompt: ~7000 characters system prompt
- Database tables: 2 new (Conversation, Message) + existing (User, Task)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Spec-First Development ✅ PASS
- ✅ Complete specification exists at `specs/003-phase3-ai-chatbot/spec.md`
- ✅ Specification approved by human (via `/sp.specify` command)
- ✅ Specification is technology-agnostic (focuses on user scenarios and requirements)
- ✅ No code will be written before plan approval

### II. Phase Isolation with Forward Compatibility ✅ PASS
- ✅ Phase 3 extends Phase 1/2 (authentication, task database) without breaking them
- ✅ Phase 3 can be tested independently (new chat endpoint + MCP tools)
- ✅ Existing REST API for tasks remains functional
- ✅ Rollback possible: disable chat endpoint, keep existing functionality

### III. Agentic Workflow Discipline ✅ PASS
- ✅ Following workflow: spec (done) → plan (this document) → tasks (next) → implement (after approval)
- ✅ No features added beyond specification requirements
- ✅ ADR suggestions will be made for architecturally significant decisions (MCP design, agent prompt structure, stateless patterns)

### IV. Human-in-the-Loop Governance ✅ PASS
- ✅ This plan requires human approval before proceeding to `/sp.tasks`
- ✅ Architecture decisions will surface for human review
- ✅ Deployment to Hugging Face requires explicit human instruction
- ✅ PHR will be created for this planning session

### V. Clean Architecture and Modularity ✅ PASS
- ✅ Clear separation: MCP tools → Agent layer → API layer → Frontend
- ✅ Dependencies flow one direction: Frontend → API → Agent → MCP → Database
- ✅ External integrations abstracted: OpenAI API behind agent wrapper, database behind SQLModel
- ✅ Error handling explicit: All MCP tools return structured success/error responses
- ✅ Configuration externalized: All secrets in .env files

### VI. Deterministic and Observable Behavior ✅ PASS
- ✅ MCP tools are pure functions (same inputs → same outputs)
- ✅ Side effects isolated to database writes (explicit and logged)
- ✅ All chat requests will log: conversation_id, tool calls, agent response
- ✅ Error messages will be user-friendly with context

### VII. Simplicity and YAGNI ✅ PASS
- ✅ Implementing only spec requirements (no speculative features)
- ✅ No premature optimization (pagination deferred to post-MVP)
- ✅ Using established frameworks (FastAPI, OpenAI SDK) not custom solutions
- ✅ Simplest stateless pattern: load from DB, execute, save to DB

**Overall Gate Status**: ✅ ALL GATES PASS - Proceed to Phase 0 Research

---

## Project Structure

### Documentation (this feature)

```text
specs/003-phase3-ai-chatbot/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   ├── chat-api.yaml    # OpenAPI spec for chat endpoint
│   └── mcp-tools.yaml   # MCP tool schemas
├── checklists/
│   └── requirements.md  # Spec quality validation (completed)
└── tasks.md             # Phase 2 output (created by /sp.tasks - NOT this command)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── database.py                # Database session management
│   ├── config.py                  # Environment configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                # User model (from Phase 2)
│   │   ├── todo.py                # Task model (from Phase 1)
│   │   ├── conversation.py        # NEW: Conversation model
│   │   └── message.py             # NEW: Message model
│   ├── mcp/
│   │   ├── __init__.py            # NEW: MCP package
│   │   ├── server.py              # NEW: MCP server initialization
│   │   ├── tools.py               # NEW: 5 MCP tool implementations
│   │   └── schemas.py             # NEW: Pydantic schemas for tools
│   ├── agent/
│   │   ├── __init__.py            # NEW: Agent package
│   │   ├── runner.py              # NEW: AgentRunner class
│   │   ├── system_prompt.py       # NEW: Agent system prompt
│   │   └── config.py              # NEW: Agent configuration
│   ├── services/
│   │   ├── __init__.py
│   │   ├── conversation.py        # NEW: Conversation persistence service
│   │   └── auth.py                # Auth service (from Phase 2)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── todos.py               # Todo routes (from Phase 1)
│   │   ├── auth.py                # Auth routes (from Phase 2)
│   │   └── chat.py                # NEW: Chat endpoint
│   └── middleware/
│       ├── __init__.py
│       └── auth.py                # Auth middleware (from Phase 2)
├── tests/
│   ├── __init__.py
│   ├── test_mcp_tools.py          # NEW: MCP tool unit tests
│   ├── test_agent.py              # NEW: Agent behavior tests
│   ├── test_chat_endpoint.py     # NEW: Chat API integration tests
│   ├── test_conversation.py      # NEW: Conversation persistence tests
│   └── test_stateless.py         # NEW: Stateless verification tests
├── alembic/
│   └── versions/
│       └── xxx_add_conversation_tables.py  # NEW: Migration
├── requirements.txt               # UPDATED: Add OpenAI SDK, MCP SDK
├── .env.example                   # UPDATED: Add OPENAI_API_KEY
└── README.md                      # UPDATED: Phase 3 instructions

frontend/
├── app/
│   ├── chat/
│   │   └── page.tsx               # NEW: ChatKit page
│   ├── todos/
│   │   └── page.tsx               # Todo UI (from Phase 1/2)
│   └── layout.tsx                 # Root layout (from Phase 2)
├── components/
│   └── ChatInterface.tsx          # NEW: ChatKit wrapper component
├── lib/
│   ├── api.ts                     # API client (from Phase 2)
│   └── chatApi.ts                 # NEW: Chat API client
├── package.json                   # UPDATED: Add @openai/chatkit
├── .env.local.example             # UPDATED: Add NEXT_PUBLIC_OPENAI_DOMAIN_KEY
└── README.md                      # UPDATED: ChatKit setup instructions

docs/
├── architecture/
│   └── phase3-mcp-agent.md        # NEW: Architecture diagram + explanation
├── deployment/
│   └── huggingface.md             # NEW: Hugging Face deployment guide
└── demo/
    └── judge-demo.md              # NEW: Hackathon demo script
```

**Structure Decision**: Web application structure (Option 2) with backend/frontend separation. Phase 3 adds new backend modules (`mcp/`, `agent/`, new routes and services) and new frontend pages (`chat/`). Existing Phase 1/2 code remains untouched except for dependency updates and database migrations.

---

## Complexity Tracking

> No constitution violations requiring justification. All complexity is essential:

- **MCP Server**: Required by specification for tool protocol compliance
- **Agent Layer**: Required for natural language understanding and tool orchestration
- **Conversation Persistence**: Required for stateless architecture and conversation resume
- **Frontend ChatKit**: Specified requirement (no custom chat UI)

---

## Phase 0: Research & Technical Decisions

**Purpose**: Resolve all technical uncertainties before design phase. Research best practices for OpenAI Agents SDK integration, MCP SDK usage, Hugging Face deployment, and stateless conversation management.

### 0.1 OpenAI Agents SDK Integration Research

**Research Questions**:
1. How to initialize OpenAI Agents SDK in stateless mode (no singleton agents)?
2. How to attach MCP tools to agent at runtime?
3. How to format conversation history for agent context?
4. How to extract tool calls from agent response?
5. How to handle agent errors and fallbacks?

**Research Outputs** (for `research.md`):
- Agent instantiation pattern (fresh per request vs pooled)
- Message format for conversation history
- Tool attachment API documentation
- Error handling best practices
- Rate limiting and retry strategies

### 0.2 MCP SDK Tool Registration Research

**Research Questions**:
1. How to register tools with official MCP SDK?
2. What schema format does MCP SDK expect (Pydantic, JSON Schema, etc.)?
3. How to enforce stateless tool execution?
4. How to return structured responses (success/error)?
5. How to handle tool invocation errors?

**Research Outputs** (for `research.md`):
- MCP server initialization code pattern
- Tool schema definition format
- Stateless database access pattern (context managers)
- Error response structure
- Tool discovery/registration flow

### 0.3 Hugging Face Spaces Deployment Research

**Research Questions**:
1. What port must FastAPI listen on for Hugging Face Spaces?
2. How to configure environment variables in Spaces?
3. How to handle secrets (OpenAI API key, database URL)?
4. What startup command format does Spaces expect?
5. Are there resource limits (memory, CPU, timeout)?

**Research Outputs** (for `research.md`):
- Hugging Face Spaces configuration file format
- Port and host binding requirements
- Environment variable management
- Startup command specification
- Resource limits and optimization strategies

### 0.4 Stateless Conversation Management Patterns

**Research Questions**:
1. How to efficiently load conversation history (pagination, limit)?
2. How to order messages chronologically for agent context?
3. How to handle very long conversations (summarization, truncation)?
4. How to prevent memory leaks in long-running server?
5. How to test statelessness (restart scenarios)?

**Research Outputs** (for `research.md`):
- Database query patterns for conversation history
- Message ordering and formatting strategy
- Conversation length limits and handling
- Memory management best practices
- Stateless verification test patterns

### 0.5 OpenAI ChatKit Frontend Integration Research

**Research Questions**:
1. How to install and configure OpenAI ChatKit for Next.js 15?
2. What is the domain allowlist configuration process?
3. How to obtain and configure domain key (NEXT_PUBLIC_OPENAI_DOMAIN_KEY)?
4. How to wire ChatKit to custom backend API?
5. How to persist conversation_id in browser sessionStorage?

**Research Outputs** (for `research.md`):
- ChatKit installation steps
- Domain key generation process
- ChatKit API integration pattern
- Session state management approach
- Error handling and loading states

### 0.6 Better Auth Integration for Chat Endpoint

**Research Questions**:
1. How to extract user_id from Better Auth JWT token?
2. How to validate JWT in chat endpoint middleware?
3. How to enforce user_id matching in MCP tools?
4. How to handle authentication errors in chat flow?
5. How to test authenticated chat endpoints?

**Research Outputs** (for `research.md`):
- JWT token validation pattern
- User_id extraction from token claims
- Auth middleware integration for chat routes
- Error response format for auth failures
- Test fixtures for authenticated requests

**Deliverable**: `research.md` with all decisions documented

---

## Phase 1: Design Artifacts

**Purpose**: Define data models, API contracts, and project structure. Update agent context with new technologies.

**Dependencies**: Phase 0 (research.md) complete

### 1.1 Data Model Design

**File**: `specs/003-phase3-ai-chatbot/data-model.md`

**Entities to Define**:

1. **Conversation**
   - Fields: id (UUID), user_id (FK to users), title (optional), created_at, updated_at
   - Relationships: One-to-many with Message
   - Indexes: user_id, created_at
   - Constraints: user_id NOT NULL, cascade delete messages

2. **Message**
   - Fields: id (UUID), conversation_id (FK to conversations), user_id (FK to users), role (enum: user/assistant/tool), content (text), tool_calls (JSON optional), tool_call_id (string optional), name (string optional), created_at
   - Relationships: Many-to-one with Conversation
   - Indexes: conversation_id + created_at (composite for chronological ordering)
   - Constraints: conversation_id NOT NULL, role NOT NULL, content NOT NULL

3. **Task** (existing from Phase 1 - no changes)
   - No modifications needed; MCP tools will query this table

4. **User** (existing from Phase 2 - no changes)
   - No modifications needed; auth system remains unchanged

**State Transitions**:
- Conversation: created → active → (optionally) archived
- Message: created only (immutable after creation)
- Task: Modified via MCP tools (pending → completed)

**Deliverable**: `data-model.md` with SQLModel schema definitions and migration strategy

### 1.2 API Contract Design

**File**: `specs/003-phase3-ai-chatbot/contracts/chat-api.yaml`

**Endpoints to Define**:

1. **POST /api/{user_id}/chat**
   - Request: `{ message: string, conversation_id?: UUID }`
   - Response: `{ conversation_id: UUID, message: string, tool_calls: ToolCall[] }`
   - Auth: Bearer token (Better Auth JWT)
   - Errors: 401 (unauthorized), 403 (forbidden), 500 (internal error)

2. **GET /api/{user_id}/conversations** (optional - for listing conversations)
   - Response: `{ conversations: Conversation[] }`
   - Auth: Bearer token
   - Pagination: query params (limit, offset)

**File**: `specs/003-phase3-ai-chatbot/contracts/mcp-tools.yaml`

**Tools to Define** (MCP protocol format):

1. **add_task**
   - Input: `{ user_id: UUID, title: string, description?: string }`
   - Output: `{ success: boolean, task?: Task, error?: string }`

2. **list_tasks**
   - Input: `{ user_id: UUID, status?: "all" | "pending" | "completed" }`
   - Output: `{ success: boolean, tasks?: Task[], error?: string }`

3. **complete_task**
   - Input: `{ user_id: UUID, task_id: int }`
   - Output: `{ success: boolean, task?: Task, error?: string }`

4. **delete_task**
   - Input: `{ user_id: UUID, task_id: int }`
   - Output: `{ success: boolean, error?: string }`

5. **update_task**
   - Input: `{ user_id: UUID, task_id: int, title?: string, description?: string }`
   - Output: `{ success: boolean, task?: Task, error?: string }`

**Deliverable**: OpenAPI YAML for chat API, MCP tool schema YAML

### 1.3 Quickstart Guide

**File**: `specs/003-phase3-ai-chatbot/quickstart.md`

**Sections**:
1. Prerequisites (Phase 1/2 running, OpenAI API key, Neon DB)
2. Environment Setup (.env configuration)
3. Database Migration (conversation and message tables)
4. Backend Startup (uvicorn command)
5. Frontend Startup (npm run dev)
6. Test Chat Interface (send first message)
7. Verify Statelessness (restart backend, resume conversation)

**Deliverable**: Step-by-step setup instructions for Phase 3

### 1.4 Agent Context Update

**Script**: `.specify/scripts/bash/update-agent-context.sh claude`

**New Technologies to Add**:
- OpenAI Agents SDK (agentic orchestration)
- Official MCP SDK (tool protocol)
- OpenAI ChatKit (frontend component)
- Pydantic 2.5+ (MCP schemas)
- Hugging Face Spaces (deployment platform)

**Deliverable**: Updated `.claude/CONTEXT.md` with Phase 3 technologies

---

## Phase 2: Detailed Implementation Plan (Execution Phases)

**Purpose**: Break down implementation into logical, dependency-ordered phases that can be translated into tasks.

**Dependencies**: Phase 1 (data model, contracts, quickstart) complete

### Phase 3.1 — Repository & Architecture Preparation

**Purpose**: Prepare repository structure and confirm architectural patterns before implementation.

**Components Built**:
1. Backend package structure (`app/mcp/`, `app/agent/`, updated `app/models/`)
2. Frontend package structure (`app/chat/`, `components/ChatInterface.tsx`)
3. Test directories (`tests/test_mcp_tools.py`, etc.)

**Dependencies**: None (can start immediately after plan approval)

**Steps**:
1. Create `backend/app/mcp/` directory with `__init__.py`
2. Create `backend/app/agent/` directory with `__init__.py`
3. Create `frontend/app/chat/` directory
4. Create `backend/tests/test_mcp_tools.py` stub
5. Create `backend/tests/test_agent.py` stub
6. Create `backend/tests/test_chat_endpoint.py` stub
7. Create `backend/tests/test_stateless.py` stub
8. Update `.gitignore` to exclude new environment files if needed

**Expected Outputs**:
- Empty directory structure ready for implementation
- Test file stubs in place

**Validation**:
- Directory structure matches plan.md
- No existing code broken by new directories

---

### Phase 3.2 — Database Models & Migrations

**Purpose**: Define Conversation and Message SQLModel schemas and create database migration.

**Components Built**:
1. `backend/app/models/conversation.py` (Conversation SQLModel)
2. `backend/app/models/message.py` (Message SQLModel)
3. Alembic migration for new tables

**Dependencies**: Phase 3.1 (directory structure)

**Steps**:
1. Define Conversation model with fields per data-model.md
2. Define Message model with fields per data-model.md
3. Add relationships (Conversation has many Messages)
4. Create Alembic migration: `alembic revision --autogenerate -m "add conversation tables"`
5. Review migration SQL for indexes and constraints
6. Run migration: `alembic upgrade head`
7. Verify tables created in Neon database

**Expected Outputs**:
- `backend/app/models/conversation.py` with Conversation class
- `backend/app/models/message.py` with Message class
- Alembic migration file in `backend/alembic/versions/`
- Database tables: `conversations` and `messages`

**Validation**:
- Models import successfully
- Migration runs without errors
- Tables exist in database with correct schema
- Indexes created on conversation_id and user_id

---

### Phase 3.3 — MCP Server Initialization

**Purpose**: Set up MCP server using Official MCP SDK and prepare tool registration infrastructure.

**Components Built**:
1. `backend/app/mcp/server.py` (MCP server initialization)
2. `backend/app/mcp/schemas.py` (Pydantic schemas for tool inputs/outputs)

**Dependencies**: Phase 3.2 (models exist)

**Steps**:
1. Install Official MCP SDK: `pip install mcp`
2. Create MCP server initialization in `server.py`
3. Define tool registration function
4. Create Pydantic schemas for all 5 tools (input/output models)
5. Add MCP server startup to FastAPI lifespan event
6. Add logging for tool registration

**Expected Outputs**:
- MCP server initialized on FastAPI startup
- Tool schemas defined in `schemas.py`
- Server ready to register tools (registration in next phase)

**Validation**:
- MCP server starts without errors
- Logs show "MCP server initialized"
- No tools registered yet (that's Phase 3.4)

---

### Phase 3.4 — MCP Tool Implementations

**Purpose**: Implement all 5 MCP tools with stateless database access.

**Components Built**:
1. `backend/app/mcp/tools.py` (5 tool functions)
2. Tool registration in `server.py`

**Dependencies**: Phase 3.3 (MCP server initialized, schemas defined)

**Steps**:
1. Implement `add_task(user_id, title, description)` with database context manager
2. Implement `list_tasks(user_id, status)` with filtering logic
3. Implement `complete_task(user_id, task_id)` with ownership validation
4. Implement `delete_task(user_id, task_id)` with ownership validation
5. Implement `update_task(user_id, task_id, title, description)` with ownership validation
6. Register all 5 tools with MCP server
7. Add error handling for each tool (task not found, permission denied, etc.)
8. Return structured JSON responses per contract

**Expected Outputs**:
- 5 working MCP tools in `tools.py`
- Tools registered with MCP server
- All tools return structured success/error responses

**Validation**:
- Unit tests for each tool pass
- Tools use context managers (no module-level sessions)
- Tools enforce user_id ownership
- Tools return correct JSON structure

---

### Phase 3.5 — Conversation Persistence Service

**Purpose**: Implement service layer for conversation and message persistence.

**Components Built**:
1. `backend/app/services/conversation.py` (conversation management functions)

**Dependencies**: Phase 3.2 (models exist)

**Steps**:
1. Implement `create_conversation(user_id, title)` → returns Conversation
2. Implement `get_conversation(conversation_id, user_id)` → returns Conversation or None
3. Implement `save_message(conversation_id, role, content, tool_calls)` → returns Message
4. Implement `get_conversation_history(conversation_id, limit)` → returns List[Message]
5. Implement `list_user_conversations(user_id)` → returns List[Conversation]
6. Add update_conversation_timestamp helper
7. Add database session dependency injection

**Expected Outputs**:
- Conversation service functions in `services/conversation.py`
- All functions use database context managers
- Chronological message ordering implemented

**Validation**:
- Service functions can be called from routes
- Messages ordered by created_at ascending
- Conversation timestamps update on new messages

---

### Phase 3.6 — OpenAI Agent Design & Implementation

**Purpose**: Create AI agent with system prompt, tool integration, and natural language understanding.

**Components Built**:
1. `backend/app/agent/system_prompt.py` (agent instructions)
2. `backend/app/agent/runner.py` (AgentRunner class)
3. `backend/app/agent/config.py` (agent configuration)

**Dependencies**: Phase 3.4 (MCP tools exist), Phase 3.5 (conversation service exists)

**Steps**:
1. Write comprehensive system prompt (~7000 chars) with:
   - Intent patterns for each MCP tool
   - Tool descriptions and usage examples
   - Natural language variations (add/create/remind/etc.)
   - Error handling instructions
   - Anti-hallucination rules
2. Create AgentRunner class with:
   - OpenAI client initialization
   - Tool attachment to agent
   - Conversation history formatting
   - Agent execution method
   - Tool call extraction
   - Response formatting
3. Add configuration for model selection (GPT-4)
4. Add retry logic for OpenAI API failures

**Expected Outputs**:
- System prompt defining agent behavior
- AgentRunner class for agent orchestration
- Agent can be instantiated per request (stateless)

**Validation**:
- Agent instantiates without errors
- Agent can access all 5 MCP tools
- Agent follows system prompt instructions
- Agent returns conversational responses

---

### Phase 3.7 — Chat API Endpoint Implementation

**Purpose**: Implement POST /api/{user_id}/chat endpoint with full conversation lifecycle.

**Components Built**:
1. `backend/app/routes/chat.py` (chat endpoint)
2. Request/response models

**Dependencies**: Phase 3.5 (conversation service), Phase 3.6 (agent runner)

**Steps**:
1. Define ChatRequest model (message, conversation_id optional)
2. Define ChatResponse model (conversation_id, message, tool_calls)
3. Implement POST /api/{user_id}/chat endpoint:
   - Authenticate user (validate JWT token)
   - Verify user_id matches token
   - Load or create conversation
   - Load conversation history from database
   - Save user message to database
   - Instantiate AgentRunner
   - Execute agent with history + user message
   - Extract tool calls from agent response
   - Save agent response to database
   - Return ChatResponse
4. Add error handling (auth, database, agent failures)
5. Add logging (conversation_id, tool calls, response)
6. Register route with FastAPI app

**Expected Outputs**:
- Working POST /api/{user_id}/chat endpoint
- Chat requests create conversations and messages
- Agent executes and returns responses

**Validation**:
- Endpoint returns 200 with valid response
- Conversation and messages persist in database
- Tool calls logged correctly
- Errors return appropriate status codes

---

### Phase 3.8 — Stateless Architecture Enforcement

**Purpose**: Verify and enforce stateless design patterns throughout the system.

**Components Built**:
1. Stateless verification tests
2. Code review checklist for statelessness

**Dependencies**: Phase 3.7 (chat endpoint working)

**Steps**:
1. Audit all modules for module-level database sessions (none allowed)
2. Audit for global caches or state dictionaries (none allowed)
3. Verify all database access uses context managers
4. Verify AgentRunner instantiated per request (not singleton)
5. Write restart test: create conversation → restart server → resume conversation
6. Write multi-instance test: send requests to different instances (if possible)
7. Add logging to confirm fresh session per request

**Expected Outputs**:
- No stateful patterns detected
- Restart test passes (no data loss)
- Code review checklist for future PRs

**Validation**:
- Server restarts without losing data
- Conversations resume with full context
- No in-memory state between requests

---

### Phase 3.9 — Frontend ChatKit Integration

**Purpose**: Integrate OpenAI ChatKit UI with backend chat API.

**Components Built**:
1. `frontend/app/chat/page.tsx` (ChatKit page)
2. `frontend/components/ChatInterface.tsx` (ChatKit wrapper)
3. `frontend/lib/chatApi.ts` (chat API client)

**Dependencies**: Phase 3.7 (chat endpoint working)

**Steps**:
1. Install OpenAI ChatKit: `npm install @openai/chatkit`
2. Obtain OpenAI domain key from OpenAI dashboard
3. Add NEXT_PUBLIC_OPENAI_DOMAIN_KEY to .env.local
4. Configure domain allowlist (localhost + Vercel domain)
5. Create chat page with ChatKit component
6. Implement handleSendMessage function:
   - Get conversation_id from sessionStorage
   - Send POST request to backend chat endpoint
   - Save conversation_id to sessionStorage
   - Return agent response to ChatKit
7. Add authentication (get user_id and token from Better Auth)
8. Add error handling (network errors, auth errors)
9. Add loading states

**Expected Outputs**:
- ChatKit UI renders at `/chat` route
- Users can send messages and receive responses
- Conversation_id persists across page refreshes

**Validation**:
- ChatKit loads without errors
- Messages send and responses appear
- Conversation resume works after refresh
- Tool calls visible in UI (transparency)

---

### Phase 3.10 — Authentication Integration

**Purpose**: Wire Better Auth authentication into chat endpoint and MCP tools.

**Components Built**:
1. Auth middleware for chat routes
2. User_id extraction from JWT token

**Dependencies**: Phase 3.7 (chat endpoint), Phase 3.9 (frontend auth)

**Steps**:
1. Reuse existing Better Auth middleware from Phase 2
2. Apply auth middleware to /api/{user_id}/chat endpoint
3. Extract user_id from JWT token claims
4. Verify {user_id} path parameter matches token user_id
5. Pass authenticated user_id to MCP tools
6. Return 403 if user_id mismatch
7. Test authenticated requests from frontend

**Expected Outputs**:
- Chat endpoint requires valid JWT token
- User_id verified from token
- MCP tools enforce user ownership

**Validation**:
- Unauthenticated requests return 401
- Mismatched user_id returns 403
- Users can only access their own tasks and conversations

---

### Phase 3.11 — Hugging Face Spaces Deployment Configuration

**Purpose**: Configure backend for deployment to Hugging Face Spaces.

**Components Built**:
1. `backend/Dockerfile` or startup script
2. `backend/.env.example` with Hugging Face requirements
3. Hugging Face Spaces configuration file

**Dependencies**: Phase 3.10 (all backend functionality complete)

**Steps**:
1. Research Hugging Face Spaces requirements (port 7860 default)
2. Update FastAPI to listen on correct host/port
3. Create startup command for Hugging Face
4. Configure environment variables:
   - DATABASE_URL (Neon connection string)
   - OPENAI_API_KEY
   - BETTER_AUTH_SECRET
5. Test locally with Hugging Face port configuration
6. Create deployment documentation
7. Document secrets management

**Expected Outputs**:
- Backend configured for Hugging Face Spaces
- Startup command documented
- Environment variables documented

**Validation**:
- Backend runs on Hugging Face-compatible port
- Environment variables load correctly
- Deployment documentation clear

---

### Phase 3.12 — Testing Suite Implementation

**Purpose**: Comprehensive testing for MCP tools, agent, chat endpoint, and stateless behavior.

**Components Built**:
1. `backend/tests/test_mcp_tools.py` (tool unit tests)
2. `backend/tests/test_agent.py` (agent behavior tests)
3. `backend/tests/test_chat_endpoint.py` (API integration tests)
4. `backend/tests/test_stateless.py` (stateless verification tests)
5. `backend/tests/test_natural_language.py` (NL scenario tests)

**Dependencies**: All implementation phases (3.1-3.11) complete

**Steps**:
1. Write unit tests for each MCP tool (45+ test cases):
   - Tool inputs and outputs
   - Error conditions (task not found, permission denied)
   - User ownership enforcement
2. Write agent behavior tests:
   - Intent classification accuracy
   - Tool selection correctness
   - Multi-step tool chaining
   - Hallucination detection
3. Write chat endpoint integration tests:
   - Conversation creation
   - Message persistence
   - Agent integration
   - Error handling
4. Write stateless verification tests:
   - Server restart scenario
   - Conversation resume
   - No in-memory state detection
5. Write natural language scenario tests (45+ scenarios per skill document)
6. Add test fixtures for authenticated requests
7. Add database fixtures for test isolation

**Expected Outputs**:
- Comprehensive test suite with 100+ tests
- All tests passing
- Test coverage >85% for Phase 3 code

**Validation**:
- `pytest` runs successfully
- All critical tests pass
- Stateless verification test passes
- Natural language tests cover spec scenarios

---

### Phase 3.13 — Documentation & Deliverables

**Purpose**: Complete all documentation for hackathon submission and judge review.

**Components Built**:
1. `README.md` updates (Phase 3 instructions)
2. `docs/architecture/phase3-mcp-agent.md` (architecture diagram)
3. `docs/deployment/huggingface.md` (deployment guide)
4. `docs/demo/judge-demo.md` (demo script)

**Dependencies**: All implementation and testing complete

**Steps**:
1. Update repository README.md:
   - Add Phase 3 overview
   - Add setup instructions
   - Add chat interface screenshots
   - Add architecture diagram
2. Create architecture documentation:
   - System diagram (Frontend → API → Agent → MCP → DB)
   - Request flow diagram
   - Stateless architecture explanation
3. Create deployment guide:
   - Hugging Face Spaces step-by-step
   - Vercel deployment for frontend
   - Environment variable configuration
   - Troubleshooting common issues
4. Create demo script for judges:
   - 5-minute demo walkthrough
   - Key features to highlight (natural language, statelessness, MCP)
   - Q&A preparation
   - Architecture talking points
5. Update CHANGELOG with Phase 3 additions

**Expected Outputs**:
- Complete README with Phase 3 docs
- Architecture diagrams and explanations
- Deployment guides for both platforms
- Judge-ready demo script

**Validation**:
- Documentation is clear and complete
- Diagrams accurately represent architecture
- Deployment guides tested and verified
- Demo script reviewed and rehearsed

---

## Architecture Decision Records (ADR) Candidates

The following decisions are architecturally significant and should be documented as ADRs (with human approval):

### ADR-001: Stateless Architecture with Database-Backed Conversation Persistence

**Context**: Need to enable horizontal scalability and conversation resume across server restarts

**Decision**: Implement stateless design where conversation_id is the only state token, and all conversation history loads from PostgreSQL on each request

**Alternatives Considered**:
- In-memory session store with sticky sessions
- Redis cache for conversation history

**Consequences**:
- ✅ Horizontal scalability (any instance handles any request)
- ✅ No data loss on server restart
- ✅ Simple deployment (no Redis dependency)
- ❌ Slightly higher database load (mitigated by indexes)

### ADR-002: MCP (Model Context Protocol) for Tool Interface

**Context**: Need standardized way for AI agent to interact with task database

**Decision**: Use official MCP SDK to expose 5 stateless tools (add/list/update/complete/delete)

**Alternatives Considered**:
- Direct function calling without MCP protocol
- Custom tool protocol

**Consequences**:
- ✅ Standards-based approach (future-proof)
- ✅ Type-safe tool definitions with Pydantic
- ✅ Clear separation between agent and tools
- ❌ Additional dependency (MCP SDK)

### ADR-003: OpenAI Agents SDK for Agent Orchestration

**Context**: Need to orchestrate natural language understanding and tool calling

**Decision**: Use OpenAI Agents SDK (official) for agent runtime

**Alternatives Considered**:
- LangChain
- Custom agent implementation

**Consequences**:
- ✅ Official OpenAI support and updates
- ✅ Native function calling integration
- ✅ Proven reliability
- ❌ Vendor lock-in to OpenAI

### ADR-004: Hugging Face Spaces for Backend Deployment

**Context**: Need to deploy backend with OpenAI API access and PostgreSQL connectivity

**Decision**: Deploy backend to Hugging Face Spaces (not Railway)

**Alternatives Considered**:
- Railway (explicitly rejected by spec)
- Vercel serverless functions
- AWS Lambda

**Consequences**:
- ✅ Free tier available
- ✅ Easy deployment process
- ✅ Supports long-running processes
- ❌ Less familiar than Railway
- ❌ Potential resource limits

---

## Risk Analysis

### Risk 1: OpenAI API Latency

**Probability**: Medium | **Impact**: Medium

**Description**: OpenAI API calls add 1-2s latency to chat responses

**Mitigation**:
- Set realistic expectations (3s target includes OpenAI time)
- Consider caching for repeated queries (future optimization)
- Implement timeout and retry logic

### Risk 2: Conversation History Performance

**Probability**: Low | **Impact**: Medium

**Description**: Loading full conversation history becomes slow for 100+ message conversations

**Mitigation**:
- Database indexes on conversation_id + created_at
- Accept slower performance for MVP (<500ms acceptable)
- Document pagination strategy for post-MVP

### Risk 3: MCP SDK Compatibility

**Probability**: Low | **Impact**: High

**Description**: Official MCP SDK may not work as expected with OpenAI Agents SDK

**Mitigation**:
- Research SDK compatibility in Phase 0
- Test MCP tool registration early
- Have fallback to custom tool protocol if needed

### Risk 4: Hugging Face Deployment Issues

**Probability**: Medium | **Impact**: Medium

**Description**: Unfamiliarity with Hugging Face Spaces may cause deployment delays

**Mitigation**:
- Research Hugging Face deployment in Phase 0
- Test minimal deployment early
- Have detailed deployment documentation

### Risk 5: Agent Hallucination

**Probability**: Medium | **Impact**: High

**Description**: Agent may claim to complete actions without calling tools

**Mitigation**:
- System prompt with anti-hallucination rules
- Validation testing comparing agent claims to tool calls
- Tool call transparency in UI
- Production monitoring

---

## Dependencies Graph

```
Phase 3.1 (Directory Structure)
    ↓
Phase 3.2 (Database Models) ← Phase 3.3 (MCP Server Init)
    ↓                              ↓
Phase 3.5 (Conversation Service)   Phase 3.4 (MCP Tools)
    ↓                              ↓
Phase 3.6 (Agent Design) ←────────┘
    ↓
Phase 3.7 (Chat API Endpoint)
    ↓
Phase 3.8 (Stateless Verification)
    ↓
Phase 3.9 (Frontend ChatKit) ← Phase 3.10 (Auth Integration)
    ↓
Phase 3.11 (Hugging Face Config)
    ↓
Phase 3.12 (Testing Suite)
    ↓
Phase 3.13 (Documentation)
```

**Critical Path**: 3.1 → 3.2 → 3.5 → 3.6 → 3.7 → 3.9 → 3.12 → 3.13

**Parallel Work Possible**:
- 3.3 and 3.2 can run in parallel
- 3.4 can start once 3.3 is done (independent of 3.5)
- 3.10 can run in parallel with 3.9

---

## Success Metrics Alignment

This plan directly addresses all 19 success criteria from the specification:

**Natural Language Understanding** (SC-001 to SC-003):
- Achieved via Phase 3.6 (agent system prompt with intent patterns)
- Validated in Phase 3.12 (natural language test suite)

**Stateless Architecture Verification** (SC-004 to SC-007):
- Achieved via Phase 3.8 (stateless enforcement)
- Validated in Phase 3.12 (restart tests)

**Agent Behavior Quality** (SC-008 to SC-011):
- Achieved via Phase 3.6 (system prompt with anti-hallucination rules)
- Validated in Phase 3.12 (agent behavior tests)

**User Experience** (SC-012 to SC-015):
- Achieved via Phase 3.7 (optimized chat endpoint)
- Achieved via Phase 3.9 (ChatKit UI)
- Validated in Phase 3.12 (performance tests)

**Integration & Deployment** (SC-016 to SC-019):
- Achieved via Phase 3.11 (Hugging Face configuration)
- Achieved via Phase 3.10 (Better Auth integration)
- Validated in deployment testing

---

## Next Steps

1. **Human Review**: Review this plan for approval
2. **Phase 0 Execution**: Research all technical questions and create `research.md`
3. **Phase 1 Execution**: Create data models, contracts, and quickstart guide
4. **Plan Approval**: Human approves final plan after research
5. **Run `/sp.tasks`**: Generate dependency-ordered task list from this plan
6. **Run `/sp.implement`**: Execute tasks via Claude Code
7. **Validation**: Run test suite and verify all success criteria met
8. **Demo Preparation**: Practice judge demo and prepare presentation

**Estimated Timeline**: 2-3 days for full Phase 3 implementation (assumes 8-hour work days)

---

**Plan Status**: ✅ READY FOR HUMAN REVIEW AND APPROVAL
