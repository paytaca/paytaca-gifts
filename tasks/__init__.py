from celery import Celery
import settings

app = Celery(
    "tasks",
    broker=f"{settings.REDIS_URI}/0",
    backend=f"{settings.REDIS_URI}/1"
)