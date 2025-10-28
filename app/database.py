from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# SQLite database URL pointing to a local file named tasks.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./tasks.db"

# For SQLite, check_same_thread must be False for use with FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session factory configuration
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator:
    """Provide a transactional database session for dependency injection.

    Yields a SQLAlchemy session and ensures it is properly closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

