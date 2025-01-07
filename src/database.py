from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config

# Use the DATABASE_URL from Config
DATABASE_URL = Config.DATABASE_URL

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency that provides a database session.
    Automatically closes the session after the request is completed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
