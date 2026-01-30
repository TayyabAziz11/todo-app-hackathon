"""
Todo API - FastAPI Backend

IMPORTANT: The /health endpoint is defined FIRST to ensure Railway healthcheck
works even if other imports or database connections fail.
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
# DETECT DEPLOYMENT ENVIRONMENT
# =============================================================================
def detect_environment() -> tuple[str, str]:
    """
    Detect runtime environment and configure root_path for reverse proxy support.

    Hugging Face Spaces serves apps behind /spaces/<username>/<space-name>/
    FastAPI needs to know this via root_path to generate correct OpenAPI/docs URLs.

    Returns:
        tuple[str, str]: (environment_name, root_path)
    """
    # Check for Hugging Face Spaces
    space_id = os.getenv("SPACE_ID") or os.getenv("HF_SPACE_ID")

    if space_id:
        # Format: username/space-name
        root_path = f"/spaces/{space_id}"
        logger.info(f"✓ Detected Hugging Face Spaces environment")
        logger.info(f"  SPACE_ID: {space_id}")
        logger.info(f"  root_path: {root_path}")
        return "huggingface", root_path

    # Local or other deployment (Railway, etc.)
    logger.info("✓ Detected local/standard deployment")
    logger.info("  root_path: (none)")
    return "local", ""


# Detect environment and get root_path
ENV_NAME, ROOT_PATH = detect_environment()

# =============================================================================
# CREATE APP IMMEDIATELY - before any imports that might fail
# =============================================================================
app = FastAPI(
    title="Todo API",
    version="3.0.0",
    description="Phase III: AI-Powered Todo Chatbot with Stateless Conversation Management",
    root_path=ROOT_PATH,  # Critical for Hugging Face Spaces
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# =============================================================================
# CORS MIDDLEWARE - must be registered at app creation, NOT in lifespan
# =============================================================================
try:
    from app.config import settings
    # Use configured CORS origins from settings
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
# HEALTH ENDPOINT - defined FIRST, no dependencies
# =============================================================================
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for Railway/container orchestration.
    Returns 200 OK immediately - no database or auth required.
    """
    return {"status": "ok", "version": "3.0.0"}


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API information."""
    return {
        "message": "Todo API v3.0.0 - AI-Powered Chatbot",
        "environment": ENV_NAME,
        "docs": f"{ROOT_PATH}/docs" if ROOT_PATH else "/docs",
        "health": f"{ROOT_PATH}/health" if ROOT_PATH else "/health"
    }


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
    """
    Register API routers.

    CRITICAL: Routers must be registered for the app to function.
    If this fails, the app should not start.
    """
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
        logger.error(f"FATAL: Router setup failed: {e}")
        logger.error("App cannot function without routes - startup aborted")
        raise  # Re-raise to prevent app from starting without routes


# =============================================================================
# REGISTER ROUTERS - at module level to ensure they're always available
# =============================================================================
setup_routers()


# =============================================================================
# STARTUP/SHUTDOWN - using lifespan context
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("=" * 70)
    logger.info("Todo API v3.0.0 - Starting...")
    logger.info("=" * 70)

    # Log environment information
    logger.info(f"Environment: {ENV_NAME}")
    logger.info(f"Root Path: {ROOT_PATH if ROOT_PATH else '(none - standard deployment)'}")

    # Log accessible URLs
    if ROOT_PATH:
        logger.info("")
        logger.info("Accessible URLs (via reverse proxy):")
        logger.info(f"  - Health: {ROOT_PATH}/health")
        logger.info(f"  - Docs: {ROOT_PATH}/docs")
        logger.info(f"  - ReDoc: {ROOT_PATH}/redoc")
        logger.info(f"  - API: {ROOT_PATH}/api/*")
    else:
        logger.info("")
        logger.info("Accessible URLs (direct):")
        logger.info("  - Health: /health")
        logger.info("  - Docs: /docs")
        logger.info("  - ReDoc: /redoc")
        logger.info("  - API: /api/*")

    logger.info("")

    # Initialize database (non-blocking)
    init_database()

    logger.info("=" * 70)
    logger.info("Application ready to serve requests")
    logger.info("=" * 70)
    yield

    logger.info("Application shutting down...")


# Apply lifespan to app
app.router.lifespan_context = lifespan


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
