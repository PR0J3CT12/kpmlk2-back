from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from kpm.apps.users.models import User
from kpm.apps.logs.models import Log
from kpm.apps.users.permissions import IsNotAuthenticated, IsAdmin
import json
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.hashers import check_password, make_password
from rest_framework_simplejwt.exceptions import TokenError


SECRET_KEY = settings.SECRET_KEY


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    user_id = request.user.id
    current_user = User.objects.get(id=user_id)
    if request.body:
        request_body = json.loads(request.body)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=400)
    try:
        id_ = request_body["id"]
        password_ = str(request_body["password"])
        user = User.objects.get(id=id_)
        if not user:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Пользователь не существует.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=404)
        if user_id == id_ or current_user.is_admin is True:
            encrypted_password = make_password(password_, SECRET_KEY)
            user.password = encrypted_password
            user.default_password = None
            user.save()
            log = Log(operation='UPDATE', from_table='users', details=f"Изменен пароль у пользователя {id_}.")
            log.save()
            refresh = request.data.get('refresh')
            if not refresh:
                return HttpResponse(
                    json.dumps({'state': 'error', 'message': 'Отсутствует refresh токен.', 'details': {},
                                'instance': request.path},
                               ensure_ascii=False), status=400)
            token = RefreshToken(refresh)
            token.blacklist()
            return HttpResponse(
                json.dumps(
                    {'state': 'success', 'message': 'Пароль изменен.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=200)
        else:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': 'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=401)
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
    except Exception as e:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {},
                 'instance': request.path},
                ensure_ascii=False), status=404)


@api_view(["POST"])
@permission_classes([IsNotAuthenticated])
def login(request):
    if request.body:
        request_body = json.loads(request.body)
    else:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {},
                        'instance': request.path},
                       ensure_ascii=False), status=400)
    try:
        login_ = request_body["login"]
        password_ = request_body["password"]
        user = User.objects.get(login=login_)
        default_password = user.default_password
        if default_password:
            if password_ == default_password:
                request.session['login'] = login_
                request.session['id'] = user.id
                id_ = user.id
                tokens = get_tokens_for_user(user)
                return HttpResponse(
                    json.dumps(
                        {'state': 'success', 'message': 'Необходима смена пароля.',
                         'details': {'id': id_, 'tokens': tokens, 'is_default': 1}},
                        ensure_ascii=False),
                    status=200)
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
                return HttpResponse(
                    json.dumps(
                        {'state': 'success', 'message': 'Вход успешно выполнен.',
                         'details': {'id': id_, 'tokens': tokens, 'is_default': 0}},
                        ensure_ascii=False),
                    status=200)
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
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {},
                 'instance': request.path},
                ensure_ascii=False), status=404)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def logout(request):
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