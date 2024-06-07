from kpm.celery import app
from kpm.apps.users.models import User
from datetime import datetime
from django.conf import settings


@app.task
def add(x, y):
    return x + y