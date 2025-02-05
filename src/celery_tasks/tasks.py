from celery import shared_task
from src.services.big_workflow_service import orchestrate_big_workflow
from src.repositories.procesamiento_repository import create_sesion_online
from src.database import SessionLocal

@shared_task(name="celery_tasks.tasks.big_workflow_task")
def big_workflow_task(data: dict) -> dict:
    """
    Celery task to run the big workflow asynchronously.
    Inserts the main record to obtain a session ID and then passes it along with
    the provided data to the orchestrator.
    Returns a dict with useful info, e.g., the session ID.
    """
    print("before creating a fresh DB session for Celery")
    db = SessionLocal()  # Create a fresh DB session for Celery
    print("after creating a fresh DB session for Celery")
    try:
        # Insert the main record immediately and obtain the session ID.
        sesion_id = create_sesion_online(db, data)
        # Optionally, add the session ID to the data dictionary if needed downstream.
        data["sesion_id"] = sesion_id
        # Now call the orchestrator with the pre-inserted session ID.
        result = orchestrate_big_workflow(sesion_id, data, db)
        return result
    except Exception as e:
        # Log or handle errors as needed
        raise e
    finally:
        db.close()
