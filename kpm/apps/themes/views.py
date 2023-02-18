from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .customfunctions import get_variable
from kpm.apps.logs.models import Log
from kpm.apps.users.models import User
import json
from kpm.apps.themes.models import Theme
from kpm.apps.users.permissions import IsAdmin


@api_view(["GET"])
@permission_classes([IsAdmin])
def get_theme(request):
    try:
        id_ = get_variable("id", request)
        if not id_:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Не указано id работы.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=404)
        theme = Theme.objects.get(id=id_)
        if not theme:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Тема не найдена.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=404)
        if theme.type == 0:
            text = 'домашняя работа'
        elif theme.type == 1:
            text = 'классная работа'
        elif theme.type == 2:
            text = 'блиц'
        elif theme.type == 3:
            text = 'экзамен письменный'
        elif theme.type == 4:
            text = 'экзамен устный'
        else:
            text = 'вне статистики'
        theme_info = {"id": theme.id, "name": theme.name, "type": theme.type, "type_text": text}
        return HttpResponse(
            json.dumps({'state': 'success', 'message': 'Тема получена.', 'details': {'theme': theme_info}}, ensure_ascii=False),
            status=200)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


@api_view(["GET"])
@permission_classes([IsAdmin])
def get_themes(request):
    class_ = get_variable("class", request)
    if not class_:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Не указан класс ученика.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    else:
        if class_ not in ['4', '5', '6']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
    try:
        themes_ = Theme.objects.filter(school_class=class_)
        themes_list = []
        for theme in themes_:
            if theme.type == 0:
                text = 'домашняя'
            elif theme.type == 1:
                text = 'классная'
            elif theme.type == 2:
                text = 'блиц'
            elif theme.type == 3:
                text = 'экз. письменный'
            elif theme.type == 4:
                text = 'экз. устный'
            else:
                text = 'вне статистики'
            theme_info = {"id": theme.id, "name": theme.name, "type": theme.type, "type_text": text}
            themes_list.append(theme_info)
        return HttpResponse(
            json.dumps({'state': 'success', 'message': 'Все темы получены.', 'details': {'themes': themes_list}}, ensure_ascii=False),
            status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


# todo: обработка ошибок
@api_view(["POST"])
@permission_classes([IsAdmin])
def create_theme(request):
    if request.body:
        request_body = json.loads(request.body)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=400)
    try:
        theme = Theme(name=request_body["name"], type=request_body["type"], school_class=request_body["class"])
        theme.save()
        log = Log(operation='INSERT', from_table='themes', details='Добавлена новая тема в таблицу themes.')
        log.save()
        return HttpResponse(
            json.dumps({'state': 'success', 'message': 'Тема успешно добавлена.', 'details': {}}, ensure_ascii=False),
            status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


# todo: обработка ошибок
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_theme(request):
    if request.body:
        request_body = json.loads(request.body)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=400)
    try:
        theme = Theme.objects.get(id=request_body["id"])
        log_details = f'Удалена тема из таблицы themes. ["id": {theme.id} | "name": "{theme.name}" | "type": {theme.type} | "school_class":{theme.school_class}]'
        theme.delete()
        log = Log(operation='DELETE', from_table='themes', details=log_details)
        log.save()
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)
    return HttpResponse(
        json.dumps({'state': 'success', 'message': 'Тема успешно удалена.', 'details': {}}, ensure_ascii=False),
        status=205)


# todo: обработка ошибок
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_themes(request):
    class_ = get_variable("class", request)
    if not class_:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Не указан класс ученика.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    else:
        if class_ not in ['4', '5', '6']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
    try:
        themes = Theme.objects.filter(school_class=class_)
        for theme in themes:
            Log(operation='DELETE', from_table='themes',
                details=f'Удалена тема из таблицы themes. ["id": {theme.id} | "name": "{theme.name}" | "type": {theme.type} | "school_class":{theme.school_class}]').save()
        themes.delete()
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)
    return HttpResponse(
        json.dumps({'state': 'success', 'message': 'Все темы успешно удалены.', 'details': {}}, ensure_ascii=False),
        status=205)