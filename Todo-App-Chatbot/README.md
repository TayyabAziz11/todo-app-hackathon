---
title: Todo App Backend API
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# Todo App Backend - AI-Powered Task Management API

FastAPI backend for an AI-powered todo application with natural language processing capabilities.

## Features

- 🤖 **AI Chatbot** - Natural language task management via OpenAI
- 🔧 **MCP Tools** - 5 specialized tools (add, list, update, complete, delete tasks)
- 🔐 **JWT Authentication** - Secure user management
- 💾 **PostgreSQL** - Persistent data storage with SQLModel
- 📡 **RESTful API** - Complete CRUD operations
- 🎯 **Stateless Architecture** - Horizontally scalable

## Environment Variables

Set these in Hugging Face Space Settings → Variables:

```
DATABASE_URL=postgresql://user:password@host:port/dbname
JWT_SECRET_KEY=your-secret-key-min-32-chars
OPENAI_API_KEY=sk-your-openai-api-key
FRONTEND_URL=https://your-frontend-url.vercel.app
```

## Endpoints

### Health Check
- `GET /health` - Server health status

### Authentication
- `POST /auth/register` - Create new user
- `POST /auth/login` - User login (returns JWT)

### Todos
- `GET /api/todos` - List all todos
- `POST /api/todos` - Create todo
- `PUT /api/todos/{id}` - Update todo
- `DELETE /api/todos/{id}` - Delete todo

### AI Chat
- `POST /api/{user_id}/chat` - Chat with AI assistant

## Tech Stack

- **Framework**: FastAPI 0.115+
- **Database**: PostgreSQL + SQLModel
- **AI**: OpenAI GPT-4 + MCP Protocol
- **Auth**: JWT (python-jose)

## Frontend

The frontend is deployed separately on Vercel. Set `NEXT_PUBLIC_API_URL` in Vercel to point to this Space's URL.
