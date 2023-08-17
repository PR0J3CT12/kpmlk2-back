from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from kpm.apps.users.permissions import IsAdmin
from .functions import get_variable, mana_generation
from kpm.apps.logs.models import Log
from kpm.apps.users.models import User
from kpm.apps.works.models import Work
from kpm.apps.themes.models import Theme
from kpm.apps.grades.models import Grade, Mana
import json
from django.db.models import Sum, Q, Count
import random
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.grades.docs import *


# todo: внимательно потестить ману, чтобы не генерилось лишнее(в том числе когда вносят новые оценки и удаляется старая мана)
@swagger_auto_schema(method='POST', operation_summary="Проставить оценки.",
                     request_body=insert_grades_request_body,
                     responses=insert_grades_responses)
@api_view(["POST"])
@permission_classes([IsAdmin])
def insert_grades(request):
    global_change = None
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)
        for change in request_body["changes"]:
            global_change = change
            work = Work.objects.get(id=int(change["work_id"]))
            student = User.objects.get(id=int(change["user_id"]))
            grade = Grade.objects.get(student_id=student, work_id=work)
            work_grades = list(map(float, work.grades.split("_._")))
            new_max_score = sum(work_grades)
            new_grades = grade.grades.split("_._")
            new_exercises = work.exercises
            new_score = 0
            if change["value"] == '':
                change["value"] = '#'
            new_grades[int(change["cell_number"])] = change["value"]
            if work.exercises < len(new_grades):
                return HttpResponse(
                    json.dumps({'state': 'error', 'message': f'Неверное количество оценок.', 'details': {}, 'instance': request.path},
                               ensure_ascii=False), status=400)
            for i in range(len(new_grades)):
                if ',' in new_grades[i]:
                    new_grades[i] = new_grades[i].replace(',', '.')
                if new_grades[i] == '-':
                    work_grades[i] = 0
                    new_exercises -= 1
                    new_max_score -= work_grades[i]
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
                    if cast > float(work_grades[i]):
                        return HttpResponse(
                            json.dumps({'state': 'error', 'message': f'Указанная оценка больше максимальной.', 'details': {"student_id": change["student_id"], "work_id": change["work_id"], "cell_number": change["cell_number"], "cell_name": f'{change["student_id"]}_{change["work_id"]}_{change["cell_number"]}'},
                                        'instance': request.path},
                                       ensure_ascii=False), status=400)
                new_score += cast
            log_grades_string = grade.grades
            new_grades_string = '_._'.join(new_grades)
            if grade.score != new_score:
                manas_delete = Mana.objects.filter(Q(student=student) & Q(work=work))
                manas_delete.delete()
            green, blue = mana_generation(int(work.theme.type), new_score, new_max_score)
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
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except ValueError:
        change = global_change
        return HttpResponse(json.dumps({'state': 'error', 'message': f'Указаны недопустимые символы.', 'details': {"student_id": change["student_id"], "work_id": change["work_id"], "cell_number": change["cell_number"], "cell_name": f'{change["student_id"]}_{change["work_id"]}_{change["cell_number"]}'}, 'instance': request.path},
                                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


# todo: обработка херовых значений в request_body["works"]
@swagger_auto_schema(method='GET', operation_summary="Получить оценки.",
                     manual_parameters=[class_param, theme_param, type_param],
                     responses=get_grades_responses)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_grades(request):
    try:
        class_ = get_variable("class", request)
        theme = get_variable("theme", request)
        type_ = get_variable("type", request)
        if class_ not in ['4', '5', '6']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс учеников.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        grades = Grade.objects.filter(user__school_class=int(class_))
        if type_ in ['0', '1', '2', '3', '4', '5', '6', '7']:
            grades = grades.filter(user__school_class=int(class_), work__theme__type=int(type_))
        if theme:
            theme_id = int(theme)
            grades = grades.filter(user__school_class=int(class_), work__theme__id=theme_id)
        works_list = grades.distinct('work').values_list('work', flat=True)
        works = Work.objects.filter(id__in=works_list)
        works_data = []
        for work in works:
            works_data.append({'id': work.id, 'name': work.name, 'max_score': work.max_score, 'grades': list(map(int, work.grades.split("_._")))})
        students = User.objects.filter(Q(is_admin=0) & Q(school_class=int(class_)))
        students_data = []
        for student in students:
            student_object = {'id': student.id, 'name': student.name, 'experience': student.experience, 'grades': []}
            full_score = grades.filter(user_id=student.id).aggregate(Sum('score'))['score__sum']
            max_full_score = grades.filter(user_id=student.id).aggregate(Sum('max_score'))['max_score__sum']
            if max_full_score != 0:
                percentage_full_score = round(full_score / max_full_score * 100, 1)
            else:
                percentage_full_score = ""
            student_object['percentage_full_score'] = percentage_full_score
            for work in works:
                current_student_grades = grades.get(work=work, user_id=student.id)
                score = current_student_grades.score
                max_score = current_student_grades.max_score
                if float(max_score) != 0:
                    percentage = str(round(float(score) / float(max_score) * 100, 1))
                else:
                    percentage = ""
                current_student_grades_list = current_student_grades.grades.split("_._")
                is_empty = True
                for i in range(len(current_student_grades_list)):
                    if current_student_grades_list[i] == '#':
                        current_student_grades_list[i] = ''
                    else:
                        is_empty = False
                if is_empty:
                    score = ""
                    percentage = ""
                student_result = {"work_id": work.id, "grades": current_student_grades_list, "score": score, "percentage": percentage}
                student_object['grades'].append(student_result)
            students_data.append(student_object)
        return HttpResponse(json.dumps({"works": works_data, "students": students_data}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except ZeroDivisionError as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получить список ожидающих ману.",
                     manual_parameters=[class_param],
                     responses=get_mana_waiters_responses)
@api_view(["GET"])
@permission_classes([IsAdmin])
def get_mana_waiters(request):
    try:
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
                        {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {}, 'instance': request.path},
                        ensure_ascii=False), status=404)
        waiters = []
        students = User.objects.filter(Q(is_admin=0) & Q(school_class=int(class_)))
        for student in students:
            manas = Mana.objects.filter(Q(student=student.id) & Q(is_given=0))
            green = manas.filter(color='green').aggregate(Count('id'))
            blue = manas.filter(color='blue').aggregate(Count('id'))
            waiter = {"id": student.id, "name": student.name, "green": green["id__count"], "blue": blue["id__count"]}
            if int(green["id__count"]) + int(blue["id__count"]) > 0:
                waiters.append(waiter)
        return HttpResponse(json.dumps({'waiters': waiters}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@api_view(["POST"])
@permission_classes([IsAdmin])
def get_some_mana_waiters(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)
        waiters = []
        for student in request_body["students"]:
            student = User.objects.get(id=int(student))
            mana_earned = int(student.mana_earned)
            grades = Grade.objects.filter(student_id=student)
            mana = int(grades.aggregate(Sum('mana'))['mana__sum'])
            waiting_mana = mana - mana_earned
            waiter = {'id': student.id, 'mana': waiting_mana, 'name': student.name}
            if waiting_mana > 0:
                waiters.append(waiter)
        return HttpResponse(json.dumps({'waiters': waiters}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


# todo: обработка ошибок(выдача маны > чем возможно)
@api_view(["POST"])
@permission_classes([IsAdmin])
def give_mana(request):
    try:
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
        student = User.objects.get(id=int(id_))
        old_mana = int(student.mana_earned)
        new_mana = old_mana + int(mana)
        student.mana_earned = new_mana
        log_details = f'Обновлена мана для ученика {student.id}. ["old_mana": {old_mana}, "new_mana": {new_mana}]'
        student.save()
        log = Log(operation='UPDATE', from_table='users', details=log_details)
        log.save()
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


@swagger_auto_schema(method='POST', operation_summary="Выдать ману ученику.",
                     manual_parameters=[id_param],
                     responses=give_mana_responses)
@api_view(["POST"])
@permission_classes([IsAdmin])
def give_mana_all(request):
    try:
        id_ = get_variable("id", request)
        if not id_:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=404)
        student = User.objects.get(id=int(id_))
        manas = Mana.objects.filter(student=int(id_))
        log_details = f'Обновлена мана для ученика {student.id}.'
        for mana in manas:
            mana.is_given = 1
        manas.save()
        log = Log(operation='UPDATE', from_table='mana', details=log_details)
        log.save()
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
