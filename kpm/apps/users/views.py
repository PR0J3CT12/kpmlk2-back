from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .customfunctions import get_variable, login_password_creator
from kpm.apps.users.models import User
from kpm.apps.logs.models import Log
from kpm.apps.works.models import Work
from kpm.apps.grades.models import Grade
import json
from django.db.models import Sum, Q, Count
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from kpm.apps.users.permissions import IsAdmin


SECRET_KEY = settings.SECRET_KEY


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user(request):
    id_ = get_variable("id", request)
    if not id_:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано id ученика.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    try:
        # ПЕРЕДЕЛАТЬ
        logged_user = User.objects.get(id=request.user.id)
        if not (logged_user.is_admin == 1 or logged_user.id == id_):
            return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=403)
        student = User.objects.get(id=id_)
        student_info = {"id": student.id, "name": student.name, "login": student.login, "password": student.password,
                        "experience": student.experience, "mana_earned": student.mana_earned,
                        "last_homework_id": student.last_homework_id, "last_classwork_id": student.last_classwork_id}
        return HttpResponse(
            json.dumps({'state': 'success', 'message': '', 'details': {'student': student_info}}, ensure_ascii=False),
            status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


@api_view(["GET"])
@permission_classes([IsAdmin])
def get_users(request):
    class_ = get_variable("class", request)
    if not class_:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Не указан класс ученика.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    else:
        if class_ not in ['4', '5', '6']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
    try:
        students = User.objects.filter(Q(is_admin=0) & Q(school_class=int(class_)))
        students_list = []
        for student in students:
            student_info = {"id": student.id, "name": student.name, "login": student.login, "default_password": student.default_password,
                            "experience": student.experience, "mana_earned": student.mana_earned,
                            "last_homework_id": student.last_homework_id, "last_classwork_id": student.last_classwork_id}
            if not student_info["default_password"]:
                student_info["default_password"] = ""
            students_list.append(student_info)
        return HttpResponse(
            json.dumps({'state': 'success', 'message': 'Все ученики получены.', 'details': {'students': students_list}}, ensure_ascii=False),
            status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


# todo: обработка ошибок
@api_view(["POST"])
@permission_classes([IsAdmin])
def create_user(request):
    if request.body:
        request_body = json.loads(request.body)
    else:
        return HttpResponse(json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path}, ensure_ascii=False), status=400)
    try:
        students = User.objects.all()
        if students:
            last_student = students.latest("id")
            last_id = last_student.id
        else:
            last_id = 0
        id_, login_, password_ = login_password_creator(request_body["name"], last_id + 1)
        student = User(id=last_id + 1, name=request_body["name"], login=login_, default_password=password_, school_class=request_body["class"], is_superuser=False)
        student.save()
        log = Log(operation='INSERT', from_table='users', details='Добавлен новый ученик в таблицу users.')
        log.save()
        works = Work.objects.all()
        for work in works:
            grades = work.grades.split('_._')
            empty_grades = '_._'.join(list('#'*len(grades)))
            grade = Grade(user_id=student.id, work_id=work.id, grades=empty_grades, max_score=0, score=0, exercises=0)
            grade.save()
        return HttpResponse(
            json.dumps({'state': 'success', 'message': 'Ученик успешно добавлен.', 'details': {}}, ensure_ascii=False),
            status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


# todo: обработка ошибок
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_user(request):
    id_ = get_variable("id", request)
    if not id_:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    try:
        student = User.objects.get(id=id_)
        log_details = f'Удален ученик из таблицы users. ["id": {student.id} | "name": "{student.name}" | "login": {student.login} | "password": {student.password} | "experience": {student.experience} | "mana_earned": {student.mana_earned} | "last_homework_id": {student.last_homework_id} | "last_classwork_id": {student.last_classwork_id} | "school_class": {student.school_class}]'
        student.delete()
        log = Log(operation='DELETE', from_table='users', details=log_details)
        log.save()
        return HttpResponse(
            json.dumps({'state': 'success', 'message': 'Ученик успешно удален.', 'details': {}}, ensure_ascii=False),
            status=205)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)


# todo: обработка ошибок
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_users(request):
    class_ = get_variable("class", request)
    if not class_:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Не указан класс ученика.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    else:
        if class_ not in ['4', '5', '6']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
    try:
        students = User.objects.filter(school_class=int(class_))
        for student in students:
            Log(operation='DELETE', from_table='users',
                details=f'Удален ученик из таблицы users. ["id": {student.id} | "name": "{student.name}" | "login": {student.login} | "password": {student.password} | "experience": {student.experience} | "mana_earned": {student.mana_earned} | "last_homework_id": {student.last_homework_id} | "last_classwork_id": {student.last_classwork_id} | "school_class": {student.school_class}]').save()
        students.delete()
        return HttpResponse(
            json.dumps({'state': 'success', 'message': 'Все ученики успешно удалены.', 'details': {}},
                       ensure_ascii=False),
            status=205)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps({'state': 'error', 'message': f'{e}', 'details': {}, 'instance': request.path},
                                       ensure_ascii=False), status=404)