from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from kpm.apps.users.permissions import IsAdmin
from kpm.apps.users.functions import is_trusted
from .functions import get_variable
from kpm.apps.logs.models import Log
from kpm.apps.users.models import User
from kpm.apps.messages.models import Message
import json
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.messages.docs import *


@swagger_auto_schema(method='POST', operation_summary="Отправить сообщение.",
                     request_body=send_message_request_body,
                     responses=send_message_responses)
@api_view(["POST"])
@permission_classes([IsAdmin])
def send_message(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        receivers_ids = request_body['users_to']
        receivers = User.objects.filter(id__in=receivers_ids)
        sender = User.objects.get(id=request.user.id)
        text = request_body['text']
        for receiver in receivers:
            message = Message(user_to=receiver, user_from=sender, text=text)
            message.save()
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


@swagger_auto_schema(method='GET', operation_summary="Прочитать сообщение.",
                     manual_parameters=[id_param],
                     responses=read_message_responses)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def read_message(request):
    try:
        id_ = get_variable('id', request)
        message = Message.objects.get(id=id_)
        if message.user_to != request.user.id:
            return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=401)
        message.is_viewed = True
        message.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Сообщение не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получить сообщение.",
                     manual_parameters=[id_param],
                     responses=get_message_responses)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_message(request):
    try:
        id_ = get_variable('id', request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id сообщения.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        message = Message.objects.get(id=id_)
        if not is_trusted(request, message.user_to):
            return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=401)
        return HttpResponse(json.dumps({
            'id': message.id,
            'user_to': message.user_to,
            'user_from': message.user_from,
            'text': message.text,
            'is_viewed': message.is_viewed,
            'datetime': str(message.datetime)
        }, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Сообщение не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получить сообщения.",
                     manual_parameters=[id_user_param],
                     responses=get_messages_responses)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_messages(request):
    try:
        id_ = get_variable('id', request)
        messages = Message.objects.filter(user_to=id_)
        if not is_trusted(request, id_):
            return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=401)
        messages_list = []
        if not messages:
            return HttpResponse(json.dumps({'messages': messages_list}, ensure_ascii=False), status=200)
        for message in messages:
            messages_list.append(
                {
                    'id': message.id,
                    'user_to': message.user_to,
                    'user_from': message.user_from,
                    'text': message.text,
                    'is_viewed': message.is_viewed,
                    'datetime': str(message.datetime)
                }
            )
        return HttpResponse(json.dumps({'messages': messages_list}, ensure_ascii=False), status=200)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='DELETE', operation_summary="Удалить сообщение.",
                     manual_parameters=[id_param],
                     responses=delete_message_responses)
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_message(request):
    try:
        id_ = get_variable('id', request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id сообщения.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        message = Message.objects.get(id=id_)
        message.delete()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Сообщение не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


