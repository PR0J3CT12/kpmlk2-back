from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from kpm.apps.users.permissions import IsAdmin
from kpm.apps.users.functions import is_trusted
from .functions import *
from kpm.apps.ratings.models import *
from kpm.apps.logs.models import Log
from kpm.apps.users.models import User
import json
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.ratings.docs import *


@swagger_auto_schema(method='GET', operation_summary="Получение рейтингов.",
                     manual_parameters=[class_param],
                     responses=get_ratings_responses)
@api_view(["GET"])
@permission_classes([IsAdmin])
def get_ratings(request):
    try:
        class_ = get_variable("class", request)
        if class_ not in ['4', '5', '6', 4, 5, 6]:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс учеников.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        ratings = League.objects.all()
        ratings_list = []
        for rating in ratings:
            rating_students = LeagueUser.objects.filter(league=rating).order_by('-user__experience')
            students_list = []
            for student in rating_students:
                total_exp = student.user.experience
                lvl, exp, base_exp = count_lvl(total_exp)
                students_list.append({
                    'id': student.user.id,
                    'name': student.user.name,
                    'lvl': lvl,
                    'exp': exp,
                    'base_exp': base_exp,
                    'total_exp': total_exp
                })
            ratings_list.append({
                'id': rating.id,
                'name': rating.name,
                'students': students_list
            })
        return HttpResponse(json.dumps({'ratings': ratings_list}, ensure_ascii=False), status=200)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='POST', operation_summary="Создание рейтинга.",
                     request_body=create_rating_request_body,
                     responses=create_rating_responses)
@api_view(["POST"])
@permission_classes([IsAdmin])
def create_rating(request):
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
        league = League(name=request_body['name'], school_class=int(request_body['class']))
        league.save()
        log = Log(operation='INSERT', from_table='ratings', details='Добавлена новый рейтинг в таблицу ratings.')
        log.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='POST', operation_summary="Создание рейтинга.",
                     manual_parameters=[id_param],
                     responses=delete_rating_responses)
@api_view(["POST"])
@permission_classes([IsAdmin])
def delete_rating(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id рейтинга.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        league = League.objects.get(id=id_)
        log_details = f'Удален рейтинг из таблицы ratings. ["id": {league.id} | "name": "{league.name}"]'
        league.delete()
        log = Log(operation='DELETE', from_table='ratings', details=log_details)
        log.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Рейтинг не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='PATCH', operation_summary="Добавление ученика в рейтинг.",
                     manual_parameters=[id_param, user_param],
                     responses=add_to_rating_responses)
@api_view(["PATCH"])
@permission_classes([IsAdmin])
def add_to_rating(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id рейтинга.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        student_id = get_variable("student", request)
        if (student_id is None) or (student_id == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        student = User.objects.get(id=student_id)
        league = League.objects.get(id=id_)
        current_league = LeagueUser.objects.filter(user=student)
        if current_league:
            current_league[0].delete()
        new_league = LeagueUser(user=student, league=league)
        new_league.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Рейтинг или пользователь не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='PATCH', operation_summary="Удаление ученика из рейтинга.",
                     manual_parameters=[user_param],
                     responses=delete_from_rating_responses)
@api_view(["PATCH"])
@permission_classes([IsAdmin])
def delete_from_rating(request):
    try:
        student_id = get_variable("student", request)
        if (student_id is None) or (student_id == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        student = User.objects.get(id=student_id)
        current_league = LeagueUser.objects.filter(user=student)
        if current_league:
            current_league[0].delete()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Пользователь не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получение рейтинга ученика.",
                     manual_parameters=[user_param],
                     responses=get_user_rating_responses)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_rating(request):
    try:
        student_id = get_variable("student", request)
        if (student_id is None) or (student_id == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        if not is_trusted(request, student_id):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        student = User.objects.get(id=student_id)
        league_ = LeagueUser.objects.filter(user=student)
        if not league_:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Пользователь не состоит в рейтинге.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=404)
        league = league_[0].league
        students_in_league = LeagueUser.objects.filter(league=league).order_by('-user__experience')
        rating = []
        for student_ in students_in_league:
            total_exp = student_.user.experience
            lvl, exp, base_exp = count_lvl(total_exp)
            rating.append({
                'name': student_.user.name,
                'lvl': lvl,
                'exp': exp,
                'base_exp': base_exp,
                'total_exp': total_exp
            })
        return HttpResponse(json.dumps({'rating': rating}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Пользователь не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)