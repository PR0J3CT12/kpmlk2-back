from django.utils.timezone import now
from kpm.apps.users.models import History


class LastLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user = request.user

            # Обновляем поле `last_login`, только если с последнего обновления прошло, например, 5 минут
            if user.last_login is None or (now() - user.last_login).total_seconds() > 300:
                user.last_login = now()
                user.save(update_fields=['last_login'])

            logons = History.objects.filter(user=user).order_by('-datetime')
            if logons:
                last_logon = logons[0]
                current_date = now()
                if not (last_logon.datetime.date() == current_date.date() and last_logon.datetime.hour == current_date.hour):
                    login_obj = History(user=user)
                    login_obj.save()
            else:
                login_obj = History(user=user)
                login_obj.save()

        response = self.get_response(request)
        return response
