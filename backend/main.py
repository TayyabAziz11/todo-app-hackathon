import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database() -> bool:
    """
    Initialize database tables. Returns True on success, False on failure.
    This is non-blocking - errors are logged but don't crash the app.
    """
    try:
        # Import engine here to avoid import-time database connection
        from app.database import engine
        # Import models so SQLModel knows about them
        from app.models.user import User
        from app.models.todo import Todo

        logger.info("Creating database tables...")
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        logger.warning("App will continue running - database may not be ready yet")
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Database initialization is non-blocking - healthcheck works even if DB fails.
    """
    # Startup: attempt database initialization (non-blocking)
    init_database()
    yield
    # Shutdown: cleanup if needed
    logger.info("Application shutting down")


# Import routers after defining lifespan to avoid circular imports
from app.routers.auth import router as auth_router
from app.routers.todos import router as todos_router

app = FastAPI(
    title="Todo API",
    version="2.0.0",
    description="Phase II: Multi-user Todo Application with Authentication",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Register routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(todos_router, prefix="/api", tags=["Todos"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
