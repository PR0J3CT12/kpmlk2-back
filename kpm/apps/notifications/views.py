from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from kpm.apps.users.permissions import *
from kpm.apps.users.functions import is_trusted
from kpm.apps.notifications.functions import *
from kpm.apps.notifications.docs import *
from kpm.apps.messages.models import Message
from kpm.apps.works.models import WorkUser
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import json
from django.db.models import Sum, Q, Count, F, Avg, ExpressionWrapper, FloatField
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from kpm.apps.users.docs import permissions_operation_description
from kpm.apps.works.validators import validate_class


host = settings.MEDIA_HOST_PATH


@swagger_auto_schema(method='GET', operation_summary="Получить уведомления пользователя.",
                     manual_parameters=[id_param, class_param],
                     responses=get_notifications_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAuthenticated']}")
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEnabled])
def get_notifications(request):
    try:
        id_ = get_variable('id', request)
        if not is_trusted(request, id_):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        user = User.objects.get(id=id_)
        messages = Message.objects.filter(user_to=user, is_viewed=False).count()
        if user.is_admin:
            class_ = get_variable('class', request)
            if not validate_class(class_):
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Неверно указан класс учеников.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=400)
            works = WorkUser.objects.filter(user=user, status__in=[1, 5], work__school_class=class_).count()
        else:
            works = WorkUser.objects.filter(user=user, status__in=[0, 3, 4]).count()
        notifications = {
            'messages': messages,
            'works': works
        }
        return HttpResponse(json.dumps(notifications, ensure_ascii=False), status=200)
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
