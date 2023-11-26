from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from kpm.apps.works.models import Work, Exam
from kpm.apps.logs.models import Log
from kpm.apps.users.models import User
from kpm.apps.themes.models import Theme
from kpm.apps.grades.models import Grade
import json
from django.db.models import Sum, Q, Count
from kpm.apps.users.permissions import *
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.works.docs import *
from kpm.apps.works.functions import *
from django.utils import timezone


@swagger_auto_schema(method='GET', operation_summary="Получение списка работ.",
                     manual_parameters=[class_param, theme_param, type_param],
                     responses=get_works_responses,
                     operation_description=operation_description)
@api_view(["GET"])
@permission_classes([IsAdmin])
def get_works(request):
    try:
        class_ = get_variable("class", request)
        theme = get_variable("theme", request)
        type_ = get_variable("type", request)
        if class_ not in ['4', '5', '6', 4, 5, 6]:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс учеников.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        works = Work.objects.filter(school_class=int(class_)).exclude(type=5).select_related("theme").order_by('-id')
        if (theme is not None) and (theme != ''):
            works = works.filter(theme_id=theme)
        if type_ in ['0', '1', '2', '3', '4', '5', '6', '9']:
            works = works.filter(type=type_)
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
                "work_type": work.type,
                "is_homework": work.is_homework
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
                     responses=get_work_responses,
                     operation_description=operation_description)
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
                "type": work.type,
                "is_homework": work.is_homework
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
                     responses=create_work_responses,
                     operation_description=operation_description)
@api_view(["POST"])
@permission_classes([IsAdmin])
def create_work(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        if request_body["type"] not in [0, 1, 2, 3, 4, 5, 6, 9]:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс тип работы.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        if request_body["type"] == 2:
            grades_list = ["1", "1", "1"]
        else:
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

        theme = Theme.objects.get(id=request_body["theme_id"])
        if request_body["class"] not in ['4', '5', '6', 4, 5, 6]:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        if request_body["type"] in [0, 5, 6, 7]:
            is_homework = True
        else:
            is_homework = False
        students = User.objects.filter(Q(is_admin=0) & Q(school_class=request_body["class"]))
        if request_body["type"] not in [3, 5]:
            work = Work(name=request_body["name"], grades=grades, theme=theme, max_score=max_score,
                        exercises=len(grades_list), school_class=request_body["class"], type=request_body["type"],
                        is_homework=is_homework)
            log = Log(operation='INSERT', from_table='works', details='Добавлена новая работа в таблицу works.')
            work.save()
            log.save()
            for student in students:
                empty_grades = '_._'.join(list('#' * len(grades_list)))
                grade = Grade(user=student, work_id=work.id, grades=empty_grades, max_score=0, score=0, exercises=0)
                grade.save()
        elif request_body["type"] == 5:
            work = Work(name=request_body["name"], grades=grades, theme=theme, max_score=max_score,
                        exercises=len(grades_list), school_class=request_body["class"], type=request_body["type"],
                        is_homework=is_homework)
            log = Log(operation='INSERT', from_table='works', details='Добавлена новая работа в таблицу works.')
            grades_list_2007 = request_body["grades_2007"]
            if len(grades_list_2007) != len(grades_list):
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Введено разное количество оценок.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=404)
            max_score_2007 = 0
            for grade in grades_list_2007:
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
                max_score_2007 += cast
            grades_2007 = '_._'.join(grades_list_2007)
            work_2007 = Work(name=request_body["name"], grades=grades_2007, theme=theme, max_score=max_score_2007,
                             exercises=len(grades_list_2007), school_class=request_body["class"], type=7,
                             is_homework=is_homework)
            work.save()
            work_2007.save()
            log.save()
            for student in students:
                empty_grades_2007 = '_._'.join(list('#' * len(grades_list_2007)))
                grade = Grade(user=student, work_id=work_2007.id, grades=empty_grades_2007, max_score=0, score=0,
                              exercises=0)
                grade.save()
            link = Exam(work=work, work_2007=work_2007)
            link.save()
            for student in students:
                empty_grades = '_._'.join(list('#' * len(grades_list)))
                grade = Grade(user=student, work_id=work.id, grades=empty_grades, max_score=0, score=0, exercises=0)
                grade.save()
        else:
            work = Work(name=request_body["name"], grades=grades, theme=theme, max_score=max_score,
                        exercises=len(grades_list), school_class=request_body["class"], type=request_body["type"],
                        is_homework=is_homework)
            log = Log(operation='INSERT', from_table='works', details='Добавлена новая работа в таблицу works.')
            grades_list_2007 = request_body["grades_2007"]
            if len(grades_list_2007) != len(grades_list):
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Введено разное количество оценок.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=404)
            max_score_2007 = 0
            for grade in grades_list_2007:
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
                max_score_2007 += cast
            grades_2007 = '_._'.join(grades_list_2007)
            work_2007 = Work(name=request_body["name"], grades=grades_2007, theme=theme, max_score=max_score_2007,
                             exercises=len(grades_list_2007), school_class=request_body["class"], type=8,
                             is_homework=is_homework)
            work.save()
            work_2007.save()
            log.save()
            for student in students:
                empty_grades_2007 = '_._'.join(list('#' * len(grades_list_2007)))
                grade = Grade(user=student, work_id=work_2007.id, grades=empty_grades_2007, max_score=0, score=0,
                              exercises=0)
                grade.save()
            link = Exam(work=work, work_2007=work_2007)
            link.save()
            for student in students:
                empty_grades = '_._'.join(list('#' * len(grades_list)))
                grade = Grade(user=student, work_id=work.id, grades=empty_grades, max_score=0, score=0, exercises=0)
                grade.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
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
                     responses=update_work_responses,
                     operation_description=operation_description)
