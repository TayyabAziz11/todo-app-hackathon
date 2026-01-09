# Todo App Backend API

FastAPI backend for the Todo application with JWT authentication, PostgreSQL persistence, and OAuth support.

## Tech Stack

- **Framework**: FastAPI 0.115
- **Database**: PostgreSQL with SQLModel ORM
- **Authentication**: JWT tokens + OAuth (Google, GitHub)
- **Server**: Uvicorn ASGI

## Quick Start (Local Development)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your local settings
# At minimum, set:
#   DATABASE_URL=postgresql://user:pass@localhost:5432/todo_db
#   JWT_SECRET_KEY=<your-32-char-secret>
#   FRONTEND_URL=http://localhost:3000

# Run development server
uvicorn main:app --reload --port 8000
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT |
| GET | `/api/auth/google/url` | Get Google OAuth URL |
| POST | `/api/auth/google/callback` | Google OAuth callback |
| GET | `/api/auth/github/url` | Get GitHub OAuth URL |
| POST | `/api/auth/github/callback` | GitHub OAuth callback |
| GET | `/api/{user_id}/tasks` | List user's todos |
| POST | `/api/{user_id}/tasks` | Create todo |
| PUT | `/api/{user_id}/tasks/{task_id}` | Update todo |
| DELETE | `/api/{user_id}/tasks/{task_id}` | Delete todo |

## Railway Deployment

### Prerequisites

1. [Railway account](https://railway.app)
2. Railway CLI installed: `npm install -g @railway/cli`

### Step-by-Step Deployment

#### 1. Create Railway Project

```bash
# Login to Railway
railway login

# Initialize new project in backend directory
cd backend
railway init
```

#### 2. Add PostgreSQL Database

In Railway Dashboard:
1. Open your project
2. Click "New" → "Database" → "PostgreSQL"
3. Railway automatically sets `DATABASE_URL` for you

#### 3. Set Environment Variables

In Railway Dashboard → Your Service → Variables:

**Required Variables:**
```
JWT_SECRET_KEY=<generate-with: openssl rand -hex 32>
FRONTEND_URL=https://your-vercel-app.vercel.app
```

**Optional Variables:**
```
APP_ENV=production
JWT_EXPIRE_MINUTES=15
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
GITHUB_CLIENT_ID=<your-github-client-id>
GITHUB_CLIENT_SECRET=<your-github-client-secret>
```

> Note: `DATABASE_URL` is automatically set when you add the PostgreSQL plugin.

#### 4. Deploy

```bash
# Deploy from backend directory
railway up
```

Or connect GitHub for automatic deployments:
1. Railway Dashboard → Settings → Connect GitHub
2. Select repository and set root directory to `/backend`

#### 5. Get Your Backend URL

After deployment:
1. Railway Dashboard → Your Service → Settings
2. Under "Networking", click "Generate Domain"
3. Your backend URL will be: `https://your-service.up.railway.app`

### Health Check

Verify deployment:
```bash
curl https://your-service.up.railway.app/health
# Expected: {"status":"ok","version":"2.0.0"}
```

## Vercel Frontend Integration

Update your Vercel frontend environment:

```
NEXT_PUBLIC_API_URL=https://your-service.up.railway.app
```

Ensure your frontend makes API calls to this URL.

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `JWT_SECRET_KEY` | Yes | - | Secret for JWT signing (min 32 chars) |
| `FRONTEND_URL` | Yes | - | Frontend URL for CORS |
| `APP_ENV` | No | production | Environment name |
| `JWT_ALGORITHM` | No | HS256 | JWT signing algorithm |
| `JWT_EXPIRE_MINUTES` | No | 15 | Token expiration time |
| `GOOGLE_CLIENT_ID` | No | - | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | No | - | Google OAuth client secret |
| `GITHUB_CLIENT_ID` | No | - | GitHub OAuth client ID |
| `GITHUB_CLIENT_SECRET` | No | - | GitHub OAuth client secret |

## Troubleshooting

### App won't start
- Check Railway logs: `railway logs`
- Ensure all required env vars are set
- `JWT_SECRET_KEY` must be at least 32 characters

### CORS errors
- Verify `FRONTEND_URL` matches your Vercel deployment exactly
- Don't include trailing slash in `FRONTEND_URL`

### Database connection fails
- Ensure PostgreSQL plugin is added
- Check `DATABASE_URL` format (Railway auto-configures this)
- If using external DB, ensure SSL mode is set correctly

### OAuth not working
- Verify OAuth credentials are correct
- Update OAuth provider redirect URIs to match your production URLs:
  - Google: `https://your-vercel-app.vercel.app/auth/google/callback`
  - GitHub: `https://your-vercel-app.vercel.app/auth/github/callback`

## Project Structure

```
backend/
├── main.py              # FastAPI app entry point
├── Procfile             # Railway/Heroku start command
├── railway.json         # Railway configuration
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
└── app/
    ├── config.py        # Settings and env validation
    ├── database.py      # Database connection
    ├── models/          # SQLModel data models
    ├── schemas/         # Pydantic request/response schemas
    ├── routers/         # API route handlers
    └── auth/            # Authentication utilities
```

## License

MIT
