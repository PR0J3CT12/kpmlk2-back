import time
from collections import defaultdict
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from kpm.apps.works.models import *
from kpm.apps.themes.models import Theme
from kpm.apps.grades.models import Grade, Mana
import json
from django.db.models import Sum, Q, Count, Prefetch, F, Value, OuterRef, Subquery
from kpm.apps.users.permissions import *
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.works.docs import *
from kpm.apps.works.functions import *
from django.utils import timezone
import os
from django.conf import settings
from kpm.apps.grades.functions import validate_grade
from kpm.apps.groups.models import GroupUser, GroupWorkFile, Group, GroupWorkDate
from datetime import datetime
from kpm.apps.grades.functions import is_number_float, mana_generation
from kpm.apps.users.docs import permissions_operation_description


MEDIA_ROOT = settings.MEDIA_ROOT
LOGGER = settings.LOGGER


@swagger_auto_schema(method='GET', operation_summary="Получение списка работ.",
                     manual_parameters=[class_param, theme_param, type_param],
                     responses=get_works_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']} | {operation_description}")
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_works(request):
    try:
        class_ = get_variable("class", request)
        theme = get_variable("theme", request)
        type_ = get_variable("type", request)
        if class_ not in ['4', '5', '6', '7']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс учеников.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        works = Work.objects.filter(school_class=int(class_)).exclude(type=7).exclude(type=8).select_related(
            "theme").order_by('-id')
        if (theme is not None) and (theme != ''):
            works = works.filter(theme_id=theme)
        if type_ in ['0', '1', '2', '3', '4', '5', '6', '9']:
            works = works.filter(type=type_)
        works_list = []
        works = works.values('id', 'name', 'grades', 'max_score', 'exercises', 'theme_id', 'theme__name', 'type', 'is_homework')
        for work in works:
            works_list.append({
                "id": work['id'],
                "name": work['name'],
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


@swagger_auto_schema(method='GET', operation_summary="Получение работы.",
                     manual_parameters=[id_param],
                     responses=get_work_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']} | {operation_description}")
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_work(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        work = Work.objects.get(id=id_)
        result = {
            "id": work.id,
            "name": work.name,
            "grades": work.grades,
            "max_score": work.max_score,
            "exercises": work.exercises,
            "theme_id": work.theme_id,
            "theme_name": work.theme.name,
            "type": work.type,
            "is_homework": work.is_homework,
            "created_at": str(work.created_at),
            "has_attachments": work.has_attachments
        }
        if work.has_attachments:
            host = settings.MEDIA_HOST_PATH
            files = WorkFile.objects.filter(work=work)
            files_list = []
            for file in files:
                link = file.file.name
                name = link.split('/')[1]
                ext = name.split('.')[-1]
                files_list.append({'id': file.id, 'link': f'{host}/{link}', 'name': name, 'ext': ext})
            work_users = WorkUser.objects.filter(work=work).select_related('user').values('user__id', 'user__name')
            users_list = []
            for user in work_users:
                users_list.append({'id': user['user__id'], 'name': user['user__name']})
            result['text'] = work.text
            result['answers'] = work.answers
            result['files'] = files_list
            result['users'] = users_list
        if work.is_homework:
            groups_dict = {}
            groups = Group.objects.filter(school_class=work.school_class).order_by("created_at").values("id", "name", "marker")
            for group in groups:
                groups_dict[group['id']] = {
                    "id": group['id'],
                    "name": group['name'],
                    "color": group['marker'],
                    "date": None
                }
            groups_in_work = GroupWorkDate.objects.filter(work=work).values("group_id", "date")
            for gin in groups_in_work:
                groups_dict[gin['group_id']]['date'] = str(gin['date'])
            result["groups"] = list(groups_dict.values())
        return HttpResponse(
            json.dumps(result, ensure_ascii=False), status=200)
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
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierTwo']} | {operation_description}")
@api_view(["POST"])
@permission_classes([IsTierTwo, IsEnabled])
def create_work(request):
    try:
        if request.POST or request.FILES:
            data = request.POST
            files = request.FILES
        else:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=400)
        type_ = data["type"]
        school_class = data["class"]
        name = data["name"]
        if type_ not in ['0', '1', '2', '3', '4', '5', '6', '9']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан тип работы.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        if school_class not in ['4', '5', '6', '7']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        if type_ == 2:
            grades = ["1", "1", "1"]
        else:
            grades = data.getlist("grades")
        max_score = 0
        for grade in grades:
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

        theme = Theme.objects.get(id=data["theme_id"])
        if type_ in ['0', '5', '6', '7']:
            is_homework = True
        else:
            is_homework = False
        students = User.objects.filter(Q(is_admin=0) & Q(school_class=school_class))
        exercises = len(grades)
        if type_ not in ['3', '5']:
            work = Work(name=name, grades=grades, theme=theme, max_score=max_score,
                        exercises=exercises, school_class=school_class, type=type_,
                        is_homework=is_homework, author_id=request.user.id)
            work.full_clean()
            work_2007 = None
            link = None
        else:
            if type_ == 5:
                type_2007 = 7
            else:
                type_2007 = 8

            grades_2007 = data["grades_2007"]
            if len(grades_2007) != len(grades):
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Введено разное количество оценок.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=404)
            max_score_2007 = 0
            for grade in grades_2007:
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

            work = Work(name=name, grades=grades, theme=theme, max_score=max_score,
                        exercises=exercises, school_class=school_class, type=type_,
                        is_homework=is_homework, author_id=request.user.id)
            work_2007 = Work(name=name, grades=grades_2007, theme=theme, max_score=max_score_2007,
                             exercises=exercises, school_class=school_class, type=type_2007,
                             is_homework=is_homework, author_id=request.user.id)
            work.full_clean()
            work_2007.full_clean()
            link = Exam(work=work, work_2007=work_2007)
            link.full_clean()

        has_attachments = data["has_attachments"].lower() == "true" if "has_attachments" in data else False
        if has_attachments:
            text = data["text"]
            answers = data.getlist("answers")
            if len(answers) != exercises:
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Введено разное количество ответов.', 'details': {},
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
            work.has_attachments = True
            work.text = text
            work.answers = answers
            work.full_clean()
            work.save()
            for file in files:
                ext = file.name.split('.')[1]
                work_file = WorkFile(work=work, file=file, ext=ext)
                work_file.save()
            if work_2007 and link:
                work_2007.save()
                link.save()
        else:
            work.save()

        empty_grades = list('#' * exercises)
        for student in students:
            grade = Grade(user=student, work=work, grades=empty_grades, max_score=0, score=0, exercises=0)
            grade.save()
        if work_2007:
            for student in students:
                grade = Grade(user=student, work=work_2007, grades=empty_grades, max_score=0, score=0, exercises=0)
                grade.save()
        LOGGER.info(f'Created work {work.id} by user {request.user.id}.')
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
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierTwo']} | {operation_description}")
@api_view(["PATCH"])
@permission_classes([IsTierTwo, IsEnabled])
def update_work(request):
    try:
        if request.POST or request.FILES:
            data = request.POST
            files = request.FILES
        else:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=400)
        id_ = data['id']
        work = Work.objects.get(id=id_)
        if "grades" in data:
            grades_list = data.getlist("grades")
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
            grades = grades_list
            work.grades = grades
            work.max_score = max_score
            work.updated_at = timezone.now()
        if "name" in data:
            new_name = data["name"]
            work.name = new_name
            work.updated_at = timezone.now()
        has_attachments = data["has_attachments"].lower() == "true" if "has_attachments" in data else False
        if has_attachments:
            if not work.has_attachments:
                text = data["text"]
                answers = data.getlist("answers")
                work.text = text
                work.answers = answers
                work.has_attachments = True
            else:
                if "text" in data:
                    work.text = data["text"]
                if "answers" in data:
                    answers = data.getlist("answers")
                    work.answers = answers
            if "files" in files:
                files = files.getlist('files')
                for file in files:
                    if 'image' in str(file.content_type):
                        pass
                    elif file.content_type in ['application/pdf']:
                        pass
                    else:
                        return HttpResponse(
                            json.dumps(
                                {'state': 'error', 'message': 'Недопустимый файл.', 'details': {},
                                 'instance': request.path},
                                ensure_ascii=False), status=404)
                    ext = file.name.split('.')[1]
                    work_file = WorkFile(work=work, file=file, ext=ext)
                    work_file.save()
            work.save()
        LOGGER.info(f'Updated work {work.id} by user {request.user.id}.')
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
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierTwo']} | {operation_description}")
@api_view(["DELETE"])
@permission_classes([IsTierTwo, IsEnabled])
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
        if type_ in [3, 5]:
            link = Exam.objects.get(work=work)
            work_ = link.work_2007
            link.delete()
            work_.delete()
        elif type_ in [7, 8]:
            link = Exam.objects.get(work_2007=work)
            work_ = link.work
            link.delete()
            work_.delete()
        work.delete()
        LOGGER.info(f'Deleted work {id_} by user {request.user.id}.')
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
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierTwo']} | {operation_description}")
@api_view(["DELETE"])
@permission_classes([IsTierTwo, IsEnabled])
def delete_works(request):
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
                        {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=404)
        works = Work.objects.filter(school_class=class_)
        works.delete()
        LOGGER.warning(f'Deleted all works by user {request.user.id}.')
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


@swagger_auto_schema(method='PATCH', operation_summary="Удаление файла у работы.",
                     manual_parameters=[file_param],
                     responses=delete_file_from_homework_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierOne']}")
@api_view(["PATCH"])
@permission_classes([IsTierOne, IsEnabled])
def delete_file_from_work(request):
    try:
        file_id = get_variable("file", request)
        if (file_id is None) or (file_id == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id файла.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        work_file = WorkFile.objects.get(id=file_id)
        path = os.path.join(MEDIA_ROOT, f'{work_file.file}')
        if path is not None:
            try:
                os.remove(path)
            except:
                pass
        work_file.delete()
        LOGGER.info(f'Deleted file from work {work_file.work_id} by user {request.user.id}.')
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


@swagger_auto_schema(method='PATCH', operation_summary="Открыть доступ к работе ученику.",
                     manual_parameters=[id_param, student_param],
                     responses=add_to_homework_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierOne']}")
@api_view(["PATCH"])
@permission_classes([IsTierOne, IsEnabled])
def add_to_work(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        student_id = get_variable("student", request)
        if (student_id is None) or (student_id == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        work = Work.objects.get(id=id_)
        student = User.objects.get(id=student_id)
        if student.school_class != work.school_class:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Класс ученика не соответствует классу работы.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        answers = ['#'] * work.exercises
        work_user = WorkUser.objects.filter(work=work, user=student)
        if work_user:
            work_user = work_user[0]
            work_user.is_closed = False
        else:
            work_user = WorkUser(work=work, user=student, answers=answers)
        work_user.save()
        LOGGER.info(f'Added student {student_id} to work {id_} by user {request.user.id}.')
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


@swagger_auto_schema(method='PATCH', operation_summary="Закрыть доступ к работе ученику.",
                     manual_parameters=[id_param, student_param],
                     responses=delete_from_homework_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierOne']}")
@api_view(["PATCH"])
@permission_classes([IsTierOne, IsEnabled])
def delete_from_work(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        student_id = get_variable("student", request)
        if (student_id is None) or (student_id == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        work = Work.objects.get(id=id_)
        student = User.objects.get(id=student_id)
        work_user = WorkUser.objects.get(work=work, user=student)
        work_user.is_closed = True
        work_user.save()
        LOGGER.info(f'Deleted student {student_id} from work {id_} by user {request.user.id}.')
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Работа или пользователь не существует или у пользователя нет доступа к этой работе.', 'details': {},
                 'instance': request.path},
                ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получение работы(пользователь).",
                     manual_parameters=[id_param],
                     responses=get_user_homework_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAuthenticated']}")
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEnabled])
def get_user_work(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        work = Work.objects.get(id=id_)
        student = User.objects.get(id=request.user.id)
        work_user = WorkUser.objects.filter(user=student, work=work)
        if not work_user:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        work_user = work_user[0]
        files = WorkFile.objects.filter(work=work)
        files_list = []
        host = settings.MEDIA_HOST_PATH
        for file in files:
            link = file.file.name
            name = link.split('/')[1]
            ext = name.split('.')[-1]
            files_list.append({'link': f'{host}/{link}', 'name': name, 'ext': ext})
        response = {
            'id': work.id,
            'name': work.name,
            'text': work.text,
            'fields': work.exercises,
            'files': files_list,
            'class': work.school_class,
            'is_done': work.is_done,
            'is_checked': work.is_checked,
            'created_at': str(work.created_at)
        }
        grade = Grade.objects.get(work=work, user=student)
        max_score = grade.max_score
        score = grade.max_score
        if work_user.is_done:
            response['user_answers'] = work_user.answers
            user_files = WorkUserFile.objects.filter(link=work_user)
            user_files_list = []
            for file in user_files:
                link = file.file.name
                name = link.split('/')[1]
                user_files_list.append({'link': link, 'name': name, 'ext': file.ext})
            response['user_files'] = user_files_list
            response['answered_at'] = str(work_user.answered_at)
        if work_user.is_checked:
            response['answers'] = work.answers
            response['score'] = score
            response['max_score'] = max_score
        response['comment'] = work_user.comment
        return HttpResponse(json.dumps(response, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Работа не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='POST', operation_summary="Ответ на домашнюю работу.",
                     request_body=create_response_request_body,
                     responses=create_response_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAuthenticated']}")
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsEnabled])
def create_response(request):
    try:
        if request.POST or request.FILES:
            data = request.POST
            files = request.FILES
        else:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=400)
        id_ = data['id']
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        work = Work.objects.get(id=id_)
        student = User.objects.get(id=request.user.id)
        work_user = WorkUser.objects.filter(user=student, work=work)
        if not work_user:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        work_user = work_user[0]
        if work_user.is_closed:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Работа закрыта.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        answers = data.getlist("answers")
        fields = len(answers)
        if fields != work.exercises:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Некорректное количество ответов.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=403)
        files = files.getlist('files')
        for file in files:
            if 'image' in str(file.content_type):
                pass
            elif file.content_type in ('application/pdf', 'application/octet-stream'):
                pass
            else:
                return HttpResponse(
                    json.dumps({'state': 'error', 'message': 'Недопустимый файл.', 'details': {'ct': file.content_type},
                                'instance': request.path},
                               ensure_ascii=False), status=404)
        work_user.is_done = True
        work_user.answers = answers
        work_user.answered_at = timezone.now()
        for file in files:
            ext = file.name.split('.')[1]
            to_jpeg = False
            if ext == 'heic':
                ext = 'jpeg'
                to_jpeg = True
            homework_file = WorkUserFile(link=work_user, file=file, ext=ext)
            homework_file.save()
            if to_jpeg:
                path = os.path.join(MEDIA_ROOT, f'{homework_file.file}')
                new_path = heif_to_jpeg(path)
                new_name = f'{str(homework_file.file).split(".")[0]}.jpeg'
                if new_path is not None:
                    homework_file.file = new_name
                    homework_file.save()
                    os.remove(path)
        work_user.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Работа не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='PATCH', operation_summary="Проверка домашней работы(админка).",
                     request_body=check_user_homework_request_body,
                     responses=check_user_homework_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']}")
@api_view(["PATCH"])
@permission_classes([IsAdmin, IsEnabled])
def check_user_homework(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        id_ = request_body['id']
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        student_id = request_body['student']
        if (student_id is None) or (student_id == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        work = Work.objects.get(id=id_)
        student = User.objects.get(id=student_id)
        admin = User.objects.get(id=request.user.id)
        work_user = WorkUser.objects.filter(user=student, work=work)
        if not work_user:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        work_user = work_user[0]
        grade_row = Grade.objects.get(user=student, work=work)
        work_grades = list(map(float, work.grades))
        new_grades = grade_row.grades
        grades = request_body["grades"]
        old_score = grade_row.score
        score = 0
        max_score = 0
        exercises = 0
        is_empty = True
        for i, value in enumerate(grades):
            if ',' in value:
                value = value.replace(',', '.')
            if not validate_grade(value):
                return HttpResponse(
                    json.dumps({'state': 'error', 'message': 'Некорректное значение оценки.', 'details': {},
                                'instance': request.path},
                               ensure_ascii=False), status=400)
            if value == '-':
                is_empty = False
                pass
            elif value == '#':
                exercises += 1
                max_score += work_grades[i]
            else:
                is_empty = False
                exercises += 1
                max_score += work_grades[i]
                score += float(value)
            if score > work.max_score:
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': 'Некорректное значение оценок. Сумма вышла больше максимума.',
                         'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=404)
            if is_empty:
                exercises = 0
                max_score = 0
                score = 0
                work_user.is_checked = False
                work_user.checked_at = None
                work_user.is_done = False
                work_user.checker = None
            else:
                work_user.is_checked = True
                work_user.checked_at = timezone.now()
                work_user.is_done = True
                work_user.checker = admin
            new_grades[i] = value
        grade_row.score = score
        grade_row.exercises = exercises
        grade_row.max_score = max_score
        grade_row.grades = new_grades
        grade_row.save()
        if 'comment' in request_body.keys():
            comment = request_body['comment']
            work_user.comment = comment
        work_user.save()
        if score != old_score:
            manas_delete = Mana.objects.filter(Q(user=student) & Q(work=work))
            manas_delete.delete()
        if work.type == 6:
            count = 0
            for grade_ in new_grades:
                if is_number_float(grade_):
                    if float(grade_) > 0:
                        count += 1
            green, blue = mana_generation(int(work.type), work.is_homework, count, 0)
        else:
            green, blue = mana_generation(int(work.type), work.is_homework, score, max_score)
        if score != old_score:
            for i in range(0, green):
                mana = Mana(user=student, work=work, color='green')
                mana.save()
            for i in range(0, blue):
                mana = Mana(user=student, work=work, color='blue')
                mana.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Работа или пользователь не существует.', 'details': {},
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


@swagger_auto_schema(method='PATCH', operation_summary="Вернуть домашнюю работу с комментариями(админка).",
                     request_body=return_user_homework_request_body,
                     responses=return_user_homework_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']}")
@api_view(["PATCH"])
@permission_classes([IsAdmin, IsEnabled])
def return_user_homework(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        id_ = request_body['id']
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        student_id = request_body['student']
        if (student_id is None) or (student_id == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        work = Work.objects.get(id=id_)
        student = User.objects.get(id=student_id)
        admin = User.objects.get(id=request.user.id)
        work_user = WorkUser.objects.filter(user=student, work=work)
        if not work_user:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        work_user = work_user[0]
        comment = request_body["comment"]
        work_user.checker = admin
        work_user.is_done = False
        work_user.comment = comment
        work_user.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Работа или пользователь не существует.', 'details': {},
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


@swagger_auto_schema(method='GET', operation_summary="Получение списка домашних(пользователь).",
                     responses=get_my_homeworks_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAuthenticated']}")
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEnabled])
def get_my_homeworks(request):
    try:
        student = User.objects.get(id=request.user.id)
        work_user = WorkUser.objects.filter(user=student, is_closed=False).select_related('work').order_by('work__created_at').values('name', 'is_done', 'is_checked')
        works_list = {}
        for work in work_user:
            works_list[work['id']] = {
                'name': work['name'],
                'is_done': work['is_done'],
                'is_checked': work['is_checked'],
                'green': 0,
                'blue': 0
            }
        grades = Grade.objects.filter(work_id__in=list(works_list.keys()), work__is_homework=True).select_related(
            'work').values('max_score', 'work_id', 'work__max_score', 'score')
        manas = Mana.objects.filter(work_id__in=list(works_list.keys()), user=student).values('work_id', 'color', 'is_given')
        for grade in grades:
            if grade['max_score']:
                works_list[grade['work_id']]['max_score'] = grade['max_score']
            else:
                works_list[grade['work_id']]['max_score'] = grade['work__max_score']
            works_list[grade['work_id']]['score'] = grade['score']
        for mana in manas:
            if mana['work_id'] in works_list:
                works_list[mana['work_id']][mana['color']] += 1
        homeworks_list = []
        for homework in works_list:
            result = {
                'id': homework,
                'name': works_list[homework]['title'],
                'is_done': works_list[homework]['is_done'],
                'is_checked': works_list[homework]['is_checked']
            }
            if works_list[homework]['is_checked']:
                result['score'] = works_list[homework]['score']
                result['max_score'] = works_list[homework]['max_score']
                result['blue'] = works_list[homework]['blue']
                result['green'] = works_list[homework]['green']
            homeworks_list.append(result)
        return HttpResponse(json.dumps({'homeworks': homeworks_list}, ensure_ascii=False), status=200)
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


@swagger_auto_schema(method='GET', operation_summary="Получение списка классных(пользователь).",
                     responses=get_my_classworks_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAuthenticated']}")
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEnabled])
def get_my_classworks(request):
    try:
        student = User.objects.get(id=request.user.id)
        groups = GroupUser.objects.filter(user=student).select_related('group')
        files = GroupWorkFile.objects.filter(group__in=groups).select_related('work').order_by('added_at').values(
            'file', 'ext', 'work__id', 'work__name')
        classworks_list = {}
        host = settings.MEDIA_HOST_PATH
        for file in files:
            link = file['file']
            name = link.split('/')[1]
            ext = file['ext']
            if file['work_id'] not in classworks_list:
                classworks_list[file['work__id']] = {
                    'name': file['work__name'],
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
            ext = file.name.split('.')[1]
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
        school_class = work.school_class
        host = settings.MEDIA_HOST_PATH
        group_files = GroupWorkFile.objects.filter(work=work).values('id', 'file', 'ext', 'group_id')
        files_dict = defaultdict(list)
        for file in group_files:
            name = file['file'].split('/')[1]
            link = f"{host}/{file['file']}"
            ext = file['ext']
            files_dict[file['group_id']].append({
                'id': file['id'],
                'name': name,
                'link': link,
                'ext': ext
            })

        groups = Group.objects.filter(school_class=school_class).values('id', 'name', 'marker')
        groups_list = []
        for group in groups:
            group_files = files_dict[group['id']] if group['id'] in files_dict else []
            groups_list.append({
                'group_id': group['id'],
                'group_name': group['name'],
                'group_marker': group['marker'],
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


@swagger_auto_schema(method='POST', operation_summary="Установить дату проведения домашней работы для группы.",
                     request_body=set_homework_date_request_body,
                     responses=set_homework_date_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierOne']}")
@api_view(["POST"])
@permission_classes([IsTierOne, IsEnabled])
def set_homework_date(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        group_id = request_body['group']
        work_id = request_body['work']
        date = request_body['date']
        if date:
            date = datetime.strptime(date, '%d.%m.%Y')
        group = Group.objects.get(id=group_id)
        work = Work.objects.get(id=work_id)
        row = GroupWorkDate.objects.filter(work=work, group=group)
        if row:
            row = row[0]
            row.date = date
        else:
            row = GroupWorkDate(work=work, group=group, date=date)
        if date <= datetime.today():
            row.is_given = True
            answers = ['#'] * work.exercises
            students = GroupUser.objects.filter(group=group).select_related('user')
            for student in students:
                user = student.user
                try:
                    if user.school_class == work.school_class:
                        work_user = WorkUser(user=user, work=work, answers=answers)
                        work_user.save()
                except Exception as e:
                    pass
        row.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except ObjectDoesNotExist as e:
        return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Группа или работа не существует.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='DELETE', operation_summary="Удалить дату проведения домашней работы для группы.",
                     manual_parameters=[work_param, group_param],
                     responses=delete_homework_date_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierOne']}")
@api_view(["DELETE"])
@permission_classes([IsTierOne, IsEnabled])
def delete_homework_date(request):
    try:
        group_id = get_variable("group", request)
        if not group_id:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id группы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=400)
        work_id = get_variable("work", request)
        if not work_id:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=400)
        group = Group.objects.get(id=group_id)
        work = Work.objects.get(id=work_id)
        row = GroupWorkDate.objects.filter(work=work, group=group)
        if row:
            row = row[0]
            row.delete()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Группа или работа не существует.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получить даты проведения домашних работ для группы, либо для домашней работы получить даты проведения в группах.",
                     manual_parameters=[work_param, group_param],
                     responses=get_homeworks_dates_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']}")
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_homeworks_dates(request):
    try:
        group_filter = False
        work_filter = False
        group_id = get_variable("group", request)
        if group_id not in [None, '']:
            group_filter = True
        work_id = get_variable("work", request)
        if work_id not in [None, '']:
            group_filter = False
            work_filter = True

        result = []
        if group_filter:
            group = Group.objects.get(id=group_id)
            rows = GroupWorkDate.objects.filter(group=group).values('work_id', 'date')
            for row in rows:
                result.append({
                    'work_id': row['work_id'],
                    'group_id': group_id,
                    'date': row['date'].strftime('%d.%m.%Y'),
                })
        elif work_filter:
            work = Work.objects.get(id=work_id)
            rows = GroupWorkDate.objects.filter(work=work).values('group_id', 'date')
            for row in rows:
                result.append({
                    'work_id': row['work_id'],
                    'group_id': group_id,
                    'date': row['date'].strftime('%d.%m.%Y'),
                })
        else:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Необходимо указать либо work, либо group.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        return HttpResponse(json.dumps({'groups_works_dates': result}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Группа или работа не существует.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получение списка домашних работ.",
                     manual_parameters=[class_param, theme_param, type_param],
                     responses=get_homeworks_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']} | {operation_description}")
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_homeworks(request):
    try:
        class_ = get_variable("class", request)
        theme = get_variable("theme", request)
        type_ = get_variable("type", request)
        if class_ not in ['4', '5', '6', '7']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс учеников.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        works = Work.objects.filter(is_homework=True, school_class=int(class_)).exclude(type__in=[1, 2, 3, 4, 7, 8, 9]).select_related("theme").order_by('-created_at')
        works_users = WorkUser.objects.filter(work__in=works).select_related('user').values('work_id', 'user_id', 'is_checked', 'is_done')
        works_users_dict = {}
        for wu in works_users:
            if wu['work_id'] not in works_users_dict:
                works_users_dict[wu['work_id']] = {
                    'amount': 0,
                    'not_checked': 0
                }
            works_users_dict[wu['work_id']]['amount'] += 1
            if wu['is_done'] and not wu['is_checked']:
                works_users_dict[wu['work_id']]['not_checked'] += 1
        if (theme is not None) and (theme != ''):
            works = works.filter(theme_id=theme)
        if type_ in ['0', '5', '6']:
            works = works.filter(type=type_)
        works = works.values('id', 'name', 'grades', 'max_score', 'exercises', 'theme__id', 'theme__name', 'type',
                             'is_homework')
        works_list = []
        for work in works:
            if work['id'] in works_users_dict:
                amount = works_users_dict[work['id']]['amount']
                not_checked = works_users_dict[work['id']]['not_checked']
            else:
                amount = 0
                not_checked = 0
            works_list.append({
                "id": work['id'],
                "name": work['name'],
                "grades": work['grades'],
                "max_score": work['max_score'],
                "exercises": work['exercises'],
                "theme_id": work['theme__id'],
                "theme_name": work['theme__name'],
                "work_type": work['type'],
                "is_homework": work['is_homework'],
                "amount": amount,
                "not_checked": not_checked,
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


@swagger_auto_schema(method='GET', operation_summary="Получение списка классных работ.",
                     manual_parameters=[class_param, theme_param, type_param],
                     responses=get_works_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']} | {operation_description}")
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_classworks(request):
    try:
        class_ = get_variable("class", request)
        theme = get_variable("theme", request)
        type_ = get_variable("type", request)
        if class_ not in ['4', '5', '6', '7']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс учеников.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        works = Work.objects.filter(is_homework=False, school_class=int(class_)).exclude(type__in=[0, 5, 6, 7, 8, 9]).select_related("theme").order_by('-id')
        if (theme is not None) and (theme != ''):
            works = works.filter(theme_id=theme)
        if type_ in ['1', '2', '3', '4']:
            works = works.filter(type=type_)
        works = works.values('id', 'name', 'grades', 'max_score', 'exercises', 'theme_id', 'theme__name', 'type', 'is_homework')
        works_list = []
        for work in works:
            works_list.append({
                "id": work['id'],
                "name": work['name'],
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


@swagger_auto_schema(method='GET', operation_summary="Получение ответов на работу(для таблицы).",
                     manual_parameters=[id_param],
                     responses=get_all_answers_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']}")
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_all_answers(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        admin = Admin.objects.get(user_id=request.user.id)
        work = Work.objects.get(id=id_)
        grades = Grade.objects.filter(work=work).values('user_id', 'score', 'max_score')
        grades_dict = {}
        for grade in grades:
            if grade['user_id'] not in grades_dict:
                grades_dict[grade['user_id']] = {'score': 0,'max_score': 0, 'green': 0, 'blue': 0}
            grades_dict[grade['user_id']]['score'] = grade['score']
            grades_dict[grade['user_id']]['max_score'] = grade['max_score'] if grade['max_score'] else work.max_score
        manas = Mana.objects.filter(work=work, is_given=False).values('user_id', 'color')
        for mana in manas:
            if mana['color'] == 'blue':
                grades_dict[mana['user_id']]['blue'] += 1
            if mana['color'] == 'green':
                grades_dict[mana['user_id']]['green'] += 1
        response = {'id': work.id, 'name': work.name, 'answers': work.answers,
                    'students': []}
        work_users = WorkUser.objects.filter(work=work).order_by('user_id').select_related('user', 'checker').values(
            'id', 'user_id', 'user__name', 'is_done', 'is_checked', 'comment', 'checker_id', 'checker__name',
            'checked_at', 'added_at', 'answered_at', 'answers', 'is_closed'
        )
        groups_users = GroupUser.objects.filter(group__school_class=4).select_related('group').values('user_id', 'group_id', 'group__marker', 'group__name')
        user_groups_dict = {}
        for gu in groups_users:
            if gu['user_id'] not in user_groups_dict:
                user_groups_dict[gu['user_id']] = []
            user_groups_dict[gu['user_id']].append({
                'id': gu['group_id'],
                'color': gu['group__marker'],
                'name': gu['group__name']
            })
        work_user_files = WorkUserFile.objects.filter(link__work=work).values('link', 'file', 'ext')
        files_dict = {}
        for user_file in work_user_files:
            if user_file['link'] not in files_dict:
                files_dict[user_file['link']] = []
            files_dict[user_file['link']].append({
                'file': user_file['file'],
                'ext': user_file['ext']
            })
        students_list = []
        host = settings.MEDIA_HOST_PATH
        for wu in work_users:
            student_data = {'id': wu['user_id'], 'name': wu['user__name'], 'answers': [], 'files': [], 'groups': []}
            if wu['user_id'] in user_groups_dict:
                student_data['groups'] = user_groups_dict[wu['user_id']]
            if wu['is_done']:
                answers_list = wu['answers']
                if wu['id'] in files_dict:
                    files = files_dict[wu['id']]
                    for file in files:
                        name = file['file'].split('/')[1]
                        link = f"{host}/{file['file']}"
                        ext = file['ext']
                        student_data['files'].append({'link': link, 'name': name, 'ext': ext})
            else:
                answers_list = [''] * len(work.answers)
            if wu['is_checked']:
                score = grades_dict[wu['user_id']]['score']
                max_score = grades_dict[wu['user_id']]['max_score']
                green = grades_dict[wu['user_id']]['green']
                blue = grades_dict[wu['user_id']]['blue']
            else:
                score = None
                max_score = None
                green = None
                blue = None
            if wu['checker_id']:
                if admin.user_id == wu['checker_id']:
                    checker = wu['checker__name']
                elif admin.tier == 0:
                    checker = ""
                else:
                    checker = wu['checker__name']
            else:
                checker = ""
            comment = wu['comment']
            student_data['answers'] = answers_list
            student_data['score'] = score
            student_data['max_score'] = max_score
            student_data['comment'] = comment
            student_data['checker'] = checker
            student_data['is_done'] = wu['is_done']
            student_data['is_checked'] = wu['is_checked']
            student_data['is_closed'] = wu['is_closed']
            student_data['green'] = green
            student_data['blue'] = blue
            if wu['checked_at']:
                checked_at = str(wu['checked_at'])
            else:
                checked_at = None
            if wu['answered_at']:
                answered_at = str(wu['answered_at'])
            else:
                answered_at = None
            if wu['added_at']:
                added_at = str(wu['added_at'])
            else:
                added_at = None
            student_data['checked_at'] = checked_at
            student_data['answered_at'] = answered_at
            student_data['added_at'] = added_at
            students_list.append(student_data)
        response['students'] = students_list
        return HttpResponse(json.dumps(response, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Работа не существует.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)