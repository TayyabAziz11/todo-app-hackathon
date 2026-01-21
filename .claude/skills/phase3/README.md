# Phase 3 Skills - AI Chatbot

**Location**: `.claude/skills/phase3/`
**Version**: 1.15.0
**Purpose**: Skills for Phase 3 AI-Powered Chatbot implementation

---

## Overview

Phase 3 transforms the Todo App into an AI-powered chatbot where users can manage tasks through natural language commands. This folder contains skills for building the MCP tools, AI agent, conversation persistence, and frontend integration.

---

## Skills Index

### MCP & Tool Layer

| Skill | Purpose | Primary Agent |
|-------|---------|---------------|
| [design-mcp-tools](./design-mcp-tools.md) | Design stateless MCP tools for task CRUD | mcp-tool-architect |
| [implement-mcp-server](./implement-mcp-server.md) | Implement MCP server with tool registration | mcp-tool-architect |

### Database Layer

| Skill | Purpose | Primary Agent |
|-------|---------|---------------|
| [design-conversation-models](./design-conversation-models.md) | SQLModel schemas for Conversation and Message | conversation-persistence |
| [implement-message-storage](./implement-message-storage.md) | Service functions for message persistence and retrieval | conversation-persistence |

### AI Agent Layer

| Skill | Purpose | Primary Agent |
|-------|---------|---------------|
| [define-agent-system-prompt](./define-agent-system-prompt.md) | System prompt with intent mapping and guardrails | todo-ai-agent-designer |
| [map-intents-to-tools](./map-intents-to-tools.md) | NL intent classification with confidence thresholds | todo-ai-agent-designer |
| [configure-agent-runner](./configure-agent-runner.md) | OpenAI Agents SDK orchestration with MCP tools | todo-ai-agent-designer |
| `implement-tool-chaining` (planned) | Multi-step tool orchestration | todo-ai-agent-designer |

### API Layer

| Skill | Purpose | Primary Agent |
|-------|---------|---------------|
| [orchestrate-request-cycle](./orchestrate-request-cycle.md) | Complete stateless request lifecycle orchestration | chat-api-orchestrator |
| [implement-chat-endpoint](./implement-chat-endpoint.md) | POST /api/{user_id}/chat with conversation persistence | chat-api-orchestrator |
| `implement-streaming-chat` (planned) | Streaming chat responses with SSE | chat-api-orchestrator |

### Frontend Layer

| Skill | Purpose | Primary Agent |
|-------|---------|---------------|
| [integrate-chatkit-ui](./integrate-chatkit-ui.md) | ChatKit UI with backend API integration and conversation persistence | chatkit-frontend-integrator |
| [configure-domain-allowlist](./configure-domain-allowlist.md) | OpenAI ChatKit domain key setup and environment configuration | chatkit-frontend-integrator |

### Validation

| Skill | Purpose | Primary Agent |
|-------|---------|---------------|
| [validate-mcp-architecture](./validate-mcp-architecture.md) | MCP compliance validation with automated tests | mcp-compliance-validator |
| [validate-agent-tool-usage](./validate-agent-tool-usage.md) | Agent tool usage validation (no hallucination, proper chaining) | phase3-qa-demo |
| [run-natural-language-tests](./run-natural-language-tests.md) | End-to-end natural language testing for all CRUD operations and multi-step commands | phase3-qa-demo |
| [verify-stateless-behavior](./verify-stateless-behavior.md) | Stateless architecture verification with server restart and conversation resume testing | mcp-compliance-validator |
| [prepare-judge-demo](./prepare-judge-demo.md) | Complete hackathon demo preparation with script, talking points, and Q&A | phase3-qa-demo |

---

