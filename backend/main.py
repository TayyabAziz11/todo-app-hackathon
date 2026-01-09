"""
Todo API - FastAPI Backend

IMPORTANT: The /health endpoint is defined FIRST to ensure Railway healthcheck
works even if other imports or database connections fail.
"""

import logging
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
# CREATE APP IMMEDIATELY - before any imports that might fail
# =============================================================================
app = FastAPI(
    title="Todo API",
    version="2.0.0",
    description="Phase II: Multi-user Todo Application with Authentication"
)

# =============================================================================
# CORS MIDDLEWARE - must be registered at app creation, NOT in lifespan
# =============================================================================
try:
    from app.config import settings
    # Use configured frontend URL or fallback to localhost
    cors_origins = [settings.FRONTEND_URL] if settings.FRONTEND_URL else ["http://localhost:3000"]
    logger.info(f"Configuring CORS for origins: {cors_origins}")
except Exception as e:
    logger.warning(f"Could not load FRONTEND_URL from settings: {e}")
    cors_origins = ["*"]  # Fallback to allow all origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# =============================================================================
# HEALTH ENDPOINT - defined FIRST, no dependencies
# =============================================================================
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for Railway/container orchestration.
    Returns 200 OK immediately - no database or auth required.
    """
    return {"status": "ok", "version": "2.0.0"}


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - redirects to docs."""
    return {"message": "Todo API v2.0.0", "docs": "/docs", "health": "/health"}


# =============================================================================
# LAZY INITIALIZATION - only after health endpoint is registered
# =============================================================================
def init_database() -> bool:
    """
    Initialize database tables. Non-blocking - errors are logged but don't crash.
    """
    try:
        from app.database import get_engine, create_db_and_tables
        from app.models.user import User
        from app.models.todo import Todo

        logger.info("Initializing database...")
        create_db_and_tables()
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.warning("App will continue - database features may not work")
        return False


def setup_routers():
    """Register API routers."""
    try:
        from app.routers.auth import router as auth_router
        from app.routers.todos import router as todos_router

        app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
        app.include_router(todos_router, prefix="/api", tags=["Todos"])
        logger.info("Routers registered successfully")
    except Exception as e:
        logger.error(f"Router setup failed: {e}")


# =============================================================================
# STARTUP/SHUTDOWN - using lifespan context
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Application starting...")

    # Setup (non-blocking) - CORS already configured at module level
    setup_routers()
    init_database()

    logger.info("Application ready to serve requests")
    yield

    logger.info("Application shutting down...")


# Apply lifespan to app
app.router.lifespan_context = lifespan


# =============================================================================
# LOCAL DEVELOPMENT
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
