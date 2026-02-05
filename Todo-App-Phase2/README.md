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

- **User Authentication** (JWT + OAuth)
- **Todo CRUD Operations** (Create, Read, Update, Delete)
- **PostgreSQL Persistence** (Neon Serverless Database)
- **NO AI/Chatbot Features** (Phase 3 is deployed separately)

## Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (JWT)
- `POST /api/auth/google/callback` - Google OAuth
- `POST /api/auth/github/callback` - GitHub OAuth

### Todos
- `GET /api/{user_id}/tasks` - List user's todos
- `POST /api/{user_id}/tasks` - Create new todo
- `PUT /api/{user_id}/tasks/{task_id}` - Update todo
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete todo

### Documentation
- `GET /health` - Health check
- `GET /docs` - Interactive Swagger UI
- `GET /redoc` - ReDoc documentation

## Environment Variables

Set these in Space Settings → Variables:

- `DATABASE_URL` - PostgreSQL connection string (required)
- `JWT_SECRET_KEY` - JWT signing key, min 32 chars (required)
- `FRONTEND_URL` - Your Vercel frontend URL (required for CORS)
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` - Google OAuth (optional)
- `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` - GitHub OAuth (optional)

## Architecture

**Phase 2 (This Space)**: Traditional REST API
**Phase 3 (Separate Space)**: AI-Powered Chatbot with OpenAI

Both backends are independent deployments.

## Tech Stack

- **Framework**: FastAPI 0.115.0
- **Database**: PostgreSQL (via SQLModel)
- **Auth**: JWT (python-jose) + OAuth
- **Server**: Uvicorn on port 7860
- **Python**: 3.11+

---

**Deployment**: Hugging Face Spaces (Docker)
**Version**: 2.0.0
**Phase**: Phase 2 - Traditional REST
