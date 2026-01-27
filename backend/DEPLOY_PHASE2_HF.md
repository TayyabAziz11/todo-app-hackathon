# Phase 2 Backend Deployment on Hugging Face Spaces

## Overview

This document explains how to deploy **Phase 2 (Traditional REST API)** as a **separate** Hugging Face Space.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Vercel)                        │
│                 https://your-app.vercel.app                  │
└────────────────┬─────────────────────┬──────────────────────┘
                 │                     │
                 │                     │
    ┌────────────▼─────────────┐     ┌▼──────────────────────┐
    │   Phase 2 Backend        │     │  Phase 3 Backend      │
    │   (HF Spaces - NEW)      │     │  (HF Spaces - EXISTS) │
    │                          │     │                       │
    │ - Auth (JWT + OAuth)     │     │ - AI Chatbot          │
    │ - Todo CRUD              │     │ - OpenAI GPT-4        │
    │ - PostgreSQL             │     │ - MCP Tools           │
    │                          │     │                       │
    │ URL: TBD after deploy    │     │ URL: already deployed │
    └──────────────────────────┘     └───────────────────────┘
```

**Key Points:**
- ✅ Phase 2 and Phase 3 are **SEPARATE** deployments
- ✅ Phase 2 does NOT require OpenAI API keys
- ✅ Phase 3 deployment remains untouched
- ✅ Frontend connects to Phase 2 for traditional REST operations

---

## Prerequisites

1. **Hugging Face Account**
   - Sign up at: https://huggingface.co/join
   - Create access token: https://huggingface.co/settings/tokens

2. **PostgreSQL Database**
   - Recommended: [Neon.tech](https://neon.tech) (Serverless, free tier)
   - Alternative: [Supabase](https://supabase.com), Railway (if available)
   - You need: Connection string (DATABASE_URL)

3. **JWT Secret**
   - Generate with: `openssl rand -hex 32`
   - Or: `python -c "import secrets; print(secrets.token_hex(32))"`

---

## Step 1: Create Hugging Face Space

1. Go to: https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Configure:
   - **Space name**: `todo-phase2-backend` (or your choice)
   - **License**: Apache 2.0
   - **SDK**: Docker
   - **Hardware**: CPU Basic (free)
   - **Visibility**: Public

4. Click **"Create Space"**

---

## Step 2: Prepare Repository Files

### Option A: Clone and Push (Recommended)

```bash
# Clone your HF Space repo
git clone https://huggingface.co/spaces/YOUR_USERNAME/todo-phase2-backend
cd todo-phase2-backend

# Copy Phase 2 files from your backend directory
cp /path/to/backend/main_phase2.py ./main.py
cp /path/to/backend/requirements_phase2.txt ./requirements.txt
cp /path/to/backend/Dockerfile.phase2 ./Dockerfile
cp /path/to/backend/.dockerignore.phase2 ./.dockerignore

# Copy app directory (all modules)
cp -r /path/to/backend/app ./

# REMOVE Phase 3 modules
rm -rf ./app/agent
rm -rf ./app/mcp
rm -f ./app/routers/chat.py

# Create README
cat > README.md << 'EOF'
---
title: Todo Backend (Phase 2)
emoji: 📝
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Todo API - Phase 2 Backend

Traditional REST API for Todo application with:
- User authentication (JWT + OAuth)
- Todo CRUD operations
- PostgreSQL persistence

**Phase 3 (AI Chatbot)** is deployed separately.

## Endpoints

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/{user_id}/tasks` - List todos
- `POST /api/{user_id}/tasks` - Create todo
- `PUT /api/{user_id}/tasks/{task_id}` - Update todo
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete todo
- `GET /health` - Health check
- `GET /docs` - Swagger UI

## Environment Variables

Set these in Space Settings → Variables:
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - JWT signing key (min 32 chars)
- `FRONTEND_URL` - Your Vercel frontend URL
EOF

# Commit and push
git add .
git commit -m "deploy: Phase 2 backend (Traditional REST API)"
git push
```

### Option B: Use HF Web UI

1. In your Space, click **"Files"**
2. Click **"Add file"** → **"Upload files"**
3. Upload:
   - `main_phase2.py` → rename to `main.py`
   - `requirements_phase2.txt` → rename to `requirements.txt`
   - `Dockerfile.phase2` → rename to `Dockerfile`
   - `.dockerignore.phase2` → rename to `.dockerignore`
   - Entire `app/` directory (except `app/agent/`, `app/mcp/`, `app/routers/chat.py`)

---

## Step 3: Set Environment Variables

