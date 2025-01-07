from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models.processing_models import TProcesamientoSesionOnline, TProcesamientoTipoGenerar
from pydantic import BaseModel

router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for request/response
class SesionOnlineCreate(BaseModel):
    id_programa_general: int
    id_p_especifico_padre: int
    id_p_especifico_hijo: int
    tipo_programa: str
    sesion: str
    url_video: str

class TipoGenerarCreate(BaseModel):
    id_procesamiento_sesion_online: int
    tipo: str
    registro_url: str = None

# Endpoint: Create a new processing session
@router.post("/procesamiento/sesion-online/")
def create_sesion_online(data: SesionOnlineCreate, db: Session = Depends(get_db)):
    sesion_online = TProcesamientoSesionOnline(**data.dict())
    db.add(sesion_online)
    db.commit()
    db.refresh(sesion_online)
    return sesion_online

# Endpoint: List all processing sessions
@router.get("/procesamiento/sesion-online/")
def list_sesiones_online(db: Session = Depends(get_db)):
    return db.query(TProcesamientoSesionOnline).all()

# Endpoint: Create a new task for a session
@router.post("/procesamiento/tipo-generar/")
def create_tipo_generar(data: TipoGenerarCreate, db: Session = Depends(get_db)):
    # Ensure the parent session exists
    session = db.query(TProcesamientoSesionOnline).filter(TProcesamientoSesionOnline.id == data.id_procesamiento_sesion_online).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    tipo_generar = TProcesamientoTipoGenerar(**data.dict())
    db.add(tipo_generar)
    db.commit()
    db.refresh(tipo_generar)
    return tipo_generar

# Endpoint: List all tasks for a session
@router.get("/procesamiento/tipo-generar/{session_id}")
def list_tipos_generar(session_id: int, db: Session = Depends(get_db)):
    return db.query(TProcesamientoTipoGenerar).filter(TProcesamientoTipoGenerar.id_procesamiento_sesion_online == session_id).all()
