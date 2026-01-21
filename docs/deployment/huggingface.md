# Hugging Face Spaces Deployment Guide

**Target Platform**: Hugging Face Spaces
**Backend**: FastAPI + OpenAI Agents SDK + PostgreSQL (Neon)
**Architecture**: Stateless with conversation persistence
**Date**: 2026-01-21

## Overview

This guide walks through deploying the Todo AI Chatbot backend to Hugging Face Spaces with Neon PostgreSQL as the database.

**Why Hugging Face Spaces?**
- Free public hosting with HTTPS
- Automatic SSL/TLS certificates
- Simple deployment via Git push
- Environment variable management in UI
- No credit card required for basic usage

## Prerequisites

Before deploying, ensure you have:

1. **Hugging Face Account**
   - Sign up at https://huggingface.co/join
   - Verify your email address

2. **Neon PostgreSQL Database**
   - Create free account at https://neon.tech/
   - Free tier: 3 databases, 10 GB storage

3. **OpenAI API Key**
   - Create account at https://platform.openai.com/
   - Generate API key from https://platform.openai.com/api-keys
   - Billing must be enabled for API access

4. **Git Repository**
   - Your Todo App code in a Git repository
   - GitHub, GitLab, or Hugging Face repository

## Step 1: Create Neon PostgreSQL Database

### 1.1 Create Database

1. Go to https://console.neon.tech/
2. Click "Create a project"
3. Configure project:
   - **Name**: `todo-ai-chatbot-prod`
   - **Region**: Choose closest to your users (e.g., `us-east-2`)
   - **Postgres version**: 15 or later
4. Click "Create project"

### 1.2 Get Connection String

1. In Neon dashboard, go to your project
2. Navigate to "Connection Details"
3. Copy the connection string:
   ```
   Format: postgresql://user:password@ep-xxx-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
   ```

**IMPORTANT**: The connection string MUST include `?sslmode=require` at the end for SSL encryption.

**Example**:
```
postgresql://neondb_owner:abc123XYZ@ep-cool-dawn-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### 1.3 Initialize Database Schema

The FastAPI app will automatically create tables on first startup via SQLModel. No manual schema setup required.

## Step 2: Create Hugging Face Space

### 2.1 Create New Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Configure Space:
   - **Owner**: Your username or organization
   - **Space name**: `todo-ai-chatbot` (or your preferred name)
   - **License**: Apache 2.0 (recommended)
   - **SDK**: Choose **"Docker"** (NOT Gradio or Streamlit)
   - **Space hardware**: CPU basic (free tier is sufficient)
   - **Visibility**: Public or Private (your choice)

4. Click "Create Space"

### 2.2 Clone Space Repository

After creation, clone your Space repository:

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/todo-ai-chatbot
cd todo-ai-chatbot
```

### 2.3 Copy Backend Files

Copy your backend code to the Space repository:

```bash
# From your Todo App repository root:
cp -r backend/* todo-ai-chatbot/backend/
cp app.py todo-ai-chatbot/
cp requirements.txt todo-ai-chatbot/  # If you have one at root
```

### 2.4 Create Dockerfile (If Not Using app.py)

If you prefer Docker deployment, create a `Dockerfile` in the Space root:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ backend/
COPY app.py app.py

# Expose Hugging Face Spaces port
EXPOSE 7860

# Set environment
ENV PORT=7860
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "app.py"]
```

**Note**: If using `app.py` (recommended), Hugging Face will automatically detect and run it without a Dockerfile.

## Step 3: Configure Environment Variables

### 3.1 Access Space Settings

1. Go to your Space page on Hugging Face
2. Click "Settings" tab
3. Scroll to "Repository secrets" section

### 3.2 Add Required Environment Variables

Click "New secret" and add each of the following:

#### Required Secrets

| Variable | Value | Example |
|----------|-------|---------|
| `DATABASE_URL` | Neon connection string from Step 1.2 | `postgresql://user:pass@ep-...neon.tech/db?sslmode=require` |
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-proj-abc123...` |
| `JWT_SECRET_KEY` | Random 64-char hex string | Generate: `openssl rand -hex 32` |
| `FRONTEND_URL` | Your frontend URL | `https://your-app.vercel.app` or `http://localhost:3000` |
| `APP_ENV` | Environment name | `production` |

#### Optional Secrets