1. Go to your Space: `https://huggingface.co/spaces/YOUR_USERNAME/todo-phase2-backend`
2. Click **"Settings"**
3. Scroll to **"Variables and secrets"**
4. Add the following secrets:

### Required Variables

```
Name:  DATABASE_URL
Value: postgresql://user:password@host.neon.tech/database?sslmode=require
```

```
Name:  JWT_SECRET_KEY
Value: <paste your generated 32+ char secret>
```

```
Name:  FRONTEND_URL
Value: https://your-vercel-app.vercel.app
```

### Optional Variables (OAuth)

```
Name:  GOOGLE_CLIENT_ID
Value: <your-google-client-id>
```

```
Name:  GOOGLE_CLIENT_SECRET
Value: <your-google-client-secret>
```

```
Name:  GITHUB_CLIENT_ID
Value: <your-github-client-id>
```

```
Name:  GITHUB_CLIENT_SECRET
Value: <your-github-client-secret>
```

---

## Step 4: Wait for Build

1. Space will automatically build (takes ~5-10 minutes)
2. Monitor logs: Click **"Logs"** tab in your Space
3. Look for:
   ```
   ✓ Installing dependencies
   ✓ Building Docker image
   ✓ Phase 2 Backend starting...
   ✓ Phase 2 Routers registered successfully
   ✓ Application ready on 0.0.0.0:7860
   ```

---

## Step 5: Verify Deployment

### Test Health Endpoint

```bash
curl https://huggingface.co/spaces/YOUR_USERNAME/todo-phase2-backend/health
```

**Expected response:**
```json
{
  "status": "ok",
  "version": "2.0.0",
  "phase": "Phase 2 - Traditional REST"
}
```

### Test Swagger Docs

Visit: `https://huggingface.co/spaces/YOUR_USERNAME/todo-phase2-backend/docs`

