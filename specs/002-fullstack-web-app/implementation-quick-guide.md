# Phase II Implementation Quick Guide

**Reference**: See [implementation-execution-plan.md](./implementation-execution-plan.md) for detailed Phase A-C execution

This document provides condensed execution guidance for Phases D-G and overall coordination strategy.

---

## Phases D-G: Condensed Execution Guide

### PHASE D: Backend API Implementation (8 tasks, ~90 min)

**Agent**: `fastapi-backend-architect`
**Prerequisites**: Phases A, B, C complete

**Quick Execution**:
```bash
cd backend
source venv/bin/activate

# D.1-D.2: Auth endpoints (register, login)
# Create app/routers/auth.py with registration and login endpoints
# Create app/services/user_service.py for user business logic

# D.3: Todo schemas
# Create app/schemas/todo.py with TodoCreate, TodoUpdate, TodoResponse

# D.4-D.7: Todo CRUD endpoints
# Create app/routers/todos.py with create, list, update, delete endpoints
# Create app/services/todo_service.py for todo business logic

# D.8: Register routers in main.py
# Add: app.include_router(auth_router) and app.include_router(todos_router)
```

**Key Files to Create**:
1. `backend/app/routers/auth.py` - POST /api/auth/register, POST /api/auth/login
2. `backend/app/routers/todos.py` - CRUD endpoints for todos
3. `backend/app/schemas/todo.py` - Pydantic models
4. `backend/app/services/user_service.py` - User business logic
5. `backend/app/services/todo_service.py` - Todo business logic

**Validation**:
```bash
# Start backend
uvicorn main:app --reload &

# Test registration
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Test create todo (use token from login response)
TOKEN="<access_token>"
curl -X POST http://localhost:8000/api/user123/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Todo","description":"Test"}'
```

---

### PHASE E: Frontend Application (11 tasks, ~120 min)

**Agent**: `nextjs-frontend-architect`
**Prerequisites**: Phases A, D complete (needs backend API)

**Quick Execution**:
```bash
cd frontend

# E.1: API client (src/lib/api.ts)
# Create apiClient() function with JWT header injection

# E.2: TypeScript types (src/types/)
# Create user.ts, todo.ts, auth.ts interfaces

# E.3: Auth context (src/lib/auth.ts)
# Create AuthContext, AuthProvider, useAuth hook

# E.4-E.5: Auth pages
# Create src/app/page.tsx (login)
# Create src/app/register/page.tsx (registration)
# Create src/components/auth/LoginForm.tsx
# Create src/components/auth/RegisterForm.tsx

# E.6: Dashboard (src/app/dashboard/page.tsx)
# Protected route with logout button

# E.7-E.10: Todo components
# Create src/components/todos/TodoList.tsx
# Create src/components/todos/TodoItem.tsx
# Create src/components/todos/TodoForm.tsx
# Create src/hooks/useTodos.ts

# E.11: Responsive styles (update Tailwind classes)
```

**Key Files to Create**:
1. `frontend/src/lib/api.ts` - API client with auth
2. `frontend/src/lib/auth.ts` - AuthContext and hooks
3. `frontend/src/types/` - TypeScript interfaces
4. `frontend/src/app/page.tsx` - Login page
5. `frontend/src/app/register/page.tsx` - Registration page
6. `frontend/src/app/dashboard/page.tsx` - Dashboard
7. `frontend/src/components/auth/` - Auth components
8. `frontend/src/components/todos/` - Todo components
9. `frontend/src/hooks/useTodos.ts` - Data fetching hook

**Validation**:
```bash
# Start frontend
npm run dev

# Open browser: http://localhost:3000
# Test: Register → Login → Create todo → Mark complete → Delete
```

---

### PHASE F: Integration & End-to-End Flow (5 tasks, ~60 min)

**Agent**: `test-qa-validator` and `auth-security-architect`

