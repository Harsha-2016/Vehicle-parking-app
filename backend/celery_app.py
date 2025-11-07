
# backend/celery_app.py
from celery import Celery
import os

def make_celery():
    celery = Celery(
        "backend",
        broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
        backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    )

    # safer serializers and explicit content types
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
    )

    # import schedule safely (no circular import because it's just a dict)
    try:
        from backend.beat_schedule import CELERY_BEAT_SCHEDULE
        celery.conf.beat_schedule = CELERY_BEAT_SCHEDULE
    except Exception as e:
        # If beat_schedule can't be imported in some contexts, continue – not fatal
        print("⚠️ Could not import beat_schedule:", e)

    celery.conf.timezone = "Asia/Kolkata"

    # autodiscover tasks under backend.tasks (helps worker register them)
    celery.autodiscover_tasks(['backend.tasks'])
    return celery

celery = make_celery()
