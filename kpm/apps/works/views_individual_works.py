from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from kpm.apps.works.models import *
import json
from django.db.models import Sum, Case, When, IntegerField, Count, Q
from kpm.apps.users.permissions import *
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.works.docs import *
from kpm.apps.works.functions import *
from django.conf import settings
from kpm.apps.users.docs import permissions_operation_description


HOST = settings.MEDIA_HOST_PATH
MEDIA_ROOT = settings.MEDIA_ROOT
LOGGER = settings.LOGGER


@swagger_auto_schema(method='GET', operation_summary="Получение списка самостоятельных работ.",
                     manual_parameters=[class_param, type_param, course_param],
                     responses=get_all_individual_works_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']} | {operation_description}")
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_all_individual_works(request):
    try:
        class_ = get_variable("class", request)
        type_ = get_variable("type", request)
        course = get_variable("course", request)
        if class_ not in ['4', '5', '6', '7']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс учеников.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=400)
        if type_ not in [None, '', '2', '10', '11']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан тип учеников.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=400)
        if course not in [None, '', '0', '1', '2', '3', '4']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан курс работы.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=400)
        query = Q(school_class=int(class_))
        if class_ == '4':
            type_ = '2'
        else:
            if type_ == '2':
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Тип работы не соответствует классу ученика.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=400)
        if type_ not in [None, '']:
            query &= Q(type=int(type_))
        if course not in [None, '']:
            query &= Q(course=int(course))
        works = Work.objects.filter(query).order_by('-id')
        works_list = []
        works = works.values('id', 'name', 'grades', 'max_score', 'exercises', 'type', 'is_homework', 'course')
        for work in works:
            works_list.append({
                "id": work['id'],
                "name": work['name'],
                "course": work['course'],
                "grades": work['grades'],
                "max_score": work['max_score'],
                "exercises": work['exercises'],
                "work_type": work['type'],
                "is_homework": work['is_homework']
            })
        return HttpResponse(json.dumps({'works': works_list}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)