from kpm.celery import app
from kpm.apps.groups.models import Group, GroupUser, GroupWorkDate
from kpm.apps.works.models import Work, WorkUser
from kpm.apps.grades.models import Grade
from datetime import datetime, timedelta
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


LOGGER = settings.LOGGER


@app.task
def open_homeworks():
    try:
        today = datetime.today()
        group_work_dates = GroupWorkDate.objects.filter(date__lte=today, is_given=False)
        for group_work_date in group_work_dates:
            work_id = group_work_date.work_id
            group_id = group_work_date.group_id
            try:
                work = Work.objects.get(id=work_id)
                answers = ['#'] * work.exercises
                group = Group.objects.get(id=group_id)
                students = GroupUser.objects.filter(group=group).select_related('user')
                for student in students:
                    user = student.user
                    try:
                        if user.school_class == work.school_class:
                            work_user = WorkUser(user=user, work=work, answers=answers)
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


@app.task
def works_deadlines():
    try:
        deadline = datetime.today() - timedelta(days=8)
        works_users = WorkUser.objects.filter(added_at__lte=deadline, status=0).select_related('work')
        for work_user in works_users:
            grade = Grade.objects.get(user=work_user.user, work=work_user.work)
            grade.max_score = work_user.work.max_score
            grade.exercises = work_user.work.exercises
            new_grades = ["0"] * work_user.work.exercises
            grade.grades = new_grades
            work_user.status = 4
            grade.full_clean()
            work_user.save()
            grade.save()
            LOGGER.info(f'[CELERY | works_deadlines] Deadline passed on work {work_user.work_id} by student {work_user.user_id}.')
    except Exception as e:
        LOGGER.error(f'[CELERY | works_deadlines] Error: {str(e)}.')