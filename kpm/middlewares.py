from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from django.http import HttpResponse
import json


class CustomAuthMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, AuthenticationFailed):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Пользователь не аутентифицирован.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=401)

        if isinstance(exception, PermissionDenied):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'У вас нет доступа к этому ресурсу.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=403)

        return None