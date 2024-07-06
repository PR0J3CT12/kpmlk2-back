import jwt
from django.urls import reverse
from django.conf import settings
from kpm.apps.users.functions import get_tokens_for_user, get_user_id_from_refresh_token, get_new_access_for_refresh_token
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
import time
from django.utils.deprecation import MiddlewareMixin

EXCLUDE_FROM_MIDDLEWARE = [
    reverse('login'),
    reverse('logout'),
    reverse('swagger-schema')
]


class AuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path in EXCLUDE_FROM_MIDDLEWARE:
            return None
        try:
            access = request.COOKIES.get('access_token', None)
            if access:
                access_payload = jwt.decode(access, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = access_payload['user_id']
                if request.user.is_disabled:
                    return HttpResponse(f'Access denied.', status=401)
                setattr(request, 'user_id', user_id)
                request.META['HTTP_AUTHORIZATION'] = f'kpm {access}'
            else:
                return HttpResponse(f'Access token not provided', status=401)
        except jwt.ExpiredSignatureError:
            user_id, message = get_user_id_from_refresh_token(request, settings.SECRET_KEY)
            if user_id is None:
                return HttpResponse(f'Access token is expired and {message}', status=401)

            if request.user.is_disabled:
                return HttpResponse(f'Access denied.', status=401)
            setattr(request, 'user_id', str(user_id))
            access, message = get_new_access_for_refresh_token(request)
            if access:
                request.META['HTTP_AUTHORIZATION'] = f'yuh {access}'
            else:
                return HttpResponse(f'Invalid refresh token and {message}', status=401)
            return None
        except jwt.DecodeError:
            user_id, message = get_user_id_from_refresh_token(request, settings.SECRET_KEY)
            if user_id is None:
                return HttpResponse(f'Access token invalid or missing and {message}', status=401)

            if request.user.is_disabled:
                return HttpResponse(f'Access denied.', status=401)
            setattr(request, 'user_id', str(user_id))
            access, message = get_new_access_for_refresh_token(request)
            if access:
                request.META['HTTP_AUTHORIZATION'] = f'yuh {access}'
            else:
                return HttpResponse(f'Invalid refresh token and {message}', status=401)
            return None
        return None

    def process_response(self, request, response):
        if request.path in EXCLUDE_FROM_MIDDLEWARE:
            return response
        if hasattr(request, 'user_id'):
            tokens = get_tokens_for_user(request.user_id)
            if tokens['refresh']:
                response.set_cookie(
                    key='refresh_token',
                    value=tokens['refresh'],
                    expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                )
            else:
                response.delete_cookie('refresh_token')

            if tokens['access']:
                response.set_cookie(
                    key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                    value=tokens['access'],
                    expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                )
            else:
                response.delete_cookie('access_token')

        return response