**Quick Execution**:
```bash
# F.1: CORS already configured in Phase A (verify)

# F.2-F.3: E2E tests
cd frontend
npm install -D @playwright/test
npx playwright install

# Create __tests__/e2e/registration.test.ts
# Create __tests__/e2e/todos.test.ts

# F.4: Security tests
cd backend
# Create tests/test_data_isolation.py

# F.5: Token expiration tests
# Create tests/test_token_expiration.py
```

**Validation**:
```bash
# Run E2E tests
cd frontend
npx playwright test

# Run backend security tests
cd backend
pytest tests/test_data_isolation.py -v
```

---

### PHASE G: QA, Validation & Documentation (10 tasks, ~90 min)

**Agent**: `test-qa-validator` and `hackathon-judge-reviewer`

**Quick Execution**:
```bash
# G.1: Backend tests
cd backend
pytest --cov=app --cov-report=html --cov-report=term-missing

# G.2: Frontend tests
cd frontend
npm test -- --coverage

# G.3: Traceability matrix
# Create specs/002-fullstack-web-app/traceability.md

# G.4: Security audit
# Create specs/002-fullstack-web-app/security-audit.md

# G.5: Performance benchmark
cd backend
pip install locust
# Create benchmark script

# G.6: Update README
# Edit root README.md with Phase II documentation

# G.7: ADRs
# Create history/adr/0001-monorepo-structure.md
# Create history/adr/0002-jwt-storage-localstorage.md
# ... (5 ADRs total)

# G.8: Compliance report
# Create specs/002-fullstack-web-app/hackathon-compliance.md

# G.9: Create PHR for implementation

# G.10: Final code review
cd backend && black . && mypy app/
cd frontend && npm run lint
```

---

## Parallel Execution Strategy

### Stage 1: Foundation (Sequential)
```bash
# Must run in order
Phase A → Phase B → Phase C
```

### Stage 2: Backend & Frontend Preparation (Parallel)
```bash
# After Phase C, can run in parallel:
Terminal 1: Phase D (Backend API)
Terminal 2: Phase E tasks E.1-E.3 (Frontend infrastructure)
```

### Stage 3: Frontend UI (Sequential after D)
```bash
# Requires Phase D complete
Phase E tasks E.4-E.11 (UI components)
```

### Stage 4: Integration (Sequential after E)
```bash
# Requires both D and E complete
Phase F
```

### Stage 5: QA (Partially Parallel)
```bash
# Can run in parallel:
Terminal 1: G.1 (Backend tests)
Terminal 2: G.2 (Frontend tests)

# Then sequential:
G.3 → G.4 → G.5 → G.6 → G.7 → G.8 → G.9 → G.10
```

---

## Agent Execution Summary

### fullstack-spec-architect
**Phases**: A (setup), G.7 (ADRs), G.9 (PHR)
**Total Tasks**: 8
**Estimated Time**: 90 minutes

**Execution Order**:
1. A.1: Directory structure
2. A.4: Environment templates
3. G.7: Create 5 ADRs
4. G.9: Create implementation PHR

---

### fastapi-backend-architect
**Phases**: A (backend), B (database), D (API)
**Total Tasks**: 18
**Estimated Time**: 4 hours

**Execution Order**:
1. A.3: Backend requirements
2. A.5: FastAPI initialization
3. B.1-B.5: Database layer
4. D.1-D.8: API implementation

**Critical Files**:
- `backend/main.py`
- `backend/app/models/`
- `backend/app/routers/`
- `backend/app/services/`

---

### auth-security-architect
**Phases**: C (auth), F (security tests), G (audit)
**Total Tasks**: 7
**Estimated Time**: 2.5 hours

**Execution Order**:
1. C.1-C.4: Auth implementation
2. F.4: Data isolation tests
3. F.5: Token expiration tests
4. G.4: Security audit

---

### nextjs-frontend-architect
**Phases**: A (frontend), E (UI)
**Total Tasks**: 13
**Estimated Time**: 3.5 hours

**Execution Order**:
1. A.2: Frontend configuration
2. A.6: Next.js initialization
3. E.1-E.11: Frontend implementation

