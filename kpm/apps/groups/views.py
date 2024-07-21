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
        groups = GroupUser.objects.filter(group__school_class=class_).select_related('group', 'user').order_by('group__created_at').values(
            'group__id', 'group__name', 'group__marker', 'user__id', 'user__name')
        groups_works_dates = GroupWorkDate.objects.filter(group__school_class=class_).select_related('work').order_by('group_id', 'date').values(
            'group_id', 'work__id', 'work__name', 'date')
        for row in groups:
            if row['group__id'] not in groups_dict:
                groups_dict[row['group__id']] = {
                    'id': row['group__id'],
                    'name': row['group__name'],
                    'color': row['group__marker'],
                    'students': [{
                        'id': row['user__id'],
                        'name': row['user__name']
                    }],
                    'works_dates': []
                }
            else:
                groups_dict[row['group__id']]['students'].append({
                    'id': row['user__id'],
                    'name': row['user__name']
                })
        for row in groups_works_dates:
            work_id = row['work__id']
            work_name = row['work__name']
            date = row['date']
            group_id = row['group_id']
            groups_dict[group_id]['works_dates'].append({
                'work_id': work_id,
                'work_name': work_name,
                'date': date
            })
        return HttpResponse(json.dumps({'groups': list(groups_dict.values())}, ensure_ascii=False), status=200)
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
        groups_users = GroupUser.objects.filter(group=group).select_related('user').values('user__id', 'user__name')
        groups_works_dates = GroupWorkDate.objects.filter(group=group).select_related('work').order_by('date').values('work__id', 'work__name', 'date')
        result = {
            'id': group.id,
            'name': group.name,
            'marker': group.marker,
            'students': [],
            'works_dates': []
        }
        for user in groups_users:
            result['students'].append({
                'id': user['user__id'],
                'name': user['user__name'],
            })
        for row in groups_works_dates:
            work_id = row['work__id']
            work_name = row['work__name']
            date = row['date']
            result['works_dates'].append({
                'work_id': work_id,
                'work_name': work_name,
                'date': date
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
        if "works_dates" in request_body:
            current_works_dates = GroupWorkDate.objects.filter(group=group)
            current_works_dates.delete()
            for work_date in request_body["works_dates"]:
                GroupWorkDate.objects.create(group=group, work_id=work_date["work_id"], date=work_date["date"])
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
            group_user = GroupUser.objects.create(group=group, user_id=student)
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