## Phase 3 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                              │
│                  ┌─────────────────────┐                            │
│                  │   OpenAI ChatKit    │                            │
│                  │   conversation_id   │                            │
│                  └─────────────────────┘                            │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ POST /api/{user_id}/chat
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Chat API (FastAPI)                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌────────────────┐  │
│  │ Conversation    │    │  OpenAI Agent   │    │   MCP Server   │  │
│  │ Persistence     │    │     Runner      │    │                │  │
│  └─────────────────┘    └─────────────────┘    └────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ Tool Calls
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         MCP Tools                                    │
│  ┌───────────┬───────────┬───────────┬───────────┬───────────────┐ │
│  │ add_task  │list_tasks │update_task│complete_  │ delete_task   │ │
│  │           │           │           │   task    │               │ │
│  └───────────┴───────────┴───────────┴───────────┴───────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ SQLModel ORM
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      PostgreSQL Database                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐ │
│  │    users    │  │    todos    │  │ conversations │  messages   │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Common Workflows

### Workflow 1: MCP Tools Implementation
```
design-mcp-tools
  ↓
implement-mcp-server
  ↓
validate-mcp-compliance
  ↓
unit test generation
```

### Workflow 2: AI Agent Development
```
define-agent-system-prompt
  ↓
map-intents-to-tools
  ↓
implement-tool-chaining
  ↓
integration testing
```

### Workflow 3: Full Chat Feature
```
design-chat-api-endpoint
  ↓
implement-conversation-persistence
  ↓
integrate-chatkit-ui
  ↓
demo-chatbot-scenarios
```

---

## Key Design Principles

1. **Statelessness**: No in-memory state between requests
2. **User Isolation**: All operations scoped to authenticated user
3. **Tool Determinism**: Same inputs always produce same outputs
4. **Error Graceful**: All failures return structured error responses
5. **Horizontal Scalability**: Any instance can handle any request

---

## Dependencies on Phase 2

Phase 3 builds on these Phase 2 artifacts:
- `User` model (`backend/app/models/user.py`)
- `Todo` model (`backend/app/models/todo.py`)
- Database connection (`backend/app/database.py`)
- JWT authentication (`backend/app/auth/`)

---

## Version History

- **1.15.0** (2026-01-20) - Added hackathon demo preparation skill
  - `prepare-judge-demo` skill created
  - Complete 5-minute demo script with timing breakdown
  - 3 polished demo scenarios (quick task management, multi-step intelligence, stateless proof)
  - Technical talking points for MCP, stateless architecture, and spec-driven development
  - 8+ anticipated judge questions with prepared answers
  - Visual aids including architecture diagram and code snippets
  - Backup plans for technical issues during live demo
  - Judge handout template (one-page technical summary)
  - Pre-demo checklist and success metrics
  - Phase 3 skills library now complete with 17 documented skills

- **1.14.0** (2026-01-20) - Added stateless behavior verification skill
  - `verify-stateless-behavior` skill created
  - Comprehensive verification procedures for stateless architecture compliance
  - Server restart testing with conversation and task persistence validation
  - Conversation resume testing with full history and context verification
  - Database persistence validation (single source of truth, user isolation, ordering)
  - Horizontal scaling tests for multi-instance deployment readiness
  - Automated pytest suite with database connection fixtures
  - Manual verification checklist with step-by-step procedures
  - Common violation patterns with remediation examples
  - CI/CD integration with GitHub Actions workflow
  - Verification report templates for production sign-off

- **1.13.0** (2026-01-20) - Added natural language testing skill
  - `run-natural-language-tests` skill created
  - Comprehensive test suite for all CRUD operations via natural language
  - 45+ test scenarios covering basic operations, multi-step commands, and edge cases
  - Automated pytest implementation with fixtures and parameterized tests
  - Manual testing protocol for ChatKit UI and direct API testing
  - Demo scenarios and success metrics for hackathon presentation
  - Test result reporting templates with pass/fail analysis

- **1.12.0** (2026-01-20) - Added agent tool usage validation skill
  - `validate-agent-tool-usage` skill created
  - Agent behavior validation (correct tool usage, no hallucination, proper chaining, error handling)
  - Automated test suite with 4 test categories and 12+ scenarios
  - Manual validation protocol and report templates
  - Production monitoring setup for runtime validation
  - Integration with phase3-qa-demo agent for comprehensive testing

