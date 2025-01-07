from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from pydantic import BaseModel
from services.big_workflow_service import orchestrate_big_workflow
from typing import List
from celery_tasks.tasks import big_workflow_task

router = APIRouter()

class BigWorkflowRequest(BaseModel):
    IdProgramaGeneral: int
    IdPEspecificoPadre: int | None = None
    IdPEspecificoHijo: int | None = None
    TipoPrograma: list[int] = []
    Sesion: str
    UrlVideo: str

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
        # Convert pydantic model to dict
        data = req.dict()
        # Enqueue the Celery task
        result = big_workflow_task.delay(data)
        task_ids.append(result.id)

    return {"message": "Batch queued", "tasks": task_ids}
