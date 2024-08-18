from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from kpm.apps.users.permissions import *
from kpm.apps.users.functions import *
from kpm.apps.groups.models import Group, GroupUser
from django.core.exceptions import ObjectDoesNotExist
import json
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.groups.docs import *
from django.db import IntegrityError
from kpm.apps.users.docs import permissions_operation_description
from kpm.apps.groups.validators import validate_group_type_for_class
from django.core.exceptions import ValidationError


LOGGER = settings.LOGGER


@swagger_auto_schema(method='GET', operation_summary="Получение групп.",
                     manual_parameters=[class_param],
                     responses=get_groups_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']} | {operation_description}")
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_groups(request):
    try:
        class_ = get_variable("class", request)
        if class_ not in ['4', '5', '6', '7']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс учеников.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        groups_dict = {}
        groups = Group.objects.filter(school_class=class_).values('id', 'name', 'marker', 'type')
        groups_ids = []
        for row in groups:
            if row['id'] not in groups_dict:
                groups_ids.append(row['id'])
                groups_dict[row['id']] = {
                    'id': row['id'],
                    'name': row['name'],
                    'color': row['marker'],
                    'type': row['type'],
                    'students': [],
                }
        groups_users = GroupUser.objects.filter(group_id__in=groups_ids).select_related('user').values('group_id', 'user__id', 'user__name')
        for user in groups_users:
            groups_dict[user['group_id']]['students'].append({
                'id': user['user__id'],
                'name': user['user__name'],
            })
        return HttpResponse(json.dumps({'groups': list(groups_dict.values())}, ensure_ascii=False), status=200)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получение группы.",
                     manual_parameters=[id_group_param],
                     responses=get_group_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']}")
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
        groups_users = GroupUser.objects.filter(group=group).select_related('user').values('user__id', 'user__name')
        result = {
            'id': group.id,
            'name': group.name,
            'marker': group.marker,
            'type': group.type,
            'students': [],
        }
        for user in groups_users:
            result['students'].append({
                'id': user['user__id'],
                'name': user['user__name'],
            })
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
                     responses=create_group_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierOne']}")
@api_view(["POST"])
@permission_classes([IsTierOne, IsEnabled])
def create_group(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        if request_body["class"] not in [4, 5, 6, 7]:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        if not validate_group_type_for_class(request_body["type"], request_body["class"]):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан тип группы.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        type_ = None if request_body["class"] == 4 else request_body["type"]
        group = Group(name=request_body['name'], school_class=request_body['class'], marker=request_body['marker'], type=type_)
        group.save()
        if "students" in request_body:
            for student in request_body["students"]:
                try:
                    group_user = GroupUser.objects.create(group=group, user_id=student)
                except IntegrityError:
                    group_user = GroupUser.objects.filter(user_id=student)
                    group_user.group = group
                    group_user.save()
                except Exception:
                    pass
        LOGGER.info(f'Created group {group.id} by user {request.user.id}.')
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ValidationError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Ошибка валидации данных.', 'details': {'message': str(e)}, 'instance': request.path},
                       ensure_ascii=False), status=404)
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
                     responses=update_group_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierOne']}")
@api_view(["PATCH"])
@permission_classes([IsTierOne, IsEnabled])
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
        group.save()
        LOGGER.info(f'Updated group {group.id} by user {request.user.id}.')
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ValidationError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Ошибка валидации данных.', 'details': {'message': str(e)}, 'instance': request.path},
                       ensure_ascii=False), status=404)
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
                     responses=delete_group_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierTwo']}")
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
                     responses=add_to_group_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierOne']}")
@api_view(["PATCH"])
@permission_classes([IsTierOne, IsEnabled])
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
        students_ids = request_body["students"]
        students = User.objects.filter(id__in=students_ids)
        for student in students:
            if group.school_class != student.school_class:
                continue
            group_user = GroupUser.objects.create(group=group, user=student)
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
                     responses=delete_from_group_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierOne']}")
@api_view(["PATCH"])
@permission_classes([IsTierOne, IsEnabled])
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


@swagger_auto_schema(method='GET', operation_summary="Получение типов групп.",
                     manual_parameters=[class_param],
                     responses=get_groups_types_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']}")
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_groups_types(request):
    try:
        class_ = get_variable("class", request)
        if class_ == '4':
            result = []
        elif class_ in ['5', '6']:
            result = [
                {'id': 0, 'name': 'Продвинутые'},
                {'id': 1, 'name': 'Углубленные'},
            ]
        elif class_ == '7':
            result = [
                {'id': 0, 'name': 'Продвинутые'},
                {'id': 2, 'name': 'Углубленные алгебра'},
                {'id': 3, 'name': 'Углубленные геометрия'},
            ]
        else:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс учеников.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        return HttpResponse(json.dumps({'types': result}, ensure_ascii=False), status=200)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)
