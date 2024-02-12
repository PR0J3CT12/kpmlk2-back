from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from kpm.apps.users.permissions import IsAdmin
from .functions import *
from kpm.apps.logs.models import Log
from kpm.apps.users.models import User
from kpm.apps.works.models import Work, Exam
from kpm.apps.themes.models import Theme
from kpm.apps.grades.models import Grade, Mana
import json
from django.db.models import Sum, Case, When, IntegerField, Count, Q
import random
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.grades.docs import *
from django.core.exceptions import ObjectDoesNotExist


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
        work = Work.objects.get(id=int(request_body["work_id"]))
        if work.type == 5:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Закрытая таблица.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        student = User.objects.get(id=int(request_body["user_id"]))
        work_tech = None
        if work.type in [7, 8]:
            link = Exam.objects.get(work_2007=work)
            work_tech = link.work
        grade = Grade.objects.get(user=student, work=work)
        work_grades = list(map(float, work.grades.split("_._")))
        new_max_score = sum(work_grades)
        new_grades = grade.grades.split("_._")
        new_exercises = work.exercises
        new_score = 0
        if request_body["value"] == '':
            request_body["value"] = '#'
        new_grades[int(request_body["cell_number"])] = request_body["value"]
        coefficient_2007 = []
        for i in range(len(new_grades)):
            if ',' in new_grades[i]:
                new_grades[i] = new_grades[i].replace(',', '.')
            if new_grades[i] == '-':
                new_exercises -= 1
                new_max_score -= work_grades[i]
                if work.type in [7, 8]:
                    coefficient_2007.append('-')
                continue
            elif new_grades[i] == '#':
                cast = 0
                if work.type in [7, 8]:
                    coefficient_2007.append('#')
            else:
                cast = float(new_grades[i])
                if cast < 0:
                    return HttpResponse(
                        json.dumps({'state': 'error', 'message': f'Указано недопустимое значение.',
                                    'details': {"user_id": request_body["user_id"], "work_id": request_body["work_id"],
                                                "cell_number": request_body["cell_number"],
                                                "cell_name": f'{request_body["user_id"]}_{request_body["work_id"]}_{request_body["cell_number"]}'},
                                    'instance': request.path},
                                   ensure_ascii=False), status=400)
                if cast > float(work_grades[i]):
                    return HttpResponse(
                        json.dumps({'state': 'error', 'message': f'Указанная оценка больше максимальной.',
                                    'details': {"user_id": request_body["user_id"], "work_id": request_body["work_id"],
                                                "cell_number": request_body["cell_number"],
                                                "cell_name": f'{request_body["user_id"]}_{request_body["work_id"]}_{request_body["cell_number"]}'},
                                    'instance': request.path},
                                   ensure_ascii=False), status=400)
                if work.type in [7, 8]:
                    coefficient_2007.append(cast / work_grades[i])
            new_score += cast
        log_grades_string = grade.grades
        work_is_empty = True
        for grade_ in new_grades:
            if grade_ != '#':
                work_is_empty = False
        new_grades_string = '_._'.join(new_grades)
        if log_grades_string == new_grades_string:
            return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
        if work_tech:
            grade_tech = Grade.objects.get(user=student, work=work_tech)
            work_tech_grades = list(map(float, work_tech.grades.split("_._")))
            max_score_tech = 0
            score_tech = 0
            exercises_tech = 0
            new_grades_list_tech = []
            for i in range(len(work_tech_grades)):
                if coefficient_2007[i] == '-':
                    new_grades_list_tech.append('-')
                elif coefficient_2007[i] == '#':
                    exercises_tech += 1
                    max_score_tech += work_tech_grades[i]
                    new_grades_list_tech.append('#')
                else:
                    exercises_tech += 1
                    current_grade_tech = round(coefficient_2007[i] * work_tech_grades[i])
                    max_score_tech += work_tech_grades[i]
                    score_tech += current_grade_tech
                    new_grades_list_tech.append(str(current_grade_tech))
            if work_is_empty:
                max_score_tech = 0
                exercises_tech = 0
            grade_tech.exercises = exercises_tech
            grade_tech.max_score = max_score_tech
            new_grades_string_tech = '_._'.join(new_grades_list_tech)
            grade_tech.grades = new_grades_string_tech
            grade_tech.score = score_tech
            grade_tech.save()
        if grade.score != new_score:
            manas_delete = Mana.objects.filter(Q(user=student) & Q(work=work))
            manas_delete.delete()
        if work.type == 6:
            count = 0
            for grade_ in new_grades:
                if is_number_float(grade_):
                    if float(grade_) > 0:
                        count += 1
            green, blue = mana_generation(int(work.type), work.is_homework, count, 0)
        elif work.type == 2:
            green, blue = mana_generation(int(work.type), True, new_score, new_max_score)
        else:
            green, blue = mana_generation(int(work.type), work.is_homework, new_score, new_max_score)
        if grade.score != new_score:
            for i in range(0, green):
                mana = Mana(user=student, work=work, color='green')
                mana.save()
            for i in range(0, blue):
                mana = Mana(user=student, work=work, color='blue')
                mana.save()
        if work_is_empty:
            new_max_score = 0
            new_exercises = 0
        grade.grades = new_grades_string
        grade.max_score = new_max_score
        grade.score = new_score
        grade.exercises = new_exercises
        log_details = f'Обновлены оценки для ученика {student.id} в работе {work.id}. ["old_grades": {log_grades_string}, "new_grades": {new_grades_string}]'
        grade.save()
        if work.type in [0, 1, 4, 6, 7, 8]:
            if work.is_homework:
                if student.last_homework_id is None:
                    student.last_homework_id = work.id
                else:
                    try:
                        last_homework = Work.objects.get(id=student.last_homework_id)
                        if work.added_at > last_homework.added_at:
                            student.last_homework_id = work.id
                    except ObjectDoesNotExist:
                        student.last_homework_id = work.id
            else:
                if student.last_classwork_id is None:
                    student.last_classwork_id = work.id
                else:
                    try:
                        last_classwork = Work.objects.get(id=student.last_classwork_id)
                        if work.added_at > last_classwork.added_at:
                            student.last_classwork_id = work.id
                    except ObjectDoesNotExist:
                        student.last_classwork_id = work.id
            student.save()
        #total_scores = Grade.objects.filter(user=student, work__type__in=[0, 5, 6]).aggregate(sum_score=Sum('score'))
        #total_experience = int(total_scores['sum_score'])
        aggregated_data = Grade.objects.filter(
            user=student,
            work__type__in=[0, 5, 6]
        ).aggregate(
            total_experience=Sum('score'),
            exam_experience=Sum(
                Case(
                    When(work__type=5, then='score'),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            oral_exam_experience=Sum(
                Case(
                    When(work__type=6, then='score'),
                    default=0,
                    output_field=IntegerField(),
                )
            )
        )
        experience = aggregated_data['total_experience'] if aggregated_data else 0
        exam_experience = aggregated_data['exam_experience'] if aggregated_data else 0
        oral_exam_experience = aggregated_data['oral_exam_experience'] if aggregated_data else 0
        student.experience = experience
        student.exam_experience = exam_experience
        student.oral_exam_experience = oral_exam_experience
        student.save()
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
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Что-то не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получить оценки.",
                     manual_parameters=[class_param, theme_param, type_param, group_param],
                     responses=get_grades_responses)
@api_view(["GET"])
@permission_classes([IsAdmin])
def get_grades(request):
    try:
        class_ = get_variable("class", request)
        theme = get_variable("theme", request)
        type_ = get_variable("type", request)
        group = get_variable("group", request)
        if class_ not in ['4', '5', '6', 4, 5, 6]:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс учеников.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        grades = Grade.objects.filter(user__school_class=int(class_)).exclude(work__type=5).exclude(work__type=3).order_by('work__added_at').select_related('work', 'user')
        if (theme is not None) and (theme != ''):
            if theme == '8':
                grades = grades.filter(work__theme__id=int(theme))
            else:
                grades = grades.filter(work__theme__id=int(theme))
        if type_ in ['0', '1', '2', '4', '6', '7', '8', '9']:
            grades = grades.filter(work__type=int(type_))
        if (group is not None) and (group != ''):
            grades = grades.filter(user__group=int(group))
        grades_dict = {}
        MARKER_CHOICES = {
            0: '#ff8282',
            1: '#ffb875',
            2: '#fdff96',
            3: '#93ff91',
            4: '#78ffef',
            5: '#7776d6',
            6: '#bfa0de',
            7: None
        }
        for grade in grades:
            if grade.user_id not in grades_dict:
                if grade.user.group:
                    marker = grade.user.group.marker
                else:
                    marker = 7
                grades_dict[grade.user_id] = {
                    'total_score': 0,
                    'total_max_score': 0,
                    'student_data': {
                        'id': grade.user.id,
                        'name': grade.user.name,
                        'experience': grade.user.experience,
                        'grades': [],
                        'color': MARKER_CHOICES[marker]
                    }
                }
            if grade.work_id not in grades_dict[grade.user_id]:
                grades_dict[grade.user_id][grade.work_id] = {
                    'score': grade.score,
                    'max_score': grade.max_score,
                    'grades': grade.grades,
                    'exercises': grade.exercises,
                }
                grades_dict[grade.user_id]['total_score'] += grade.score
                grades_dict[grade.user_id]['total_max_score'] += grade.max_score
        works_list = grades.order_by('work__added_at').values_list('work', flat=True)
        works_list = custom_distinct(works_list)
        works = Work.objects.filter(id__in=works_list).order_by('added_at')
        works_data = []
        links = None
        if ((type_ == '7') or (type_ == '8')) or (theme == '8'):
            links = Exam.objects.filter(work_2007__in=works)
        if (group is not None) and (group != ''):
            students = User.objects.filter(
                Q(is_admin=0) & Q(school_class=int(class_)) & Q(group=int(group))).select_related('group').order_by(
                'group', 'id')
        else:
            students = User.objects.filter(Q(is_admin=0) & Q(school_class=int(class_))).select_related(
                'group').order_by('group', 'id')
        if works:
            works_dict = {}
            for work in works:
                data = {'id': work.id, 'name': work.name, 'max_score': work.max_score, 'grades': list(map(int, work.grades.split("_._")))}
                if ((type_ == '7') or (type_ == '8')) or (theme == '8'):
                    work_tech = links.get(work_2007=work)
                    grades_tech = list(map(int, work_tech.work.grades.split("_._")))
                    data['grades_tech'] = grades_tech
                works_data.append(data)
                if work.id not in works_dict:
                    works_dict[work.id] = data

            students_data = []
            for student_ in students:
                student = grades_dict[student_.id]
                student_object = student['student_data']
                full_score = student['total_score']
                max_full_score = student['total_max_score']
                if max_full_score != 0:
                    percentage_full_score = round(full_score / max_full_score * 100, 1)
                else:
                    percentage_full_score = ""
                student_object['percentage_full_score'] = percentage_full_score
                for work_ in works:
                    work_id = work_.id
                    current_student_grades = student[work_id]
                    score = current_student_grades['score']
                    max_score = current_student_grades['max_score']
                    if float(max_score) != 0:
                        percentage = str(round(float(score) / float(max_score) * 100, 1))
                    else:
                        percentage = ""
                    current_student_grades_list = current_student_grades['grades'].split("_._")
                    is_empty = True
                    for i in range(len(current_student_grades_list)):
                        if current_student_grades_list[i] == '#':
                            current_student_grades_list[i] = ''
                        else:
                            is_empty = False
                    if is_empty:
                        score = ""
                        percentage = ""
                    student_result = {"work_id": work_id, "grades": current_student_grades_list, "score": score, "percentage": percentage}
                    student_object['grades'].append(student_result)
                students_data.append(student_object)
        else:
            students = User.objects.filter(Q(is_admin=0) & Q(school_class=int(class_)))
            students_data = []
            for student in students:
                student_object = {'id': student.id, 'name': student.name, 'experience': student.experience, 'grades': [], 'percentage_full_score': 0}
                students_data.append(student_object)
        return HttpResponse(json.dumps({"works": works_data, "students": students_data}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получить список ожидающих ману.",
                     manual_parameters=[class_param, group_param],
                     responses=get_mana_waiters_responses)
@api_view(["GET"])
@permission_classes([IsAdmin])
def get_mana_waiters(request):
    try:
        group = get_variable("group", request)
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
                        {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {}, 'instance': request.path},
                        ensure_ascii=False), status=404)
        waiters = []
        MARKER_CHOICES = {
            0: '#ff8282',
            1: '#ffb875',
            2: '#fdff96',
            3: '#93ff91',
            4: '#78ffef',
            5: '#7776d6',
            6: '#bfa0de',
            7: None
        }
        if (group is not None) and (group != ''):
            students = User.objects.filter(Q(is_admin=0) & Q(school_class=int(class_)) & Q(group=int(group))).select_related('group').order_by('group', 'id')
        else:
            students = User.objects.filter(Q(is_admin=0) & Q(school_class=int(class_))).select_related('group').order_by('group', 'id')
        for student in students:
            if student.group:
                marker = student.group.marker
            else:
                marker = 7
            manas = Mana.objects.filter(Q(user=student) & Q(is_given=0))
            green = manas.filter(color='green').aggregate(Count('id'))
            blue = manas.filter(color='blue').aggregate(Count('id'))
            waiter = {"id": student.id, "name": student.name, "green": green["id__count"], "blue": blue["id__count"], 'color': MARKER_CHOICES[marker]}
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


@swagger_auto_schema(method='POST', operation_summary="Выдать ману ученику.",
                     manual_parameters=[id_param],
                     responses=give_mana_responses)
@api_view(["POST"])
@permission_classes([IsAdmin])
def give_mana_all(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=404)
        student = User.objects.get(id=int(id_))
        manas = Mana.objects.filter(user=student)
        log_details = f'Обновлена мана для ученика {student.id}.'
        for mana in manas:
            mana.is_given = 1
            mana.save()
        log = Log(operation='UPDATE', from_table='mana', details=log_details)
        log.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Пользователь не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)
