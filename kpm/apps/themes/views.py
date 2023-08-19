from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from .functions import get_variable
from kpm.apps.logs.models import Log
import json
from kpm.apps.themes.models import Theme
from kpm.apps.users.permissions import IsAdmin
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.themes.docs import *


@swagger_auto_schema(method='GET', operation_summary="Получение темы.",
                     manual_parameters=[id_param],
                     responses=get_theme_responses,
                     operation_description=operation_description)
@api_view(["GET"])
@permission_classes([IsAdmin])
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
                "type": theme.type,
                "is_homework": theme.is_homework,
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
                     manual_parameters=[class_param],
                     responses=get_themes_responses,
                     operation_description=operation_description)
@api_view(["GET"])
@permission_classes([IsAdmin])
def get_themes(request):
    try:
        class_ = get_variable("class", request)
        if not class_:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан класс ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        else:
            if class_ not in ['4', '5', '6', 4, 5, 6]:
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=404)
        themes_ = Theme.objects.filter(school_class=class_)
        if not themes_:
            return HttpResponse(json.dumps({'themes': []}, ensure_ascii=False), status=200)
        themes_list = []
        for theme in themes_:
            theme_info = {
                "id": theme.id,
                "name": theme.name,
                "type": theme.type,
                "is_homework": theme.is_homework,
                "school_class": theme.school_class
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
                     operation_description=operation_description)
@api_view(["POST"])
@permission_classes([IsAdmin])
def create_theme(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=400)
        type_ = int(request_body["type"])
        if type_ in [0, 3, 4]:
            is_homework = True
        else:
            is_homework = False
        if request_body["class"] not in ['4', '5', '6', 4, 5, 6]:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс учеников.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        theme = Theme(name=request_body["name"], type=request_body["type"], school_class=int(request_body["class"]), is_homework=is_homework)
        theme.save()
        log = Log(operation='INSERT', from_table='themes', details='Добавлена новая тема в таблицу themes.')
        log.save()
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
                     operation_description=operation_description)
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_theme(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        theme = Theme.objects.get(id=id_)
        log_details = f'Удалена тема из таблицы themes. ["id": {theme.id} | "name": "{theme.name}" | "type": {theme.type} | "school_class": {theme.school_class} | "is_homework": {theme.is_homework}]'
        theme.delete()
        log = Log(operation='DELETE', from_table='themes', details=log_details)
        log.save()
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
                     operation_description=operation_description)
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_themes(request):
    try:
        class_ = get_variable("class", request)
        if not class_:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан класс ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        else:
            if class_ not in ['4', '5', '6', 4, 5, 6]:
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=404)
        themes = Theme.objects.filter(school_class=class_)
        if not themes:
            return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
        for theme in themes:
            Log(operation='DELETE', from_table='themes',
                details=f'Удалена тема из таблицы themes. ["id": {theme.id} | "name": "{theme.name}" | "type": {theme.type} | "school_class": {theme.school_class}] | "is_homework": {theme.is_homework}').save()
        themes.delete()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)