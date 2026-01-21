# Skills Library

**Location**: `.claude/skills/`
**Version**: 1.0.0
**Purpose**: Centralized repository of reusable skills for AI agents

---

## Quick Reference

This folder contains the skills library that defines modular, reusable capabilities for all Claude agents working on the Todo-app hackathon project.

### Main Document

**[skills_library.md](./skills_library.md)** - Complete skills library with 24 skills across 6 categories

---

## Skills by Category

### 1. Specification Skills (4 skills)
Skills for creating, validating, and managing feature specifications:
- `requirement-decomposition` - Break down user goals into testable requirements
- `acceptance-criteria-generation` - Generate Given-When-Then acceptance criteria
- `spec-validation` - Validate specs for completeness and constitutional compliance
- `phase-boundary-definition` - Define clear phase boundaries and transitions

### 2. Planning & Task Skills (4 skills)
Skills for planning implementations and breaking down work:
- `task-decomposition` - Create dependency-ordered task lists
- `dependency-analysis` - Identify and map task/module dependencies
- `phase-safe-planning` - Ensure plans respect phase isolation
- `architecture-decision-identification` - Detect ADR-worthy decisions

### 3. Implementation Skills (4 skills)
Skills for writing production-quality code:
- `python-cli-pattern-implementation` - Implement CLI interfaces
- `modular-architecture-implementation` - Create clean, modular code
- `error-handling-implementation` - Implement comprehensive error handling
- `configuration-externalization` - Externalize config and secrets

### 4. Testing & QA Skills (4 skills)
Skills for ensuring quality and detecting issues:
- `unit-test-generation` - Generate comprehensive unit tests
- `integration-test-generation` - Create end-to-end test scenarios
- `cli-input-output-validation` - Validate CLI behavior
- `regression-detection` - Detect regressions in existing functionality

### 5. Documentation Skills (4 skills)
Skills for creating project documentation:
- `readme-generation` - Create comprehensive README files
- `adr-creation` - Document architectural decisions
- `judge-facing-narrative-writing` - Create hackathon judge documentation
- `phr-creation` - Record prompt history for traceability

### 6. Review & Analysis Skills (4 skills)
Skills for reviewing work and ensuring quality:
- `cross-artifact-consistency-check` - Validate spec/plan/tasks/code alignment
- `spec-vs-implementation-comparison` - Verify code matches spec acceptance criteria
- `risk-identification` - Identify technical and architectural risks
- `code-quality-review` - Review code for quality and best practices

---

## How to Use This Library

### For Agents

When working on tasks, reference skills from this library to:
1. **Invoke appropriate expertise** - Use the skill that matches your current task
2. **Chain skills together** - Combine multiple skills for complex workflows
3. **Ensure consistency** - Follow established patterns across all phases

### For Humans

Use this library to:
1. **Understand agent capabilities** - See what skills agents can leverage
2. **Design workflows** - Chain skills to create effective development processes
3. **Validate outputs** - Check that agent work follows skill quality standards

---

## Skill Structure

Each skill in the library includes:
1. **Name** - Unique identifier (kebab-case)
2. **Purpose** - What the skill accomplishes
3. **Applicable Agents** - Which agents can use this skill
4. **Input** - Required inputs
5. **Output** - Expected deliverables
6. **Scope & Boundaries** - What the skill can and cannot do
7. **Reusability Notes** - How to reuse across phases
8. **Dependencies** - Required resources or prerequisites
9. **Quality Expectations** - Standards outputs must meet
10. **Example Use Case** - Concrete usage example

---

## Common Skill Workflows

### Workflow 1: Feature Specification (Phase Start)
```
requirement-decomposition
  ↓
acceptance-criteria-generation
  ↓
phase-boundary-definition
  ↓
spec-validation
```

### Workflow 2: Implementation (Development)
```
task-decomposition
  ↓
dependency-analysis
  ↓
python-cli-pattern-implementation
  ↓
modular-architecture-implementation
  ↓
error-handling-implementation
  ↓
unit-test-generation
```

### Workflow 3: Quality Assurance (Phase Completion)
```
integration-test-generation
  ↓
regression-detection
  ↓
cross-artifact-consistency-check
  ↓
spec-vs-implementation-comparison
  ↓
code-quality-review
```

---

## Version History

- **1.0.0** (2025-12-29) - Initial skills library creation
  - 24 skills across 6 categories
  - Aligned with Todo-app hackathon requirements
  - Supports Spec-Driven Development workflow
  - Compatible with all agents (spec-architect, python-cli-expert, test-qa-validator, etc.)

---

## Maintenance

### Adding New Skills

When adding new skills:
1. Follow the 10-component structure
2. Add to appropriate category
3. Update this README with skill name and description
4. Include concrete examples
5. Version the skills_library.md document

### Updating Existing Skills

When modifying skills:
1. Update version number
2. Document changes in version history
3. Ensure backward compatibility where possible
4. Update related workflows if needed

---

## Phase-Specific Skills

### Phase 2: Full-Stack Web App
**Location**: `./phase2/`

Skills for building the authenticated full-stack web application:
- `fullstack-requirement-orchestration` - Cross-stack specification coordination
- `cross-layer-consistency-validation` - Frontend/backend alignment
- `jwt-auth-flow-specification` - JWT authentication design
- `rest-api-contract-definition` - REST endpoint contracts
- `relational-schema-design` - SQLModel database design
- ... and 13 more skills

### Phase 3: AI Chatbot
**Location**: `./phase3/`

Skills for building the AI-powered chatbot interface:
- `design-mcp-tools` - MCP tool definitions for task CRUD operations
- `implement-mcp-server` - MCP server with tool registration and invocation
- `define-agent-system-prompt` - System prompt with intent mapping and guardrails
- `map-intents-to-tools` - NL intent classification with confidence thresholds
- `implement-conversation-persistence` (planned) - Chat history storage
- `integrate-chatkit-ui` (planned) - OpenAI ChatKit frontend

---

## Related Documentation

- **Constitution**: `.specify/memory/constitution.md` - Project principles
- **Agent Definitions**: `.claude/agents/*.md` - Individual agent capabilities
- **Commands**: `.claude/commands/*.md` - Slash commands that invoke workflows
- **Templates**: `.specify/templates/*.md` - Document templates

---

**Maintained by**: Todo-app Hackathon Team
**Last Updated**: 2026-01-19
