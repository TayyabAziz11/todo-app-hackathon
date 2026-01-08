"""
Database connection and session management.
"""

from typing import Generator
from sqlmodel import Session, SQLModel, create_engine
from app.config import settings

# Create database engine
# Connection pool settings:
# - pool_size=5: number of connections to maintain in the pool
# - max_overflow=10: additional connections allowed beyond pool_size
# - pool_pre_ping=True: validate connections before using (handles stale connections)
# - echo=False: disable SQL query logging (set to True for debugging)
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False,  # Set to True to log SQL queries
)


def create_db_and_tables() -> None:
    """
    Create all database tables based on SQLModel metadata.

    This function should be called during application startup to ensure
    all tables exist. In production, use Alembic migrations instead.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    Yields a SQLModel Session that is automatically closed after use.
    Use this as a dependency in route handlers:

    Example:
        @app.get("/users")
        async def get_users(session: Session = Depends(get_session)):
            users = session.exec(select(User)).all()
            return users
    """
    with Session(engine) as session:
        yield session
