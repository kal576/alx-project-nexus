import os
from celery.schedules import crontab
from django.conf import settings
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce_backend.settings")

app = Celery("ecommerce_backend")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "release-unpaid-orders": {
        "task": "orders.tasks.release_unpaid_orders",
        "schedule": crontab(minute=0),  # Runs every hour
    },
}
