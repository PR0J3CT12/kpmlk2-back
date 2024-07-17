from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from kpm.apps.users.models import *
from kpm.apps.users.permissions import *
from kpm.apps.users.functions import *
from kpm.apps.works.models import Work
from kpm.apps.groups.models import Group, GroupUser, GroupWorkDate
from django.core.exceptions import ObjectDoesNotExist
import json
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.groups.docs import *
from django.utils import timezone
from datetime import datetime, timedelta
from django.db import IntegrityError


LOGGER = settings.LOGGER


@swagger_auto_schema(method='GET', operation_summary="Получение групп.",
                     manual_parameters=[class_param],
                     responses=get_groups_responses)
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_groups(request):
    try:
        class_ = get_variable("class", request)
        if class_ not in ['4', '5', '6', 4, 5, 6]:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс учеников.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        groups_dict = {}
        groups = Group.objects.filter(school_class=class_).order_by('created_at')
        for group in groups:
            groups_dict[group.id] = {
                'id': group.id,
                'name': group.name,
                'marker': group.marker,
                'students_ids': [],
                'students': []
            }
        groups_users = GroupUser.objects.filter(group__in=groups).select_related('user')
        for user in groups_users:
            if user.user.id not in groups_dict[user.group_id]['students_ids']:
                groups_dict[user.group_id]['students_ids'].append(user.user.id)
                groups_dict[user.group_id]['students'].append({
                    'id': user.user.id,
                    'name': user.user.name
                })
        group_list = []
        for group in groups_dict:
            del groups_dict[group]['students_ids']
            group_list.append(groups_dict[group])
        return HttpResponse(json.dumps({'groups': group_list}, ensure_ascii=False), status=200)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получение группы.",
                     manual_parameters=[id_group_param],
                     responses=get_group_responses)
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_group(request):
    try:
        id_ = get_variable("id", request)
        if not id_:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан ID группы.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        group = Group.objects.get(id=id_)
        groups_users = GroupUser.objects.filter(group=group).select_related('user')
        result = {
            'id': group.id,
            'name': group.name,
            'marker': group.marker,
            'students_ids': [],
            'students': []
        }
        for user in groups_users:
            if user.user.id not in result['students_ids']:
                result['students_ids'].append(user.user.id)
                result['students'].append({
                    'id': user.user.id,
                    'name': user.user.name
                })
        del result['students_ids']
        return HttpResponse(json.dumps(result, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Группа не существует.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='POST', operation_summary="Создание группы.",
                     request_body=create_group_request_body,
                     responses=create_group_responses)
@api_view(["POST"])
@permission_classes([IsAdmin, IsEnabled])
def create_group(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        if request_body["class"] not in ['4', '5', '6', 4, 5, 6]:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        group = Group(name=request_body['name'], school_class=int(request_body['class']), marker=request_body['marker'])
        group.save()
        if "students" in request_body:
            for student in request_body["students"]:
                try:
                    group_user = GroupUser.objects.create(group=group, user_id=student)
                except IntegrityError:
                    group_user = GroupUser.objects.filter(user_id=student)
                    group_user.group = group
                    group_user.save()
        LOGGER.info(f'Created group {group.id} by user {request.user.id}.')
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Пользователь не существует.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='PATCH', operation_summary="Изменение группы.",
                     request_body=update_group_request_body,
                     responses=update_group_responses)
@api_view(["PATCH"])
@permission_classes([IsAdmin, IsEnabled])
def update_group(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        id_ = request_body['id']
        group = Group.objects.get(id=id_)
        if "name" in request_body:
            group.name = request_body['name']
        if "marker" in request_body:
            group.marker = request_body['marker']
        if "students" in request_body:
            current_students = GroupUser.objects.filter(group=group)
            current_students.delete()
            for student in request_body["students"]:
                group_user = GroupUser.objects.create(group=group, user_id=student)
        LOGGER.info(f'Updated group {group.id} by user {request.user.id}.')
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Пользователь не существует.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='DELETE', operation_summary="Удаление группы.",
                     manual_parameters=[id_group_param],
                     responses=delete_group_responses)
@api_view(["DELETE"])
@permission_classes([IsTierTwo, IsEnabled])
def delete_group(request):
    try:
        id_ = get_variable("group", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id группы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        group = Group.objects.get(id=id_)
        group.delete()
        LOGGER.warning(f'Deleted group {id_} by user {request.user.id}.')
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Группа не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='PATCH', operation_summary="Добавление учеников в группу.",
                     request_body=add_to_group_request_body,
                     responses=add_to_group_responses)
@api_view(["PATCH"])
@permission_classes([IsAdmin, IsEnabled])
def add_to_group(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        id_ = request_body['id']
        group = Group.objects.get(id=id_)
        students = request_body["students"]
        for student in students:
            try:
                group_user = GroupUser.objects.create(group=group, user_id=student)
            except IntegrityError:
                group_user = GroupUser.objects.filter(user_id=student)
                group_user.group = group
                group_user.save()
            LOGGER.info(f'Added student {student.id} to group {id_} by user {request.user.id}.')
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Группа или пользователь не существует.', 'details': {},
                        'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='PATCH', operation_summary="Удаление учеников из группы.",
                     request_body=delete_from_group_request_body,
                     responses=delete_from_group_responses)
@api_view(["PATCH"])
@permission_classes([IsAdmin, IsEnabled])
def delete_from_group(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        students = request_body['students']
        groups_users = GroupUser.objects.filter(id__in=students)
        for student in groups_users:
            old_group = student.group_id
            student.delete()
            LOGGER.info(f'Deleted student {student.id} from group {old_group} by user {request.user.id}.')
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Пользователь не существует.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)