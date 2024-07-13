import time

from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from kpm.apps.users.models import *
from kpm.apps.users.permissions import *
from kpm.apps.users.functions import *
from kpm.apps.works.models import Work
from kpm.apps.grades.models import Grade
from django.core.exceptions import ObjectDoesNotExist
import json
from django.db.models import Sum, Q, Count
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.hashers import check_password, make_password
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.users.docs import *
from django.utils import timezone
from datetime import datetime, timedelta


SECRET_KEY = settings.SECRET_KEY
UNIVERSAL = settings.UNIVERSAL
LOGGER = settings.LOGGER


@swagger_auto_schema(method='GET', operation_summary="Получение пользователя.",
                     manual_parameters=[id_param],
                     responses=get_user_responses)
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEnabled])
def get_user(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        if not is_trusted(request, id_):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        student = User.objects.get(id=id_)
        student.last_login = timezone.now()
        student.save()
        logons = History.objects.filter(user=student).order_by('-datetime')
        if logons:
            last_logon = logons[0]
            current_date = datetime.now()
            if not (
                    last_logon.datetime.date() == current_date.date() and last_logon.datetime.hour == current_date.hour):
                login_obj = History(user=student)
                login_obj.save()
        else:
            login_obj = History(user=student)
            login_obj.save()
        name_splitted = student.name.split(' ')
        if len(name_splitted) == 2:
            name = name_splitted[1]
        else:
            name = student.name
        result = {
            "id": student.id,
            "name": name,
            "login": student.login,
            "default_password": student.default_password,
            "class": student.school_class,
            "is_default": student.is_default,
            "experience": student.experience,
            "mana_earned": student.mana_earned,
            "last_homework_id": student.last_homework_id,
            "last_classwork_id": student.last_classwork_id
        }
        if student.is_admin:
            tier = Admin.objects.get(user=student).tier
            result['admin_tier'] = tier
        return HttpResponse(
            json.dumps(result, ensure_ascii=False),
            status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
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


@swagger_auto_schema(method='GET', operation_summary="Получение пользователей.",
                     manual_parameters=[class_param, is_admin_param],
                     responses=get_users_responses)
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_users(request):
    try:
        is_admin = get_variable("is_admin", request)
        if is_admin:
            query = Q(is_admin=1)
        else:
            class_ = get_variable("class", request)
            if not class_:
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Не указан класс ученика.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=404)
            else:
                if class_ not in ['4', '5', '6', 4, 5, 6]:
                    return HttpResponse(
                        json.dumps(
                            {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {},
                             'instance': request.path},
                            ensure_ascii=False), status=404)
            query = Q(is_admin=0) & Q(school_class=int(class_))
        students = User.objects.filter(query).select_related('group').order_by('name')
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
        students_list = []
        if not students:
            return HttpResponse(
                json.dumps({'students': students_list}, ensure_ascii=False), status=200)
        for student in students:
            if not student.default_password:
                default_password = ""
            else:
                default_password = student.default_password
            if student.group:
                marker = student.group.marker
                group_name = student.group.name
                group_id = student.group.id
            else:
                marker = 7
                group_name = None
                group_id = None
            student_info = {"id": student.id,
                            "name": student.name,
                            "login": student.login,
                            "default_password": default_password,
                            "experience": student.experience,
                            "mana_earned": student.mana_earned,
                            "last_homework_id": student.last_homework_id,
                            "last_classwork_id": student.last_classwork_id,
                            "group_id": group_id,
                            "group_name": group_name,
                            "color": MARKER_CHOICES[marker],
                            "is_disabled": student.is_disabled
                            }
            students_list.append(student_info)
        return HttpResponse(
            json.dumps({'students': students_list}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='POST', operation_summary="Создание пользователя.",
                     request_body=create_user_request_body,
                     responses=create_user_responses)
@api_view(["POST"])
@permission_classes([IsAdmin, IsEnabled])
def create_user(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        students = User.objects.all()
        if students:
            last_student = students.latest("id")
            last_id = last_student.id
        else:
            last_id = 0
        id_, login_, password_ = login_password_creator(request_body["name"], last_id + 1)
        if request_body["class"] not in ['4', '5', '6', 4, 5, 6]:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        encrypted_password = make_password(password_, SECRET_KEY)
        student = User(id=last_id + 1, name=request_body["name"], login=login_, default_password=password_,
                       password=encrypted_password, school_class=request_body["class"], is_superuser=False)
        student.save()
        works = Work.objects.all()
        for work in works:
            grades = work.grades.split('_._')
            empty_grades = '_._'.join(list('#' * len(grades)))
            grade = Grade(user=student, work=work, grades=empty_grades, max_score=0, score=0, exercises=0)
            grade.save()
        LOGGER.info(f'Created student {student.id} by user {request.user.id}.')
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


@swagger_auto_schema(method='DELETE', operation_summary="Удаление пользователя.",
                     manual_parameters=[id_param],
                     responses=delete_user_responses)
@api_view(["DELETE"])
@permission_classes([IsTierTwo, IsEnabled])
def delete_user(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        student = User.objects.get(id=id_)
        student.delete()
        LOGGER.warning(f'Deleted student {id_} by user {request.user.id}.')
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
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


@swagger_auto_schema(method='DELETE', operation_summary="Удаление пользователей.",
                     manual_parameters=[class_param],
                     responses=delete_users_responses)
@api_view(["DELETE"])
@permission_classes([IsTierTwo, IsEnabled])
def delete_users(request):
    try:
        class_ = get_variable("class", request)
        if not class_:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан класс учеников.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        else:
            if class_ not in ['4', '5', '6', 4, 5, 6]:
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Неверно указан класс учеников.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=404)
        students = User.objects.filter(school_class=int(class_))
        if not students:
            return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
        students.delete()
        LOGGER.warning(f'Deleted all students by user {request.user.id}.')
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


@swagger_auto_schema(method='PATCH', operation_summary="Изменение пароля.",
                     request_body=change_password_request_body,
                     responses=change_password_responses)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsEnabled])
def change_password(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=400)
        is_default = False
        if 'id' not in request_body.keys():
            id_ = request.user.id
            password_ = str(request_body["password"])
        else:
            id_ = request_body["id"]
            password_ = password_creator()
            is_default = True
        if not is_trusted(request, id_):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        user = User.objects.get(id=id_)
        if not is_default:
            encrypted_password = make_password(password_, SECRET_KEY)
            user.password = encrypted_password
            user.default_password = None
            user.is_default = False
        else:
            user.default_password = password_
            user.is_default = True
            user.password = ""
        user.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except TokenError as e:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Токен недействителен.', 'details': {},
                 'instance': request.path},
                ensure_ascii=False), status=400)
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