| Variable | Value | Default |
|----------|-------|---------|
| `PORT` | Server port | `7860` (HF Spaces default) |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_EXPIRE_MINUTES` | Token expiry | `15` |

### 3.3 Generate JWT Secret

**On macOS/Linux**:
```bash
openssl rand -hex 32
```

**On Windows (PowerShell)**:
```powershell
[System.Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
```

**On Python**:
```python
import secrets
print(secrets.token_hex(32))
```

### 3.4 Verify Environment Variables

After adding all secrets:
1. Scroll down and click "Save"
2. Verify all required variables are listed
3. Space will automatically restart with new configuration

## Step 4: Deploy to Hugging Face Spaces

### 4.1 Commit and Push

```bash
# From your Space repository
git add .
git commit -m "Initial deployment: Todo AI Chatbot backend"
git push
```

### 4.2 Monitor Deployment

1. Go to your Space page
2. Watch the "Logs" section for build progress
3. Wait for "Running" status (usually 1-3 minutes)

**Expected log output**:
```
Starting server on 0.0.0.0:7860
INFO:     Application starting...
INFO:     Initializing database...
INFO:     ✓ Routers registered successfully
INFO:     Application ready to serve requests
INFO:     Uvicorn running on http://0.0.0.0:7860
```

### 4.3 Test Deployment

Once running, your Space will be available at:
```
https://huggingface.co/spaces/YOUR_USERNAME/todo-ai-chatbot
```

Test the health endpoint:
```bash
curl https://YOUR_USERNAME-todo-ai-chatbot.hf.space/health
```

**Expected response**:
```json
{
  "status": "ok",
  "version": "3.0.0"
}
```

## Step 5: Database Connection Validation

### 5.1 Verify SSL Connection

Check that your Neon connection string includes SSL:

```python
# In Python shell or test script
from sqlmodel import create_engine

DATABASE_URL = "your_neon_connection_string"

# Should include sslmode=require
assert "sslmode=require" in DATABASE_URL, "SSL mode not enabled!"

# Test connection
engine = create_engine(DATABASE_URL, echo=True)
with engine.connect() as conn:
    result = conn.execute("SELECT version()")
    print(result.fetchone())
```

### 5.2 Verify Tables Created

After first deployment, tables should be auto-created:

```sql
-- Connect to Neon database via SQL Editor
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';
```

**Expected tables**:
- `user`
- `todo`
- `conversation`
- `message`

## Step 6: Test Chat API Endpoint

### 6.1 Create Test User (Optional)

If using authentication:

```bash
# POST to /api/auth/register
curl -X POST https://YOUR_USERNAME-todo-ai-chatbot.hf.space/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123",
    "name": "Test User"
  }'
```

### 6.2 Test Chat Endpoint

```bash
# Replace {user_id} with actual user ID
# Replace {jwt_token} with actual JWT token

curl -X POST https://YOUR_USERNAME-todo-ai-chatbot.hf.space/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries"
  }'
```

**Expected response**:
```json
{
  "message": "I've added 'Buy groceries' to your task list.",
  "conversation_id": "uuid-here",
  "tool_calls": [
    {
      "tool": "add_task",
      "input": {"title": "Buy groceries", ...},
      "result": {"success": true, ...}
    }
  ],
  "finish_reason": "stop"
}
```

### 6.3 Test MCP Tools

Test each MCP tool:

**List Tasks**:
```json
{"message": "Show my tasks"}
```

**Update Task**:
```json
{"message": "Change task 1 to Buy organic groceries"}
```

**Complete Task**:
```json
{"message": "Mark task 1 as done"}
```

**Delete Task**:
```json
{"message": "Delete task 1"}
```

## Step 7: Validate Stateless Resume

### 7.1 Test Conversation Persistence

1. Send initial message and note `conversation_id`
2. Send second message with same `conversation_id`
3. Agent should remember context from first message

**Request 1**:
```json
{
  "message": "Add a task to buy milk"
}
```

**Response 1**:
```json
{
  "conversation_id": "abc-123-def"
}
```

**Request 2** (with conversation_id):
```json
{
  "message": "Mark it as done",
  "conversation_id": "abc-123-def"
}
```

**Expected**: Agent knows "it" refers to the milk task from Request 1.

### 7.2 Test Restart Resume

1. Note `conversation_id` from a conversation
2. Restart the Space (Settings > Factory reboot)
3. Send new message with same `conversation_id`
4. Agent should retrieve full conversation history from database

## Troubleshooting

### Common Issues

#### 1. Database Connection Fails

**Error**: `could not connect to server`

**Solutions**:
- Verify DATABASE_URL includes `?sslmode=require`
- Check Neon database is active (not paused)
- Verify connection string credentials are correct
- Check Neon project region is accessible

#### 2. OpenAI API Errors

**Error**: `AuthenticationError: Invalid API key`

**Solutions**:
- Verify OPENAI_API_KEY is correct
- Check billing is enabled on OpenAI account
- Ensure API key has not expired
- Test key with curl: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

#### 3. Port Binding Issues

**Error**: `Address already in use`

**Solutions**:
- Ensure PORT environment variable is set to 7860
- Check no other process is using port 7860
- Restart the Space

#### 4. CORS Errors

**Error**: `No 'Access-Control-Allow-Origin' header`

**Solutions**:
- Verify FRONTEND_URL is set correctly
- Check CORS middleware configuration in main.py
- Ensure frontend URL matches exactly (no trailing slash)

#### 5. JWT Validation Fails

**Error**: `Invalid token`

**Solutions**:
- Verify JWT_SECRET_KEY is set
- Ensure secret is at least 32 characters
- Check token expiry (default 15 minutes)

### View Logs

Access deployment logs:
1. Go to your Space page
2. Click "Logs" tab
3. Filter by severity: Info, Warning, Error

### Manual Database Connection Test

Test Neon connection from local machine:

```bash
# Install psql (PostgreSQL client)
# On macOS: brew install postgresql
# On Ubuntu: sudo apt install postgresql-client