**Expected:** Interactive Swagger UI with endpoints:
- `/health`
- `/api/auth/register`
- `/api/auth/login`
- `/api/{user_id}/tasks` (GET, POST, PUT, DELETE)
- **NO** `/api/{user_id}/chat` (that's Phase 3)

---

## Step 6: Update Frontend (Vercel)

1. Go to your Vercel project dashboard
2. Click **"Settings"** → **"Environment Variables"**
3. Update or add:

```
Name:  NEXT_PUBLIC_API_URL
Value: https://huggingface.co/spaces/YOUR_USERNAME/todo-phase2-backend
```

4. Click **"Save"**
5. Go to **"Deployments"** → Click **"Redeploy"** on latest deployment

---

## Step 7: Test End-to-End

1. Visit your Vercel frontend
2. Try:
   - Register new account
   - Login
   - Create todo
   - List todos
   - Update todo
   - Delete todo

**All should work using Phase 2 backend!**

---

## Troubleshooting

### Build Fails

**Error:** `ModuleNotFoundError: No module named 'openai'`

**Fix:** You accidentally included Phase 3 dependencies. Ensure:
- Using `requirements_phase2.txt` (no openai/mcp)
- Dockerfile references `main_phase2.py`
- No `app/agent/` or `app/mcp/` directories
- No `app/routers/chat.py`

### Database Connection Fails

**Error:** `Database initialization failed`

**Fix:**
1. Verify `DATABASE_URL` is set in Space settings
2. Ensure format: `postgresql://user:pass@host:port/db?sslmode=require`
3. Test connection from local machine first
4. Check PostgreSQL provider allows connections from HF Spaces IPs

### CORS Errors

**Error:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Fix:**
1. Verify `FRONTEND_URL` matches your Vercel domain exactly
2. Include protocol: `https://` not just `your-app.vercel.app`
3. Check Space logs for CORS middleware configuration

### Auth Fails

**Error:** `Invalid token` or `Signature verification failed`

**Fix:**
1. Verify `JWT_SECRET_KEY` is set in Space settings
2. Ensure key is at least 32 characters
3. Frontend and backend must use same secret (if frontend validates)

---

## Architecture Diagram

```
Production Deployment:

┌──────────────────────────────────────────────────────────────┐
│  Frontend (Vercel)                                           │
│  https://your-todo-app.vercel.app                            │
│  NEXT_PUBLIC_API_URL → Phase 2 backend URL                   │
└───────────────┬──────────────────────────────────────────────┘
                │
                │ REST API calls
                ▼
┌──────────────────────────────────────────────────────────────┐
│  Phase 2 Backend (HF Spaces)                                 │
│  https://huggingface.co/spaces/YOU/todo-phase2-backend       │
│                                                              │
│  Routes:                                                     │
│  - POST /api/auth/register                                   │
│  - POST /api/auth/login                                      │
│  - GET/POST/PUT/DELETE /api/{user_id}/tasks                  │
│  - GET /health                                               │
│                                                              │
│  Database: Neon PostgreSQL                                   │
│  Auth: JWT (no OpenAI required)                              │
└──────────────────────────────────────────────────────────────┘

Phase 3 Backend (Separate - Already Deployed):
┌──────────────────────────────────────────────────────────────┐
│  https://huggingface.co/spaces/TayyabAziz/Todo-App-Chatbot   │
│  - AI Chatbot with OpenAI                                    │
│  - Not modified by this deployment                           │
└──────────────────────────────────────────────────────────────┘
```

---

## Files Checklist

### Required Files in HF Space Repo

- ✅ `main.py` (from `main_phase2.py`)
- ✅ `requirements.txt` (from `requirements_phase2.txt`)
- ✅ `Dockerfile` (from `Dockerfile.phase2`)
- ✅ `.dockerignore` (from `.dockerignore.phase2`)
- ✅ `README.md` (HF Space metadata)
- ✅ `app/__init__.py`
- ✅ `app/config.py`
- ✅ `app/database.py`
- ✅ `app/models/` (user.py, todo.py)
- ✅ `app/routers/auth.py`
- ✅ `app/routers/todos.py`
- ✅ `app/schemas/` (auth.py, todo.py)
- ✅ `app/auth/` (dependencies.py, jwt.py, password.py)

### Excluded Files (Phase 3 only)

- ❌ `app/agent/`
- ❌ `app/mcp/`
- ❌ `app/routers/chat.py`
- ❌ `app/models/conversation.py`
- ❌ `app/models/message.py`
- ❌ `test_protocol_compliance.py`
- ❌ `test_tool_normalization.py`

---

## Environment Variables Summary

| Variable | Required | Example | Purpose |
|----------|----------|---------|---------|
| `DATABASE_URL` | ✅ Yes | `postgresql://user:pass@host.neon.tech/db?sslmode=require` | PostgreSQL connection |
| `JWT_SECRET_KEY` | ✅ Yes | `abc123...` (32+ chars) | JWT token signing |
| `FRONTEND_URL` | ✅ Yes | `https://your-app.vercel.app` | CORS allowed origin |
| `GOOGLE_CLIENT_ID` | ❌ Optional | `123.apps.googleusercontent.com` | Google OAuth |
| `GOOGLE_CLIENT_SECRET` | ❌ Optional | `GOCSPX-...` | Google OAuth |
| `GITHUB_CLIENT_ID` | ❌ Optional | `Iv1.abc123...` | GitHub OAuth |
| `GITHUB_CLIENT_SECRET` | ❌ Optional | `ghp_...` | GitHub OAuth |
| `APP_ENV` | ❌ Optional | `production` | Environment name |
| `PORT` | ❌ Auto-set | `7860` | HF Spaces port |

---

## Final Verification

After deployment, verify:

- [ ] Space builds successfully (check Logs tab)
- [ ] `/health` returns 200 OK
- [ ] `/docs` shows Swagger UI with Phase 2 endpoints
- [ ] NO `/api/chat` endpoint (that's Phase 3)
- [ ] Database connection works (check logs)
- [ ] Frontend can register/login users
- [ ] Frontend can create/list/update/delete todos
- [ ] Phase 3 chatbot backend still works independently

---

## Maintenance

### Updating Code

```bash
cd todo-phase2-backend
# Make changes to files
git add .
git commit -m "fix: your changes"
git push
# HF Spaces will rebuild automatically
```

### Viewing Logs

1. Go to Space: `https://huggingface.co/spaces/YOU/todo-phase2-backend`
2. Click **"Logs"** tab
3. View real-time application logs

### Restarting Space

1. Go to Space settings
2. Click **"Factory reboot"**
3. Wait ~5 minutes for rebuild

---

## Cost

- **Hugging Face Spaces**: Free (CPU Basic tier)
- **Neon PostgreSQL**: Free tier available (500 MB storage)
- **Vercel Frontend**: Free tier available

**Total cost**: $0/month for development/testing

---

## Security Notes

1. **Never commit** `.env` files with real secrets
2. **Always use** HF Spaces "Variables and secrets" for sensitive data
3. **Rotate** JWT_SECRET_KEY periodically
4. **Use HTTPS** only (HF Spaces provides this automatically)
5. **Set CORS** to specific frontend domain, not `*` in production

---

## Support

- **HF Spaces Docs**: https://huggingface.co/docs/hub/spaces
- **Neon Docs**: https://neon.tech/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com

---

**Deployment Status**: ✅ Ready for production
