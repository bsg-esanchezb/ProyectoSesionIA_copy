from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from pydantic import BaseModel
from src.services.big_workflow_service import orchestrate_big_workflow
from typing import List
from src.celery_tasks.tasks import big_workflow_task

router = APIRouter()

class BigWorkflowRequest(BaseModel):
    # Cambiamos nombres de las columnas antiguas a las nuevas:
    IdPEspecifico: int
    IdPEspecificoSesion: int | None = None
    # Antes era TipoPrograma (list[int]) => ahora se llama TipoResumenGrabacionOnline (list[int])
    TipoResumenGrabacionOnline: List[int] = []
    Sesion: str
    UrlVideo: str
    # Eliminamos IdPEspecificoHijo porque la columna ya no existe

@router.post("/big-workflow")
def run_big_workflow(request: BigWorkflowRequest, db: Session = Depends(get_db)):
    try:
        result = orchestrate_big_workflow(request.dict(), db)
        return {
            "message": "Workflow triggered",
            "details": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch", summary="Run multiple big workflow jobs asynchronously")
def big_workflow_batch_endpoint(requests: List[BigWorkflowRequest]):
    """
    Accepts an array of workflow inputs and queues each one in Celery.
    Returns a list of Celery task IDs.
    """
    task_ids = []
    for req in requests:
        data = req.dict()
        result = big_workflow_task.delay(data)
        task_ids.append(result.id)

    return {"message": "Batch queued", "tasks": task_ids}
