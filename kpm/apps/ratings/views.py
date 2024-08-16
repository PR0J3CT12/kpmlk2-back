from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from kpm.apps.users.permissions import *
from kpm.apps.users.functions import is_trusted
from .functions import *
from kpm.apps.ratings.models import *
from kpm.apps.users.models import User
import json
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.ratings.docs import *
from django.db.models import Count
from django.conf import settings
from django.db import IntegrityError
from kpm.apps.users.docs import permissions_operation_description


LOGGER = settings.LOGGER


@swagger_auto_schema(method='GET', operation_summary="Получение рейтингов.",
                     manual_parameters=[class_param],
                     responses=get_ratings_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']}")
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_ratings(request):
    try:
        class_ = get_variable("class", request)
        if class_ not in ['4', '5', '6', '7']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс учеников.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        ratings = League.objects.filter(school_class=class_).values('id', 'name', 'description', 'rating_type')
        ratings_dict = {}
        rating_ids = []
        for rating in ratings:
            if rating['id'] not in rating_ids:
                rating_ids.append(rating['id'])
            ratings_dict[rating['id']] = {
                'id': rating['id'],
                'name': rating['name'],
                'description': rating['description'],
                'type': rating['rating_type'],
                'students': 0
            }
        users_per_league = LeagueUser.objects.filter(league__id__in=rating_ids).values('league').annotate(
            user_count=Count('user'))
        for item in users_per_league:
            ratings_dict[item['league']]['students'] = item['user_count']
        ratings_list = list(ratings_dict.values())
        return HttpResponse(json.dumps({'ratings': ratings_list}, ensure_ascii=False), status=200)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получение рейтинга.",
                     manual_parameters=[id_param],
                     responses=get_rating_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAuthenticated']}")
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEnabled])
def get_rating(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id рейтинга.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        user = User.objects.get(id=request.user.id)
        rating = League.objects.get(id=id_)
        if user.is_admin:
            rating_students = LeagueUser.objects.filter(league=rating).select_related('user')
        else:
            rating_students = LeagueUser.objects.filter(league=rating, user=user).select_related('user')
            if not rating_students:
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Отказано в доступе.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=403)
        students_list = []
        if rating.rating_type == 0:
            rating_students = rating_students.order_by('-user__experience').values(
                'user_id', 'user__name', 'user__experience'
            )
            for student in rating_students:
                total_exp = student['user__experience']
                lvl, exp, base_exp = count_lvl(total_exp)
                students_list.append({
                    'id': student['user_id'],
                    'name': student['user__name'],
                    'lvl': lvl,
                    'exp': exp,
                    'base_exp': base_exp,
                    'total_exp': total_exp
                })
        elif rating.rating_type == 1:
            rating_students = rating_students.order_by('-user__exam_experience').values(
                'user_id', 'user__name', 'user__exam_experience'
            )
            for student in rating_students:
                total_exp = student['user__exam_experience']
                lvl, exp, base_exp = count_lvl(total_exp)
                students_list.append({
                    'id': student['userid'],
                    'name': student['user__name'],
                    'lvl': lvl,
                    'exp': exp,
                    'base_exp': base_exp,
                    'total_exp': total_exp
                })
        elif rating.rating_type == 2:
            rating_students = rating_students.order_by('-user__oral_exam_experience').values(
                'user_id', 'user__name', 'user__oral_exam_experience'
            )
            for student in rating_students:
                total_exp = student['user__oral_exam_experience']
                lvl, exp, base_exp = count_lvl(total_exp)
                students_list.append({
                    'id': student['user_id'],
                    'name': student['user__name'],
                    'lvl': lvl,
                    'exp': exp,
                    'base_exp': base_exp,
                    'total_exp': total_exp
                })
        return HttpResponse(json.dumps({
            'id': rating.id,
            'name': rating.name,
            'description': rating.description,
            'type': rating.rating_type,
            'students': students_list
        }, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Рейтинг не существует.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='POST', operation_summary="Создание рейтинга.",
                     request_body=create_rating_request_body,
                     responses=create_rating_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierTwo']}")
@api_view(["POST"])
@permission_classes([IsTierTwo, IsEnabled])
def create_rating(request):
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
        if request_body["type"] not in [0, 1, 2]:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан тип рейтинга.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        if 'description' in request_body:
            description = request_body['description']
        else:
            description = None
        league = League(name=request_body['name'], school_class=int(request_body['class']),
                        rating_type=int(request_body['type']), description=description)
        league.save()

        if "students" in request_body:
            if request_body["students"]:
                for student in request_body["students"]:
                    try:
                        league_user = LeagueUser.objects.create(league=league, user_id=student)
                    except IntegrityError:
                        pass
        LOGGER.info(f'Created rating {league.id} by user {request.user.id}.')
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


@swagger_auto_schema(method='PATCH', operation_summary="Изменение рейтинга.",
                     request_body=update_rating_request_body,
                     responses=update_rating_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierTwo']}")
@api_view(["PATCH"])
@permission_classes([IsTierTwo, IsEnabled])
def update_rating(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        id_ = request_body['id']
        league = League.objects.get(id=id_)
        if 'name' in request_body:
            league.name = request_body['name']
        if 'description' in request_body:
            league.description = request_body['description']
        if "students" in request_body:
            current_students = LeagueUser.objects.filter(league=league)
            current_students.delete()
            users = User.objects.filter(id__in=request_body["students"])
            for student in users:
                league_user = LeagueUser.objects.create(league=league, user=student)
                LOGGER.info(f'Added student {student} to rating {id_} by user {request.user.id}.')
        league.save()
        LOGGER.info(f'Updated rating {id_} by user {request.user.id}.')
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Рейтинг не существует.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='DELETE', operation_summary="Удаление рейтинга.",
                     manual_parameters=[id_param],
                     responses=delete_rating_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierTwo']}")
@api_view(["DELETE"])
@permission_classes([IsTierTwo, IsEnabled])
def delete_rating(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id рейтинга.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        league = League.objects.get(id=id_)
        league.delete()
        LOGGER.warning(f'Deleted rating {id_} by user {request.user.id}.')
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Рейтинг не существует.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='PATCH', operation_summary="Добавление учеников в рейтинг.",
                     manual_parameters=[id_param],
                     request_body=add_to_rating_request_body,
                     responses=add_to_rating_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierTwo']}")
@api_view(["PATCH"])
@permission_classes([IsTierTwo, IsEnabled])
def add_to_rating(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        id_ = request_body['id']
        students_ids = request_body['students']
        students = User.objects.filter(id__in=students_ids).values('id', 'school_class')
        league = League.objects.get(id=id_)
        for student in students:
            try:
                if student['school_class'] == league.school_class:
                    league_user = LeagueUser.objects.create(league=league, user_id=student['id'])
            except IntegrityError:
                pass
            LOGGER.info(f'Added student {student} to rating {id_} by user {request.user.id}.')
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Рейтинг или пользователь не существует.', 'details': {},
                        'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='PATCH', operation_summary="Удаление учеников из рейтинга.",
                     request_body=delete_from_rating_request_body,
                     responses=delete_from_rating_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierTwo']}")
@api_view(["PATCH"])
@permission_classes([IsTierTwo, IsEnabled])
def delete_from_rating(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        id_ = request_body['id']
        students = request_body['students']
        league = League.objects.get(id=id_)
        new_leagues = LeagueUser.objects.filter(league=league, user_id__in=students)
        for student in new_leagues:
            student.delete()
            LOGGER.info(f'Deleted student {student.user_id} to rating {id_} by user {request.user.id}.')
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


@swagger_auto_schema(method='GET', operation_summary="Получение рейтингов ученика.",
                     manual_parameters=[user_param],
                     responses=get_user_ratings_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAuthenticated']}")
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEnabled])
def get_user_ratings(request):
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
        leagues = LeagueUser.objects.filter(user_id=student_id).select_related('league').values(
            'league_id', 'league__name', 'league__description', 'league__rating_type'
        )
        ratings = []
        for league in leagues:
            ratings.append({
                'id': league['league_id'],
                'name': league['league__name'],
                'description': league['league__description'],
                'type': league['league__rating_type']
            })
        return HttpResponse(json.dumps({'ratings': ratings}, ensure_ascii=False), status=200)
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
