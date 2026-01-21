---

description: "Dependency-ordered task list for Phase 3 AI-Powered Todo Chatbot implementation"
---

# Tasks: AI-Powered Todo Chatbot (Phase 3)

**Input**: Design documents from `/specs/003-phase3-ai-chatbot/`
**Prerequisites**: plan.md (approved), spec.md (approved)

**Tests**: This feature does NOT explicitly request tests in the specification. Test tasks are therefore NOT included. Testing will be manual verification against acceptance scenarios defined in spec.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/app/`, `frontend/app/`, `frontend/components/`
- Paths follow the project structure defined in plan.md

---

## Phase 0: Research & Technical Decisions

**Purpose**: Resolve all technical uncertainties before implementation. Research OpenAI Agents SDK, MCP SDK, Hugging Face Spaces deployment, and stateless conversation patterns.

**⚠️ CRITICAL**: All research must be documented in `research.md` before proceeding to Phase 1

- [X] T001 Research OpenAI Agents SDK stateless instantiation patterns and conversation history formatting in specs/003-phase3-ai-chatbot/research.md
- [X] T002 [P] Research Official MCP SDK tool registration, schema formats, and stateless execution patterns in specs/003-phase3-ai-chatbot/research.md
- [X] T003 [P] Research Hugging Face Spaces deployment requirements (port 7860, env vars, startup commands, resource limits) in specs/003-phase3-ai-chatbot/research.md
- [X] T004 [P] Research OpenAI ChatKit installation, domain allowlist configuration, and Next.js 15 integration in specs/003-phase3-ai-chatbot/research.md
- [X] T005 [P] Research stateless conversation management patterns (database query optimization, message ordering, conversation limits) in specs/003-phase3-ai-chatbot/research.md
- [X] T006 [P] Research Better Auth JWT token validation and user_id extraction for chat endpoint in specs/003-phase3-ai-chatbot/research.md

**Deliverable**: `specs/003-phase3-ai-chatbot/research.md` with all technical decisions documented

**Checkpoint**: Research complete - can proceed to Phase 1 design artifacts

---

## Phase 1: Design Artifacts

**Purpose**: Define data models, API contracts, and project structure based on research findings

**Dependencies**: Phase 0 (research.md) complete

- [X] T007 Create data model design document in specs/003-phase3-ai-chatbot/data-model.md with Conversation and Message SQLModel schemas, relationships, indexes, and constraints
- [X] T008 [P] Create chat API contract specification in specs/003-phase3-ai-chatbot/contracts/chat-api.yaml for POST /api/{user_id}/chat endpoint
- [X] T009 [P] Create MCP tool contract specifications in specs/003-phase3-ai-chatbot/contracts/mcp-tools.yaml for all 5 tools (add_task, list_tasks, complete_task, delete_task, update_task)
- [X] T010 [P] Create quickstart guide in specs/003-phase3-ai-chatbot/quickstart.md with Phase 3 setup instructions, database migrations, and test scenarios
- [X] T011 Update agent context via .specify/scripts/bash/update-agent-context.sh to add Phase 3 technologies (OpenAI Agents SDK, MCP SDK, ChatKit, Hugging Face Spaces)

**Checkpoint**: Design artifacts complete - ready for Phase 2 foundational implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation

**Dependencies**: Phase 1 (design artifacts) complete

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T012 Create backend MCP package directory structure in backend/app/mcp/ with __init__.py
- [X] T013 [P] Create backend agent package directory structure in backend/app/agent/ with __init__.py
- [X] T014 [P] Create frontend chat directory structure in frontend/app/chat/
- [X] T015 Define Conversation SQLModel in backend/app/models/conversation.py with id, user_id, title, created_at, updated_at fields and relationships
- [X] T016 [P] Define Message SQLModel in backend/app/models/message.py with id, conversation_id, user_id, role, content, tool_calls, tool_call_id, name, created_at fields
- [X] T017 Create Alembic migration for conversation and message tables via alembic revision --autogenerate -m "add conversation tables"
- [X] T018 Review and run migration with alembic upgrade head and verify tables in Neon database
- [X] T019 Install OpenAI Agents SDK and Official MCP SDK in backend/requirements.txt
- [X] T020 [P] Install OpenAI ChatKit in frontend/package.json via npm install @openai/chatkit
- [X] T021 Create MCP server initialization in backend/app/mcp/server.py with tool registration infrastructure
- [X] T022 Create Pydantic schemas for all 5 MCP tools in backend/app/mcp/schemas.py (AddTaskInput, ListTasksInput, CompleteTaskInput, DeleteTaskInput, UpdateTaskInput, ToolResponse)
- [X] T023 Create conversation persistence service in backend/app/services/conversation.py with create_conversation, get_conversation, save_message, get_conversation_history, list_user_conversations functions

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 5 - Stateless Conversation Resume (Priority: P1) 🎯 ARCHITECTURAL FOUNDATION

**Goal**: Enable users to resume conversations after server restart or device switch with full context loaded from database

**Independent Test**: Create conversation with 5 messages → restart backend server → send new message that references previous context → verify agent responds with full context awareness

**Why First**: This is the architectural foundation that all other stories depend on. Without stateless conversation persistence, the entire system cannot be production-ready.

### Implementation for User Story 5

- [X] T024 [US5] Implement create_conversation(user_id, title) in backend/app/services/conversation.py returning Conversation
- [X] T025 [US5] Implement get_conversation(conversation_id, user_id) in backend/app/services/conversation.py returning Conversation or None
- [X] T026 [US5] Implement save_message(conversation_id, role, content, tool_calls) in backend/app/services/conversation.py returning Message
- [X] T027 [US5] Implement get_conversation_history(conversation_id, limit) in backend/app/services/conversation.py returning List[Message] ordered by created_at
- [X] T028 [US5] Create ChatRequest Pydantic model in backend/app/routers/chat.py with message (required) and conversation_id (optional) fields
- [X] T029 [US5] Create ChatResponse Pydantic model in backend/app/routers/chat.py with conversation_id, message, and tool_calls fields
- [X] T030 [US5] Implement POST /api/{user_id}/chat endpoint skeleton in backend/app/routers/chat.py with auth validation, conversation loading/creation, and database session management
- [X] T031 [US5] Add conversation history loading to chat endpoint using get_conversation_history service function
- [X] T032 [US5] Add user message persistence to chat endpoint using save_message service function
- [X] T033 [US5] Add placeholder agent response persistence (hardcoded response for now) using save_message service function
- [X] T034 [US5] Add error handling for authentication failures (401), user_id mismatch (403), and database errors (500) in chat endpoint
- [X] T035 [US5] Add request logging (conversation_id, user_id, message length) to chat endpoint
- [X] T036 [US5] Register chat route with FastAPI app in backend/main.py

**Checkpoint**: Stateless conversation persistence working - can save/load conversations from database. Ready for agent integration.

---

## Phase 4: User Story 1 - Natural Language Task Creation (Priority: P1) 🎯 MVP CORE VALUE

**Goal**: Users can create tasks by describing them in natural language without forms or buttons

**Independent Test**: Send natural language message "Add a task to buy groceries" → verify task appears in database with correct title and user association

**Why Now**: This is the core value proposition of the AI chatbot. With stateless foundation (US5) complete, we can now add the agent layer to deliver immediate user value.

### Implementation for User Story 1

- [X] T037 [P] [US1] Implement add_task MCP tool in backend/app/mcp/tools.py accepting user_id, title, description and returning ToolResponse with created task
- [X] T038 [US1] Add user ownership validation to add_task tool (verify user_id before creating task)
- [X] T039 [US1] Add error handling to add_task tool for database failures and validation errors
- [X] T040 [US1] Register add_task tool with MCP server in backend/app/mcp/server.py
- [X] T041 [US1] Write agent system prompt in backend/app/agent/prompts.py with intent patterns for task creation (add/create/remind/make task variations)
- [X] T042 [US1] Add tool descriptions for add_task to system prompt with usage examples and parameter extraction rules
- [X] T043 [US1] Add anti-hallucination rules to system prompt (agent MUST call add_task tool, cannot claim success without tool call)
- [X] T044 [US1] Create AgentRunner class in backend/app/agent/runner.py with OpenAI client initialization
- [X] T045 [US1] Add tool attachment to AgentRunner (attach add_task MCP tool to OpenAI agent)
- [X] T046 [US1] Add conversation history formatting in AgentRunner (convert Message list to OpenAI format)
- [X] T047 [US1] Add agent execution method in AgentRunner that takes conversation history and user message, runs agent, returns response and tool_calls
- [X] T048 [US1] Add error handling and retry logic for OpenAI API failures in AgentRunner
- [X] T049 [US1] Create agent configuration in backend/app/agent/runner.py with model selection (GPT-4) and API key loading
- [X] T050 [US1] Integrate AgentRunner into chat endpoint (replace placeholder response with real agent execution)
- [X] T051 [US1] Add tool call extraction and logging to chat endpoint
- [X] T052 [US1] Add OPENAI_API_KEY to backend/.env.example with setup instructions

**Checkpoint**: Natural language task creation working - users can say "Add a task to buy groceries" and task is created via MCP tool

---

## Phase 5: User Story 2 - Conversational Task Querying (Priority: P1) 🎯 MVP QUERY INTERFACE

**Goal**: Users can ask about their tasks using natural language queries

**Independent Test**: Create 5 tasks (3 pending, 2 completed) → ask "Show my pending tasks" → verify only 3 pending tasks returned in conversational format

**Why Now**: Second core capability that justifies the chatbot interface. Completes the MVP by enabling both task creation (US1) and task querying (US2).

### Implementation for User Story 2

- [X] T053 [P] [US2] Implement list_tasks MCP tool in backend/app/mcp/tools.py accepting user_id and status filter (all/pending/completed) and returning ToolResponse with task list
- [X] T054 [US2] Add user ownership filtering to list_tasks tool (only return tasks belonging to user_id)
- [X] T055 [US2] Add status filtering logic to list_tasks tool (pending, completed, or all)
- [X] T056 [US2] Add error handling to list_tasks tool for database failures
- [X] T057 [US2] Register list_tasks tool with MCP server in backend/app/mcp/server.py
- [X] T058 [US2] Add intent patterns for task querying to system prompt in backend/app/agent/system_prompt.py (show/list/what tasks variations)
- [X] T059 [US2] Add tool descriptions for list_tasks to system prompt with usage examples and conversational response guidelines
- [X] T060 [US2] Add empty task list handling to system prompt (friendly "You don't have any tasks yet" response)
- [X] T061 [US2] Update AgentRunner to attach list_tasks tool alongside add_task tool
- [X] T062 [US2] Add conversational response formatting rules to system prompt (friendly language, not raw JSON)

**Checkpoint**: Natural language task querying working - users can ask "What's on my plate today?" and receive conversational task list

---

## Phase 6: User Story 3 - Context-Aware Task Completion (Priority: P2)

**Goal**: Users can complete tasks by referring to them naturally without task IDs

**Independent Test**: Create task "Buy groceries" → complete it with "I finished buying groceries" → verify agent matches task by title and marks complete

**Dependencies**: US1 and US2 (agent can create and list tasks)

### Implementation for User Story 3

- [X] T063 [P] [US3] Implement complete_task MCP tool in backend/app/mcp/tools.py accepting user_id and task_id and returning ToolResponse with updated task
- [X] T064 [US3] Add user ownership validation to complete_task tool (verify user owns task before completing)
- [X] T065 [US3] Add task existence validation to complete_task tool (return error if task not found)
- [X] T066 [US3] Add error handling to complete_task tool for database failures and permission denied errors
- [X] T067 [US3] Register complete_task tool with MCP server in backend/app/mcp/server.py
- [X] T068 [US3] Add intent patterns for task completion to system prompt (finished/completed/done variations)
- [X] T069 [US3] Add tool descriptions for complete_task to system prompt with task matching strategies (by ID, by title, by context reference)
- [X] T070 [US3] Add task not found handling to system prompt (show available tasks if match fails)
- [X] T071 [US3] Update AgentRunner to attach complete_task tool alongside existing tools
- [X] T072 [US3] Add tool chaining examples to system prompt (list tasks to find ID, then complete by ID)

**Checkpoint**: Context-aware task completion working - users can say "I finished the groceries task" and agent finds and completes it

---

## Phase 7: User Story 4 - Multi-Step Task Operations (Priority: P2)

**Goal**: Users can request complex operations requiring multiple tool calls in a single command

**Independent Test**: Send "Show my tasks and mark the first one as complete" → verify agent chains list_tasks followed by complete_task

**Dependencies**: US1, US2, US3 (all basic tools available)

### Implementation for User Story 4

- [X] T073 [US4] Add multi-step operation examples to system prompt (list then complete, search then delete, create then list)
- [X] T074 [US4] Add tool chaining strategy to system prompt (explicit step-by-step reasoning)
- [X] T075 [US4] Add context preservation rules to system prompt (use results from first tool call in second tool call)
- [X] T076 [US4] Update AgentRunner to support multiple sequential tool calls in single response
- [X] T077 [US4] Add tool call logging for multi-step operations in chat endpoint (log all tool calls in sequence)

**Checkpoint**: Multi-step operations working - users can request complex workflows and agent executes multiple tools in sequence

---

## Phase 8: User Story 6 - Task Update and Modification (Priority: P3)

**Goal**: Users can update task details (title, description) through natural language

**Independent Test**: Create task → modify it with "Change task 1 title to 'Call dad'" → verify update in database

**Dependencies**: US1 (agent can create tasks)

### Implementation for User Story 6

- [X] T078 [P] [US6] Implement update_task MCP tool in backend/app/mcp/tools.py accepting user_id, task_id, optional title, and optional description
- [X] T079 [US6] Add user ownership validation to update_task tool
- [X] T080 [US6] Add task existence validation to update_task tool
- [X] T081 [US6] Add partial update logic to update_task tool (only update provided fields)
- [X] T082 [US6] Add error handling to update_task tool
- [X] T083 [US6] Register update_task tool with MCP server in backend/app/mcp/server.py
- [X] T084 [US6] Add intent patterns for task updates to system prompt (change/update/modify/edit variations)
- [X] T085 [US6] Add tool descriptions for update_task to system prompt with field update strategies
- [X] T086 [US6] Update AgentRunner to attach update_task tool alongside existing tools

**Checkpoint**: Task updates working - users can modify task details through natural language

---

## Phase 9: Delete Task Support (Cross-Cutting)

**Purpose**: Add delete_task MCP tool to complete the 5 required tools (supports US4 multi-step operations)

**Dependencies**: Phase 2 (foundation) complete

- [X] T087 [P] Implement delete_task MCP tool in backend/app/mcp/tools.py accepting user_id and task_id
- [X] T088 Add user ownership validation to delete_task tool
- [X] T089 Add task existence validation to delete_task tool
- [X] T090 Add error handling to delete_task tool
- [X] T091 Register delete_task tool with MCP server in backend/app/mcp/server.py
- [X] T092 Add intent patterns for task deletion to system prompt (delete/remove variations)
- [X] T093 Add tool descriptions for delete_task to system prompt with confirmation strategies
- [X] T094 Update AgentRunner to attach delete_task tool alongside existing tools

**Checkpoint**: All 5 MCP tools implemented and registered (add, list, update, complete, delete)

---

## Phase 10: Frontend ChatKit Integration

**Purpose**: Connect OpenAI ChatKit UI to backend chat API

**Dependencies**: Phase 4 (US1) complete (basic agent functionality working)

- [X] T095 Obtain OpenAI domain key from OpenAI dashboard for ChatKit authorization
- [X] T096 Add NEXT_PUBLIC_OPENAI_DOMAIN_KEY to frontend/.env.local.example with setup instructions
- [X] T097 Configure ChatKit domain allowlist (localhost:3000 and future Vercel domain)
- [X] T098 Create ChatInterface component in frontend/components/ChatInterface.tsx wrapping OpenAI ChatKit
- [X] T099 Create chat API client in frontend/lib/chatApi.ts with sendMessage function calling POST /api/{user_id}/chat
- [X] T100 Add authentication to chat API client (extract user_id and JWT token from Better Auth)
- [X] T101 Add conversation_id persistence in ChatInterface using sessionStorage
- [X] T102 Implement handleSendMessage function in ChatInterface (get conversation_id from storage, call backend API, save conversation_id, return response to ChatKit)
- [X] T103 Add error handling to ChatInterface (network errors, authentication errors, display user-friendly messages)
- [X] T104 Add loading states to ChatInterface while waiting for agent response
- [X] T105 Create chat page in frontend/app/chat/page.tsx rendering ChatInterface component
- [X] T106 Add tool call transparency to ChatInterface (display which MCP tools were invoked in UI)

**Checkpoint**: ChatKit UI working - users can send messages from browser and receive agent responses

---

## Phase 11: Hugging Face Spaces Deployment Configuration

**Purpose**: Configure backend for Hugging Face Spaces deployment

**Dependencies**: All backend functionality complete (Phases 2-9)

- [X] T107 Update FastAPI app in backend/app/main.py to listen on port 7860 (Hugging Face Spaces default) configurable via environment variable
- [X] T108 Update FastAPI host binding to 0.0.0.0 for Hugging Face Spaces compatibility
- [X] T109 Create Hugging Face Spaces configuration file (app.py or Dockerfile) with startup command for uvicorn
- [X] T110 Update backend/.env.example with all required environment variables (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET) and Hugging Face-specific notes
- [X] T111 Create deployment documentation in docs/deployment/huggingface.md with step-by-step Hugging Face Spaces deployment instructions
- [X] T112 Document secrets management for Hugging Face Spaces (how to add environment variables in Spaces UI)
- [X] T113 Document Neon PostgreSQL connection from Hugging Face Spaces (connection string format, SSL requirements)

**Checkpoint**: Backend configured for Hugging Face Spaces - deployment documentation ready

---

## Phase 12: Documentation & Deliverables

**Purpose**: Complete all hackathon documentation and demo preparation

**Dependencies**: All implementation complete (Phases 2-11)

- [X] T114 Update repository README.md with Phase 3 overview section explaining AI chatbot features
- [X] T115 [P] Add Phase 3 setup instructions to README.md (environment variables, database migration, ChatKit configuration)
- [X] T116 [P] Add chat interface screenshots to README.md showing natural language interactions
- [X] T117 Create architecture diagram in docs/architecture/phase3-mcp-agent.md showing Frontend → API → Agent → MCP → Database flow
- [X] T118 Add stateless architecture explanation to architecture documentation (conversation_id as state token, database as source of truth)
- [X] T119 Add request flow diagram to architecture documentation (detailed lifecycle of a chat request)
- [ ] T120 Create Vercel deployment guide in docs/deployment/vercel.md for frontend deployment
- [ ] T121 Add environment variable configuration instructions for both platforms (Hugging Face and Vercel)
- [ ] T122 Add troubleshooting section to deployment documentation (common issues and solutions)
- [ ] T123 Create judge demo script in docs/demo/judge-demo.md with 5-minute walkthrough
- [ ] T124 Add key features to highlight in demo script (natural language, statelessness, MCP protocol, tool transparency)
- [ ] T125 Add Q&A preparation to demo script (anticipated judge questions and answers)
- [ ] T126 Add architecture talking points to demo script (emphasize production-ready stateless design)
- [ ] T127 Update CHANGELOG.md with Phase 3 additions and features

**Checkpoint**: Documentation complete - hackathon submission ready

---

## Phase 13: Manual Validation Against Acceptance Scenarios

**Purpose**: Manually test each user story against acceptance scenarios defined in spec.md

**Dependencies**: All phases complete

**⚠️ NOTE**: No automated tests were requested in the specification. All testing is manual verification.

- [ ] T128 Validate User Story 1 acceptance scenarios (4 scenarios for natural language task creation) manually and document results
- [ ] T129 Validate User Story 2 acceptance scenarios (4 scenarios for conversational task querying) manually and document results
- [ ] T130 Validate User Story 3 acceptance scenarios (4 scenarios for context-aware completion) manually and document results
- [ ] T131 Validate User Story 4 acceptance scenarios (4 scenarios for multi-step operations) manually and document results
- [ ] T132 Validate User Story 5 acceptance scenarios (4 scenarios for stateless conversation resume including server restart test) manually and document results
- [ ] T133 Validate User Story 6 acceptance scenarios (3 scenarios for task updates) manually and document results
- [ ] T134 Validate edge cases from spec.md (empty task list, ambiguous references, task not found, server restart, concurrent requests, agent hallucination prevention)
- [ ] T135 Document validation results in specs/003-phase3-ai-chatbot/validation-report.md with pass/fail status for each scenario

**Checkpoint**: All acceptance scenarios validated - feature ready for demo

---

## Dependencies & Execution Order

### Phase Dependencies

- **Research (Phase 0)**: No dependencies - can start immediately
- **Design (Phase 1)**: Depends on Phase 0 research completion
- **Foundational (Phase 2)**: Depends on Phase 1 design artifacts - BLOCKS all user stories
- **User Story 5 (Phase 3)**: Depends on Phase 2 foundational - MUST complete first (architectural foundation)
- **User Story 1 (Phase 4)**: Depends on Phase 3 (US5) - Core MVP value
- **User Story 2 (Phase 5)**: Depends on Phase 4 (US1) - Completes MVP
- **User Story 3 (Phase 6)**: Depends on Phases 4 and 5 (US1, US2) - Enhancement
- **User Story 4 (Phase 7)**: Depends on Phases 4, 5, 6 (US1, US2, US3) - Advanced capability
- **User Story 6 (Phase 8)**: Depends on Phase 4 (US1) - Lower priority
- **Delete Tool (Phase 9)**: Depends on Phase 2 (can run in parallel with user stories)
- **Frontend (Phase 10)**: Depends on Phase 4 (US1) minimum - works with basic agent
- **Deployment Config (Phase 11)**: Depends on all backend functionality (Phases 2-9)
- **Documentation (Phase 12)**: Depends on all implementation (Phases 2-11)
- **Validation (Phase 13)**: Depends on all implementation and documentation

### Critical Path (Must Complete in Order)

```
Phase 0 (Research)
  ↓
