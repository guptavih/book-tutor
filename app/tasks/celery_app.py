from celery import Celery
from app.config import settings

celery_app = Celery(
    "book_tutor",
    broker=settings.redis_url,
    backend=settings.redis_url
)

@celery_app.task
def ping_task():
    return "pong"