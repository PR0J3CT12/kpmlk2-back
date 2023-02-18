from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .customfunctions import get_variable
from kpm.apps.works.models import Work
from kpm.apps.logs.models import Log
from kpm.apps.users.models import User
from kpm.apps.themes.models import Theme
from kpm.apps.grades.models import Grade
import json
from django.db.models import Sum, Q, Count
from kpm.apps.users.permissions import IsAdmin


@api_view(["GET"])
@permission_classes([IsAdmin])
def get_works_sorted_by_theme(request):
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
        themes_list = []
        for theme in themes_dict.keys():
            tmp = []
            tmp_dict = {}
            for work in themes_dict[theme]:
                tmp.append(work)
            tmp_dict["theme"] = theme
            tmp_dict["works"] = tmp
            themes_list.append(tmp_dict)
        return HttpResponse(
            json.dumps({'state': 'success', 'message': 'Работы получены.', 'details': {'themes': themes_list}}, ensure_ascii=False),
            status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


@api_view(["GET"])
@permission_classes([IsAdmin])
def get_works(request):
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
            json.dumps({'state': 'success', 'message': 'Работы получены.', 'details': {'works': works_list}}, ensure_ascii=False),
            status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


@api_view(["POST"])
@permission_classes([IsAdmin])
def get_some_works(request):
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


@api_view(["GET"])
@permission_classes([IsAdmin])
def get_works_id(request):
    filter_ = get_variable("filter", request)
    param = get_variable("param", request)
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
            json.dumps({'state': 'success', 'message': f'ID работ получены.', 'details': {'works': works_id_list}},
                       ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)


# todo: обработка ошибок
@api_view(["POST"])
@permission_classes([IsAdmin])
def create_work(request):
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
        students = User.objects.filter(Q(is_admin=0) & Q(school_class=request_body["class"]))
        for student in students:
            empty_grades = '_._'.join(list('#' * len(grades_list)))
            grade = Grade(student_id=student.id, work_id=work.id, grades=empty_grades, max_score=0, score=0, exercises=0)
            grade.save()
        return HttpResponse(
            json.dumps({'state': 'success', 'message': 'Работа успешно добавлена.', 'details': {}}, ensure_ascii=False),
            status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)


# todo: обработка ошибок
@api_view(["PATCH"])
@permission_classes([IsAdmin])
def update_work(request):
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
        return HttpResponse(
            json.dumps({'state': 'success', 'message': 'Работа успешно обновлена.', 'details': {}}, ensure_ascii=False),
            status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)


# todo: обработка ошибок
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_work(request):
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
        return HttpResponse(
            json.dumps({'state': 'success', 'message': 'Работа успешно удалена.', 'details': {}}, ensure_ascii=False),
            status=205)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_works(request):
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
        return HttpResponse(
            json.dumps({'state': 'success', 'message': 'Все работы успешно удалены.', 'details': {}},
                       ensure_ascii=False),
            status=205)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


@api_view(["PATCH"])
@permission_classes([IsAdmin])
def update_work_grades(request):
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
