import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Use DATABASE_URL from environment (Railway) or default to local SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nudge_bot.db")

# Fix for older Railway/Heroku Postgres URLs that start with 'postgres://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Add SSL requirements for Cloud Databases (Postgres)
if "postgresql" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """Initialize the database and create tables."""
    import database.models
    Base.metadata.create_all(bind=engine)
    print("--- Database Initialized! ---")

def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
