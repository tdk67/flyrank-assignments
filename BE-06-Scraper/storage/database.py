import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from storage.models import Base

logger = logging.getLogger("BE-06-Scraper.Database")

# Create SQLite engine with thread check disabled for multithreaded GUI/async compatibility
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=False
)

# Auto-create all tables in SQLite database on startup
Base.metadata.create_all(bind=engine)
logger.info(f"Initialized SQLite database at {settings.DATABASE_URL}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
