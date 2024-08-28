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
        files = GroupWorkFile.objects.filter(group_id__in=groups).select_related('work').order_by('added_at').values(
            'file', 'ext', 'work_id', 'work__name')
        classworks_list = {}
        host = HOST
        for file in files:
            link = file['file']
            name = link.split('/')[-1]
            ext = file['ext']
            if file['work_id'] not in classworks_list:
                classworks_list[file['work_id']] = {
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
        if not validate_work_type_for_group_type(work.type, group.type):
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Тип работы не подходит для этого типа группы.', 'details': {},
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
        school_class = work.school_class
        host = HOST
        group_files = GroupWorkFile.objects.filter(work=work).values('id', 'file', 'ext', 'group_id')
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

        groups = Group.objects.filter(school_class=school_class).values('id', 'name', 'marker', 'type')
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