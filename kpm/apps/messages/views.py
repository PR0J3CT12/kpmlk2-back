import datetime
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from kpm.apps.users.permissions import IsAdmin, IsEnabled, IsTierOne
from kpm.apps.users.functions import is_trusted
from .functions import get_variable
from kpm.apps.users.models import User
from kpm.apps.messages.models import Message, MessageGroup, MessageGroupFile
import json
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.messages.docs import *
from django.conf import settings
from django.utils import timezone
from django.core.files import File
from kpm.apps.users.docs import permissions_operation_description
import requests
import os
from kpm.apps.works.functions import heif_to_jpeg


LOGGER = settings.LOGGER
CHAT_ID = settings.TG_SUPPORT_CHAT
BOT_TOKEN = settings.TG_BOT_TOKEN


@swagger_auto_schema(method='POST', operation_summary="Отправить сообщение.",
                     request_body=send_message_request_body,
                     responses=send_message_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAuthenticated']}")
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsEnabled])
def send_message(request):
    try:
        if request.POST or request.FILES:
            data = request.POST
            files = request.FILES
        else:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=400)
        receivers_ids = data.getlist('users_to')
        receivers = User.objects.filter(id__in=receivers_ids)
        sender = User.objects.get(id=request.user.id)
        text = data['text']
        title = data['title']
        files = files.getlist('files')
        for file in files:
            if 'image' in str(file.content_type):
                pass
            elif file.content_type in ['application/pdf', 'application/octet-stream']:
                pass
            else:
                return HttpResponse(
                    json.dumps({'state': 'error', 'message': 'Недопустимый файл.', 'details': {},
                                'instance': request.path},
                               ensure_ascii=False), status=404)
        messages_group = MessageGroup()
        messages_group.save()
        for receiver in receivers:
            message = Message(user_to=receiver, user_from=sender, text=text, group=messages_group, title=title)
            message.save()
        for file in files:
            temp_path = f'/tmp/{file.name}'
            ext = file.name.split('.')[-1]
            new_path = None
            with open(temp_path, 'wb+') as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)
            if file.name.lower().endswith('.heif') or file.name.lower().endswith('.heic'):
                new_path = heif_to_jpeg(temp_path)
                if new_path:
                    with open(new_path, 'rb') as jpeg_file:
                        django_file = File(jpeg_file, name=os.path.basename(new_path))
                        message_file = MessageGroupFile(message_group=messages_group, file=django_file, ext=ext)
                        message_file.save()
                else:
                    continue
            else:
                message_file = MessageGroupFile(message_group=messages_group, file=file, ext=ext)
                message_file.save()
            os.remove(temp_path)
            if new_path:
                os.remove(new_path)
        LOGGER.info(f'Send message {messages_group.id} (msg_group) by user {request.user.id}.')
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


