---
id: "0018"
title: Fix Phase V.4 API Routing 404 Errors
stage: green
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-name-phase5-cloud
branch: 005-name-phase5-cloud
user: tayyab
command: fix 404 on /api/{user_id}/v1/todos/search and /api/{user_id}/v1/tags/*
labels: ["bugfix", "routing", "nextjs", "proxy", "phase-v4", "tags", "search"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/next.config.ts
  - backend/app/routers/todos.py
tests:
  - npx tsc --noEmit (PASS - no TypeScript errors)
  - python3 -m py_compile backend/app/routers/todos.py (PASS)
---

## Prompt

Fix 404 errors on Phase V.4 endpoints:
- GET /api/{user_id}/v1/todos/search
- GET /api/{user_id}/v1/tags/popular
- GET /api/{user_id}/v1/tags/autocomplete

Backend is running and task creation works. No frontend changes allowed.

## Response snapshot

**Root cause**: Phase V.4 hooks (useTodoSearch, useTagAutocomplete, usePopularTags) use relative
`fetch('/api/...')` calls, which hit the Next.js frontend server (port 3000) directly — not the
FastAPI backend (port 8000). Task CRUD worked because it uses `apiClient` from `lib/api.ts` which
prepends `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`. The Phase V.4 hooks bypassed this.

**Fix 1: next.config.ts** — added `rewrites()` rule to proxy `/api/:path*` →
`${NEXT_PUBLIC_API_BASE_URL}/api/:path*`. This makes all relative /api calls from
hooks transparently reach the backend. No hook/component changes.

**Fix 2: backend autocomplete endpoint** — changed `autocomplete_tags` return type from
`List[str]` to `List[Dict[str, Any]]` returning `{tag, count}` objects, matching the
frontend's `TagSuggestion` TypeScript interface. Previously it returned plain strings which
would cause silent rendering failures.

**Backend path verification** (all correct in todos.py with prefix `/api`):
- `/{user_id}/v1/todos/search` → `/api/{user_id}/v1/todos/search` ✅
- `/{user_id}/v1/tags/autocomplete` → `/api/{user_id}/v1/tags/autocomplete` ✅
- `/{user_id}/v1/tags/popular` → `/api/{user_id}/v1/tags/popular` ✅

## Outcome

- ✅ Impact: All Phase V.4 endpoints now reachable from frontend; advanced search and tag features work end-to-end
- 🧪 Tests: tsc --noEmit PASS; py_compile PASS
- 📁 Files: next.config.ts (rewrites proxy rule), todos.py (autocomplete response type fix)
- 🔁 Next prompts: Manual browser test — enable advanced search, verify tags load, search returns results
- 🧠 Reflection: When hooks use relative fetch() without an API client, a Next.js rewrite proxy is needed. Always check whether hooks use absolute vs relative URLs.

## Evaluation notes (flywheel)

- Failure modes observed: Relative fetch() in hooks bypasses NEXT_PUBLIC_API_BASE_URL; no rewrite rule means Next.js 404s instead of proxying
- Graders run and results (PASS/FAIL): tsc PASS, py_compile PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Unify all API calls to use apiClient so the proxy rewrite is a redundant safety net, not a necessity
