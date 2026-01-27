"""
Todo API - Phase 2 Backend (Traditional REST API)

This is the Phase 2 backend with:
- User authentication (register, login, OAuth)
- Todo CRUD operations
- PostgreSQL persistence
- NO AI/Chatbot features (Phase 3 is separate)

Deployment: Hugging Face Spaces
Port: 7860 (HF Spaces default)
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
    """
    Initialize database tables. Non-blocking - errors are logged but don't crash.
    """
    try:
        from app.database import create_db_and_tables
        from app.models.user import User
        from app.models.todo import Todo

        logger.info("Initializing Phase 2 database...")
        create_db_and_tables()
        logger.info("✓ Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.warning("App will continue - database features may not work")
        return False


# =============================================================================
# LIFESPAN CONTEXT
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - for startup/shutdown only."""
    logger.info("Phase 2 Backend starting...")

    # Initialize database (non-blocking)
    db_ok = init_database()

    if db_ok:
        logger.info("✓ Phase 2 Backend ready (full functionality)")
    else:
        logger.warning("⚠ Phase 2 Backend ready (database unavailable)")

    yield

    logger.info("Phase 2 Backend shutting down...")


# =============================================================================
# CREATE FASTAPI APP
# =============================================================================
app = FastAPI(
    title="Todo API - Phase 2 (Traditional REST)",
    version="2.0.0",
    description="Todo CRUD API with Authentication (No AI features)",
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
# ROOT HEALTH ENDPOINTS
# =============================================================================
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for container orchestration.
    Returns 200 OK immediately - no database or auth required.
    """
    return {"status": "ok", "version": "2.0.0", "phase": "Phase 2 - Traditional REST"}


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API information."""
    return {
        "message": "Todo API v2.0.0 - Phase 2 (Traditional REST)",
        "phase": "Phase 2",
        "features": ["Authentication", "Todo CRUD", "OAuth"],
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


# =============================================================================
# REGISTER PHASE 2 ROUTERS ONLY (NO CHAT)
# =============================================================================
try:
    from app.routers.auth import router as auth_router
    from app.routers.todos import router as todos_router

    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(todos_router, prefix="/api", tags=["Todos"])

    logger.info("✓ Phase 2 Routers registered successfully")
    logger.info("  - /api/auth/* (Authentication)")
    logger.info("  - /api/todos/* (Todo CRUD)")
    logger.info("  ⚠ NO /api/chat (Phase 3 chatbot is separate deployment)")
except Exception as e:
    logger.error(f"Router registration failed: {e}")
    logger.warning("App will run with limited functionality (health and docs only)")


# =============================================================================
# HUGGING FACE SPACES DEPLOYMENT
# =============================================================================
if __name__ == "__main__":
    import uvicorn

    # Hugging Face Spaces port
    port = int(os.getenv("PORT", "7860"))

    logger.info(f"Starting Phase 2 backend on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
