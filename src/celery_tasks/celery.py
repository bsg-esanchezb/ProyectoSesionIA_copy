# celery_tasks/celery.py
from celery import Celery
from src.config import Config

celery_app = Celery(
    "big_workflow",
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
    # Make sure we include the module that contains the tasks
    include=["src.celery_tasks.tasks"]
)

# Optional additional config
celery_app.conf.update({
    "task_track_started": True,
    "task_serializer": "json",
    "result_serializer": "json",
    "accept_content": ["json"],
})
