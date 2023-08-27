from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from kpm.apps.logs.models import Log
from kpm.apps.homeworks.models import *
import json
from django.db.models import Sum, Q, Count
from kpm.apps.users.permissions import IsAdmin
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.homeworks.docs import *
from kpm.apps.homeworks.functions import *
from django.utils import timezone


#@swagger_auto_schema(method='POST', operation_summary="Создание работы.",
#                     request_body=create_work_request_body,
#                     responses=create_work_responses,
#                     operation_description=operation_description)
@api_view(["POST"])
@permission_classes([IsAdmin])
def create_homework(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        author = User.objects.get(id=request.user.id)

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


#@swagger_auto_schema(method='DELETE', operation_summary="Удаление работы.",
#                     manual_parameters=[id_param],
#                     responses=delete_work_responses,
#                     operation_description=operation_description)
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_homework(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        homework = Homework.objects.get(id=id_)
        homework.delete()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Работа не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)
