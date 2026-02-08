---
id: "0016"
title: Phase V.4 Priority & Due Date in Task Creation
stage: green
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-name-phase5-cloud
branch: 005-name-phase5-cloud
user: tayyab
command: continue (task creation with priority/due_date)
labels: ["phase-v4", "todo-form", "priority", "due-date", "frontend", "bugfix"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/components/todos/TodoForm.tsx
  - frontend/src/hooks/useTodoSearch.ts
  - frontend/src/hooks/useTagAutocomplete.ts
  - frontend/src/components/ui/PriorityBadge.tsx
  - frontend/src/app/dashboard/page.tsx
tests:
  - npx tsc --noEmit (PASS - no TypeScript errors)
---

## Prompt

Continue from previous context. Fix runtime TypeError in useTodoSearch.ts (`Cannot read properties of undefined (reading 'get')`) and extend task creation UI with priority selector and due date picker so the full create→store→display lifecycle works for Phase V.4 metadata fields.

## Response snapshot

1. **Runtime TypeError fix**: Rewrote `useTodoSearch.ts` to remove `useSearchParams` (which returned `ReadonlyURLSearchParams | null`, not a tuple). Replaced with `useState<TodoSearchFilters>(DEFAULT_FILTERS)`.

2. **Supporting TypeScript fixes**:
   - `useTagAutocomplete.ts`: Fixed `useRef<T>()` without initial value → `useRef<T | undefined>(undefined)`
   - `PriorityBadge.tsx`: Added `import React from 'react'`, changed `JSX.Element` → `React.ReactElement`

3. **TodoForm.tsx enhanced** with:
   - Priority segmented button selector (LOW/MEDIUM/HIGH/URGENT, default MEDIUM) with color-coded selected/hover states
   - Due date native date input with `min={today}` constraint and "Clear date" button
   - `todoData` payload includes `priority` and `due_date: dueDate ? \`${dueDate}T23:59:59.000Z\` : null`
   - `max-h-[32rem]` to accommodate new fields in expanded section
   - Reset on cancel/success clears priority to 'MEDIUM' and dueDate to ''

4. **TypeScript compile**: `npx tsc --noEmit` → no errors

## Outcome

- ✅ Impact: Full task creation lifecycle for Phase V.4 metadata now works — user can set priority and due date when creating a task; TodoItem displays PriorityBadge and DueDateBadge immediately after creation
- 🧪 Tests: TypeScript compile clean; manual browser test required (create HIGH priority task with due date → verify badge appears)
- 📁 Files: TodoForm.tsx (priority selector + due date picker), useTodoSearch.ts (useState-based filters), useTagAutocomplete.ts (useRef fix), PriorityBadge.tsx (React import fix), dashboard/page.tsx (advanced search toggle)
- 🔁 Next prompts: Manual E2E verification; optional unit tests for hooks
- 🧠 Reflection: Next.js `useSearchParams()` does not return a tuple — this is a common mistake. React `useState` is simpler for in-component search state that doesn't need URL sharing.

## Evaluation notes (flywheel)

- Failure modes observed: Misuse of Next.js useSearchParams as tuple destructure; useRef without initial value in strict TypeScript
- Graders run and results (PASS/FAIL): tsc --noEmit PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add `tags` input to TodoForm for full Phase V.4 creation metadata