@swagger_auto_schema(method='POST', operation_summary="Вход в аккаунт.",
                     request_body=login_request_body,
                     responses=login_responses)
@api_view(["POST"])
def login(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=400)
        login_ = request_body["login"]
        password = request_body["password"]
        user = User.objects.get(login=login_)
        if user.is_disabled:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Аккаунт заблокирован.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=403)
        if check_password(password, UNIVERSAL) and not user.is_admin:
            is_passed = True
        else:
            is_passed = check_password(password, user.password)
        if is_passed:
            tokens = get_tokens_for_user(user)
            request.session['login'] = login_
            request.session['id'] = user.id
            return HttpResponse(json.dumps(
                    {'id': user.id, 'tokens': tokens, 'is_admin': user.is_admin}, ensure_ascii=False), status=200)
        else:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Неверный пароль.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=400)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': 'Пользователь не существует.', 'details': {},
             'instance': request.path},
            ensure_ascii=False), status=404)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {},
                        'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Выход из аккаунта.",
                     responses=logout_responses)
@api_view(["GET"])
def logout(request):
    try:
        refresh = request.data.get('refresh', None)
        if refresh:
            token = RefreshToken(refresh)
            token.blacklist()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET',
                     operation_summary="Список последних входов всех пользователей.",
                     responses=get_all_logons_responses)
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_all_logons(request):
    try:
        logons = History.objects.all().select_related('user').order_by('-datetime')
        logons_list = []
        for logon in logons:
            logons_list.append({
                'user_id': logon.user.id,
                'user_name': logon.user.name,
                'date': str(logon.datetime.date()),
                'hour': f'{logon.datetime.hour}:00',
                'datetime': str(logon.datetime)
            })
        return HttpResponse(json.dumps({'logons': logons_list}, ensure_ascii=False), status=200)
    except Exception as e:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Произошла странная ошибка.',
                 'details': {'error': str(e)},
                 'instance': request.path},
                ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получение групп.",
                     manual_parameters=[class_param],
                     responses=get_groups_responses,
                     operation_description=operation_description)
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
        groups_users = User.objects.filter(group__in=groups).select_related('group')
        for user in groups_users:
            if user.id not in groups_dict[user.group_id]['students_ids']:
                groups_dict[user.group_id]['students_ids'].append(user.id)
                groups_dict[user.group_id]['students'].append({
                    'id': user.id,
                    'name': user.name
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


@swagger_auto_schema(method='POST', operation_summary="Создание группы.",
                     request_body=create_group_request_body,
                     responses=create_group_responses,
                     operation_description=operation_description)
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
        if "students" in request_body:
            users = User.objects.filter(id__in=request_body["students"])
            for user in users:
                user.group = group
                user.save()
        group.save()
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
                     responses=update_group_responses,
                     operation_description=operation_description)
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
            users = User.objects.filter(id__in=request_body["students"])
            for user in users:
                user.group = group
                user.save()
        group.save()
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
                     manual_parameters=[group_param],
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
        users = User.objects.filter(id__in=students)
        for student in users:
            student.group = group
            student.save()
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
        users = User.objects.filter(id__in=students)
        for student in users:
            old_group = student.group_id
            student.group = None
            student.save()
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


@swagger_auto_schema(method='POST', operation_summary="Включить/выключить пользователя пользователя.",
                     manual_parameters=[user_param],
                     responses=toggle_suspending_user_responses)
@api_view(["POST"])
@permission_classes([IsTierTwo, IsEnabled])
def toggle_suspending_user(request):
    try:
        student_id = get_variable("student", request)
        if (student_id is None) or (student_id == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        student = User.objects.get(id=student_id)
        state = False if student.is_disabled else True
        student.is_disabled = state
        student.save()
        if state:
            LOGGER.info(f'Enabled student {student_id} by user {request.user.id}.')
        else:
            LOGGER.info(f'Disabled student {student_id} by user {request.user.id}.')
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
