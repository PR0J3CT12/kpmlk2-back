from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from kpm.apps.users.permissions import IsAdmin
from .customfunctions import get_variable
from kpm.apps.logs.models import Log
from kpm.apps.users.models import User
from kpm.apps.works.models import Work
from kpm.apps.themes.models import Theme
from kpm.apps.grades.models import Grade, Mana
import json
from django.db.models import Sum, Q, Count
import random


# todo: внимательно потестить ману, чтобы не генерилось лишнее
@api_view(["POST"])
@permission_classes([IsAdmin])
def insert_grades(request):
    if request.body:
        request_body = json.loads(request.body)
    else:
        return HttpResponse(json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)
    global_change = None
    try:
        for change in request_body["changes"]:
            global_change = change
            work = Work.objects.get(id=int(change["work_id"]))
            student = User.objects.get(id=int(change["student_id"]))
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
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_grades(request):
    if request.body:
        request_body = json.loads(request.body)
    else:
        return HttpResponse(json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)
    try:
        colors = {"0-25": "#ea9999", "25-50": "#f9cb9c", "50-75": "#ffe599", "75-100": "#b6d7a8", "None": "#ffffff"}
        works_order = list(map(int, request_body["works"]))
        grades = Grade.objects.filter(work_id__in=works_order)
        students = User.objects.filter(Q(is_admin=0) & Q(school_class=request_body["class"]))
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


@api_view(["GET"])
@permission_classes([IsAdmin])
def get_mana_waiters(request):
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
        students = User.objects.filter(Q(is_admin=0) & Q(school_class=int(class_)))
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


@api_view(["POST"])
@permission_classes([IsAdmin])
def get_some_mana_waiters(request):
    if request.body:
        request_body = json.loads(request.body)
    else:
        return HttpResponse(json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)
    try:
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
        return HttpResponse(json.dumps({'state': 'success', 'message': 'Ожидающие ману успешно получены.', 'details': {'waiters': waiters}}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


# todo: обработка ошибок(выдача маны > чем возможно)
@api_view(["POST"])
@permission_classes([IsAdmin])
def give_mana(request):
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
        student = User.objects.get(id=int(id_))
        old_mana = int(student.mana_earned)
        new_mana = old_mana + int(mana)
        student.mana_earned = new_mana
        log_details = f'Обновлена мана для ученика {student.id}. ["old_mana": {old_mana}, "new_mana": {new_mana}]'
        student.save()
        log = Log(operation='UPDATE', from_table='users', details=log_details)
        log.save()
        return HttpResponse(json.dumps({'state': 'success', 'message': 'Мана успешно выдана.', 'details': {}}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


@api_view(["POST"])
@permission_classes([IsAdmin])
def give_mana_all(request):
    id_ = get_variable("id", request)
    if not id_:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    try:
        student = User.objects.get(id=int(id_))
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
