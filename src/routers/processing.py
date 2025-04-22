from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models.processing_models import TProcesamientoSesionOnline, TProcesamientoTipoGenerar
from pydantic import BaseModel

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for request/response
class SesionOnlineCreate(BaseModel):
    # Renombramos columnas:
    id_pe_especifico: int
    id_pe_especifico_sesion: int | None = None
    tipo_resumen_grabacion_online: str
    sesion: str
    url_video: str
    # Eliminamos id_p_especifico_hijo

class TipoGenerarCreate(BaseModel):
    id_procesamiento_sesion_online: int
    # Cambiamos "tipo" => "id_resumen_grabacion_online" (INT)
    id_resumen_grabacion_online: int
    registro_url: str | None = None

@router.post("/procesamiento/sesion-online/")
def create_sesion_online(data: SesionOnlineCreate, db: Session = Depends(get_db)):
    try:
        sesion_online = TProcesamientoSesionOnline(**data.dict())
        db.add(sesion_online)
        db.commit()
        db.refresh(sesion_online)
        return sesion_online
    except Exception as e:
        db.rollback()
        raise e

@router.get("/procesamiento/sesion-online/")
def list_sesiones_online(db: Session = Depends(get_db)):
    return db.query(TProcesamientoSesionOnline).all()

@router.post("/procesamiento/tipo-generar/")
def create_tipo_generar(data: TipoGenerarCreate, db: Session = Depends(get_db)):
    # Verificar que exista la sesión relacionada
    session = db.query(TProcesamientoSesionOnline).filter(
        TProcesamientoSesionOnline.id == data.id_procesamiento_sesion_online
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        tipo_generar = TProcesamientoTipoGenerar(**data.dict())
        db.add(tipo_generar)
        db.commit()
        db.refresh(tipo_generar)
        return tipo_generar
    except Exception as e:
        db.rollback()
        raise e

@router.get("/procesamiento/tipo-generar/{session_id}")
def list_tipos_generar(session_id: int, db: Session = Depends(get_db)):
    return db.query(TProcesamientoTipoGenerar).filter(
        TProcesamientoTipoGenerar.id_procesamiento_sesion_online == session_id
    ).all()
