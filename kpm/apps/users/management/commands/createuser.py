from django.core.management.base import BaseCommand
from kpm.apps.users.models import User
from django.conf import settings
from django.contrib.auth.hashers import make_password


SECRET_KEY = settings.SECRET_KEY


class Command(BaseCommand):
    help = 'Create user | python manage.py createuser "login" "fullname" "password"'

    def add_arguments(self, parser):
        parser.add_argument('login', type=str, help='User login')
        parser.add_argument('fullname', type=str, help='User fullname')
        parser.add_argument('password', type=str, help='User password')

    def handle(self, *args, **kwargs):
        try:
            login = kwargs['login']
            fullname = kwargs['fullname']
            password = kwargs['password']
            encrypted_password = make_password(password, SECRET_KEY)
            students = User.objects.all()
            if students:
                last_student = students.latest("id")
                last_id = last_student.id
            else:
                last_id = 0
            user = User(id=last_id + 1, login=login, name=fullname, password=encrypted_password, is_superuser=False, is_admin=True, default_password="", is_default=False, experience=None, mana_earned=None)
            user.save()
            self.stdout.write(f'Пользователь создан.')
        except Exception as e:
            self.stdout.write(f'Произошла ошибка | {str(e)}')