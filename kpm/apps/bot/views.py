from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from kpm.apps.users.permissions import IsAdmin, IsEnabled, IsTierOne
from kpm.apps.users.functions import is_trusted
from .functions import get_variable, get_vda2_usage
from kpm.apps.users.models import User
import json
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.messages.docs import *
from django.conf import settings
from kpm.apps.users.docs import permissions_operation_description
import requests
import os
import psycopg2


LOGGER = settings.LOGGER
CHAT_ID = settings.TG_SUPPORT_CHAT
BOT_TOKEN = settings.TG_BOT_TOKEN
ALLOWED_CHATS = settings.TG_ALLOWED_CHATS
DB_NAME = settings.DATABASES['default']['NAME']
DB_USER = settings.DATABASES['default']['USER']
DB_USER_PASSWORD = settings.DATABASES['default']['PASSWORD']
DB_HOST = settings.DATABASES['default']['HOST']
DB_PORT = settings.DATABASES['default']['PORT']


#@swagger_auto_schema(method='POST', operation_summary="Отправить сообщение в поддержку.",
#                     request_body=support_request_body,
#                     responses=support_responses,
#                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAuthenticated']}")
@api_view(["GET"])
def report(request):
    try:
        month = get_variable('month', request)
        DB_PARAMS = {
            "dbname": "progressivemath2024",
            "user": DB_USER,
            "password": DB_USER_PASSWORD,
            "host": DB_HOST,
            "port": DB_PORT
        }
        with psycopg2.connect(**DB_PARAMS) as connection:
            with connection.cursor() as cursor:
                query = f"""
                            SELECT 
                                COUNT(works_users.id) AS count, 
                                users.name
                            FROM users
                            LEFT JOIN works_users ON works_users.checker_id = users.id 
                                AND EXTRACT(MONTH FROM works_users.checked_at) = {int(month)}
                            WHERE users.is_admin IS TRUE
                            GROUP BY users.name
                            ORDER BY count DESC;
                        """
                cursor.execute(query)
                results = cursor.fetchall()
                msg = f"Отчет за месяц {month}:\n"
                for row in results:
                    msg += f'{row[1]} | {row[0]}\n'
                res = requests.post(
                    url=f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?parse_mode=Markdown&disable_web_page_preview=True',
                    data={'chat_id': 469447997, 'text': msg}
                ).json()
        memory = get_vda2_usage()
        res = requests.post(
            url=f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?parse_mode=Markdown&disable_web_page_preview=True',
            data={'chat_id': 469447997, 'text': memory}
        ).json()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)
