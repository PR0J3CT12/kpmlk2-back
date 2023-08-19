from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from kpm.apps.users.models import User
from kpm.apps.users.permissions import *
from kpm.apps.users.functions import is_trusted
from kpm.apps.stats.functions import *
from kpm.apps.logs.models import Log
from kpm.apps.works.models import Work
from kpm.apps.grades.models import Grade, Mana
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import json
from django.db.models import Sum, Q, Count
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.users.docs import *
from django.utils import timezone
from datetime import datetime, timedelta


#@swagger_auto_schema(method='GET', operation_summary="Получить персональную статистику ученика.",
#                     manual_parameters=[id_param],
#                     responses=get_stats_responses)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_stats(request):
    try:
        id_ = get_variable('id', request)
        if not is_trusted(request, id_):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        student = User.objects.get(id=id_, is_admin=False)

        if student.last_homework_id is None:
            last_homework_current = None
            last_homework_others = None
        else:
            try:
                last_homework_work = Work.objects.get(id=student.last_homework_id)
                last_homework = Grade.objects.filter(work=last_homework_work)
                last_homework_current = last_homework.filter(user=student)
                last_homework_others = last_homework.exclude(user=student)
            except ObjectDoesNotExist:
                last_homework_current = None
                last_homework_others = None
        if not last_homework_current:
            last_homework_perc_current = None
        else:
            last_homework_current = last_homework_current[0]
            last_homework_perc_current = round(last_homework_current.score / last_homework_current.max_score * 100)
        if not last_homework_others:
            last_homework_perc_others = None
        else:
            total = 0
            total_perc = 0
            for student_ in last_homework_others:
                if student_.max_score <= 0:
                    continue
                total_perc += round(student_.score / student_.max_score * 100)
                total += 1
            if total > 0:
                last_homework_perc_others = total_perc // total
            else:
                last_homework_perc_others = None

        if student.last_classwork_id is None:
            last_classwork = None
        else:
            try:
                last_classwork_work = Work.objects.get(id=student.last_classwork_id)
                last_classwork = Grade.objects.filter(work=last_classwork_work, user=student)
            except ObjectDoesNotExist:
                last_classwork = None
        if not last_classwork:
            last_classwork_perc = None
        else:
            last_classwork = last_classwork[0]
            last_classwork_perc = round(last_classwork.score / last_classwork.max_score * 100)

        homeworks = Grade.objects.filter(work__is_homework=True, user=student)
        if not homeworks:
            homeworks_perc = None
        else:
            total = 0
            total_perc = 0
            for homework in homeworks:
                if homework.max_score <= 0:
                    continue
                homework_perc = round(homework.score / homework.max_score * 100)
                total_perc += homework_perc
                total += 1
            if total > 0:
                homeworks_perc = total_perc // total
            else:
                homeworks_perc = None

        classworks = Grade.objects.filter(work__is_homework=False, user=student)
        if not classworks:
            classworks_perc = None
        else:
            total = 0
            total_perc = 0
            for classwork in classworks:
                if classwork.max_score <= 0:
                    continue
                classwork_perc = round(classwork.score / classwork.max_score * 100)
                total_perc += classwork_perc
                total += 1
            if total > 0:
                classworks_perc = total_perc // total
            else:
                classworks_perc = None

        manas = Mana.objects.filter(Q(user=student) & Q(is_given=0))
        green = manas.filter(color='green').aggregate(Count('id'))["id__count"]
        blue = manas.filter(color='blue').aggregate(Count('id'))["id__count"]

        return HttpResponse(json.dumps({
            'last_homework_current': last_homework_perc_current,
            'last_homework_others': last_homework_perc_others,
            'last_classwork': last_classwork_perc,
            'homeworks': homeworks_perc,
            'classworks': classworks_perc,
            'green': green,
            'blue': blue
        }, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Пользователь не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)