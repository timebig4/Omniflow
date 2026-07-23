from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create tables if they don't exist yet.

    For a real production system, switch to Alembic migrations. This is
    fine for getting the MVP running quickly on Railway.
    """
    from app import models  # noqa: F401  (ensures models are registered)
    Base.metadata.create_all(bind=engine)
