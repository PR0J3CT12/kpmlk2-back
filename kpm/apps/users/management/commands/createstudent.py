from django.core.management.base import BaseCommand
from kpm.apps.users.models import User, Admin
from django.conf import settings
from django.contrib.auth.hashers import make_password


SECRET_KEY = settings.SECRET_KEY


class Command(BaseCommand):
    help = 'Create user | python manage.py createuser "fullname" "login/password"'

    def add_arguments(self, parser):
        parser.add_argument('fullname', type=str, help='User fullname')
        parser.add_argument('login/password', type=str, help='User password')

    def handle(self, *args, **kwargs):
        try:
            fullname = kwargs['fullname']
            login, password = kwargs['login/password'].split(' / ')
            students = User.objects.all()
            if students:
                last_student = students.latest("id")
                last_id = last_student.id
            else:
                last_id = 0
            user = User(id=last_id + 1, login=login, name=fullname, default_password=password)
            user.save()
            self.stdout.write(f'Пользователь создан.')
        except Exception as e:
            self.stdout.write(f'Произошла ошибка | {str(e)}')