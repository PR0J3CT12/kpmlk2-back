import jwt
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
import json
from kpm.apps.users.functions import get_tokens_for_user
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist


EXCLUDE_FROM_MIDDLEWARE = [
    reverse('login'),
    reverse('logout'),
    reverse('swagger-schema')
]


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.check_auth(request)
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {}
        if isinstance(response, Response):
            response.render()

        return response

    def check_auth(self, request):
        if request.path in EXCLUDE_FROM_MIDDLEWARE:
            return self.get_response(request)
        access = request.COOKIES.get('access', None)
        try:
            access_payload = jwt.decode(access, settings.SECRET_KEY, algorithms='HS256')
        except jwt.ExpiredSignatureError:
            user_id, message = self.get_user_id_from_refresh_token(request)
            if user_id is None:
                return Response(f'Access token is expired and {message}', status=401)

            setattr(request, 'user_id', str(user_id))
            response = self.get_response(request)

            tokens = get_tokens_for_user(user_id)
            if tokens['refresh']:
                response.set_cookie(
                    key='refresh',
                    value=tokens['refresh'],
                    expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                )
            else:
                del response.cookies['refresh']
            if tokens['access']:
                response.set_cookie(
                    key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                    value=tokens['access'],
                    expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                )
            else:
                del response.cookies['access']
            return response
        except jwt.DecodeError:
            user_id, message = self.get_user_id_from_refresh_token(request)
            if user_id is None:
                return Response(f'Access token invalid or missing and {message}', status=401)

            setattr(request, 'user_id', str(user_id))
            response = self.get_response(request)

            tokens = get_tokens_for_user(user_id)
            if tokens['refresh']:
                response.set_cookie(
                    key='refresh',
                    value=tokens['refresh'],
                    expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                )
            else:
                del response.cookies['refresh']
            if tokens['access']:
                response.set_cookie(
                    key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                    value=tokens['access'],
                    expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                )
            else:
                del response.cookies['access']
            return response

        user_id = access_payload['user_id']
        setattr(request, 'user_id', user_id)
        if access:
            request.META['HTTP_AUTHORIZATION'] = f'kpm {access}'
            request.META['Authorization'] = f'Bearer {access}'

        return self.get_response(request)

    def get_user_id_from_refresh_token(self, request):
        try:
            refresh_token = request.COOKIES['refresh']
            refresh_payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms='HS256')
            user_id = refresh_payload['user_id']
            return user_id, ""
        except KeyError:
            return None, 'refresh token is missing'
        except jwt.ExpiredSignatureError:
            return None, 'refresh token is expired'
        except jwt.DecodeError:
            return None, 'refresh token is invalid'
        except ObjectDoesNotExist:
            return None, 'user does not exist'
