from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from kpm.apps.users.models import *
from kpm.apps.users.permissions import *
from kpm.apps.users.functions import *
from kpm.apps.logs.models import Log
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


@swagger_auto_schema(method='GET', operation_summary="Получение пользователя.",
                     manual_parameters=[id_param],
                     responses=get_user_responses)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
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
                     manual_parameters=[class_param],
                     responses=get_users_responses)
@api_view(["GET"])
@permission_classes([IsAdmin])
def get_users(request):
    try:
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
                        {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=404)
        students = User.objects.filter(Q(is_admin=0) & Q(school_class=int(class_))).select_related('group').order_by('name')
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
            else:
                marker = 7
            student_info = {"id": student.id,
                            "name": student.name,
                            "login": student.login,
                            "default_password": default_password,
                            "experience": student.experience,
                            "mana_earned": student.mana_earned,
                            "last_homework_id": student.last_homework_id,
                            "last_classwork_id": student.last_classwork_id,
                            "group": student.group,
                            "color": MARKER_CHOICES[marker]
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
@permission_classes([IsAdmin])
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
        student = User(id=last_id + 1, name=request_body["name"], login=login_, default_password=password_,
                       school_class=request_body["class"], is_superuser=False)
        student.save()
        log = Log(operation='INSERT', from_table='users', details='Добавлен новый ученик в таблицу users.')
        log.save()
        works = Work.objects.all()
        for work in works:
            grades = work.grades.split('_._')
            empty_grades = '_._'.join(list('#' * len(grades)))
            grade = Grade(user=student, work=work, grades=empty_grades, max_score=0, score=0, exercises=0)
            grade.save()
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
@permission_classes([IsTierTwo])
def delete_user(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        student = User.objects.get(id=id_)
        log_details = f'Удален ученик из таблицы users. ["id": {student.id} | "name": "{student.name}" | "login": {student.login} | "password": {student.password} | "experience": {student.experience} | "mana_earned": {student.mana_earned} | "last_homework_id": {student.last_homework_id} | "last_classwork_id": {student.last_classwork_id} | "school_class": {student.school_class}]'
        student.delete()
        log = Log(operation='DELETE', from_table='users', details=log_details)
        log.save()
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
@permission_classes([IsTierTwo])
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
        for student in students:
            log = Log(operation='DELETE', from_table='users',
                      details=f'Удален ученик из таблицы users. ["id": {student.id} | "name": "{student.name}" | "login": {student.login} | "password": {student.password} | "experience": {student.experience} | "mana_earned": {student.mana_earned} | "last_homework_id": {student.last_homework_id} | "last_classwork_id": {student.last_classwork_id} | "school_class": {student.school_class}]')
            log.save()
        students.delete()
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
@permission_classes([IsAuthenticated])
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
        log = Log(operation='UPDATE', from_table='users', details=f"Изменен пароль у пользователя {id_}.")
        log.save()
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
@permission_classes([IsNotAuthenticated])
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
        password_ = request_body["password"]
        user = User.objects.get(login=login_)
        if user.is_default:
            if password_ == user.default_password:
                request.session['login'] = login_
                request.session['id'] = user.id
                id_ = user.id
                tokens = get_tokens_for_user(user)
                return HttpResponse(json.dumps(
                    {'id': id_, 'tokens': tokens, 'is_admin': user.is_admin}, ensure_ascii=False), status=200)
            else:
                return HttpResponse(
                    json.dumps({'state': 'error', 'message': 'Неверный пароль.', 'details': {},
                                'instance': request.path},
                               ensure_ascii=False), status=400)
        else:
            if check_password(password_, user.password):
                request.session['login'] = login_
                request.session['id'] = user.id
                id_ = user.id
                tokens = get_tokens_for_user(user)
                return HttpResponse(json.dumps(
                    {'id': id_, 'tokens': tokens, 'is_admin': user.is_admin}, ensure_ascii=False), status=200)
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


@swagger_auto_schema(method='POST', operation_summary="Выход из аккаунта.",
                     responses=logout_responses)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh = request.data.get('refresh')
        if not refresh:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Отсутствует refresh токен.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=400)
        token = RefreshToken(refresh)
        token.blacklist()
        return HttpResponse(
            json.dumps({'state': 'success', 'message': f'Успешный выход.', 'details': {},
                        'instance': request.path},
                       ensure_ascii=False), status=200)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET',
                     operation_summary="Список последних входов всех пользователей.",
                     responses=get_all_logons_responses)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_logons(request):
    try:
        logons = History.objects.all().order_by('-datetime')
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
@permission_classes([IsAdmin])
def get_groups(request):
    try:
        class_ = get_variable("class", request)
        if class_ not in ['4', '5', '6', 4, 5, 6]:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс учеников.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        groups_users = GroupUser.objects.filter(group__school_class=class_).select_related('group', 'user')
        groups_dict = {}
        for row in groups_users:
            if row.group_id not in groups_dict:
                groups_dict[row.group_id] = {
                    'id': row.group.id,
                    'name': row.group.name,
                    'marker': row.group.marker,
                    'students_ids': [],
                    'students': []
                }
            if row.user_id not in groups_dict[row.group_id]['students_ids']:
                groups_dict[row.group_id]['students_ids'].append(row.user_id)
                groups_dict[row.group_id]['students'].append({
                    'id': row.user.id,
                    'name': row.user.name
                })
        for group in groups_dict:
            del groups_dict[group]['students_ids']
        return HttpResponse(json.dumps({'groups': groups_dict}, ensure_ascii=False), status=200)
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
@permission_classes([IsAdmin])
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
        log = Log(operation='INSERT', from_table='groups', details='Добавлена новая группа в таблицу groups.')
        log.save()
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
@permission_classes([IsTierTwo])
def delete_group(request):
    try:
        id_ = get_variable("group", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id группы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        group = Group.objects.get(id=id_)
        log_details = f'Удалена группа из таблицы groups. ["id": {group.id} | "name": "{group.name}" | "marker": "{group.marker}" | "school_class": "{group.school_class}"]'
        group.delete()
        log = Log(operation='DELETE', from_table='groups', details=log_details)
        log.save()
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


@swagger_auto_schema(method='PATCH', operation_summary="Добавление ученика в группу.",
                     manual_parameters=[group_param, user_param],
                     responses=add_to_group_responses)
@api_view(["PATCH"])
@permission_classes([IsAdmin])
def add_to_group(request):
    try:
        id_ = get_variable("group", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id группы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        student_id = get_variable("student", request)
        if (student_id is None) or (student_id == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        student = User.objects.get(id=student_id)
        group = Group.objects.get(id=id_)
        current_group = GroupUser.objects.filter(user=student)
        if current_group:
            current_group[0].delete()
        new_group = GroupUser(user=student, group=group)
        new_group.save()
        student.group = group
        student.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
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


@swagger_auto_schema(method='PATCH', operation_summary="Удаление ученика из группы.",
                     manual_parameters=[user_param],
                     responses=delete_from_group_responses)
@api_view(["PATCH"])
@permission_classes([IsAdmin])
def delete_from_group(request):
    try:
        student_id = get_variable("student", request)
        if (student_id is None) or (student_id == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        student = User.objects.get(id=student_id)
        current_group = GroupUser.objects.filter(user=student)
        if current_group:
            current_group[0].delete()
        student.group = None
        student.save()
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
