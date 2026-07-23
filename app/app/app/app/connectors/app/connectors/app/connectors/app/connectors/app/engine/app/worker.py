from celery import Celery

from app.config import settings

celery_app = Celery("omniflow", broker=settings.redis_url, backend=settings.redis_url)

celery_app.conf.beat_schedule = {
    "poll-cron-workflows-every-minute": {
        "task": "app.engine.tasks.poll_cron_workflows",
        "schedule": 60.0,
    }
}
celery_app.conf.timezone = "UTC"

# Make sure tasks module is imported so Celery registers the tasks.
import app.engine.tasks  # noqa: E402,F401
