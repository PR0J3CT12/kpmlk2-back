from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from kpm.apps.works.models import Work
from kpm.apps.logs.models import Log
from kpm.apps.users.models import User
from kpm.apps.themes.models import Theme
from kpm.apps.grades.models import Grade
import json
from django.db.models import Sum, Q, Count
from kpm.apps.users.permissions import IsAdmin
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.works.docs import *
from kpm.apps.works.functions import *


@swagger_auto_schema(method='GET', operation_summary="Получение списка работ.",
                     manual_parameters=[class_param],
                     responses=get_works_responses)
@api_view(["GET"])
@permission_classes([IsAdmin])
def get_works(request):
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
        filter_ = get_variable("filter", request)
        filter_value = get_variable("filter_value", request)
        works = Work.objects.filter(school_class=int(class_)).select_related("theme")
        if filter_:
            if not filter_value:
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Указан фильтр, но не указано значение фильтра.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=404)
        if not filter_:
            pass
        elif filter_ == 'theme':
            works = works.filter(theme_id=filter_value)
        elif filter_ == 'type':
            works = works.filter(theme__type=filter_value)
        elif filter_ == 'homework':
            works = works.filter(theme__type=filter_value)
        else:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Некорректное значение фильтра.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        works_list = []
        for work in works:
            works_list.append({
                "id": work.id,
                "name": work.name,
                "grades": work.grades.split('_._'),
                "max_score": work.max_score,
                "exercises": work.exercises,
                "theme_id": work.theme_id,
                "theme_name": work.theme.name,
                "theme_type": work.theme.type,
                "is_homework": work.theme.is_homework
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


@swagger_auto_schema(method='GET', operation_summary="Получение работы.",
                     manual_parameters=[id_param],
                     responses=get_work_responses)
@api_view(["GET"])
@permission_classes([IsAdmin])
def get_work(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        work = Work.objects.get(id=id_).select_related("theme")
        return HttpResponse(
            json.dumps({
                "id": work.id,
                "name": work.name,
                "grades": work.grades.split('_._'),
                "max_score": work.max_score,
                "exercises": work.exercises,
                "theme_id": work.theme_id,
                "theme_name": work.theme.name,
                "theme_type": work.theme.type,
                "is_homework": work.theme.is_homework
            }, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Работа не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='POST', operation_summary="Создание работы.",
                     request_body=create_work_request_body,
                     responses=create_work_responses)
@api_view(["POST"])
@permission_classes([IsAdmin])
def create_work(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)
        grades_list = request_body["grades"]
        max_score = 0
        for grade in grades_list:
            if not is_number(grade):
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Введены некорректные оценки.', 'details': {}, 'instance': request.path},
                        ensure_ascii=False), status=404)
            if float(grade) < 0:
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Введены некорректные оценки.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=404)
            cast = float(grade)
            max_score += cast
        grades = '_._'.join(grades_list)
        theme = Theme.objects.get(id=request_body["theme_id"])
        if request_body["class"] not in ['4', '5', '6', 4, 5, 6]:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        work = Work(name=request_body["name"], grades=grades, theme=theme, max_score=max_score, exercises=len(grades_list), school_class=request_body["class"])
        work.save()
        log = Log(operation='INSERT', from_table='works', details='Добавлена новая работа в таблицу works.')
        log.save()
        students = User.objects.filter(Q(is_admin=0) & Q(school_class=request_body["class"]))
        for student in students:
            empty_grades = '_._'.join(list('#' * len(grades_list)))
            grade = Grade(user_id=student.id, work_id=work.id, grades=empty_grades, max_score=0, score=0, exercises=0)
            grade.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=404)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Тема не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='PATCH', operation_summary="Изменение работы.",
                     request_body=update_work_request_body,
                     responses=update_work_responses)
@api_view(["PATCH"])
@permission_classes([IsAdmin])
def update_work(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)
        work = Work.objects.get(id=request_body["id"])
        if "grades" in request_body.keys():
            grades_list = request_body["grades"]
            max_score = 0
            for grade in grades_list:
                if not is_number(grade):
                    return HttpResponse(
                        json.dumps(
                            {'state': 'error', 'message': f'Введены некорректные оценки.', 'details': {},
                             'instance': request.path},
                            ensure_ascii=False), status=404)
                if float(grade) < 0:
                    return HttpResponse(
                        json.dumps(
                            {'state': 'error', 'message': f'Введены некорректные оценки.', 'details': {},
                             'instance': request.path},
                            ensure_ascii=False), status=404)
                cast = float(grade)
                max_score += cast
            grades = '_._'.join(grades_list)
            old_grades = work.grades
            old_maximum = work.max_score
            work.grades = grades
            work.max_score = max_score
            work.save()
            log = Log(operation='UPDATE', from_table='works', details=f'Изменены оценки в работе {request_body["id"]} в таблице works. ["grades": "{old_grades}", "max_score": "{old_maximum}"]')
            log.save()
        if "name" in request_body.keys():
            old_name = work.name
            new_name = request_body["name"]
            work.name = new_name
            work.save()
            log = Log(operation='UPDATE', from_table='works',
                      details=f'Изменено имя работы {request_body["id"]} в таблице works. ["name": "{old_name}"]')
            log.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=404)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Работа не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='DELETE', operation_summary="Удаление работы.",
                     manual_parameters=[id_param],
                     responses=delete_work_responses)
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_work(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        work = Work.objects.get(id=id_)
        log_details = f'Удалена работа из таблицы works. ["id": {work.id} | "name": "{work.name}" | "grades": {", ".join(map(str, work.grades.split("_._")))} | "max_score": "{work.max_score}" | "exercises": "{work.exercises}" | "theme_id": {work.theme_id} | "school_class": {work.school_class}]'
        work.delete()
        log = Log(operation='DELETE', from_table='works', details=log_details)
        log.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Работа не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='DELETE', operation_summary="Удаление работ.",
                     manual_parameters=[class_param],
                     responses=delete_work_responses)
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_works(request):
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
        works = Work.objects.filter(school_class=class_)
        if not works:
            return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
        for work in works:
            Log(operation='DELETE', from_table='works',
                details=f'Работа удалена из таблицы works. ["id": {work.id} | "name": "{work.name}" | "grades": {", ".join(map(str, work.grades.split("_._")))} | "max_score": "{work.max_score}" | "exercises": "{work.exercises}" | "theme_id": {work.theme_id} | "school_class": {work.school_class}]').save()
        works.delete()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


"""
@api_view(["PATCH"])
@permission_classes([IsAdmin])
def update_work_grades(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=400)
        global_change = None
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
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
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
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)
"""""