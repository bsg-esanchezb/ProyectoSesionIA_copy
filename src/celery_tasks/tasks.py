from celery import shared_task
from src.services.big_workflow_service import orchestrate_big_workflow
from src.repositories.procesamiento_repository import create_sesion_online
from src.database import SessionLocal

@shared_task(name="celery_tasks.tasks.big_workflow_task")
def big_workflow_task(data: dict) -> dict:
    """
    Celery task to run the big workflow asynchronously.
    Receives data with 'sesion_id' already created by the endpoint.
    Calls orchestrate_big_workflow for further processing.
    """
    print("before creating a fresh DB session for Celery")
    db = SessionLocal()
    print("after creating a fresh DB session for Celery")

    try:
        # Recupera el sesion_id, NO insertes nada
        sesion_id = data["sesion_id"]

        # Llama al orquestador
        result = orchestrate_big_workflow(sesion_id, data, db)
        return result

    except Exception as e:
        raise e
    finally:
        db.close()

