import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kpm.settings")
app = Celery("kpm")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'open_homeworks': {
        'task': 'kpm.apps.data.tasks.open_homeworks',
        'schedule': crontab(minute=26, hour=19),
    }
}
