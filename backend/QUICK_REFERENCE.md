# Backend Docker - Quick Reference

## Build Commands

```bash
# Build image
cd backend
docker build -t todo-backend:v1.0.0 -t todo-backend:latest .

# Check image
docker images | grep todo-backend
```

## Local Testing

```bash
# Run container
docker run -d --name todo-backend-test \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  -e JWT_SECRET_KEY="your-32-char-secret-key-here" \
  -e FRONTEND_URL="http://localhost:3000" \
  -e OPENAI_API_KEY="sk-your-key" \
  todo-backend:v1.0.0

# Test health
curl http://localhost:8000/health

# View logs
docker logs todo-backend-test

# Clean up
docker stop todo-backend-test && docker rm todo-backend-test
```

## Minikube

```bash
# Load image
minikube image load todo-backend:v1.0.0
minikube image load todo-backend:latest

# Verify
minikube image ls | grep todo-backend
```

## Image Info

- **Size**: 140MB (compressed)
- **Port**: 8000
- **Health**: /health
- **User**: UID 1000 (non-root)
- **Base**: python:3.11-slim

## Required Environment Variables

```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
JWT_SECRET_KEY=<min-32-chars>
OPENAI_API_KEY=sk-...
FRONTEND_URL=http://frontend:3000
```

## Files

- **Dockerfile**: `/backend/Dockerfile`
- **.dockerignore**: `/backend/.dockerignore`
- **Build Guide**: `/backend/DOCKER_BUILD_GUIDE.md`
