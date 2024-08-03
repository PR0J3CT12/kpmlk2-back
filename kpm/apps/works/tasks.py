from kpm.celery import app
from kpm.apps.groups.models import Group, GroupUser, GroupWorkDate
from kpm.apps.works.models import Work, WorkUser
from datetime import datetime, date
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


LOGGER = settings.LOGGER


@app.task
def open_homeworks():
    try:
        today = datetime.today()
        group_work_dates = GroupWorkDate.objects.filter(date__lte=today, is_given=False).values('group_id', 'work_id')
        for group_work_date in group_work_dates:
            work_id = group_work_date['work_id']
            group_id = group_work_date['group_id']
            try:
                work = Work.objects.get(id=work_id)
                group = Group.objects.get(id=group_id)
                students = GroupUser.objects.filter(group=group).select_related('user')
                for student in students:
                    try:
                        if student.user.school_class == work.school_class:
                            work_user = WorkUser(user=student, work=work)
                            work_user.save()
                            LOGGER.info(f'[CELERY | open_homeworks] Added student {student.id} to work {work_id}.')
                        else:
                            LOGGER.info(f'[CELERY | open_homeworks] Error: student {student.id} class is not equal with work {work_id} class.')
                    except Exception as e:
                        LOGGER.error(f'[CELERY | open_homeworks] Error: failed to open work {work_id} to student {student.id}. {str(e)}.')
                group_work_date.is_given = True
                group_work_date.save()
            except ObjectDoesNotExist as e:
                LOGGER.error(f'[CELERY | open_homeworks] Error: work {work_id} or group {group_id} does not exists.')
    except Exception as e:
        LOGGER.error(f'[CELERY | open_homeworks] Error: {str(e)}.')