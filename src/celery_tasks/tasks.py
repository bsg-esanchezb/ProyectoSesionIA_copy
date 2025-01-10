from celery import shared_task
from src.services.big_workflow_service import orchestrate_big_workflow
from src.database import SessionLocal

@shared_task(name="celery_tasks.tasks.big_workflow_task")
def big_workflow_task(data: dict) -> dict:
    """
    Celery task to run the big workflow asynchronously.
    Returns a dict with any useful info, e.g. session ID.
    """
    print("before create a fresh DB session for Celery")
    db = SessionLocal()  # create a fresh DB session for Celery
    print("after create a fresh DB session for Celery")
    try:
        result = orchestrate_big_workflow(data, db)
        return result
    except Exception as e:
        # Log or handle errors
        raise e
    finally:
        db.close()
