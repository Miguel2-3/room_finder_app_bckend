from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# 1. DATABASE URL (from config)
DATABASE_URL = settings.DATABASE_URL

#  2. ENGINE (Neon requires SSL, already in URL)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True  # helps Neon reconnection after sleep
)

#  3. SESSION
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 4. BASE
Base = declarative_base()


#  5. Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()