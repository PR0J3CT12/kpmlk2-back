import jwt
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
import json
from kpm.apps.users.functions import get_tokens_for_user
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.check_auth(request)
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = 'application/json'
        response.renderer_context = {}
        if isinstance(response, Response):
            response.render()
        return response

    def get_user_id(self, request):
        try:
            refresh = request.COOKIES['refresh']
            refresh_payload = jwt.decode(refresh, settings.SECRET_KEY + 'jwtoken', algorithms='HS256')
        except KeyError:
            return 'refresh token отсутствует'
        except jwt.ExpiredSignatureError:
            return 'refresh token протух'
        except jwt.DecodeError:
            return 'access token неправильный'
        else:
            user_id = refresh_payload['user_id']
            return int(user_id)

    def check_auth(self, request):
        exclude_path = [reverse('login'), reverse('logout')]
        if request.path in exclude_path:
            return self.get_response(request)

        access_token = request.COOKIES.get('access', None)
        try:
            access_payload = jwt.decode(access_token, settings.SECRET_KEY + 'jwtoken', algorithms='HS256')
        except jwt.ExpiredSignatureError:
            user_id = self.get_user_id(request)
            if isinstance(user_id, str):
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Access токен протух.', 'details': {'user_id': user_id},
                     'instance': request.path},
                    ensure_ascii=False), status=401)

            setattr(request, 'user_id', str(user_id))

            response = self.get_response(request)

            tokens = get_tokens_for_user(user_id)
            response.set_cookie(key='refresh', value=tokens['refresh'], httponly=True, expires=tokens['refresh_exp'])
            response.set_cookie(key='access', value=tokens['access'], httponly=True, expires=tokens['access_exp'])

            return response
        except jwt.DecodeError:
            user_id = self.get_user_id(request)
            if isinstance(user_id, str):
                return HttpResponse(json.dumps(
                    {'state': 'error', 'message': f'Access токен протух.', 'details': {'user_id': user_id},
                     'instance': request.path},
                    ensure_ascii=False), status=401)

            setattr(request, 'user_id', str(user_id))

            response = self.get_response(request)

            tokens = get_tokens_for_user(user_id)
            response.set_cookie(key='refresh', value=tokens['refresh'], httponly=True, expires=tokens['refresh_exp'])
            response.set_cookie(key='access', value=tokens['access'], httponly=True, expires=tokens['access_exp'])

            return response

        user_id = access_payload['user_id']
        setattr(request, 'user_id', str(user_id))

        return self.get_response(request)