@swagger_auto_schema(method='POST', operation_summary="Прочитать сообщение.",
                     manual_parameters=[id_param],
                     responses=read_message_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAuthenticated']}")
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsEnabled])
def read_message(request):
    try:
        id_ = get_variable('id', request)
        message = Message.objects.get(id=id_)
        if message.user_to.id != request.user.id:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=401)
        message.is_viewed = True
        message.viewed_at = timezone.now()
        message.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Сообщение не существует.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получить сообщение.",
                     manual_parameters=[id_param],
                     responses=get_message_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAuthenticated']}")
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEnabled])
def get_message(request):
    try:
        id_ = get_variable('id', request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id сообщения.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        message = Message.objects.get(id=id_)
        if not is_trusted(request, message.user_to_id):
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=401)
        message_group = message.group
        host = settings.MEDIA_HOST_PATH
        files = MessageGroupFile.objects.filter(message_group=message_group).values('file', 'ext')
        files_list = []
        for file in files:
            link = f"{host}/{file['file']}"
            name = file['file'].split('/')[-1]
            ext = file['ext']
            files_list.append({'link': link, 'name': name, 'ext': ext})
        return HttpResponse(json.dumps({
            'id': message.id,
            'user_to': message.user_to.id,
            'user_to_name': message.user_to.name,
            'user_from': message.user_from.id,
            'user_from_name': message.user_from.name,
            'title': message.title,
            'text': message.text,
            'is_viewed': message.is_viewed,
            'viewed_at': str(message.viewed_at),
            'datetime': str(message.group.datetime),
            'files': files_list
        }, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Сообщение не существует.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получить сообщения.",
                     manual_parameters=[id_user_param],
                     responses=get_messages_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAuthenticated']}")
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEnabled])
def get_messages(request):
    try:
        id_ = get_variable('id', request)
        if not is_trusted(request, id_):
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=401)
        messages = Message.objects.filter(user_to=id_).select_related('user_to', 'user_from', 'group').values(
            'id', 'user_to__id', 'user_to__name', 'user_from__id', 'user_from__name', 'title', 'text', 'is_viewed',
            'viewed_at', 'group__datetime', 'group_id').order_by('-group__datetime')
        groups = []
        messages_list = []
        if not messages:
            return HttpResponse(json.dumps({'messages': messages_list}, ensure_ascii=False), status=200)
        host = settings.MEDIA_HOST_PATH
        messages_dict = {}
        for message in messages:
            if message['group_id'] not in groups:
                groups.append(message['group_id'])
            messages_dict[message['group_id']] = {
                'id': message['id'],
                'user_to': message['user_to__id'],
                'user_to_name': message['user_to__name'],
                'user_from': message['user_from__id'],
                'user_from_name': message['user_from__name'],
                'title': message['title'],
                'text': message['text'],
                'is_viewed': message['is_viewed'],
                'viewed_at': str(message['viewed_at']),
                'datetime': str(message['group__datetime']),
                'files': []
            }
        msg_files = MessageGroupFile.objects.filter(message_group__in=groups).values('message_group_id', 'file', 'ext')
        for file in msg_files:
            messages_dict[file['message_group_id']]['files'].append({
                'link': f'{host}/{file["file"]}',
                'name': file['file'].split('/')[-1],
                'ext': file['ext'],
            })
        return HttpResponse(json.dumps({'messages': list(messages_dict.values())}, ensure_ascii=False), status=200)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получить отправленные сообщения.",
                     responses=get_sent_messages_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAuthenticated']}")
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEnabled])
def get_sent_messages(request):
    try:
        id_ = request.user.id
        messages = Message.objects.filter(user_from=id_).order_by('user_to__name', '-group__datetime').values(
            'id', 'group_id', 'user_from_id', 'user_from__name', 'title', 'text', 'group__datetime',
            'user_to_id', 'user_to__name', 'is_viewed', 'viewed_at'
        )
        if not is_trusted(request, id_):
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=401)
        if not messages:
            return HttpResponse(json.dumps({'messages': []}, ensure_ascii=False), status=200)
        messages_dict = {}
        messages_groups = []
        for message in messages:
            if message['group_id'] not in messages_groups:
                messages_groups.append(message['group_id'])
            if message['group_id'] not in messages_dict:
                messages_dict[message['group_id']] = {
                    'id': message['id'],
                    'user_from': message['user_from_id'],
                    'user_from_name': message['user_from__name'],
                    'title': message['title'],
                    'text': message['text'],
                    'datetime': str(message['group__datetime']),
                    'recipients': [],
                    'files': []
                }
            messages_dict[message['group_id']]['recipients'].append(
                {
                    'user_to': message['user_to_id'],
                    'user_to_name': message['user_to__name'],
                    'is_viewed': message['is_viewed'],
                    'viewed_at': str(message['viewed_at']),
                }
            )
        files = MessageGroupFile.objects.filter(message_group__in=messages_groups).values(
            'file',
            'ext',
            'message_group_id')
        host = settings.MEDIA_HOST_PATH
        files_dict = {}
        for file in files:
            link = f"{host}/{file['file']}"
            name = file['file'].split('/')[-1]
            ext = file['ext']
            if file['message_group_id'] not in files_dict:
                files_dict[file['message_group_id']] = []
            files_dict[file['message_group_id']].append({'link': link, 'name': name, 'ext': ext})
        for group in messages_groups:
            if group in files_dict:
                messages_dict[group]['files'] = files_dict[group]
        messages_list = list(messages_dict.values())
        return HttpResponse(json.dumps({'messages': messages_list}, ensure_ascii=False), status=200)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='DELETE', operation_summary="Удалить сообщение.",
                     manual_parameters=[id_param],
                     responses=delete_message_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierOne']}")
@api_view(["DELETE"])
@permission_classes([IsTierOne, IsEnabled])
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
        LOGGER.warning(f'Deleted message {id_} by user {request.user.id}.')
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Сообщение не существует.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='POST', operation_summary="Отправить сообщение в поддержку.",
                     request_body=support_request_body,
                     responses=support_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAuthenticated']}")
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsEnabled])
def support(request):
    try:
        if request.POST or request.FILES:
            data = request.POST
            files = request.FILES
        else:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=400)
        sender = User.objects.get(id=request.user.id)
        text = data['text']
        files = files.getlist('files')
        for file in files:
            if 'image' in str(file.content_type):
                pass
            elif file.content_type in ['application/pdf']:
                pass
            else:
                return HttpResponse(
                    json.dumps({'state': 'error', 'message': 'Недопустимый файл.', 'details': {},
                                'instance': request.path},
                               ensure_ascii=False), status=400)
        msg = f'*Имя пользователя*: {sender.name}\n' \
              f'*Логин пользователя*: {sender.login}\n' \
              f'*Сообщение*: {text}\n' \
              f'*Дата и время*: {datetime.datetime.now().strftime("%H:%M %d.%m.%Y")}\n'
        res = requests.post(
            url=f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?parse_mode=Markdown&disable_web_page_preview=True',
            data={'chat_id': CHAT_ID, 'text': msg}
        ).json()
        if res['ok']:
            for file in files:
                if 'image' in str(file.content_type):
                    res_f = requests.post(
                        url=f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto?chat_id={CHAT_ID}&parse_mode=Markdown&disable_web_page_preview=True',
                        files={'photo': file}
                    )
                elif file.content_type in ['application/pdf']:
                    res_f = requests.post(
                        url=f'https://api.telegram.org/bot{BOT_TOKEN}/sendDocument?chat_id={CHAT_ID}&parse_mode=Markdown&disable_web_page_preview=True',
                        files={'document': file}
                    )
            return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
        else:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не удалось отправить сообщение.',
                     'details': {},
                     'instance': request.path}, ensure_ascii=False), status=400)
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
