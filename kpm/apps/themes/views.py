from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from .functions import get_variable
import json
from kpm.apps.themes.models import Theme
from kpm.apps.users.permissions import *
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.themes.docs import *
from django.conf import settings
from kpm.apps.users.docs import permissions_operation_description
from kpm.apps.works.validators import validate_class


LOGGER = settings.LOGGER


@swagger_auto_schema(method='GET', operation_summary="Получение темы.",
                     manual_parameters=[id_param],
                     responses=get_theme_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']}")
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_theme(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=404)
        theme = Theme.objects.get(id=id_)
        return HttpResponse(
            json.dumps({
                "id": theme.id,
                "name": theme.name,
                "school_class": theme.school_class
            }, ensure_ascii=False),
            status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Тема не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получение тем.",
                     manual_parameters=[class_param, type_param],
                     responses=get_themes_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAuthenticated']}")
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEnabled])
def get_themes(request):
    try:
        class_ = get_variable("class", request)
        if not class_:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан класс ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        else:
            if not validate_class(class_):
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=400)
        themes = Theme.objects.filter(school_class=class_)
        type_ = get_variable("type", request)
        if type_ in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']:
            TYPES_CLASSIFICATOR = {  # work_type: [theme_ids]
                '0': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
                '1': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
                '2': [1],
                '3': [8],
                '4': [9],
                '5': [8],
                '6': [9],
                '7': [],
                '8': [],
                '9': [],
                '10': [10, 11, 12],
                '11': [10, 11, 12, 13, 14],
            }
            themes = themes.filter(id__in=TYPES_CLASSIFICATOR[type_])
        themes = themes.values('id', 'name', 'school_class')
        if not themes:
            return HttpResponse(json.dumps({'themes': []}, ensure_ascii=False), status=200)
        themes_list = []
        for theme in themes:
            theme_info = {
                "id": theme['id'],
                "name": theme['name'],
                "school_class": theme['school_class']
            }
            themes_list.append(theme_info)
        return HttpResponse(json.dumps({'themes': themes_list}, ensure_ascii=False), status=200)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='POST', operation_summary="Создание темы.",
                     request_body=create_theme_request_body,
                     responses=create_theme_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierTwo']}")
@api_view(["POST"])
@permission_classes([IsTierTwo, IsEnabled])
def create_theme(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=400)
        if not validate_class(request_body["class"]):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс учеников.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        theme = Theme(name=request_body["name"], school_class=int(request_body["class"]))
        theme.save()
        LOGGER.info(f'Created theme {theme.id} by user {request.user.id}.')
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


@swagger_auto_schema(method='DELETE', operation_summary="Удаление темы.",
                     manual_parameters=[id_param],
                     responses=delete_theme_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierTwo']}")
@api_view(["DELETE"])
@permission_classes([IsTierTwo, IsEnabled])
def delete_theme(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        theme = Theme.objects.get(id=id_)
        theme.delete()
        LOGGER.warning(f'Deleted theme {id_} by user {request.user.id}.')
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Тема не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='DELETE', operation_summary="Удаление тем.",
                     manual_parameters=[class_param],
                     responses=delete_themes_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierTwo']}")
@api_view(["DELETE"])
@permission_classes([IsTierTwo, IsEnabled])
def delete_themes(request):
    try:
        class_ = get_variable("class", request)
        if not class_:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан класс ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        else:
            if not validate_class(class_):
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=404)
        themes = Theme.objects.filter(school_class=class_)
        if not themes:
            return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
        themes.delete()
        LOGGER.warning(f'Deleted all themes by user {request.user.id}.')
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)