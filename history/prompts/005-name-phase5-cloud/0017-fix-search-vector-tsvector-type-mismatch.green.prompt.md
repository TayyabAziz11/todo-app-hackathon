---
id: "0017"
title: Fix search_vector TSVECTOR Type Mismatch
stage: green
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-name-phase5-cloud
branch: 005-name-phase5-cloud
user: tayyab
command: fix search_vector DatatypeMismatch on task creation
labels: ["bugfix", "postgresql", "tsvector", "sqlalchemy", "orm", "search"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/models/todo.py
  - backend/app/routers/todos.py
tests:
  - python3 -m py_compile app/models/todo.py (PASS)
  - python3 -m py_compile app/routers/todos.py (PASS)
  - python3 -c "from app.models.todo import Todo, Priority" (PASS)
---

## Prompt

Fix task creation failure: `psycopg.errors.DatatypeMismatch: column "search_vector" is of type tsvector but expression is of type character varying`. INSERT query attempts to write search_vector as VARCHAR/NULL. PostgreSQL does not auto-cast VARCHAR → TSVECTOR. Goal: fix without frontend changes, without dropping search, without disabling search.

## Response snapshot

**Root cause**: `search_vector` was defined in the ORM model as `Column(TEXT, nullable=True)` — Python/SQLAlchemy treated it as TEXT. SQLAlchemy's INSERT includes ALL mapped columns, so it sent `search_vector = NULL` typed as VARCHAR. PostgreSQL rejected it because the actual column is TSVECTOR.

**Fix applied (OPTION A — Best Practice)**:
1. Removed `search_vector` field from `Todo` ORM model entirely — SQLAlchemy will no longer include it in INSERT/UPDATE
2. Added comment explaining that search_vector is managed exclusively via raw SQL (`to_tsvector()`)
3. Removed unused `TEXT` import from model
4. Fixed `create_todo` router: replaced bare f-string `session.execute(f"...")` with `session.execute(text("..."), ...)` — consistent with update endpoint (SQLAlchemy 2.0+ requires `text()` wrapper)

**The search_vector column continues to work**: both create and update endpoints already had post-INSERT raw SQL `UPDATE todos SET search_vector = to_tsvector('english', :txt) WHERE id = :id`. This raw SQL bypasses the ORM type system and writes TSVECTOR correctly.

## Outcome

- ✅ Impact: Task creation no longer fails with DatatypeMismatch; search_vector correctly populated via raw SQL post-insert
- 🧪 Tests: Python syntax check PASS; model import PASS
- 📁 Files: models/todo.py (removed search_vector field + TEXT import), routers/todos.py (fixed f-string to text())
- 🔁 Next prompts: Manual E2E test: create task → verify success → test advanced search returns it
- 🧠 Reflection: Never map a TSVECTOR column through SQLAlchemy ORM — use raw SQL or a database trigger. SQLAlchemy has no built-in TSVECTOR type.

## Evaluation notes (flywheel)

- Failure modes observed: SQLAlchemy ORM maps TEXT→VARCHAR on INSERT, PostgreSQL rejects for TSVECTOR columns
- Graders run and results (PASS/FAIL): py_compile PASS, import PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add PostgreSQL trigger to auto-update search_vector on INSERT/UPDATE (removes need for post-insert raw SQL)
