"""
Todo API - Phase 2 Backend (Traditional REST API)

Production deployment on Hugging Face Spaces.
Frontend: https://todo-app-hackathon-mytask.vercel.app
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================
def init_database() -> bool:
    """Initialize database tables. Non-blocking."""
    try:
        from app.database import create_db_and_tables
        from app.models.user import User
        from app.models.todo import Todo

        logger.info("Initializing database...")
        create_db_and_tables()
        logger.info("✓ Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


# =============================================================================
# LIFESPAN CONTEXT
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("=" * 60)
    logger.info("Phase 2 Backend starting...")
    logger.info("=" * 60)

    # Initialize database
    db_ok = init_database()

    # Log all registered routes
    logger.info("")
    logger.info("Registered Routes:")
    logger.info("-" * 40)
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = ", ".join(route.methods - {"HEAD", "OPTIONS"}) if route.methods else "GET"
            logger.info(f"  {methods:8} {route.path}")
    logger.info("-" * 40)
    logger.info("")

    if db_ok:
        logger.info("✓ Phase 2 Backend ready (full functionality)")
    else:
        logger.warning("⚠ Phase 2 Backend ready (database unavailable)")

    logger.info("=" * 60)

    yield

    logger.info("Phase 2 Backend shutting down...")


# =============================================================================
# CREATE FASTAPI APP - Always expose docs
# =============================================================================
app = FastAPI(
    title="Todo API - Phase 2",
    version="2.0.0",
    description="Todo CRUD API with Authentication",
    lifespan=lifespan,
    docs_url="/docs",      # Always available
    redoc_url="/redoc",    # Always available
    openapi_url="/openapi.json"  # OpenAPI schema
)


# =============================================================================
# CORS MIDDLEWARE - Explicit production URLs
# =============================================================================
# Production frontend URL (Vercel)
VERCEL_FRONTEND = "https://todo-app-hackathon-mytask.vercel.app"

# Build CORS origins list
cors_origins = [
    VERCEL_FRONTEND,                    # Production frontend
    "http://localhost:3000",            # Local development
    "http://127.0.0.1:3000",            # Local development alt
]

# Add FRONTEND_URL from environment if set
frontend_url = os.getenv("FRONTEND_URL", "").strip()
if frontend_url and frontend_url not in cors_origins:
    cors_origins.append(frontend_url)

# Add any additional origins from CORS_ORIGINS env var
extra_origins = os.getenv("CORS_ORIGINS", "").strip()
if extra_origins:
    for origin in extra_origins.split(","):
        origin = origin.strip()
        if origin and origin not in cors_origins:
            cors_origins.append(origin)

logger.info(f"CORS origins configured: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],  # Allow all headers for flexibility
    expose_headers=["*"],
    max_age=600,  # Cache preflight for 10 minutes
)


# =============================================================================
# ROOT AND HEALTH ENDPOINTS
# =============================================================================
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": "Todo API",
        "version": "2.0.0",
        "phase": "Phase 2 - Traditional REST",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "api": "/api"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/api", tags=["API Info"])
async def api_info():
    """API root - list available endpoints."""
    return {
        "auth": {
            "register": "POST /api/auth/register",
            "login": "POST /api/auth/login",
            "me": "GET /api/auth/me"
        },
        "todos": {
            "list": "GET /api/{user_id}/tasks",
            "create": "POST /api/{user_id}/tasks",
            "update": "PUT /api/{user_id}/tasks/{task_id}",
            "delete": "DELETE /api/{user_id}/tasks/{task_id}"
        }
    }


# =============================================================================
# REGISTER ROUTERS
# =============================================================================
try:
    from app.routers.auth import router as auth_router
    from app.routers.todos import router as todos_router

    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(todos_router, prefix="/api", tags=["Todos"])

    logger.info("✓ Routers registered: /api/auth/*, /api/{user_id}/tasks")
except Exception as e:
    logger.error(f"Router registration failed: {e}")
    import traceback
    traceback.print_exc()


# =============================================================================
# HUGGING FACE SPACES DEPLOYMENT
# =============================================================================
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "7860"))
    logger.info(f"Starting server on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
