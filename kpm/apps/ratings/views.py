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


@swagger_auto_schema(method='GET', operation_summary="Получение рейтингов.",
                     manual_parameters=[class_param],
                     responses=get_ratings_responses)
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_ratings(request):
    try:
        class_ = get_variable("class", request)
        if class_ not in ['4', '5', '6', 4, 5, 6]:
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
        users_per_league = LeagueUser.objects.filter(league__id__in=rating_ids).values('league').annotate(user_count=Count('user'))
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
                     responses=get_rating_responses)
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_rating(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id рейтинга.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        rating = League.objects.get(id=id_)
        rating_students = LeagueUser.objects.filter(league=rating).select_related('user')
        students_list = []
        if rating.rating_type == 0:
            rating_students = rating_students.order_by('-user__experience')
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
        elif rating.rating_type == 1:
            rating_students = rating_students.order_by('-user__exam_experience')
            for student in rating_students:
                total_exp = student.user.exam_experience
                lvl, exp, base_exp = count_lvl(total_exp)
                students_list.append({
                    'id': student.user.id,
                    'name': student.user.name,
                    'lvl': lvl,
                    'exp': exp,
                    'base_exp': base_exp,
                    'total_exp': total_exp
                })
        elif rating.rating_type == 2:
            rating_students = rating_students.order_by('-user__oral_exam_experience')
            for student in rating_students:
                total_exp = student.user.oral_exam_experience
                lvl, exp, base_exp = count_lvl(total_exp)
                students_list.append({
                    'id': student.user.id,
                    'name': student.user.name,
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
                     responses=create_rating_responses)
@api_view(["POST"])
@permission_classes([IsAdmin, IsEnabled])
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
        if request_body["type"] not in ['0', '1', '2', 0, 1, 2]:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан тип рейтинга.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        if 'description' in request_body:
            description = request_body['description']
        else:
            description = None
        league = League(name=request_body['name'], school_class=int(request_body['class']), rating_type=int(request_body['type']), description=description)
        league.save()
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


@swagger_auto_schema(method='DELETE', operation_summary="Удаление рейтинга.",
                     manual_parameters=[id_param],
                     responses=delete_rating_responses)
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
@permission_classes([IsAdmin, IsEnabled])
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
@permission_classes([IsAdmin, IsEnabled])
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


@swagger_auto_schema(method='GET', operation_summary="Получение рейтингов ученика.",
                     manual_parameters=[user_param],
                     responses=get_user_ratings_responses)
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
        leagues = LeagueUser.objects.filter(user_id=student_id).select_related('league')
        ratings = []
        for league in leagues:
            ratings.append({
                'id': league.league.id,
                'name': league.league.name,
                'description': league.league.description,
                'type': league.league.rating_type
            })
        return HttpResponse(json.dumps({'ratings': ratings}, ensure_ascii=False), status=200)
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
                     manual_parameters=[user_param, id_param],
                     responses=get_user_rating_responses)
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEnabled])
def get_user_rating(request):
    try:
        student_id = get_variable("student", request)
        if (student_id is None) or (student_id == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id рейтинга.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        if not is_trusted(request, student_id):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        student = User.objects.get(id=student_id)
        league = LeagueUser.objects.get(league__id=id_, user=student)
        students_in_league = LeagueUser.objects.filter(league__id=id_)
        current_type = league.league.rating_type
        if current_type == 0:
            students_in_league = students_in_league.order_by('-user__experience')
        elif current_type == 1:
            students_in_league = students_in_league.order_by('-user__exam_experience')
        elif current_type == 2:
            students_in_league = students_in_league.order_by('-user__oral_exam_experience')
        rating = []
        for student_ in students_in_league:
            if current_type == 0:
                total_exp = student_.user.experience
            elif current_type == 1:
                total_exp = student_.user.exam_experience
            elif current_type == 2:
                total_exp = student_.user.oral_exam_experience
            else:
                total_exp = 0
            lvl, exp, base_exp = count_lvl(total_exp)
            rating.append({
                'id': student_.user.id,
                'name': student_.user.name,
                'lvl': lvl,
                'exp': exp,
                'base_exp': base_exp,
                'total_exp': total_exp
            })
        return HttpResponse(json.dumps({
            'id': id_,
            'name': league.league.name,
            'description': league.league.description,
            'rating_type': current_type,
            'students': rating
        }, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Пользователь или рейтинг не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)