from django.core.management.base import BaseCommand
from kpm.apps.users.models import User, Admin
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist


SECRET_KEY = settings.SECRET_KEY


class Command(BaseCommand):
    help = 'Create user | python manage.py droppassword "login" "password"'

    def add_arguments(self, parser):
        parser.add_argument('login', type=str, help='User login')
        parser.add_argument('password', type=str, help='User password')

    def handle(self, *args, **kwargs):
        try:
            login = kwargs['login']
            password = kwargs['password']
            encrypted_password = make_password(password, SECRET_KEY)
            print(encrypted_password)
            users = User.objects.all()
            print(users)
            user = User.objects.get(login=login)
            user.password = encrypted_password
            user.save()
            self.stdout.write(f'Пользователь создан.')
        except ObjectDoesNotExist:
            self.stdout.write(f'Пользователь с таким логином не найден.')
        except Exception as e:
            self.stdout.write(f'Произошла ошибка | {str(e)}')