**Critical Files**:
- `frontend/src/lib/api.ts`
- `frontend/src/lib/auth.ts`
- `frontend/src/app/`
- `frontend/src/components/`

---

### test-qa-validator
**Phases**: F (E2E), G (QA)
**Total Tasks**: 6
**Estimated Time**: 2.5 hours

**Execution Order**:
1. F.2-F.3: E2E tests
2. G.1: Backend test suite
3. G.2: Frontend test suite
4. G.5: Performance benchmarks

---

### hackathon-judge-reviewer
**Phases**: G (documentation & compliance)
**Total Tasks**: 4
**Estimated Time**: 2 hours

**Execution Order**:
1. G.3: Traceability matrix
2. G.6: README update
3. G.8: Compliance report
4. G.10: Final code review

---

## Quick Start Scripts

### Script 1: Setup Environment
```bash
#!/bin/bash
# setup-phase2.sh

set -e

echo "Setting up Phase II environment..."

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
cp .env.example .env
echo "⚠️  Edit backend/.env with your DATABASE_URL and JWT_SECRET_KEY"
cd ..

# Frontend setup
cd frontend
npm install
cp .env.example .env.local
cd ..

echo "✅ Environment setup complete"
echo "Next: Configure backend/.env, then run ./run-phase2.sh"
```

### Script 2: Run Development Servers
```bash
#!/bin/bash
# run-phase2.sh

set -e

echo "Starting Phase II development servers..."

# Start backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"
cd ..

# Start frontend
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"
cd ..

echo ""
echo "✅ Servers running:"
echo "   Backend:  http://localhost:8000 (OpenAPI: /docs)"
echo "   Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"

# Trap Ctrl+C to kill both processes
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT

# Wait for both processes
wait
```

### Script 3: Run All Tests
```bash
#!/bin/bash
# test-phase2.sh

set -e

echo "Running Phase II test suite..."

# Backend tests
echo "=== Backend Tests ==="
cd backend
source venv/bin/activate
pytest --cov=app --cov-report=term-missing --cov-report=html -v
cd ..

# Frontend tests
echo "=== Frontend Tests ==="
cd frontend
npm test -- --coverage --watchAll=false
cd ..

echo "✅ All tests complete"
echo "Coverage reports:"
echo "   Backend:  backend/htmlcov/index.html"
echo "   Frontend: frontend/coverage/lcov-report/index.html"
```

---

## Troubleshooting Guide

### Issue: Database connection fails
**Symptoms**: `sqlalchemy.exc.OperationalError` or connection refused
**Solutions**:
```bash
# Check DATABASE_URL format
echo $DATABASE_URL

# Test PostgreSQL connection
psql $DATABASE_URL -c "SELECT 1"

# For Neon: Ensure SSL mode is included
# postgresql://user:pass@host/db?sslmode=require
```

### Issue: JWT errors (401 Unauthorized)
**Symptoms**: All API calls return 401
**Solutions**:
```bash
# Verify JWT_SECRET_KEY is set
cd backend && source venv/bin/activate
python -c "from app.config import settings; print(settings.JWT_SECRET_KEY)"

# Generate new secret if needed
openssl rand -hex 32

# Test token creation
python -c "from app.auth.jwt import create_access_token; print(create_access_token('test'))"
```

### Issue: CORS errors in browser console
**Symptoms**: "Access to fetch blocked by CORS policy"
**Solutions**:
```bash
# Verify CORS middleware in backend/main.py
grep -A 5 "CORSMiddleware" backend/main.py

# Verify FRONTEND_URL matches
# Backend .env should have: FRONTEND_URL=http://localhost:3000
# No trailing slash

# Test CORS with curl
curl -X OPTIONS http://localhost:8000/health \
  -H "Origin: http://localhost:3000" \
  -v 2>&1 | grep "Access-Control"
```

