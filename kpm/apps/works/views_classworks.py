from collections import defaultdict
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from kpm.apps.works.models import *
import json
from kpm.apps.users.permissions import *
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.works.docs import *
from kpm.apps.works.functions import *
from django.conf import settings
from kpm.apps.groups.models import GroupUser, GroupWorkFile, Group
from kpm.apps.users.docs import permissions_operation_description
from kpm.apps.works.validators import *
from kpm.apps.grades.models import Grade


HOST = settings.MEDIA_HOST_PATH
MEDIA_ROOT = settings.MEDIA_ROOT
LOGGER = settings.LOGGER


@swagger_auto_schema(method='GET', operation_summary="Получение списка классных(пользователь).",
                     responses=get_my_classworks_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAuthenticated']}")
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEnabled])
def get_my_classworks(request):
    try:
        student = User.objects.get(id=request.user.id)
        groups = GroupUser.objects.filter(user=student).select_related('group').values_list('group_id', flat=True)
        files = GroupWorkFile.objects.filter(group_id__in=groups).select_related('work').order_by('-added_at').values(
            'file', 'ext', 'work_id', 'work__name', 'work__course')
        classworks_list = {}
        host = HOST
        for file in files:
            link = file['file']
            name = link.split('/')[-1]
            ext = file['ext']
            if file['work_id'] not in classworks_list:
                classworks_list[file['work_id']] = {
                    'name': file['work__name'],
                    'course': file['work__course'],
                    'files': [{
                        'link': f'{host}/{link}',
                        'name': name,
                        'ext': ext,
                    }]
                }
            else:
                classworks_list[file['work_id']]['files'].append({
                    'link': f'{host}/{link}',
                    'name': name,
                    'ext': ext,
                })
        return HttpResponse(json.dumps({'classworks': list(classworks_list.values())}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Пользователь не существует.', 'details': {},
                        'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='POST', operation_summary="Прикрепить файлы к классной работе(админ).",
                     request_body=apply_files_to_classwork_request_body,
                     responses=apply_files_to_classwork_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']}")
@api_view(["POST"])
@permission_classes([IsAdmin, IsEnabled])
def apply_files_to_classwork(request):
    try:
        if request.POST or request.FILES:
            data = request.POST
            files = request.FILES
        else:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=400)
        group = Group.objects.get(id=data['group'])
        work = Work.objects.get(id=data['work'])
        if not validate_work_type_for_group_type(work.type, group.type):
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Тип работы не подходит для этого типа группы.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=400)
        if not validate_work_course_for_group_type(work.course, group.type):
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Курс работы не подходит для этого типа группы.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=400)
        files = files.getlist('files')
        for file in files:
            if 'image' in str(file.content_type):
                pass
            elif file.content_type in ['application/pdf']:
                pass
            else:
                return HttpResponse(
                    json.dumps({'state': 'error', 'message': 'Недопустимый файл.', 'details': {},
                                'instance': request.path},
                               ensure_ascii=False), status=404)
            ext = file.name.split('.')[-1]
            GroupWorkFile.objects.create(group=group, work=work, file=file, ext=ext)
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Группа или работа не существует.', 'details': {},
                        'instance': request.path},
                       ensure_ascii=False), status=404)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='DELETE', operation_summary="Удалить файл классной работы(админ).",
                     manual_parameters=[file_param],
                     responses=delete_file_from_classwork_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']}")
