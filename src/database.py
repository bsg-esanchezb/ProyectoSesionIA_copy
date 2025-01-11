from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import Config


print("Use the DATABASE_URL from Config")
# Use the DATABASE_URL from Config
DATABASE_URL = Config.DATABASE_URL
print("Create the SQLAlchemy engine")
# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False)
print("Create a session factory")
# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
print("Ejecuta get_db funcion")
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
