# Todo-app Hackathon Project Constitution

<!--
SYNC IMPACT REPORT
==================
Version Change: Initial → 1.0.0
Created: 2025-12-29
Type: Initial constitution creation

Modified Principles:
- All principles created from scratch based on hackathon requirements
- Established 7 core principles for spec-driven, AI-native development
- Added 3 governance sections covering workflow, quality, and AI usage

Templates Requiring Updates:
✅ plan-template.md - Constitution Check section aligns with principles
✅ spec-template.md - Requirements structure supports spec-first approach
✅ tasks-template.md - Task organization reflects phase isolation principle

Command Files Status:
✅ .claude/commands/*.md - All commands reference appropriate governance rules

Follow-up TODOs:
- None (all placeholders resolved)
-->

## Core Principles

### I. Spec-First Development (NON-NEGOTIABLE)

**Rule**: No code may be written before a complete, approved specification exists.

- Specifications define WHAT the system must do, never HOW it does it
- Specifications are technology-agnostic and describe observable behavior
- Specifications include acceptance criteria in Given-When-Then format
- Specifications must be reviewed and approved by a human before implementation begins
- Once approved, specifications are immutable for that phase; changes require new spec version

**Rationale**: Specifications are the source of truth. Code is a derived artifact. This inverts the traditional relationship and ensures AI-generated code serves human intent, not vice versa.

### II. Phase Isolation with Forward Compatibility

**Rule**: Each phase (Phase 1 through Phase 5) must be independently runnable and testable.

- Later phases may extend earlier phases but MUST NOT break existing functionality
- Each phase lives in the same repository with clear boundaries (folders, modules, or feature flags)
- Phase transitions require explicit human approval
- Each phase must have its own specification document
- Rollback to any prior phase must be possible without data loss or corruption

**Rationale**: Hackathon evaluation may assess phases individually. Judges must be able to run Phase 2 without requiring Phase 5 to be complete. This also enables incremental delivery and reduces risk.

### III. Agentic Workflow Discipline

**Rule**: AI agents must follow the explicit workflow: `spec → plan → tasks → implement`.

- No workflow steps may be skipped
- Each step produces a versioned artifact (spec.md, plan.md, tasks.md, code)
- Agents must not introduce features not present in the approved specification
- Agents must ask clarifying questions when requirements are ambiguous
- Agents must suggest Architectural Decision Records (ADRs) when significant decisions are made, but NEVER auto-create them

**Rationale**: AI operates as a disciplined collaborator, not an autonomous actor. Human judgment gates each transition. This ensures traceability and prevents scope creep.

### IV. Human-in-the-Loop Governance

**Rule**: Humans approve all specifications, architectural decisions, and phase transitions.

- Humans are accountable for correctness, security, and quality
- Humans validate that AI output matches intent
- Humans review and approve before deployment or phase advancement
- AI must surface decisions explicitly and wait for approval
- AI must record all interactions in Prompt History Records (PHRs) for audit and learning

**Rationale**: AI is a tool, not a replacement for engineering judgment. Responsibility and accountability remain with humans. This constitution enforces that boundary.

### V. Clean Architecture and Modularity

**Rule**: All code must exhibit clear separation of concerns, explicit dependencies, and minimal coupling.

- Each module/component must have a single, well-defined responsibility
- Dependencies must flow in one direction (no circular dependencies)
- External integrations must be abstracted behind interfaces
- Error handling must be explicit; no silent failures
- Configuration must be externalized (environment variables, config files)

**Rationale**: Early phases may be simple, but never sloppy. Clean architecture from the start prevents technical debt and enables evolution across phases.

### VI. Deterministic and Observable Behavior

**Rule**: All system behavior must be predictable, testable, and observable.

- Functions must be pure where possible (same input → same output)
- Side effects must be explicit and isolated
- All operations must produce logs or traces for debugging
- CLI interfaces must use text in/out: stdin/args → stdout, errors → stderr
- Error messages must be actionable and include context

**Rationale**: Determinism enables reliable testing. Observability enables debugging and audit. These are non-negotiable for production-grade software, even in a hackathon.

### VII. Simplicity and YAGNI (You Aren't Gonna Need It)

**Rule**: Implement only what the specification requires. No speculative features.

- Start with the simplest solution that satisfies acceptance criteria
- Avoid premature optimization or abstraction
- Avoid frameworks or libraries unless they solve a concrete, present problem
- Refactor only when complexity is justified by actual requirements
- Prefer readability over cleverness

**Rationale**: Hackathon time is limited. Overengineering wastes time and introduces risk. Ship working software that meets the spec, nothing more.

## Development Workflow

### Workflow Gates

All development follows this mandatory sequence:

1. **Spec Creation** (`/sp.specify`):
   - Human provides feature description
   - AI generates specification with user stories and acceptance criteria
   - Human reviews and approves specification
   - Output: `specs/<feature>/spec.md`

2. **Planning** (`/sp.plan`):
   - AI reads approved spec
   - AI researches codebase and generates implementation plan
   - AI identifies architecture decisions and suggests ADRs
   - Human reviews and approves plan
   - Output: `specs/<feature>/plan.md`, `research.md`, `data-model.md`, `contracts/`

3. **Task Breakdown** (`/sp.tasks`):
   - AI reads plan and generates dependency-ordered task list
   - Tasks are grouped by user story for independent implementation
   - Tasks include exact file paths and clear descriptions
   - Human reviews and approves tasks
   - Output: `specs/<feature>/tasks.md`

4. **Implementation** (`/sp.implement`):
   - AI executes tasks in dependency order
   - AI writes code, tests, and documentation as specified
   - Human validates output at checkpoints
   - Output: Working code that passes acceptance criteria

5. **Commit and Review** (`/sp.git.commit_pr`):
   - AI generates commit messages following project conventions
   - AI creates pull requests with clear summaries
   - Human reviews and merges
   - Output: Version-controlled, auditable changes

### Prohibited Shortcuts

The following are explicitly forbidden:

- Writing code before an approved spec exists
- Skipping the planning phase
- Auto-generating ADRs without human consent
- Implementing features not in the spec
- Pushing to remote without human approval
- Amending commits made by other developers

## Quality Standards

### Code Quality

- **Readability**: Code must be self-explanatory; comments only where logic is non-obvious
- **Explicitness**: No implicit behavior; all assumptions must be stated
- **Consistency**: Follow language idioms and project conventions
- **Minimal Scope**: Functions and modules must do one thing well
- **Error Handling**: All failure modes must be handled explicitly

### Documentation Quality

- **README.md**: Must explain project purpose, phase structure, and how to run each phase
- **CLAUDE.md**: Must explain agent usage, workflows, and governance rules
- **spec.md**: Must include user stories, acceptance criteria, and success metrics
- **plan.md**: Must include technical context, architecture decisions, and structure
- **tasks.md**: Must include exact paths, dependencies, and execution order

### Testing Quality (if applicable)

- Tests must be written BEFORE implementation (Test-Driven Development)
- Tests must fail initially, then pass after implementation
- Tests must cover happy path and edge cases from acceptance criteria
- Integration tests must validate user journeys end-to-end
- Contract tests must validate API interfaces and schemas

## AI Usage Rules

### AI Responsibilities

- Generate specifications, plans, tasks, and code based on human input
- Explain reasoning at each phase transition
- Ask clarifying questions when requirements are ambiguous
- Suggest ADRs for architecturally significant decisions
- Record all interactions in Prompt History Records (PHRs)
- Surface risks, trade-offs, and alternatives explicitly

### AI Constraints

- NEVER hallucinate requirements not provided by the human
- NEVER skip workflow steps (spec → plan → tasks → implement)
- NEVER bypass human approval gates
- NEVER auto-create ADRs; always wait for human consent
- NEVER push to remote repositories without explicit human instruction
- NEVER commit without human request

### AI Output Standards

All AI-generated artifacts must be:

- **Traceable**: Every code change must map back to a spec requirement
- **Reviewable**: Output must be human-readable and understandable
- **Aligned**: Must satisfy acceptance criteria exactly as written
- **Complete**: No TODOs or placeholders unless explicitly approved by human
- **Versioned**: All artifacts must include metadata (date, version, author)

## Documentation Requirements

### Mandatory Artifacts

1. **README.md** (repository root):
   - Project purpose and hackathon context
   - Phase descriptions and how to run each phase
   - Prerequisites and setup instructions
   - Links to key documentation

2. **CLAUDE.md** (repository root):
   - Agent usage instructions
   - Workflow commands (`/sp.specify`, `/sp.plan`, `/sp.tasks`, `/sp.implement`)
   - Governance rules and guardrails
   - PHR and ADR policies

3. **Spec History** (`specs/<feature>/`):
   - `spec.md`: Feature specification
   - `plan.md`: Implementation plan
   - `tasks.md`: Task breakdown
   - `research.md`, `data-model.md`, `contracts/`: Supporting artifacts

4. **Prompt History Records** (`history/prompts/`):
   - Every user input captured verbatim
   - Routed to: `constitution/`, `<feature-name>/`, or `general/`
   - Must include full prompt text and representative response
   - Created after every implementation or planning session

5. **Architecture Decision Records** (`history/adr/`):
   - Created only when human approves after AI suggestion
   - Must document: context, decision, alternatives considered, consequences
   - Linked from relevant spec or plan documents

### Documentation Style

- Use clear, authoritative language
- Avoid marketing fluff or hyperbole
- Use numbered sections and bullet points
- Include code references where applicable: `file.py:123`
- Keep language concise but complete

## Hackathon Alignment

### Demonstration Goals

This constitution and all artifacts it governs exist to demonstrate:

1. **Spec-Driven Thinking**: Specifications precede code. Intent precedes implementation.

2. **AI-Native Development Maturity**: AI is used as a disciplined collaborator with explicit workflows, human oversight, and full traceability.

3. **Architectural Foresight**: Clean architecture, modularity, and phase isolation enable evolution without rewrite.

4. **Professional Engineering Judgment**: Human accountability, explicit decision-making, and quality standards reflect real-world engineering rigor.

5. **Clean Evolution Across Phases**: Each phase builds on prior phases without breaking them. The system grows gracefully.

### Evaluation Criteria Alignment

Judges will assess:

- **Spec Quality**: Are specifications clear, complete, and technology-agnostic?
- **Workflow Discipline**: Did the team follow spec → plan → tasks → implement?
- **AI Collaboration**: Is AI usage traceable, governed, and effective?
- **Code Quality**: Is code readable, modular, and maintainable?
- **Phase Independence**: Can each phase run independently?
- **Documentation**: Are README, CLAUDE.md, specs, and ADRs present and useful?

This constitution ensures every criterion is met.

## Governance

### Constitution Authority

- This constitution supersedes all other development practices, guidelines, or conventions.
- All specifications, plans, tasks, and code must comply with this constitution.
- Violations must be justified explicitly and documented in the relevant artifact.

### Amendment Process

- Amendments require human approval and must be documented.
- Version number must increment according to semantic versioning:
  - **MAJOR**: Backward-incompatible governance or principle changes
  - **MINOR**: New principles or material expansions
  - **PATCH**: Clarifications, wording fixes, non-semantic refinements
- Amendment history must be recorded in the Sync Impact Report (HTML comment at top of this file).
- Dependent templates (spec, plan, tasks) must be updated to reflect amendments.

### Compliance Review

- All pull requests must verify compliance with this constitution.
- Code reviews must check:
  - Does the change map to an approved spec?
  - Does the implementation follow the plan?
  - Are principles (modularity, determinism, simplicity) upheld?
  - Are documentation requirements met?
- Non-compliance must be flagged and resolved before merge.

### Runtime Guidance

For day-to-day development instructions and agent-specific workflows, see:

- **CLAUDE.md**: Claude Code agent usage and workflows
- **README.md**: Project setup and phase execution
- **.claude/commands/*.md**: Slash command documentation

---

**Version**: 1.0.0 | **Ratified**: 2025-12-29 | **Last Amended**: 2025-12-29
