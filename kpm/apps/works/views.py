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
from django.db.models import Sum, Case, When, IntegerField, Count, Q
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
from kpm.apps.works.validators import *


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
                name = link.split('/')[-1]
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
        if work.is_homework or (work.type in [2, 10, 11]):
            groups_dict = {}
            groups = Group.objects.filter(school_class=work.school_class).order_by("name").values("id", "name", "marker", "type")
            for group in groups:
                groups_dict[group['id']] = {
                    "id": group['id'],
                    "name": group['name'],
                    "color": group['marker'],
                    "type": group['type'],
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
        if school_class not in ['4', '5', '6', '7']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        if type_ not in ['0', '1', '2', '3', '4', '5', '6', '9', '10', '11']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан тип работы.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        if not validate_work_type_for_class(type_, school_class):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Несоответствие типа работы и класса.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        if school_class != '4':
            course = data['course']
        else:
            course = '0'
        name = data["name"]
        if type_ == '2':
            grades = ["1", "1", "1"]
            max_score = 3
        elif type_ in ['10', '11']:
            grades = data.getlist("grades")
            max_score = len(grades)
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

        if school_class == '4':
            theme_id = '1' if type_ == '2' else data["theme_id"]
        elif school_class == '5':
            theme_id = "10"
        elif school_class == '6':
            theme_id = "11"
        elif school_class == '7':
            theme_id = "12"
        theme = Theme.objects.get(id=theme_id)
        if type_ in ['0', '5', '6', '7']:
            is_homework = True
        else:
            is_homework = False
        students = User.objects.filter(Q(is_admin=0) & Q(school_class=school_class))
        exercises = len(grades)
        if type_ not in ['3', '5']:
            work = Work(name=name, grades=grades, theme=theme, max_score=max_score,
                        exercises=exercises, school_class=school_class, type=type_,
                        is_homework=is_homework, author_id=request.user.id, course=course)
            work.full_clean()
            work_2007 = None
            link = None
        else:
            if type_ == '5':
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
                        is_homework=is_homework, author_id=request.user.id, course=course)
            work_2007 = Work(name=name, grades=grades_2007, theme=theme, max_score=max_score_2007,
                             exercises=exercises, school_class=school_class, type=type_2007,
                             is_homework=is_homework, author_id=request.user.id, course=course)
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
                ext = file.name.split('.')[-1]
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
    except ValidationError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Ошибка валидации данных.', 'details': {'message': str(e)}, 'instance': request.path},
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
                    ext = file.name.split('.')[-1]
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