@api_view(["PATCH"])
@permission_classes([IsAdmin])
def update_work(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
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
            work.updated_at = timezone.now()
            work.save()
            log = Log(operation='UPDATE', from_table='works',
                      details=f'Изменены оценки в работе {request_body["id"]} в таблице works. ["grades": "{old_grades}", "max_score": "{old_maximum}"]')
            log.save()
        if "name" in request_body.keys():
            old_name = work.name
            new_name = request_body["name"]
            work.name = new_name
            work.updated_at = timezone.now()
            work.save()
            log = Log(operation='UPDATE', from_table='works',
                      details=f'Изменено имя работы {request_body["id"]} в таблице works. ["name": "{old_name}"]')
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


@swagger_auto_schema(method='DELETE', operation_summary="Удаление работы.",
                     manual_parameters=[id_param],
                     responses=delete_work_responses,
                     operation_description=operation_description)
@api_view(["DELETE"])
@permission_classes([IsTierTwo])
def delete_work(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        work = Work.objects.get(id=id_)
        type_ = work.type
        if type_ == 5:
            link = Exam.objects.get(work=work)
            work_ = link.work_2007
            link.delete()
            work_.delete()
            log_details = f'Удалена работа из таблицы works. ["id": {work_.id} | "name": "{work_.name}" | "grades": {", ".join(map(str, work_.grades.split("_._")))} | "max_score": "{work_.max_score}" | "exercises": "{work_.exercises}" | "theme_id": {work_.theme_id} | "school_class": {work_.school_class} | "type": {work_.type} | "is_homework": {work_.is_homework}]'
            log = Log(operation='DELETE', from_table='works', details=log_details)
            log.save()
        elif type_ == 7:
            link = Exam.objects.get(work_2007=work)
            work_ = link.work
            link.delete()
            work_.delete()
            log_details = f'Удалена работа из таблицы works. ["id": {work_.id} | "name": "{work_.name}" | "grades": {", ".join(map(str, work_.grades.split("_._")))} | "max_score": "{work_.max_score}" | "exercises": "{work_.exercises}" | "theme_id": {work_.theme_id} | "school_class": {work_.school_class} | "type": {work_.type} | "is_homework": {work_.is_homework}]'
            log = Log(operation='DELETE', from_table='works', details=log_details)
            log.save()
        log_details = f'Удалена работа из таблицы works. ["id": {work.id} | "name": "{work.name}" | "grades": {", ".join(map(str, work.grades.split("_._")))} | "max_score": "{work.max_score}" | "exercises": "{work.exercises}" | "theme_id": {work.theme_id} | "school_class": {work.school_class} | "type": {work.type} | "is_homework": {work.is_homework}]'
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
                     responses=delete_work_responses,
                     operation_description=operation_description)
@api_view(["DELETE"])
@permission_classes([IsTierTwo])
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
                details=f'Работа удалена из таблицы works. ["id": {work.id} | "name": "{work.name}" | "grades": {", ".join(map(str, work.grades.split("_._")))} | "max_score": "{work.max_score}" | "exercises": "{work.exercises}" | "theme_id": {work.theme_id} | "school_class": {work.school_class} | "type": {work.type} | "is_homework": {work.is_homework}]').save()
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