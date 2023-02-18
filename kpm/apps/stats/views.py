from django.http import HttpResponse
from .models import Theme, Student, Work, Grade, Admin, Mana
from django.db.models import Sum, Q, Count
from django.views.decorators.http import require_http_methods
import json
from kpm.customfunctions import get_variable, login_password_creator
import random


@require_http_methods(["GET"])
def index(request):
    return HttpResponse('Hello world!')


# region [theme region]
@require_http_methods(["GET"])
def get_theme(request):
    id_ = get_variable("id", request)
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
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
        json.dumps({'state': 'success', 'message': '', 'details': {'theme': theme_info}}, ensure_ascii=False),
        status=200)


@require_http_methods(["GET"])
def get_themes(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
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
            json.dumps({'state': 'success', 'message': '', 'details': {'themes': themes_list}}, ensure_ascii=False),
            status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


# todo: обработка ошибок
@require_http_methods(["POST"])
def create_theme(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
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
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)
    return HttpResponse(
        json.dumps({'state': 'success', 'message': 'Тема успешно добавлена.', 'details': {}}, ensure_ascii=False),
        status=200)


# todo: обработка ошибок
@require_http_methods(["POST"])
def delete_theme(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
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
@require_http_methods(["DELETE"])
def delete_themes(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
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
# endregion


# region [work region]
@require_http_methods(["GET"])
def get_works_sorted_by_theme(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
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
        works = Work.objects.select_related('theme').filter(school_class=class_)
        themes_dict = {}
        themes_list = []
        for work in works:
            if work.theme.type == 0:
                text = 'домашняя работа'
            elif work.theme.type == 1:
                text = 'классная работа'
            elif work.theme.type == 2:
                text = 'блиц'
            elif work.theme.type == 3:
                text = 'экзамен письменный'
            elif work.theme.type == 4:
                text = 'экзамен устный'
            else:
                text = 'вне статистики'
            if work.theme.name not in themes_dict.keys():
                themes_dict[work.theme.name] = []
            work_info = {"id": work.id, "name": work.name, "theme_id": work.theme_id, "grades": work.grades.split('_._'), "max_score": work.max_score, "exercises": work.exercises, "theme_name": work.theme.name, "type_text": text}
            themes_dict[work.theme.name].append(work_info)
        for theme in themes_dict.keys():
            tmp = []
            for work in themes_dict[theme]:
                tmp.append(work)
            themes_list.append([theme, tmp])
        return HttpResponse(
            json.dumps({'state': 'success', 'message': '', 'details': {'themes': themes_list}}, ensure_ascii=False),
            status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


@require_http_methods(["GET"])
def get_works(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
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
        works = Work.objects.filter(school_class=class_)
        works_list = []
        for work in works:
            theme = Theme.objects.get(id=work.theme_id)
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
            work_info = {"id": work.id, "name": work.name, "theme_id": work.theme_id, "grades": work.grades.split('_._'),
                         "max_score": work.max_score, "exercises": work.exercises, "theme_name": theme.name, "type_text": text}
            works_list.append(work_info)
        return HttpResponse(
            json.dumps({'state': 'success', 'message': '', 'details': {'works': works_list}}, ensure_ascii=False),
            status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


@require_http_methods(["POST"])
def get_some_works(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
    if request.body:
        request_body = json.loads(request.body)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=400)
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
        works_list = []
        if "works" not in request_body:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Работы не найдены.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        works_order = list(map(int, request_body["works"]))
        works = Work.objects.filter(Q(id__in=works_order) & Q(school_class=class_))
        if not works:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Работы не найдены.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=404)
        for work in works:
            theme = Theme.objects.get(id=work.theme_id)
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
            work_info = {"id": work.id, "name": work.name, "theme_id": work.theme_id, "grades": work.grades.split('_._'),
                         "max_score": work.max_score, "exercises": work.exercises, "theme_name": theme.name, "type_text": text}
            works_list.append(work_info)
        return HttpResponse(
            json.dumps({'state': 'success', 'message': 'Работы возвращены.', 'details': {'works': works_list}}, ensure_ascii=False),
            status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)


@require_http_methods(["GET"])
def get_works_id(request):
    filter_ = get_variable("filter", request)
    param = get_variable("param", request)
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
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
        if not filter_:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Не указан фильтр.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=404)
        else:
            if not param:
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Не указаны параметры фильтра.', 'details': {}, 'instance': request.path},
                        ensure_ascii=False), status=404)
        if filter_ == 'theme_id':
            works = Work.objects.filter(Q(theme_id=param) & Q(school_class=class_))
            works_id_list = list(works.values_list('id', flat=True))
            if not works:
                return HttpResponse(
                    json.dumps({'state': 'error', 'message': f'Работы не найдены.', 'details': {}, 'instance': request.path},
                               ensure_ascii=False), status=200)
        elif filter_ == 'theme_type':
            themes = Theme.objects.filter(Q(type=param) & Q(school_class=class_))
            if not themes:
                return HttpResponse(
                    json.dumps({'state': 'error', 'message': f'Темы не найдены.', 'details': {}, 'instance': request.path},
                               ensure_ascii=False), status=404)
            works = Work.objects.filter(Q(theme_id__in=themes) & Q(school_class=class_))
            works_id_list = list(works.values_list('id', flat=True))
            if not works:
                return HttpResponse(
                    json.dumps({'state': 'error', 'message': f'Работы не найдены.', 'details': {}, 'instance': request.path},
                               ensure_ascii=False), status=404)
        else:
            works_id_list = []
        return HttpResponse(
            json.dumps({'state': 'success', 'message': f'', 'details': {'works': works_id_list}},
                       ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)


# todo: обработка ошибок
@require_http_methods(["POST"])
def create_work(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
    if request.body:
        request_body = json.loads(request.body)
    else:
        return HttpResponse(json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)
    try:
        grades_list = request_body["grades"].replace(',', '.').split()
        max_score = 0
        for grade in grades_list:
            cast = float(grade)
            max_score += cast
        grades = '_._'.join(grades_list)
        work = Work(name=request_body["name"], grades=grades, theme_id=request_body["theme_id"], max_score=max_score, exercises=len(grades_list), school_class=request_body["class"])
        work.save()
        log = Log(operation='INSERT', from_table='works', details='Добавлена новая работа в таблицу works.')
        log.save()
        students = Student.objects.filter(Q(is_admin=0) & Q(school_class=request_body["class"]))
        for student in students:
            empty_grades = '_._'.join(list('#' * len(grades_list)))
            grade = Grade(student_id=student.id, work_id=work.id, grades=empty_grades, max_score=0, score=0, exercises=0)
            grade.save()
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)
    return HttpResponse(
        json.dumps({'state': 'success', 'message': 'Работа успешно добавлена.', 'details': {}}, ensure_ascii=False), status=200)


# todo: обработка ошибок
@require_http_methods(["POST"])
def update_work(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
    if request.body:
        request_body = json.loads(request.body)
    else:
        return HttpResponse(json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)
    try:
        grades_list = request_body["grades"].replace(',', '.').split()
        max_score = 0
        for grade in grades_list:
            cast = float(grade)
            max_score += cast
        grades = '_._'.join(grades_list)
        work = Work.objects.get(id=request_body["id"])
        old_grades = work.grades
        old_maximum = work.max_score
        work.grades = grades
        work.max_score = max_score
        work.save()
        log = Log(operation='UPDATE', from_table='works', details=f'Изменена работа {request_body["id"]} в таблице works. ["grades": "{old_grades}", "max_score": "{old_maximum}"]')
        log.save()
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)
    return HttpResponse(
        json.dumps({'state': 'success', 'message': 'Работа успешно обновлена.', 'details': {}}, ensure_ascii=False), status=200)


# todo: обработка ошибок
@require_http_methods(["POST"])
def delete_work(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
    if request.body:
        request_body = json.loads(request.body)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=400)
    try:
        work = Work.objects.get(id=request_body["id"])
        log_details = f'Удалена работа из таблицы works. ["id": {work.id} | "name": "{work.name}" | "grades": {", ".join(map(str, work.grades.split("_._")))} | "max_score": "{work.max_score}" | "exercises": "{work.exercises}" | "theme_id": {work.theme_id} | "school_class": {work.school_class}]'
        work.delete()
        log = Log(operation='DELETE', from_table='works', details=log_details)
        log.save()
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)
    return HttpResponse(
        json.dumps({'state': 'success', 'message': 'Работа успешно удалена.', 'details': {}}, ensure_ascii=False),
        status=205)


@require_http_methods(["DELETE"])
def delete_works(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
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
        works = Work.objects.filter(school_class=class_)
        for work in works:
            Log(operation='DELETE', from_table='works',
                details=f'Работа удалена из таблицы works. ["id": {work.id} | "name": "{work.name}" | "grades": {", ".join(map(str, work.grades.split("_._")))} | "max_score": "{work.max_score}" | "exercises": "{work.exercises}" | "theme_id": {work.theme_id} | "school_class": {work.school_class}]').save()
        works.delete()
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)
    return HttpResponse(
        json.dumps({'state': 'success', 'message': 'Все работы успешно удалены.', 'details': {}}, ensure_ascii=False),
        status=205)


@require_http_methods(["POST"])
def update_work_grades(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
    if request.body:
        request_body = json.loads(request.body)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=400)
    global_change = None
    try:
        works = Work.objects.all()
        changes = request_body["changes"]
        formatted_changes = {}
        for change in changes:
            if change['work_id'] not in formatted_changes.keys():
                formatted_changes[change['work_id']] = []
            formatted_changes[change['work_id']].append({'cell_number': change['cell_number'], 'value': change['value']})
        for work_ in formatted_changes.keys():
            work = works.get(id=int(work_))
            grades = Grade.objects.filter(work_id=int(work_))
            work_grades = work.grades
            new_grades = list(map(int, work_grades.split("_._")))
            new_grades_update = []
            delete_ids = []
            add_new = False
            for change in formatted_changes[work_]:
                global_change = {'work_id': work_, 'cell_number': change["cell_number"], 'values': change["value"]}
                cell_number = change["cell_number"]
                if cell_number == 'new':
                    add_new = True
                    new_grades.append(change["value"])
                else:
                    new_grades[int(change["cell_number"])] = change["value"]
                for i in range(len(new_grades)):
                    if new_grades[i] == '0' or new_grades[i] == '-':
                        #new_grades_update.append(0)
                        delete_ids.append(i)
                        continue
                    if (',' in str(new_grades[i])) or ('.' in str(new_grades[i])):
                        return HttpResponse(
                            json.dumps({'state': 'error', 'message': f'Указано недопустимое значение.',
                                        'details': {"student_id": change["student_id"], "work_id": change["work_id"],
                                                    "cell_number": change["cell_number"],
                                                    "cell_name": f'{change["student_id"]}_{change["work_id"]}_{change["cell_number"]}'},
                                        'instance': request.path},
                                       ensure_ascii=False), status=400)
                    cast = int(new_grades[i])
                    if cast < 0:
                        return HttpResponse(
                            json.dumps({'state': 'error', 'message': f'Указано недопустимое значение.',
                                        'details': {"work_id": change["work_id"],
                                                    "cell_number": change["cell_number"],
                                                    "cell_name": f'grade-cell_{change["work_id"]}_{change["cell_number"]}'},
                                        'instance': request.path},
                                       ensure_ascii=False), status=400)
                    else:
                        new_grades_update.append(cast)
            new_grades = list(map(int, new_grades_update))
            log_grades_string = work_grades
            new_grades_string = '_._'.join(list(map(str, new_grades_update)))
            max_score = sum(new_grades)
            exercises = len(new_grades)
            work.grades = new_grades_string
            work.max_score = max_score
            work.exercises = exercises
            if add_new:
                pass
            if delete_ids:
                for grade in grades:
                    old_student_grades = grade.grades.split("_._")
                    # old_student_grades = list(map(int, grade.grades.split("_._")))
                    new_student_grades = []
                    for i in range(len(old_student_grades)):
                        if i in delete_ids:
                            old_student_grades[i] = ""
                        else:
                            new_student_grades.append(old_student_grades[i])
                    real_grades = []
                    for i in range(len(new_student_grades)):
                        if new_student_grades[i] == '#':
                            pass
                        elif new_student_grades[i] == '-':
                            max_score -= int(new_grades_update[i])
                            exercises -= 1
                        else:
                            real_grades.append(float(new_student_grades[i]))
                    score = sum(real_grades)
                    new_student_grades_string = '_._'.join(new_student_grades)
                    grade.score = score
                    grade.max_score = max_score
                    grade.exercises = exercises
                    grade.grades = new_student_grades_string
                    log_details = f'Обновлены оценки у ученика {grade.student_id} в работе {work.id}. ["old_grades": {grade.grades}, "new_grades": {new_grades_string}, "old_score": {grade.score}, "new_score": {score}, "old_exercises": {grade.exercises}, "new_exercises": {exercises}]'
                    grade.save()
                    log = Log(operation='UPDATE', from_table='grades', details=log_details)
                    log.save()
            log_details = f'Обновлены максимальные оценки в работе {work.id}. ["old_grades": {log_grades_string}, "new_grades": {new_grades_string}]'
            work.save()
            log = Log(operation='UPDATE', from_table='works', details=log_details)
            log.save()
        return HttpResponse(
            json.dumps({'state': 'success', 'message': 'Оценки успешно обновлены.', 'details': {}}, ensure_ascii=False),
            status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except ValueError as e:
        change = global_change
        return HttpResponse(json.dumps({'state': 'error', 'message': f'Указаны недопустимые символы.',
                                        'details': {"work_id": change["work_id"],
                                                    "cell_number": change["cell_number"],
                                                    "cell_name": f'grade-cell_{change["work_id"]}_{change["cell_number"]}'},
                                        'instance': request.path},
                                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)
# endregion


# region [student region]
@require_http_methods(["GET"])
def get_student(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
    id_ = get_variable("id", request)
    if not id_:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано id ученика.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    try:
        logged_user = Student.objects.get(id=request.session["id"])
        if not (logged_user.is_admin == 1 or logged_user.id == id_):
            return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=403)
        student = Student.objects.get(id=id_)
        student_info = {"id": student.id, "name": student.name, "login": student.login, "password": student.password,
                        "level": student.level, "mana_earned": student.mana_earned,
                        "last_homework_id": student.last_homework_id, "last_classwork_id": student.last_classwork_id}
        return HttpResponse(
            json.dumps({'state': 'success', 'message': '', 'details': {'student': student_info}}, ensure_ascii=False),
            status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


@require_http_methods(["GET"])
def get_students(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
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
        students = Student.objects.filter(Q(is_admin=0) & Q(school_class=int(class_)))
        students_list = []
        for student in students:
            student_info = {"id": student.id, "name": student.name, "login": student.login, "password": student.password,
                            "experience": student.experience, "mana_earned": student.mana_earned,
                            "last_homework_id": student.last_homework_id, "last_classwork_id": student.last_classwork_id}
            students_list.append(student_info)
        return HttpResponse(
            json.dumps({'state': 'success', 'message': '', 'details': {'students': students_list}}, ensure_ascii=False),
            status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


# todo: обработка ошибок
@require_http_methods(["POST"])
def create_student(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
    if request.body:
        request_body = json.loads(request.body)
    else:
        return HttpResponse(json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)
    try:
        students = Student.objects.all()
        if students:
            last_student = students.latest("id")
            last_id = last_student.id
        else:
            last_id = 0
        id_, login_, password_ = login_password_creator(request_body["name"], last_id + 1)
        student = Student(id=last_id + 1, name=request_body["name"], login=login_, password=password_, school_class=request_body["class"])
        student.save()
        log = Log(operation='INSERT', from_table='students', details='Добавлен новый ученик в таблицу students.')
        log.save()
        works = Work.objects.all()
        for work in works:
            grades = work.grades.split('_._')
            empty_grades = '_._'.join(list('#'*len(grades)))
            grade = Grade(student_id=student.id, work_id=work.id, grades=empty_grades, max_score=0, score=0, exercises=0)
            grade.save()
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)
    return HttpResponse(
        json.dumps({'state': 'success', 'message': 'Ученик успешно добавлен.', 'details': {}}, ensure_ascii=False),
        status=200)


# todo: обработка ошибок
@require_http_methods(["POST"])
def delete_student(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
    if request.body:
        request_body = json.loads(request.body)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=400)
    try:
        student = Student.objects.get(id=request_body["id"])
        log_details = f'Удален ученик из таблицы students. ["id": {student.id} | "name": "{student.name}" | "login": {student.login} | "password": {student.password} | "experience": {student.experience} | "mana_earned": {student.mana_earned} | "last_homework_id": {student.last_homework_id} | "last_classwork_id": {student.last_classwork_id} | "school_class": {student.school_class}]'
        student.delete()
        log = Log(operation='DELETE', from_table='students', details=log_details)
        log.save()
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)
    return HttpResponse(
        json.dumps({'state': 'success', 'message': 'Ученик успешно удален.', 'details': {}}, ensure_ascii=False),
        status=205)


# todo: обработка ошибок
@require_http_methods(["DELETE"])
def delete_students(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
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
        students = Student.objects.filter(school_class=int(class_))
        for student in students:
            Log(operation='DELETE', from_table='students',
                details=f'Удален ученик из таблицы students. ["id": {student.id} | "name": "{student.name}" | "login": {student.login} | "password": {student.password} | "level": {student.level} | "mana_earned": {student.mana_earned} | "last_homework_id": {student.last_homework_id} | "last_classwork_id": {student.last_classwork_id} | "school_class": {student.school_class}]').save()
        students.delete()
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)
    return HttpResponse(
        json.dumps({'state': 'success', 'message': 'Все ученики успешно удалены.', 'details': {}}, ensure_ascii=False),
        status=205)


# endregion


# region [grade region]
# todo: внимательно потестить ману, чтобы не генерилось лишнее
@require_http_methods(["POST"])
def insert_grades(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
    if request.body:
        request_body = json.loads(request.body)
    else:
        return HttpResponse(json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)
    global_change = None
    try:
        for change in request_body["changes"]:
            global_change = change
            work = Work.objects.get(id=int(change["work_id"]))
            student = Student.objects.get(id=int(change["student_id"]))
            grade = Grade.objects.get(student_id=student, work_id=work)
            works_grades = list(map(float, work.grades.split("_._")))
            new_grades = grade.grades.split("_._")
            if change["value"] == '':
                change["value"] = '#'
            new_grades[int(change["cell_number"])] = change["value"]
            new_exercises = work.exercises
            if work.exercises < len(new_grades):
                return HttpResponse(
                    json.dumps({'state': 'error', 'message': f'Неверное количество оценок.', 'details': {}, 'instance': request.path},
                               ensure_ascii=False), status=400)
            new_score = 0
            for i in range(len(new_grades)):
                if ',' in new_grades[i]:
                    new_grades[i] = new_grades[i].replace(',', '.')
                if new_grades[i] == '-':
                    works_grades[i] = 0
                    new_exercises -= 1
                    continue
                elif new_grades[i] == '#':
                    cast = 0
                else:
                    cast = float(new_grades[i])
                    if cast < 0:
                        return HttpResponse(
                            json.dumps({'state': 'error', 'message': f'Указано недопустимое значение.', 'details': {"student_id": change["student_id"], "work_id": change["work_id"], "cell_number": change["cell_number"], "cell_name": f'{change["student_id"]}_{change["work_id"]}_{change["cell_number"]}'},
                                        'instance': request.path},
                                       ensure_ascii=False), status=400)
                    if cast > float(works_grades[i]):
                        return HttpResponse(
                            json.dumps({'state': 'error', 'message': f'Указанная оценка больше максимальной.', 'details': {"student_id": change["student_id"], "work_id": change["work_id"], "cell_number": change["cell_number"], "cell_name": f'{change["student_id"]}_{change["work_id"]}_{change["cell_number"]}'},
                                        'instance': request.path},
                                       ensure_ascii=False), status=400)
                new_score += cast
            log_grades_string = grade.grades
            new_max_score = sum(works_grades)
            new_grades_string = '_._'.join(new_grades)
            if grade.score != new_score:
                manas_delete = Mana.objects.filter(Q(student=student) & Q(work=work)).delete()
            theme = Theme.objects.get(id=work.theme_id)
            if theme.type == 0:
                percentage = float(new_score) / float(new_max_score) * 100
                if 0 < percentage <= 25:
                    mana = 1
                elif 25 < percentage <= 50:
                    mana = 2
                elif 50 < percentage <= 75:
                    mana = 3
                elif 75 < percentage <= 100:
                    mana = 4
                else:
                    mana = 0
            elif theme.type == 2:
                score = float(new_score)
                if 0 <= score < 0.9:
                    mana = 0
                elif 0.9 <= score < 2.4:
                    mana = 1
                elif 2.4 <= score <= 3:
                    mana = 2
                else:
                    mana = 0
            elif theme.type == 3:
                score = float(new_score)
                if score == 1:
                    mana = 1
                elif score == 2:
                    mana = 2
                elif score == 3:
                    mana = 3
                elif score >= 4:
                    mana = 4
                else:
                    mana = 0
            else:
                mana = 0
            if mana == 4:
                seed = random.randint(0, 1)
                if seed:
                    green = 4
                    blue = 0
                else:
                    green = 0
                    blue = 4
            elif mana == 3:
                green = random.randint(0, 3)
                blue = mana - green
            elif mana == 2:
                if theme.type == 2:
                    seed = random.randint(0, 1)
                    if seed:
                        green = 2
                        blue = 0
                    else:
                        green = 0
                        blue = 2
                else:
                    green = random.randint(0, 2)
                    blue = mana - green
            elif mana == 1:
                green = random.randint(0, 1)
                blue = mana - green
            else:
                green = 0
                blue = 0
            if grade.score != new_score:
                for i in range(0, green):
                    mana = Mana(student=student, work=work, color='green')
                    mana.save()
                for i in range(0, blue):
                    mana = Mana(student=student, work=work, color='blue')
                    mana.save()
            grade.grades = new_grades_string
            grade.max_score = new_max_score
            grade.score = new_score
            grade.exercises = new_exercises
            log_details = f'Обновлены оценки для ученика {student.id} в работе {work.id}. ["old_grades": {log_grades_string}, "new_grades": {new_grades_string}]'
            grade.save()
            #amount_score = Grade.objects.filter(student=student).aggregate(Sum('score'))
            log = Log(operation='UPDATE', from_table='grades', details=log_details)
            log.save()
        return HttpResponse(json.dumps({'state': 'success', 'message': 'Оценки успешно обновлены.', 'details': {}}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except ValueError:
        change = global_change
        return HttpResponse(json.dumps({'state': 'error', 'message': f'Указаны недопустимые символы.', 'details': {"student_id": change["student_id"], "work_id": change["work_id"], "cell_number": change["cell_number"], "cell_name": f'{change["student_id"]}_{change["work_id"]}_{change["cell_number"]}'}, 'instance': request.path},
                                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


# todo: обработка херовых значений в request_body["works"]
@require_http_methods(["POST"])
def get_grades(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
    if request.body:
        request_body = json.loads(request.body)
    else:
        return HttpResponse(json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)
    try:
        colors = {"0-25": "#ea9999", "25-50": "#f9cb9c", "50-75": "#ffe599", "75-100": "#b6d7a8", "None": "#ffffff"}
        works_order = list(map(int, request_body["works"]))
        grades = Grade.objects.filter(work_id__in=works_order)
        students = Student.objects.filter(Q(is_admin=0) & Q(school_class=request_body["class"]))
        students_grades = {}
        students_list = {}
        #students_lvls = {}
        #lvl_theme = {}
        #exp_list = Grade.objects.filter(Q(work__theme__type=0) & Q(student__school_class=request_body["class"])).select_related('work', 'work__theme').values_list('student_id', 'work__theme_id', 'work_id', 'score').order_by('student_id', 'work__theme_id', 'work__id')
        #print(exp_list)
        #for exp in exp_list:
        #    if exp[0] not in students_lvls.keys():
        #        students_lvls[exp[0]] = 1

        for student in students:
            full_score = grades.filter(student_id=student.id).aggregate(Sum('score'))['score__sum']
            max_full_score = grades.filter(student_id=student.id).aggregate(Sum('max_score'))['max_score__sum']
            if max_full_score != 0:
                percentage_full_score = round(full_score / max_full_score * 100, 1)
                if percentage_full_score <= 25:
                    full_score_color = colors["0-25"]
                elif percentage_full_score <= 50:
                    full_score_color = colors["25-50"]
                elif percentage_full_score <= 75:
                    full_score_color = colors["50-75"]
                elif percentage_full_score <= 100:
                    full_score_color = colors["75-100"]
                else:
                    full_score_color = colors["None"]
            else:
                percentage_full_score = ""
                full_score_color = colors["None"]
            students_list[student.id] = [student.name, percentage_full_score, full_score_color]
            student_grades = {}
            for work in works_order:
                current_student_grades = grades.get(work_id=work, student_id=student.id)
                score = current_student_grades.score
                max_score = current_student_grades.max_score
                current_student_grades_list = current_student_grades.grades.split("_._")
                is_empty = True
                for i in range(len(current_student_grades_list)):
                    if current_student_grades_list[i] == '#':
                        current_student_grades_list[i] = ''
                    else:
                        is_empty = False
                if is_empty:
                    score = ""
                if max_score == 0:
                    color = colors["None"]
                else:
                    percentage = float(score) / float(max_score) * 100
                    if percentage <= 25:
                        color = colors["0-25"]
                    elif percentage <= 50:
                        color = colors["25-50"]
                    elif percentage <= 75:
                        color = colors["50-75"]
                    elif percentage <= 100:
                        color = colors["75-100"]
                    else:
                        color = colors["None"]
                student_result = {"grades": current_student_grades_list, "score": score, "color": color}
                student_grades[str(work)] = student_result
            students_grades[str(student.id)] = student_grades
        return HttpResponse(json.dumps({'state': 'success', 'message': 'Оценки успешно возвращены.', 'details': {"grades": students_grades, "students": students_list}}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


@require_http_methods(["GET"])
def get_mana_waiters(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                print({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path})
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            print({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path})
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        print({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path})
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
    class_ = get_variable("class", request)
    if not class_:
        print({'state': 'error', 'message': f'Не указан класс ученика.', 'details': {}, 'instance': request.path})
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Не указан класс ученика.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    else:
        if class_ not in ['4', '5', '6']:
            print({'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {}, 'instance': request.path})
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
    try:
        waiters = []
        students = Student.objects.filter(Q(is_admin=0) & Q(school_class=int(class_)))
        for student in students:
            manas = Mana.objects.filter(Q(student=student.id) & Q(is_given=0))
            green = manas.filter(color='green').aggregate(Count('id'))
            blue = manas.filter(color='blue').aggregate(Count('id'))
            waiter = {"id": student.id, "name": student.name, "green": green["id__count"], "blue": blue["id__count"]}
            if int(green["id__count"]) + int(blue["id__count"]) > 0:
                waiters.append(waiter)
        print({'state': 'success', 'message': 'Ожидающие ману успешно получены.', 'details': {'waiters': waiters}})
        return HttpResponse(json.dumps({'state': 'success', 'message': 'Ожидающие ману успешно получены.', 'details': {'waiters': waiters}}, ensure_ascii=False), status=200)
    except KeyError as e:
        print({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path})
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        print({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path})
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


@require_http_methods(["POST"])
def get_some_mana_waiters(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
    if request.body:
        request_body = json.loads(request.body)
    else:
        return HttpResponse(json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)
    try:
        waiters = []
        for student in request_body["students"]:
            student = Student.objects.get(id=int(student))
            mana_earned = int(student.mana_earned)
            grades = Grade.objects.filter(student_id=student)
            mana = int(grades.aggregate(Sum('mana'))['mana__sum'])
            waiting_mana = mana - mana_earned
            waiter = {f'{student.id}': {'mana': waiting_mana, 'name': student.name}}
            if waiting_mana > 0:
                waiters.append(waiter)
        return HttpResponse(json.dumps({'state': 'success', 'message': 'Ожидающие ману успешно получены.', 'details': {'waiters': waiters}}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


# todo: обработка ошибок(выдача маны > чем возможно)
@require_http_methods(["POST"])
def give_mana(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
    id_ = get_variable("id", request)
    mana = get_variable("mana", request)
    if not id_:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    if not mana:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано количество маны.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    try:
        student = Student.objects.get(id=int(id_))
        old_mana = int(student.mana_earned)
        new_mana = old_mana + int(mana)
        student.mana_earned = new_mana
        log_details = f'Обновлена мана для ученика {student.id}. ["old_mana": {old_mana}, "new_mana": {new_mana}]'
        student.save()
        log = Log(operation='UPDATE', from_table='student', details=log_details)
        log.save()
        return HttpResponse(json.dumps({'state': 'success', 'message': 'Мана успешно выдана.', 'details': {}}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


@require_http_methods(["POST"])
def give_mana_all(request):
    if request.session:
        if "id" in request.session.keys():
            student = Student.objects.get(id=request.session["id"])
            if not student.is_admin:
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=403)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
    id_ = get_variable("id", request)
    if not id_:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    try:
        #student = Student.objects.get(id=int(id_))
        manas = Mana.objects.filter(student=int(id_))
        log_details = f'Обновлена мана для ученика {student.id}.'
        for mana in manas:
            mana.is_given = 1
        manas.save()
        log = Log(operation='UPDATE', from_table='mana', details=log_details)
        log.save()
        return HttpResponse(json.dumps({'state': 'success', 'message': 'Мана успешно выдана.', 'details': {}}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)
# endregion


# region [sessions region]
@require_http_methods(["POST"])
def login(request):
    if "id" in request.session.keys():
        return HttpResponse(
            json.dumps({'state': 'error', 'message': 'Вы уже авторизованы.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=403)
    if request.body:
        request_body = json.loads(request.body)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=400)
    try:
        login_ = request_body["login"]
        password_ = request_body["password"]
        user = Student.objects.get(login=login_)
        if not user:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Пользователь не существует.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
        if user.password == password_:
            request.session['login'] = login_
            request.session['id'] = user.id
            permissions = int(user.is_admin)
            id_ = user.id
        else:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Неверный пароль.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=400)
        return HttpResponse(
            json.dumps({'state': 'success', 'message': 'Вход успешно выполнен.', 'details': {'permissions': permissions, "id": id_}}, ensure_ascii=False),
            status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)


@require_http_methods(["GET"])
def logout(request):
    if "id" in request.session.keys():
        request.session.delete()
        return HttpResponse(
            json.dumps({'state': 'success', 'message': 'Не авторизован.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=200)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': 'Не авторизован.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=401)


@require_http_methods(["GET"])
def me(request):
    if "id" in request.session.keys():
        id_ = request.session['id']
        student = Student.objects.get(id=id_)
        if student.is_admin:
            admin = Admin.objects.get(student_id=student)
            return HttpResponse(
                json.dumps({'state': 'success', 'message': 'Авторизирован.',
                            'details': {"id": id_, "is_admin": student.is_admin, "permissions": admin.permissions, "name": student.name}}, ensure_ascii=False),
                status=200)
        else:
            return HttpResponse(
                json.dumps({'state': 'success', 'message': 'Авторизирован.', 'details': {"id": id_, "is_admin": student.is_admin, "name": student.name}}, ensure_ascii=False),
                status=200)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': 'Не авторизован.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=401)
# endregion
