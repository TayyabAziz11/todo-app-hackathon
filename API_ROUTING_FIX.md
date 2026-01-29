# Frontend-Backend API Routing Fix

## Problem
Frontend was calling relative routes like `/api/auth/login`, causing Next.js to return 404 errors because it tried to resolve them as Next.js API routes instead of proxying to the FastAPI backend.

## Root Cause
Environment variable name mismatch:
- **Code Expected:** `NEXT_PUBLIC_API_BASE_URL`
- **`.env.local` Had:** `NEXT_PUBLIC_API_URL` ❌
- **`next.config.ts` Had:** `NEXT_PUBLIC_API_URL` ❌

Result: `API_BASE_URL` was empty, causing all API calls to use relative paths.

## Solution

### 1. Fixed Environment Variables
**File: `frontend/.env.local`**
```bash
# Before
NEXT_PUBLIC_API_URL=http://localhost:8000

# After
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

**File: `frontend/next.config.ts`**
```typescript
// Before
env: {
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
}

// After
env: {
  NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
}
```

### 2. Architecture Verification
✅ **No Next.js API routes** - All API calls go directly to FastAPI backend
✅ **Centralized API client** - `frontend/src/lib/api.ts` handles all requests
✅ **Single base URL system** - All endpoints use `${API_BASE_URL}/api/*`
✅ **CORS configured** - Backend allows `http://localhost:3000`

### 3. Backend Routes Verified
```
GET  /health           → {"status":"ok","version":"3.0.0"}
GET  /docs             → Swagger UI
POST /api/auth/login   → JWT authentication
POST /api/auth/register → User registration
GET  /api/{user_id}/tasks → List todos
POST /api/{user_id}/tasks → Create todo
PUT  /api/{user_id}/tasks/{id} → Update todo
DELETE /api/{user_id}/tasks/{id} → Delete todo
POST /api/{user_id}/chat → AI chatbot
```

## Production Deployment

### Vercel (Frontend)
Set environment variable:
```
NEXT_PUBLIC_API_BASE_URL=https://tayyabaziz-todo-app-phase2.hf.space
```

### Hugging Face (Backend)
CORS already configured for production:
```python
cors_origins = [
    "https://todo-app-hackathon-mytask.vercel.app",
    "http://localhost:3000"
]
```

## Testing
✅ Backend health check works
✅ Auth endpoints functional
✅ CORS headers correct
✅ Swagger docs accessible
✅ No Next.js API route conflicts

## Files Modified
1. `frontend/.env.local` - Fixed variable name (not committed)
2. `frontend/next.config.ts` - Fixed variable name (committed)
3. No code changes needed (API helpers already correct)

## Commit
```
Commit: a07e2dc
Message: "fix: frontend-backend API routing via base URL"
```
