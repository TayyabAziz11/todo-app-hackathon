"""
Database connection and session management.

Engine creation is lazy - only happens when DATABASE_URL is set.
This allows the app to start for healthcheck even without a database.
"""

from typing import Generator, Optional
import logging
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

# Engine is created lazily when first accessed
_engine: Optional[Engine] = None


def get_engine() -> Engine:
    """
    Get or create the database engine.
    Raises RuntimeError if DATABASE_URL is not configured.
    """
    global _engine
    if _engine is None:
        from app.config import settings
        if not settings.DATABASE_URL:
            raise RuntimeError("DATABASE_URL is not configured")

        logger.info("Creating database engine...")
        _engine = create_engine(
            settings.DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=False,
        )
        logger.info("Database engine created successfully")
    return _engine


# Backwards compatibility - lazy property
@property
def engine() -> Engine:
    return get_engine()


def create_db_and_tables() -> None:
    """
    Create all database tables based on SQLModel metadata.
    Does nothing if DATABASE_URL is not configured.
    """
    try:
        eng = get_engine()
        SQLModel.metadata.create_all(eng)
        logger.info("Database tables created successfully")
    except RuntimeError as e:
        logger.warning(f"Cannot create tables: {e}")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    Raises HTTPException if DATABASE_URL is not configured.
    """
    from fastapi import HTTPException
    try:
        eng = get_engine()
        with Session(eng) as session:
            yield session
    except RuntimeError:
        raise HTTPException(
            status_code=503,
            detail="Database is not configured"
        )
