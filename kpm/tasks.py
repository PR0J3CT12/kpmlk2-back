from kpm.celery import app
from kpm.apps.users.models import User
from kpm.apps.groups.models import GroupWorkDate
from datetime import datetime, date
from django.conf import settings


@app.task
def open_homeworks():
    today = datetime.today()
    group_work_dates = GroupWorkDate.objects.filter(date__lte=today, is_given=False).values('group_id', 'work_id')
    for group_work_date in group_work_dates:
        pass