- **1.11.0** (2026-01-19) - Added MCP architecture validation skill
  - `validate-mcp-architecture` skill created
  - Comprehensive compliance checklist (statelessness, registration, schemas, layer separation)
  - Automated validation test suite
  - Common violation detection and remediation guidance
  - Pre-commit hook and CI/CD integration
  - Manual code review templates

- **1.10.0** (2026-01-19) - Added domain allowlist configuration skill
  - `configure-domain-allowlist` skill created
  - Complete OpenAI dashboard setup instructions
  - Local and Vercel environment configuration
  - Domain key security best practices
  - Comprehensive troubleshooting guide
  - Team onboarding documentation templates

- **1.9.0** (2026-01-19) - Added ChatKit UI integration skill
  - `integrate-chatkit-ui` skill created
  - Complete Next.js chat page with ChatKit component
  - Backend API integration with authentication
  - Conversation ID persistence using sessionStorage
  - Tool call transparency in UI
  - Error handling and loading states
  - No AI logic in frontend (pure presentation layer)
  - CORS and deployment configuration

- **1.8.0** (2026-01-19) - Added message storage implementation skill
  - `implement-message-storage` skill created
  - Complete service layer for conversation and message persistence
  - Stateless functions with no in-memory caching
  - Chronological ordering and multi-conversation support
  - User isolation and ownership enforcement
  - Batch operations and search functionality
  - Comprehensive testing strategy

- **1.7.0** (2026-01-19) - Added conversation models design skill
  - `design-conversation-models` skill created
  - Complete SQLModel definitions for Conversation and Message
  - Database migration with indexes and foreign keys
  - Conversation resume support with timestamp ordering
  - Query patterns and performance optimizations
  - Cascade delete and data integrity enforcement

- **1.6.0** (2026-01-19) - Added request cycle orchestration skill
  - `orchestrate-request-cycle` skill created
  - Complete 10-step stateless request lifecycle
  - Authentication, DB, conversation, agent, tools, persistence flow
  - Statelessness guarantees and horizontal scalability patterns
  - Error handling, observability, security, and testing strategies
  - Performance optimization and common pitfalls documentation

- **1.5.0** (2026-01-19) - Added chat endpoint implementation skill
  - `implement-chat-endpoint` skill created
  - Conversation and Message database models
  - Conversation persistence service functions
  - POST /api/{user_id}/chat endpoint with stateless design
  - AgentRunner integration with conversation history
  - Complete API layer for Phase 3

- **1.4.0** (2026-01-19) - Added agent runner orchestration skill
  - `configure-agent-runner` skill created
  - AgentRunner class for OpenAI Agents SDK integration
  - Message building, tool attachment, and response processing
  - Complete Phase 3 foundation: MCP tools, server, prompt, classifier, and runner

- **1.3.0** (2026-01-19) - Added intent-to-tool mapping skill
  - `map-intents-to-tools` skill created
  - Comprehensive intent patterns with confidence thresholds
  - Tool chaining logic for multi-step operations
  - Intent classifier implementation with parameter extraction

- **1.2.0** (2026-01-19) - Added AI agent system prompt skill
  - `define-agent-system-prompt` skill created
  - Complete system prompt with intent mapping
  - Guardrails and anti-hallucination rules
  - Response templates and example conversations

- **1.1.0** (2026-01-19) - Added MCP server implementation skill
  - `implement-mcp-server` skill created
  - Covers tool registration, invocation, and OpenAI SDK integration
  - Statelessness verification checklist included

- **1.0.0** (2026-01-19) - Initial Phase 3 skills
  - `design-mcp-tools` skill created
  - MCP server implementation complete
  - Tool schemas defined for all 5 operations

---

## Related Documentation

- **Phase 3 Spec**: `specs/003-phase3-ai-chatbot/`
- **MCP Implementation**: `backend/app/mcp/`
- **Phase 3 Agents**: `.claude/agents/` (mcp-tool-architect, todo-ai-agent-designer, etc.)

---

**Maintained by**: Todo-app Hackathon Team
**Last Updated**: 2026-01-20