@api_view(["DELETE"])
@permission_classes([IsAdmin, IsEnabled])
def delete_file_from_classwork(request):
    try:
        file_id = get_variable('file', request)
        if file_id is None:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Не указан id файла.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=400)
        file = GroupWorkFile.objects.get(id=file_id)
        file.delete()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Файл не существует.', 'details': {},
                        'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получить файлы классной работы подгрупп(админ).",
                     manual_parameters=[id_param],
                     responses=get_classwork_files_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']}")
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_classwork_files(request):
    try:
        id_ = get_variable('id', request)
        if id_ is None:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Не указан id работы.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=400)
        work = Work.objects.get(id=id_)
        course = work.course
        if course == 0:
            group_type = None
        else:
            group_type = course - 1
        school_class = work.school_class
        host = HOST
        group_files = GroupWorkFile.objects.filter(work=work, group__type=group_type).values('id', 'file', 'ext', 'group_id')
        files_dict = defaultdict(list)
        for file in group_files:
            name = file['file'].split('/')[-1]
            link = f"{host}/{file['file']}"
            ext = file['ext']
            files_dict[file['group_id']].append({
                'id': file['id'],
                'name': name,
                'link': link,
                'ext': ext
            })

        groups = Group.objects.filter(school_class=school_class, type=group_type).order_by('name').values('id', 'name', 'marker', 'type')
        groups_list = []
        for group in groups:
            group_files = files_dict[group['id']] if group['id'] in files_dict else []
            groups_list.append({
                'group_id': group['id'],
                'group_name': group['name'],
                'group_marker': group['marker'],
                'group_type': group['type'],
                'files': group_files
            })
        return HttpResponse(json.dumps({'groups': groups_list}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Файл не существует.', 'details': {},
                        'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получение списка классных работ.",
                     manual_parameters=[class_param, theme_param, type_param, course_param],
                     responses=get_works_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']} | {operation_description}")
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_classworks(request):
    try:
        class_ = get_variable("class", request)
        theme = get_variable("theme", request)
        type_ = get_variable("type", request)
        course = get_variable("course", request)
        if not validate_class(class_):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс учеников.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=400)
        if course not in [None, '', '0', '1', '2', '3', '4', '5', '6', '7']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан курс работы.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=400)
        if class_ == '4':
            works = Work.objects.filter(school_class=4, type__in=[1, 3, 4]).select_related("theme").order_by('-id')
        else:
            works = Work.objects.filter(is_homework=False, school_class=int(class_)).exclude(type__in=[0, 5, 6, 7, 8, 9]).select_related("theme").order_by('-id')
            if (theme is not None) and (theme != ''):
                works = works.filter(theme_id=theme)
            if type_ in ['1', '2', '3', '4']:
                works = works.filter(type=type_)
            if course in ['0', '1', '2', '3', '4', '5', '6', '7']:
                works = works.filter(course=course)
        works = works.values('id', 'name', 'grades', 'max_score', 'exercises', 'theme_id', 'theme__name', 'type', 'is_homework', 'course')
        works_list = []
        for work in works:
            works_list.append({
                "id": work['id'],
                "name": work['name'],
                "course": work['course'],
                "grades": work['grades'],
                "max_score": work['max_score'],
                "exercises": work['exercises'],
                "theme_id": work['theme_id'],
                "theme_name": work['theme__name'],
                "work_type": work['type'],
                "is_homework": work['is_homework']
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


@swagger_auto_schema(method='GET', operation_summary="Получение оценок классной работы(админка).",
                     manual_parameters=[id_param, group_param],
                     responses=get_classwork_grades_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']}")
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_classwork_grades(request):
    try:
        id_ = get_variable('id', request)
        if id_ in ['', None]:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Не указан id работы.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=400)
        group = get_variable('group', request)
        if group in ['', None]:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Не указан id группы.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=400)
        work = Work.objects.get(id=id_)
        work_grades = work.grades
        fields = len(work_grades)
        group = Group.objects.get(id=group)
        students = GroupUser.objects.filter(group=group).select_related('user').order_by('user__name')
        students_dict = {}
        for student in students:
            students_dict[student.user_id] = {
                'id': student.user_id,
                'name': student.user.name,
                'grades': []
            }
        grades_rows = Grade.objects.filter(work=work, user_id__in=list(students_dict.keys())).values('user_id', 'grades')
        for row in grades_rows:
            grades = row['grades']
            for i, grade in enumerate(grades):
                if grade == work_grades[i]:
                    students_dict[row['user_id']]['grades'].append(True)
                else:
                    students_dict[row['user_id']]['grades'].append(False)
        return HttpResponse(json.dumps({
            'fields': fields,
            'students': list(students_dict.values())
        }, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Работа или группа не существует.', 'details': {},
                        'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='PUT', operation_summary="Выставление оценки за классную работу(админка).",
                     request_body=insert_classwork_grade_request_body,
                     responses=insert_classwork_grade_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']}")
@api_view(["PUT"])
@permission_classes([IsAdmin, IsEnabled])
def insert_classwork_grade(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        id_ = request_body['work']
        student_id = request_body['user']
        work = Work.objects.get(id=id_)
        work_tech = None
        if work.type == 8:
            link = Exam.objects.get(work_2007=work)
            work_tech = link.work
        work_grades = list(map(int, work.grades))
        fields = len(work_grades)
        student = User.objects.get(id=student_id)
        cell = request_body['cell']
        if cell < 0 or cell >= fields:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Некорректный номер ячейки.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        value = request_body['value']
        if value not in [True, False]:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Некорректное значение value.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        grade_row = Grade.objects.get(work=work, user=student)
        new_grades = grade_row.grades
        log_grades = "_._".join(new_grades)
        if value:
            new_grades[cell] = str(work_grades[cell])
        else:
            new_grades[cell] = '#'
        new_score = 0
        new_max_score = sum(work_grades)
        new_exercises = work.exercises
        work_is_empty = True
        coefficient_2007 = []
        for i in range(len(new_grades)):
            if ',' in new_grades[i]:
                item_ = new_grades[i]
                new_grades[i] = item_.replace(',', '.')
            if new_grades[i] == '-':
                new_exercises -= 1
                new_max_score -= work_grades[i]
                if work.type == 8:
                    coefficient_2007.append('-')
                work_is_empty = False
                continue
            elif new_grades[i] == '#':
                cast = 0
                if work.type == 8:
                    coefficient_2007.append('#')
            else:
                cast = float(new_grades[i])
                if cast < 0:
                    return HttpResponse(
                        json.dumps({'state': 'error', 'message': f'Указано недопустимое значение.',
                                    'details': {},
                                    'instance': request.path},
                                   ensure_ascii=False), status=400)
                if cast > float(work_grades[i]):
                    return HttpResponse(
                        json.dumps({'state': 'error', 'message': f'Указанная оценка больше максимальной.',
                                    'details': {},
                                    'instance': request.path},
                                   ensure_ascii=False), status=400)
                if work.type == 8:
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
        if work_is_empty:
            new_max_score = 0
            new_exercises = 0
        grade_row.grades = new_grades
        grade_row.max_score = new_max_score
        grade_row.score = new_score
        grade_row.exercises = new_exercises
        grade_row.save()
        if work.type in [1, 4, 8]:
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
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Работа или пользователь не существует.', 'details': {},
                        'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)