Phase 1 (Design)
  ↓
Phase 2 (Foundational) ← BLOCKS EVERYTHING
  ↓
Phase 3 (US5 - Stateless Foundation) ← REQUIRED FOR ALL STORIES
  ↓
Phase 4 (US1 - Task Creation) ← MVP CORE
  ↓
Phase 5 (US2 - Task Querying) ← MVP COMPLETE
  ↓
Phase 6 (US3 - Context Completion)
  ↓
Phase 7 (US4 - Multi-Step)
  ↓
Phase 10 (Frontend ChatKit)
  ↓
Phase 11 (Hugging Face Config)
  ↓
Phase 12 (Documentation)
  ↓
Phase 13 (Validation)
```

### Parallel Opportunities

Within each phase, tasks marked [P] can run in parallel:

- **Phase 0**: T002, T003, T004, T005, T006 can run in parallel (different research areas)
- **Phase 1**: T008, T009, T010 can run in parallel (different design documents)
- **Phase 2**: T013, T014, T016, T020 can run in parallel (different directories/models)
- **Phase 4 (US1)**: T037, T041 can start in parallel (tool and prompt are independent initially)
- **Phase 5 (US2)**: T053, T058 can start in parallel
- **Phase 6 (US3)**: T063, T068 can start in parallel
- **Phase 8 (US6)**: T078, T084 can start in parallel
- **Phase 9**: T087, T092 can start in parallel
- **Phase 12**: T115, T116, T118, T120 can run in parallel (different documentation files)

### User Story Independence (After Foundational Complete)

Once Phase 2 (Foundational) and Phase 3 (US5) are complete:

- **Phase 8 (US6)** can technically run in parallel with Phases 6-7 (only depends on US1 foundation)
- **Phase 9 (Delete Tool)** can run in parallel with user story phases

However, the RECOMMENDED order is sequential by priority (US5 → US1 → US2 → US3 → US4 → US6) to deliver incremental value.

---

## Implementation Strategy

### MVP First (Minimum Viable Product)

**Scope**: Phase 0-5 only (Research → Design → Foundation → US5 → US1 → US2)

1. Complete Phase 0: Research (T001-T006)
2. Complete Phase 1: Design artifacts (T007-T011)
3. Complete Phase 2: Foundational infrastructure (T012-T023) ← CRITICAL BLOCKER
4. Complete Phase 3: User Story 5 - Stateless foundation (T024-T036)
5. Complete Phase 4: User Story 1 - Task creation (T037-T052)
6. Complete Phase 5: User Story 2 - Task querying (T053-T062)
7. **STOP and VALIDATE**: Test US1 + US2 independently
8. Add minimal frontend (Phase 10) for demo
9. Deploy and demo MVP!

**Result**: Working AI chatbot that can create and query tasks through natural language, with stateless architecture proven.

### Incremental Delivery Beyond MVP

1. **MVP** (Phases 0-5 + minimal frontend) → Demo-able stateless AI chatbot
2. **+ Phase 6 (US3)** → Add context-aware completion → Demo enhanced UX
3. **+ Phase 7 (US4)** → Add multi-step operations → Demo advanced agent capability
4. **+ Phase 8 (US6) + Phase 9** → Add update and delete → Demo complete CRUD
5. **+ Phase 11-12** → Add deployment config and docs → Hackathon-ready submission

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With 2-3 developers after foundational phase:

1. **Team completes together**: Phase 0-1-2-3 (research, design, foundation, stateless base)
2. **Split after Phase 3**:
   - Developer A: Phase 4 (US1) then Phase 6 (US3)
   - Developer B: Phase 5 (US2) then Phase 7 (US4)
   - Developer C: Phase 9 (Delete) then Phase 10 (Frontend)
3. **Reconverge**: Phase 11-12-13 (deployment, docs, validation)

---

## Validation Checkpoints

Stop at these checkpoints to validate before proceeding:

1. **After Phase 0**: Research decisions documented and reviewed
2. **After Phase 1**: Design artifacts reviewed and approved
3. **After Phase 2**: Foundation tests pass (database tables exist, services work)
4. **After Phase 3 (US5)**: Stateless conversation resume verified (restart test passes)
5. **After Phase 4 (US1)**: Natural language task creation verified against acceptance scenarios
6. **After Phase 5 (US2)**: MVP complete - both creation and querying work
7. **After Phase 10**: Frontend integration verified (end-to-end chat works)
8. **After Phase 11**: Deployment configuration tested locally
9. **After Phase 13**: All acceptance scenarios validated and documented

---

## Notes

- [P] tasks = different files, no dependencies within that group
- [Story] label maps task to specific user story for traceability
- Each user story builds on the stateless foundation (US5)
- Research phase (Phase 0) is critical - do not skip
- Design artifacts (Phase 1) prevent implementation thrashing
- Manual validation against acceptance scenarios (no automated tests requested)
- Commit frequently after each task or logical group
- Server restart test (US5) is the key stateless verification
- Agent hallucination prevention is embedded in system prompt design
- Tool call transparency in UI builds trust and demonstrates MCP protocol
