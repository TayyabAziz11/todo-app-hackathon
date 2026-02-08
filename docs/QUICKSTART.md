# Todo App - Quick Start Guide

## Phase II Full-Stack Web Application

This guide helps you quickly set up and run the Todo App for local development and testing.

---

## Prerequisites

- **Python 3.13+** (for backend)
- **Node.js 18+** (for frontend)
- **PostgreSQL** database (local or Neon cloud)
- **Git** (for cloning the repository)

---

## 1. Database Setup

### Option A: Using Neon (Cloud PostgreSQL)

1. Go to [neon.tech](https://neon.tech) and create a free account
2. Create a new project
3. Copy the connection string (looks like: `postgresql://user:password@host/dbname`)
4. Save this for Step 2

### Option B: Using Local PostgreSQL

1. Install PostgreSQL on your system
2. Create a database:
   ```bash
   createdb todo_app
   ```
3. Note your connection string: `postgresql://user:password@localhost:5432/todo_app`

---

## 2. Backend Setup

### 2.1 Navigate to Backend Directory

```bash
cd backend
```

### 2.2 Create Virtual Environment

```bash
python -m venv venv

# Activate (Linux/Mac):
source venv/bin/activate

# Activate (Windows):
venv\Scripts\activate
```

### 2.3 Install Dependencies

```bash
pip install -r requirements.txt
```

### 2.4 Configure Environment Variables

Create `backend/.env` file:

```env
DATABASE_URL=postgresql://user:password@host:port/dbname
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=15
FRONTEND_URL=http://localhost:3000
```

**Important:** Change `JWT_SECRET_KEY` to a random string for security!

Generate a secure key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2.5 Initialize Database

```bash
# Run database migrations (if using Alembic)
# alembic upgrade head

# OR create tables directly (for development)
python -c "from app.database import create_db_and_tables; create_db_and_tables()"
```

### 2.6 Start Backend Server

```bash
uvicorn main:app --reload
```

Backend should now be running at: **http://localhost:8000**

Test it:
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok","version":"2.0.0"}
```

---

## 3. Frontend Setup

### 3.1 Open New Terminal

Keep the backend running and open a new terminal window.

### 3.2 Navigate to Frontend Directory

```bash
cd frontend
```

### 3.3 Install Dependencies

```bash
npm install
```

### 3.4 Configure Environment Variables

Create `frontend/.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3.5 Start Frontend Development Server

```bash
npm run dev
```

Frontend should now be running at: **http://localhost:3000**

---

## 4. Usage

### 4.1 Open Browser

Navigate to: **http://localhost:3000**

### 4.2 Create Account

1. Click "Create one" link
2. Enter email and password (min 8 characters)
3. Click "Create Account"
4. You'll be redirected to the dashboard

### 4.3 Create Todos

1. Fill in the "Create New Todo" form
2. Add a title (required) and optional description
3. Click "Create Todo"

### 4.4 Manage Todos

- **Complete:** Click the checkbox next to a todo
- **Edit:** Click "Edit" button, modify, and click "Save"
- **Delete:** Click "Delete" button and confirm

### 4.5 Logout

Click the "Logout" button in the header to sign out.

---

## 5. API Documentation

Once the backend is running, visit:

**http://localhost:8000/docs**

This provides interactive API documentation (Swagger UI) where you can:
- See all available endpoints
- Test API requests directly
- View request/response schemas

---

## 6. Architecture Overview

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   Frontend      │         │   Backend       │         │   Database      │
│   (Next.js)     │◄───────►│   (FastAPI)     │◄───────►│  (PostgreSQL)   │
│   Port 3000     │  HTTP   │   Port 8000     │  SQL    │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
        │                           │
        │                           │
   [React UI]                  [REST API]
        │                           │
        ├── Auth Context            ├── Authentication
        ├── API Client              ├── JWT Validation
        ├── Todo Components         ├── User CRUD
        └── Type Definitions        └── Todo CRUD
```

### Key Technologies:

**Backend:**
- FastAPI - Modern Python web framework
- SQLModel - ORM for database operations
- PostgreSQL - Relational database
- JWT - Stateless authentication
- Bcrypt - Password hashing

**Frontend:**
- Next.js 16 - React framework (App Router)
- TypeScript - Type-safe JavaScript
- Tailwind CSS - Utility-first styling
- React Hooks - State management

---

## 7. Common Issues

### Issue: Backend won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:** Activate virtual environment and install dependencies:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

### Issue: Database connection error

**Error:** `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution:**
1. Check DATABASE_URL in `backend/.env`
2. Ensure PostgreSQL is running
3. Verify credentials and database name

---

### Issue: CORS errors in browser console

**Error:** `Access to fetch at '...' has been blocked by CORS policy`

**Solution:**
1. Ensure backend is running at http://localhost:8000
2. Check `FRONTEND_URL` in backend/.env is set to `http://localhost:3000`
3. Restart backend server

---

### Issue: Frontend build errors

**Error:** `Module not found: Can't resolve '@/...'`

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

### Issue: JWT token expired

**Error:** "Token has expired. Please log in again."

**Solution:** This is expected behavior. JWT tokens expire after 15 minutes for security. Simply log in again.

---

## 8. Testing

Follow the comprehensive testing guide in **TESTING.md** to validate:
- Authentication flow
- CRUD operations
- Data isolation
- Security enforcement

---

## 9. Next Steps

### For Development:
- Add unit tests (pytest for backend, Jest for frontend)
- Implement E2E tests (Playwright)
- Add database migrations (Alembic)
- Enhance error handling and validation

### For Production Deployment:
- Configure environment variables for production
- Use a production-grade PostgreSQL instance
- Enable HTTPS
- Set up CI/CD pipeline
- Implement rate limiting
- Add monitoring and logging

---

## 10. Project Structure

```
todo-app/
├── backend/
│   ├── app/
│   │   ├── auth/          # Authentication utilities
│   │   ├── models/        # Database models
│   │   ├── routers/       # API endpoints
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── config.py      # Configuration
│   │   └── database.py    # Database connection
│   ├── main.py            # FastAPI application
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js pages
│   │   ├── components/   # React components
│   │   ├── lib/          # Utilities (API, auth)
│   │   └── types/        # TypeScript types
│   ├── package.json      # Node dependencies
│   └── .env.local        # Environment variables
│
├── specs/                # Requirements and specs
├── history/              # Prompt history records
├── TESTING.md           # Testing guide
└── README.md            # Project documentation
```

---

## Support

For issues or questions:
1. Check the TESTING.md file for validation procedures
2. Review API documentation at http://localhost:8000/docs
3. Check browser console for frontend errors
4. Check backend terminal for API errors

---

## License

This is a hackathon project for demonstration purposes.

---

**Happy coding! 🚀**
