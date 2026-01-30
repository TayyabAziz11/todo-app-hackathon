"""
Todo API - FastAPI Backend

IMPORTANT: The /health endpoint is defined FIRST to ensure Railway healthcheck
works even if other imports or database connections fail.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# =============================================================================
# REVERSE PROXY MIDDLEWARE - Detect X-Forwarded-Prefix header
# =============================================================================
class ReverseProxyMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle reverse proxy headers (Hugging Face Spaces, Cloudflare, etc.).

    Reads the X-Forwarded-Prefix header and updates the ASGI scope's root_path.
    This allows FastAPI to generate correct URLs for OpenAPI, docs, and API routes
    when running behind a reverse proxy.

    Hugging Face Spaces sets: X-Forwarded-Prefix: /spaces/<username>/<space-name>
    """

    async def dispatch(self, request: Request, call_next: Callable):
        # Read the X-Forwarded-Prefix header
        forwarded_prefix = request.headers.get("x-forwarded-prefix", "").strip()

        if forwarded_prefix:
            # Update the ASGI scope to include the proxy prefix
            request.scope["root_path"] = forwarded_prefix

            # Log proxy detection (only once per unique prefix to avoid spam)
            if not hasattr(self, "_logged_prefixes"):
                self._logged_prefixes = set()

            if forwarded_prefix not in self._logged_prefixes:
                logger.info(f"✓ Reverse proxy detected via X-Forwarded-Prefix")
                logger.info(f"  Proxy prefix: {forwarded_prefix}")
                logger.info(f"  Routes will be served under: {forwarded_prefix}/*")
                self._logged_prefixes.add(forwarded_prefix)

        response = await call_next(request)
        return response


# =============================================================================
# CREATE APP - No hardcoded root_path (middleware handles it dynamically)
# =============================================================================
app = FastAPI(
    title="Todo API",
    version="3.0.0",
    description="Phase III: AI-Powered Todo Chatbot with Stateless Conversation Management",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add reverse proxy middleware FIRST (before CORS)
app.add_middleware(ReverseProxyMiddleware)

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
async def root(request: Request):
    """Root endpoint - API information with dynamic URLs based on reverse proxy."""
    root_path = request.scope.get("root_path", "")

    return {
        "message": "Todo API v3.0.0 - AI-Powered Chatbot",
        "reverse_proxy": bool(root_path),
        "root_path": root_path if root_path else None,
        "docs": f"{root_path}/docs" if root_path else "/docs",
        "health": f"{root_path}/health" if root_path else "/health",
        "redoc": f"{root_path}/redoc" if root_path else "/redoc"
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
    logger.info("")
    logger.info("Reverse Proxy Support: Enabled")
    logger.info("  - Automatically detects X-Forwarded-Prefix header")
    logger.info("  - Works with: Hugging Face Spaces, Cloudflare, nginx, etc.")
    logger.info("  - Local development: routes served at /docs, /health, /api/*")
    logger.info("  - Behind proxy: routes served at <prefix>/docs, <prefix>/health, etc.")
    logger.info("")
    logger.info("Registered Routes:")
    logger.info("  - Health: /health")
    logger.info("  - Docs: /docs")
    logger.info("  - ReDoc: /redoc")
    logger.info("  - Auth: /api/auth/*")
    logger.info("  - Todos: /api/{user_id}/tasks")
    logger.info("  - Chat: /api/{user_id}/chat")
    logger.info("")

    # Initialize database (non-blocking)
    init_database()

    logger.info("=" * 70)
    logger.info("Application ready to serve requests")
    logger.info("  Local: http://localhost:8000/docs")
    logger.info("  Proxy: Detected dynamically from X-Forwarded-Prefix header")
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
