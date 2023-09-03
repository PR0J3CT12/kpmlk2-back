from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from kpm.apps.users.models import User, History
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
        return HttpResponse(
            json.dumps({
                "id": student.id,
                "name": student.name,
                "login": student.login,
                "default_password": student.default_password,
                "class": student.school_class,
                "is_default": student.is_default,
                "experience": student.experience,
                "mana_earned": student.mana_earned,
                "last_homework_id": student.last_homework_id,
                "last_classwork_id": student.last_classwork_id}, ensure_ascii=False),
            status=200)
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
        students = User.objects.filter(Q(is_admin=0) & Q(school_class=int(class_))).order_by('name')
        students_list = []
        if not students:
            return HttpResponse(
                json.dumps({'students': students_list}, ensure_ascii=False), status=200)
        for student in students:
            if not student.default_password:
                default_password = ""
            else:
                default_password = student.default_password
            student_info = {"id": student.id,
                            "name": student.name,
                            "login": student.login,
                            "default_password": default_password,
                            "experience": student.experience,
                            "mana_earned": student.mana_earned,
                            "last_homework_id": student.last_homework_id,
                            "last_classwork_id": student.last_classwork_id}
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
@permission_classes([IsAdmin])
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
            json.dumps({'state': 'error', 'message': f'Пользователь не существует.', 'details': {}, 'instance': request.path},
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
@permission_classes([IsAdmin])
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
                json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
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
            json.dumps({'state': 'error', 'message': f'Пользователь не существует.', 'details': {}, 'instance': request.path},
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
        logons = History.objects.all()
        logons_list = []
        for logon in logons:
            logons_list.append({
                'user_id': logon.user.id,
                'user_name': logon.user.name,
                'date': logon.datetime.date(),
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