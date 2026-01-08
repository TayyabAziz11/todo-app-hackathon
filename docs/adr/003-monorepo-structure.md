# ADR 003: Monorepo Structure for Full-Stack Application

## Status
Accepted

## Context
Phase II involves building a full-stack web application with:
- **Backend**: FastAPI + PostgreSQL
- **Frontend**: Next.js + React

We need to decide how to organize the codebase:

1. **Single repository vs separate repos**
2. **Directory structure**
3. **Dependency management**
4. **Deployment strategy**

### Requirements
- **Fast iteration** - Quick switching between frontend and backend
- **Shared documentation** - Specs, ADRs, PHRs in one place
- **Independent deployment** - Frontend and backend can deploy separately
- **Clear boundaries** - No accidental cross-dependencies

### Options Considered

#### Option 1: Separate Repositories
**Structure:**
```
todo-backend/     (separate repo)
todo-frontend/    (separate repo)
todo-docs/        (separate repo)
```

**Pros:**
- **Clear ownership** - Each team owns a repo
- **Independent versioning** - Separate release cycles
- **Smaller repos** - Faster git operations

**Cons:**
- **Documentation split** - Specs, ADRs scattered across repos
- **Context switching overhead** - Open 3 repos to see full picture
- **Harder to review** - PRs span multiple repos
- **Complex setup** - New developers clone 3 repos
- **Spec-driven workflow broken** - Specs separated from implementation

#### Option 2: Monorepo with Workspaces
**Structure:**
```
todo-app/
├── backend/
├── frontend/
├── specs/
├── docs/
└── package.json (npm workspaces)
```

**Pros:**
- **Single source of truth** - All code, specs, docs in one place
- **Atomic commits** - Frontend + backend changes in one PR
- **Shared tooling** - One linter, formatter, CI/CD config
- **Easy setup** - Clone once, install once
- **Spec-driven aligned** - Specs next to implementation

**Cons:**
- **Larger repo** - More files to clone
- **Dependency confusion** - Need clear boundaries
- **Deployment complexity** - Must deploy correct service

#### Option 3: Monorepo without Workspaces
**Structure:**
```
todo-app/
├── backend/
├── frontend/
├── specs/
└── docs/
```

**Pros:**
- **Simple structure** - No workspace config needed
- **Independent dependencies** - Backend (pip), Frontend (npm) separate
- **Clear boundaries** - No shared node_modules confusion

**Cons:**
- **No shared scripts** - Can't run "build all" from root
- **Manual coordination** - Must cd into each directory

## Decision
We will use **Monorepo without Workspaces** (Option 3).

### Rationale
1. **Spec-Driven Development requires unified view** - Specs, code, docs together
2. **Hackathon simplicity** - No workspace complexity
3. **Independent tech stacks** - Backend (Python), Frontend (Node) naturally separate
4. **Clear deployment** - `backend/` and `frontend/` directories obvious targets

### Implementation Details

**Directory Structure:**
```
todo-app/
├── backend/                 # FastAPI backend
│   ├── app/
│   ├── main.py
│   ├── requirements.txt
│   └── .env (gitignored)
│
├── frontend/                # Next.js frontend
│   ├── src/
│   ├── package.json
│   └── .env.local (gitignored)
│
├── specs/                   # Spec-Driven Development artifacts
│   ├── 001-phase1-todo-cli/
│   └── 002-fullstack-web-app/
│
├── docs/                    # Documentation
│   ├── adr/                 # Architecture Decision Records
│   └── QUALITY_ASSURANCE_REPORT.md
│
├── history/                 # Prompt History Records
│   └── prompts/
│
├── .specify/                # Spec-Kit Plus templates
│   └── memory/
│       └── constitution.md
│
├── README.md                # Project overview (both phases)
├── QUICKSTART.md            # Setup guide
├── TESTING.md               # Test procedures
└── .gitignore               # Ignore backend/.env, frontend/.env.local
```

**Boundaries:**
- ✅ Backend NEVER imports from frontend
- ✅ Frontend NEVER imports from backend
- ✅ Communication ONLY via HTTP REST API
- ✅ Shared artifacts: Specs, docs, ADRs (documentation only)

**Setup Commands:**
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

**Deployment:**
- **Backend**: Deploy `backend/` directory to cloud (e.g., Fly.io, Railway)
- **Frontend**: Deploy `frontend/` directory to Vercel/Netlify
- **Independent scaling**: Scale frontend and backend separately

## Consequences

### Positive
✅ **Single clone** - New developers get everything in one `git clone`
✅ **Unified specs** - Specs, code, tests, ADRs in one place (Spec-Driven)
✅ **Atomic changes** - Frontend + backend changes in one commit/PR
✅ **Shared history** - PHRs document entire project evolution
✅ **Simple setup** - No workspace configuration needed
✅ **Clear boundaries** - Separate `backend/` and `frontend/` directories

### Negative
⚠️ **Larger repo size** - Both frontend and backend dependencies
  - **Mitigation**: .gitignore node_modules and venv
  - **Impact**: Minimal - only source code tracked

⚠️ **Manual coordination** - No "build all" script
  - **Mitigation**: Document setup in QUICKSTART.md
  - **Acceptable**: Hackathon scope doesn't need automation

⚠️ **Deployment complexity** - Must deploy correct directory
  - **Mitigation**: Clear docs, separate deploy commands
  - **Solution**: CI/CD can detect changes per directory

### Trade-offs
- **Chose simplicity over automation** - No workspace config for hackathon
- **Chose unified view over repo size** - Spec-Driven requires single source
- **Chose manual setup over build scripts** - YAGNI for current scope

## Validation
After implementation, monorepo delivered:
- ✅ **Faster development** - No context switching between repos
- ✅ **Clear specs** - Easy to trace requirements → code
- ✅ **Simple onboarding** - Single README, single clone
- ✅ **Atomic PRs** - Full-stack features in one review

## Related Decisions
- **ADR 001**: JWT stateless authentication
- **ADR 002**: SQLModel for database ORM
- **ADR 004**: Next.js App Router for frontend (future)

## References
- [Monorepo.tools](https://monorepo.tools/)
- [Spec-Driven Development Principles](.specify/memory/constitution.md)

## Date
2025-12-31

## Authors
Phase II Implementation Team (Spec-Driven Development)