# Connect to Neon
psql "postgresql://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require"

# Once connected:
\dt  # List tables
SELECT * FROM "user" LIMIT 5;  # Query users
\q  # Quit
```

## Performance Optimization

### 1. Database Connection Pooling

SQLModel automatically uses connection pooling. Verify in logs:
```
INFO:     Database connection pool initialized
```

### 2. Neon Autoscaling

Neon automatically scales compute based on usage. No configuration needed.

### 3. OpenAI Rate Limits

Monitor OpenAI usage:
- Dashboard: https://platform.openai.com/usage
- Set usage limits to avoid unexpected charges
- Consider caching frequent queries

### 4. Space Hardware

Upgrade Space hardware if needed:
- Settings > Space hardware
- Options: CPU basic (free), CPU upgrade ($0.03/hr), GPU (higher cost)
- Free tier is sufficient for moderate usage

## Security Best Practices

### 1. Environment Variables

✅ **DO**:
- Use Hugging Face Spaces secrets for all sensitive data
- Rotate JWT_SECRET_KEY periodically
- Use strong random values for secrets

❌ **DON'T**:
- Commit secrets to Git
- Share API keys publicly
- Use weak/predictable secrets

### 2. Database Access

✅ **DO**:
- Use SSL/TLS (sslmode=require)
- Use Neon's built-in connection pooling
- Implement user ownership validation in MCP tools

❌ **DON'T**:
- Expose DATABASE_URL publicly
- Disable SSL for performance
- Allow unauthenticated database access

### 3. API Security

✅ **DO**:
- Require JWT authentication for all endpoints
- Validate user_id matches token claims
- Implement rate limiting if needed

❌ **DON'T**:
- Accept unauthenticated requests
- Trust user_id from request body without validation
- Log sensitive data (passwords, tokens)

## Monitoring and Maintenance

### Health Checks

Set up automated health checks:

```bash
# Cron job or monitoring service
*/5 * * * * curl -f https://YOUR_USERNAME-todo-ai-chatbot.hf.space/health || echo "Health check failed"
```

### Database Backups

Neon provides automatic backups:
- Settings > Backups
- Point-in-time recovery available
- Download backups for local storage

### Update Deployment

To update your deployment:

```bash
# Make changes to code
git add .
git commit -m "Update: your changes"
git push

# Hugging Face automatically rebuilds and deploys
```

### Rollback

If deployment fails:

1. Go to Space Settings
2. Click "Factory reboot" to restart with last known good state
3. Or revert Git commit and push:
   ```bash
   git revert HEAD
   git push
   ```

## Cost Estimate

### Free Tier Usage

**Hugging Face Spaces** (Free):
- CPU basic hardware
- Unlimited public spaces
- 16 GB storage
- No credit card required

**Neon PostgreSQL** (Free):
- 3 databases
- 10 GB storage per database
- Unlimited compute hours (with auto-pause)
- No credit card required for free tier

**OpenAI API** (Paid):
- GPT-4: ~$0.03 per 1K tokens
- Typical chat: 500-1000 tokens per request
- Estimate: $0.015-0.03 per chat interaction
- **Monthly cost**: $5-50 depending on usage

**Total estimated cost**: $5-50/month (OpenAI only, HF Spaces + Neon are free)

## Support and Resources

### Documentation

- **Hugging Face Spaces**: https://huggingface.co/docs/hub/spaces
- **Neon PostgreSQL**: https://neon.tech/docs
- **FastAPI**: https://fastapi.tiangolo.com/
- **OpenAI Agents SDK**: https://platform.openai.com/docs/guides/agents

### Community

- **Hugging Face Discord**: https://huggingface.co/join/discord
- **Neon Community**: https://community.neon.tech/
- **OpenAI Forum**: https://community.openai.com/

### Troubleshooting Help

If you encounter issues:
1. Check deployment logs in Hugging Face Spaces
2. Verify all environment variables are set
3. Test database connection from local machine
4. Review this deployment guide
5. Open an issue in the project repository

## Conclusion

Your Todo AI Chatbot backend is now deployed on Hugging Face Spaces with:

✅ Free public HTTPS endpoint
✅ PostgreSQL database (Neon)
✅ OpenAI agent integration
✅ Stateless conversation management
✅ All 5 MCP tools (add, list, update, complete, delete)

**Next Steps**:
1. Deploy frontend to Vercel
2. Update FRONTEND_URL environment variable
3. Configure CORS for production frontend
4. Test end-to-end from frontend UI
5. Monitor usage and costs
