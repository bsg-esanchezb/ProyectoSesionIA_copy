# src/routers/session.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models.session import TAvisoProcesamiento
from pydantic import BaseModel

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class SessionCreate(BaseModel):
    correo: str
    area: str

@router.post("/sessions/")
def create_session(session_data: SessionCreate, db: Session = Depends(get_db)):  
    session = TAvisoProcesamiento(correo=session_data.correo, area=session_data.area)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session