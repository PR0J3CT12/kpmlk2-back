from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from kpm.apps.users.permissions import IsAdmin, IsEnabled
from .functions import *
from kpm.apps.users.models import User
from kpm.apps.works.models import Work, Exam
from kpm.apps.groups.models import Group, GroupUser
from kpm.apps.grades.models import Grade, Mana
import json
from django.db.models import Sum, Case, When, IntegerField, Count, Q
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.grades.docs import *
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from kpm.apps.users.docs import permissions_operation_description


LOGGER = settings.LOGGER


# todo: внимательно потестить ману, чтобы не генерилось лишнее(в том числе когда вносят новые оценки и удаляется старая мана)
@swagger_auto_schema(method='POST', operation_summary="Проставить оценки.",
                     request_body=insert_grades_request_body,
                     responses=insert_grades_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']}")
@api_view(["POST"])
@permission_classes([IsAdmin, IsEnabled])
def insert_grades(request):
    global_change = {
        "work_id": None,
        "student_id": None,
        "cell_number": None
    }
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)
        work_id = request_body["work_id"]
        if not work_id:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Не указан ID работы.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        work = Work.objects.get(id=work_id)
        if work.type == 5:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Закрытая таблица.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        user_id = request_body["user_id"]
        if not user_id:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Не указан ID пользователя.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        student = User.objects.get(id=user_id)
        work_tech = None
        if work.type in [7, 8]:
            link = Exam.objects.get(work_2007=work)
            work_tech = link.work
        grade = Grade.objects.get(user=student, work=work)
        work_grades = list(map(float, work.grades))
        new_max_score = sum(work_grades)
        new_grades = list(grade.grades)
        log_grades = '_._'.join(new_grades)
        new_exercises = work.exercises
        new_score = 0
        value = request_body["value"]
        if value == '':
            value = '#'
        cell = request_body["cell_number"]
        new_grades[cell] = value
        coefficient_2007 = []
        work_is_empty = True
        for i in range(len(new_grades)):
            if ',' in new_grades[i]:
                new_grades[i] = new_grades[i].replace(',', '.')
            if new_grades[i] == '-':
                new_exercises -= 1
                new_max_score -= work_grades[i]
                if work.type in [7, 8]:
                    coefficient_2007.append('-')
                work_is_empty = False
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
                                    'details': {"user_id": user_id, "work_id": work_id, "cell_number": cell,
                                                "cell_name": f'{user_id}_{work_id}_{cell}'},
                                    'instance': request.path},
                                   ensure_ascii=False), status=400)
                if cast > float(work_grades[i]):
                    return HttpResponse(
                        json.dumps({'state': 'error', 'message': f'Указанная оценка больше максимальной.',
                                    'details': {"user_id": user_id, "work_id": work_id, "cell_number": cell,
                                                "cell_name": f'{user_id}_{work_id}_{cell}'},
                                    'instance': request.path},
                                   ensure_ascii=False), status=400)
                if work.type in [7, 8]:
                    coefficient_2007.append(cast / work_grades[i])
                work_is_empty = False
            new_score += cast
        new_grades_check = '_._'.join(new_grades)
        if log_grades == new_grades_check:
            return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
        if work_tech:
            grade_tech = Grade.objects.get(user=student, work=work_tech)
            work_tech_grades = list(map(float, work_tech.grades))
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
            grade_tech.grades = new_grades_list_tech
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
        grade.grades = new_grades
        grade.max_score = new_max_score
        grade.score = new_score
        grade.exercises = new_exercises
        grade.save()
        if work.type in [0, 1, 4, 6, 7, 8]:
            if work.is_homework:
                if student.last_homework_id is None:
                    student.last_homework_id = work.id
                else:
                    try:
                        last_homework = Work.objects.get(id=student.last_homework_id)
                        if work.created_at > last_homework.created_at:
                            student.last_homework_id = work.id
                    except ObjectDoesNotExist:
                        student.last_homework_id = work.id
            else:
                if student.last_classwork_id is None:
                    student.last_classwork_id = work.id
                else:
                    try:
                        last_classwork = Work.objects.get(id=student.last_classwork_id)
                        if work.created_at > last_classwork.created_at:
                            student.last_classwork_id = work.id
                    except ObjectDoesNotExist:
                        student.last_classwork_id = work.id
            student.save()
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
        LOGGER.info(f'Inserted grades for student {student.id} in work {work_id} in cell {cell} by user {request.user.id}.')
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
                     responses=get_grades_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']}")
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_grades(request):
    try:
        class_ = get_variable("class", request)
        theme = get_variable("theme", request)
        type_ = get_variable("type", request)
        group = get_variable("group", request)
        if class_ not in ['4', '5', '6', '7']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс учеников.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        grades = Grade.objects.filter(user__school_class=int(class_)).exclude(work__type=5).exclude(work__type=3).order_by('work__created_at').select_related('work', 'user')
        if (theme is not None) and (theme != ''):
            if theme == '8':
                grades = grades.filter(work__theme__id=int(theme))
            else:
                grades = grades.filter(work__theme__id=int(theme))
        if type_ in ['0', '1', '2', '4', '6', '7', '8', '9']:
            grades = grades.filter(work__type=int(type_))
        if (group is not None) and (group != ''):
            grades = grades.filter(user__groupuser__group_id=int(group))
        grades = grades.values('user_id', 'user__name', 'user__experience', 'work_id', 'score', 'max_score', 'grades', 'exercises')
        grades_dict = {}
        works_list = []
        for grade in grades:
            if grade['work_id'] not in works_list:
                works_list.append(grade['work_id'])
            if grade['user_id'] not in grades_dict:
                grades_dict[grade['user_id']] = {
                    'total_score': 0,
                    'total_max_score': 0,
                    'student_data': {
                        'id': grade['user_id'],
                        'name': grade['user__name'],
                        'experience': grade['user__experience'],
                        'grades': [],
                        'groups': []
                    }
                }
            if grade['work_id'] not in grades_dict[grade['user_id']]:
                grades_dict[grade['user_id']][grade['work_id']] = {
                    'score': grade['score'],
                    'max_score': grade['max_score'],
                    'grades': grade['grades'],
                    'exercises': grade['exercises'],
                }
                grades_dict[grade['user_id']]['total_score'] += grade['score']
                grades_dict[grade['user_id']]['total_max_score'] += grade['max_score']
        works = Work.objects.filter(id__in=works_list).order_by('created_at').values('id', 'name', 'max_score', 'grades')
        works_data = []
        links_dict = {}
        if ((type_ == '7') or (type_ == '8')) or (theme == '8'):
            links = Exam.objects.filter(work_2007__in=works).select_related('work_2007').values('id', 'work_id', 'work_2007_id', 'work__grades')
            for link in links:
                links_dict[link['work_2007_id']] = {
                    'pair_work_id': link['work_id'],
                    'grades': link['work__grades']
                }
        if (group is not None) and (group != ''):
            group_users = GroupUser.objects.filter(group_id=group, user__school_class=int(class_), user__is_admin=0).order_by('group_id', 'user_id').values('user_id', 'group_id', 'group__marker')
            groups_dict = {}
            for gu in group_users:
                if gu['user_id'] not in groups_dict:
                    groups_dict[gu['user_id']] = [{
                        'group_id': gu['group_id'],
                        'color': gu['group__marker']
                    }]
                else:
                    groups_dict[gu['user_id']].append({
                        'group_id': gu['group_id'],
                        'color': gu['group__marker']
                    })
        else:
            group_users = GroupUser.objects.filter(user__school_class=int(class_), user__is_admin=0).order_by('user_id').values(
                'user_id', 'group_id', 'group__marker')
            groups_dict = {}
            for gu in group_users:
                if gu['user_id'] not in groups_dict:
                    groups_dict[gu['user_id']] = [{
                        'group_id': gu['group_id'],
                        'color': gu['group__marker']
                    }]
                else:
                    groups_dict[gu['user_id']].append({
                        'group_id': gu['group_id'],
                        'color': gu['group__marker']
                    })
        students = User.objects.filter(id__in=list(groups_dict.keys())).values('id', 'name', 'experience')
        if works:
            works_dict = {}
            for work in works:
                data = {'id': work['id'], 'name': work['name'], 'max_score': work['max_score'], 'grades': list(map(int, work['grades']))}
                if ((type_ == '7') or (type_ == '8')) or (theme == '8'):
                    work_tech = links_dict[work['id']]
                    grades_tech = list(map(int, work_tech['grades']))
                    data['grades_tech'] = grades_tech
                works_data.append(data)
                if work['id'] not in works_dict:
                    works_dict[work['id']] = data

            students_data = []
            for student_ in students:
                student_id = student_['id']
                student = grades_dict[student_id]
                student_object = student['student_data']
                full_score = student['total_score']
                max_full_score = student['total_max_score']
                if max_full_score != 0:
                    percentage_full_score = round(full_score / max_full_score * 100, 1)
                else:
                    percentage_full_score = ""
                student_object['percentage_full_score'] = percentage_full_score
                for work_ in works:
                    work_id = work_['id']
                    current_student_grades = student[work_id]
                    score = current_student_grades['score']
                    max_score = current_student_grades['max_score']
                    if float(max_score) != 0:
                        percentage = str(round(float(score) / float(max_score) * 100, 1))
                    else:
                        percentage = ""
                    current_student_grades_list = current_student_grades['grades']
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
                    student_object['groups'] = groups_dict[student_id]
                students_data.append(student_object)
        else:
            students_data = {}
            for student in students:
                if student['id'] not in students_data:
                    students_data[student['id']] = {
                        'id': student['id'],
                        'name': student['name'],
                        'experience': student['experience'],
                        'grades': [],
                        'percentage_full_score': 0,
                        'groups': groups_dict[student['id']]
                    }
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
                     manual_parameters=[class_param],
                     responses=get_mana_waiters_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']}")
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_mana_waiters(request):
    try:
        class_ = get_variable("class", request)
        if not class_:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан класс ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        else:
            if class_ not in ['4', '5', '6', '7']:
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {}, 'instance': request.path},
                        ensure_ascii=False), status=404)
        waiters = []
        students = User.objects.filter(Q(is_admin=0) & Q(school_class=int(class_))).order_by('id')
        for student in students:
            manas = Mana.objects.filter(Q(user=student) & Q(is_given=0))
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


@swagger_auto_schema(method='POST', operation_summary="Выдать ману ученику.",
                     manual_parameters=[id_param],
                     responses=give_mana_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']}")
@api_view(["POST"])
@permission_classes([IsAdmin, IsEnabled])
def give_mana_all(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=404)
        student = User.objects.get(id=int(id_))
        manas = Mana.objects.filter(user=student)
        for mana in manas:
            mana.is_given = 1
            mana.save()
        LOGGER.info(f'Given mana for student {id_} by user {request.user.id}.')
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
