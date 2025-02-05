from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from pydantic import BaseModel
from src.services.big_workflow_service import orchestrate_big_workflow
from src.repositories.procesamiento_repository import create_sesion_online
from typing import List
from src.celery_tasks.tasks import big_workflow_task

router = APIRouter()

class BigWorkflowRequest(BaseModel):
    # Updated field names according to the new schema
    IdPEspecifico: int
    IdPEspecificoSesion: int | None = None
    # Previously TipoPrograma, now a list of integers as TipoResumenGrabacionOnline
    TipoResumenGrabacionOnline: List[int] = []
    Sesion: str
    UrlVideo: str

@router.post("/big-workflow")
def run_big_workflow(request: BigWorkflowRequest, db: Session = Depends(get_db)):
    try:
        # Insert the main record immediately to obtain the session ID.
        sesion_id = create_sesion_online(db, request.dict())
        # Call the orchestrator with the pre-created session ID.
        result = orchestrate_big_workflow(sesion_id, request.dict(), db)
        return {
            "message": "Workflow triggered",
            "details": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch", summary="Run multiple big workflow jobs asynchronously")
def big_workflow_batch_endpoint(requests: List[BigWorkflowRequest], db: Session = Depends(get_db)):
    """
    Accepts an array of workflow inputs and queues each one in Celery.
    For each request, the main record is inserted immediately to obtain a session ID,
    which is then passed to the Celery task.
    Returns a list of Celery task IDs.
    """
    task_ids = []
    for req in requests:
        data = req.dict()
        # Insert the main record immediately and obtain the session ID.
        sesion_id = create_sesion_online(db, data)
        # Optionally add the session ID into the data dictionary for downstream use.
        data["sesion_id"] = sesion_id
        # Enqueue the Celery task with the updated data.
        result = big_workflow_task.delay(data)
        task_ids.append(result.id)
    return {"message": "Batch queued", "tasks": task_ids}