### Issue: Frontend can't connect to backend
**Symptoms**: Network errors, timeout
**Solutions**:
```bash
# Verify backend is running
curl http://localhost:8000/health

# Verify NEXT_PUBLIC_API_URL
cd frontend
cat .env.local | grep NEXT_PUBLIC_API_URL

# Should be: NEXT_PUBLIC_API_URL=http://localhost:8000
# (no trailing slash)

# Check browser network tab for actual request URL
```

### Issue: Alembic migration fails
**Symptoms**: `alembic upgrade head` errors
**Solutions**:
```bash
cd backend
source venv/bin/activate

# Check current revision
alembic current

# See migration history
alembic history

# Manually inspect migration file
cat alembic/versions/<migration_file>.py

# Drop all tables and re-migrate (DEVELOPMENT ONLY)
python -c "from app.database import engine; from sqlmodel import SQLModel; SQLModel.metadata.drop_all(engine)"
alembic upgrade head
```

---

## Checkpoint Validation Commands

### After Phase A
```bash
./scripts/validate-phase-a.sh
```

### After Phase D (Backend Complete)
```bash
cd backend
source venv/bin/activate

# Test all endpoints
pytest tests/ -v

# Manual API testing
./scripts/test-api-manually.sh
```

### After Phase E (Frontend Complete)
```bash
cd frontend

# Test compilation
npm run build

# Run component tests
npm test

# Start and manually verify
npm run dev
# Navigate to http://localhost:3000 and test full flow
```

### Before Final Submission
```bash
# Run complete test suite
./test-phase2.sh

# Run security audit
cd backend
python -c "from scripts.security_audit import run_audit; run_audit()"

# Generate compliance report
./scripts/generate-compliance-report.sh

# Final validation
./scripts/final-validation.sh
```

---

## Success Criteria Checklist

Before marking Phase II complete:

### Functional Requirements
- [ ] All 40 functional requirements (FR-001 to FR-040) implemented
- [ ] All requirements traceable in traceability.md

### User Stories
- [ ] User Story 1: Registration and first todo (E2E test passes)
- [ ] User Story 2: CRUD operations (E2E test passes)
- [ ] User Story 3: Multi-device access (manual test)
- [ ] User Story 4: Data isolation (security test passes)
- [ ] User Story 5: Error handling (manual test)

### Technical Validation
- [ ] Backend test coverage ≥ 80%
- [ ] Frontend test coverage ≥ 70%
- [ ] All E2E tests pass
- [ ] Security audit shows no critical vulnerabilities
- [ ] Performance: All endpoints < 300ms (p95)
- [ ] Database migrations work (up and down)

### Documentation
- [ ] README.md updated with Phase II instructions
- [ ] 5 ADRs created in history/adr/
- [ ] Traceability matrix complete
- [ ] Security audit report complete
- [ ] Hackathon compliance report complete
- [ ] Implementation PHR created

### Phase Discipline
- [ ] No Phase III+ features implemented
- [ ] No OAuth (deferred to Phase III)
- [ ] No real-time features (deferred to Phase III)
- [ ] No notifications (deferred to Phase IV)

### Quality Gates
- [ ] No console.log or print() in production code
- [ ] No hardcoded secrets or credentials
- [ ] All TODO comments resolved
- [ ] Code formatted (Black, Prettier)
- [ ] Type checking passes (mypy, tsc --noEmit)
- [ ] Linting passes (ruff, eslint)

---

## Final Submission Checklist

- [ ] All 50 tasks marked complete in tasks.md
- [ ] Git commits follow conventional format
- [ ] Branch 002-fullstack-web-app ready for PR
- [ ] README reflects current state
- [ ] All documentation in specs/002-fullstack-web-app/ complete
- [ ] Demo video/screenshots prepared (optional)
- [ ] Deployment instructions documented (optional for Phase II)

---

**Execution Status**: Ready
**Estimated Total Time**:
- Sequential: 15-20 hours
- Parallel (optimal): 6-8 hours
- With automation scripts: 4-6 hours

**Next Command**: Begin with Phase A using detailed guide in [implementation-execution-plan.md](./implementation-execution-plan.md)
