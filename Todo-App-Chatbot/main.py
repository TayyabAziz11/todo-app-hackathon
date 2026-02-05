"""
Todo API - FastAPI Backend

IMPORTANT: The /health endpoint is defined FIRST to ensure healthcheck
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
# DATABASE INITIALIZATION (for lifespan)
# =============================================================================
def init_database() -> bool:
    """
    Initialize database tables. Non-blocking - errors are logged but don't crash.
    """
    try:
        from app.database import get_engine, create_db_and_tables
        from app.models.user import User
        from app.models.todo import Todo
        from app.models.conversation import Conversation
        from app.models.message import Message

        logger.info("Initializing database...")
        create_db_and_tables()
        logger.info("✓ Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.warning("App will continue - database features may not work")
        return False


# =============================================================================
# LIFESPAN CONTEXT - Only for startup/shutdown tasks, NOT for route registration
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - for startup/shutdown only."""
    logger.info("Application starting...")

    # Initialize database (non-blocking)
    db_ok = init_database()

    if db_ok:
        logger.info("✓ Application ready to serve requests (full functionality)")
    else:
        logger.warning("⚠ Application ready (database unavailable)")

    yield

    logger.info("Application shutting down...")


# =============================================================================
# CREATE APP WITH LIFESPAN
# =============================================================================
app = FastAPI(
    title="Todo API v3.0.0 - AI-Powered Chatbot",
    version="3.0.0",
    description="Phase III: AI-Powered Todo Chatbot with Stateless Conversation Management",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# =============================================================================
# CORS MIDDLEWARE
# =============================================================================
try:
    from app.config import settings
    cors_origins = settings.get_cors_origins()
    logger.info(f"Configuring CORS for origins: {cors_origins}")
except Exception as e:
    logger.warning(f"Could not load CORS settings: {e}")
    cors_origins = ["*"]  # Fallback to allow all origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# =============================================================================
# ROOT HEALTH ENDPOINTS - defined immediately, no dependencies
# =============================================================================
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for container orchestration.
    Returns 200 OK immediately - no database or auth required.
    """
    return {"status": "ok", "version": "3.0.0"}


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API information."""
    return {
        "message": "Todo API v3.0.0 - AI-Powered Chatbot",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


# =============================================================================
# REGISTER ROUTERS - at module level, NOT in lifespan
# =============================================================================
try:
    from app.routers.auth import router as auth_router
    from app.routers.todos import router as todos_router
    from app.routers.chat import router as chat_router

    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(todos_router, prefix="/api", tags=["Todos"])
    app.include_router(chat_router, prefix="/api", tags=["Chat"])
    logger.info("✓ Routers registered successfully")
    logger.info("  - /api/auth/* (Authentication)")
    logger.info("  - /api/todos/* (Todos)")
    logger.info("  - /api/chat/* (Chat - Phase 3 AI Chatbot)")
except Exception as e:
    logger.error(f"Router registration failed: {e}")
    logger.warning("App will run with limited functionality (health and docs only)")


# =============================================================================
# LOCAL DEVELOPMENT & DEPLOYMENT
# =============================================================================
if __name__ == "__main__":
    import os
    import uvicorn

    # Port configuration:
    # - Hugging Face Spaces: 7860 (default)
    # - Railway/local: 8000 (default)
    # - Can be overridden with PORT environment variable
    port = int(os.getenv("PORT", "7860"))

    logger.info(f"Starting server on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
