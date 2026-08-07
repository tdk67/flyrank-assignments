import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from storage.models import Base

logger = logging.getLogger("BE-06-Scraper.Database")

def create_db_engine():
    try:
        engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            echo=False
        )
        # Test connection
        with engine.connect() as conn:
            pass
        logger.info(f"Connected to PostgreSQL database at {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
        return engine
    except Exception as e:
        logger.warning(f"Could not connect to PostgreSQL ({e}). Falling back to local SQLite database (flyrank_scraper.db).")
        sqlite_url = "sqlite:///./flyrank_scraper.db"
        sqlite_engine = create_engine(sqlite_url, echo=False)
        Base.metadata.create_all(bind=sqlite_engine)
        return sqlite_engine

engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
