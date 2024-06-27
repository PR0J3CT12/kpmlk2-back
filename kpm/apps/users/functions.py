from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.datastructures import MultiValueDictKeyError
from transliterate import translit
import random
from kpm.apps.users.models import User
from datetime import datetime, timezone
import jwt


def get_tokens_for_user(user):
    try:
        user = User.objects.get(id=user)
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        refresh_exp = datetime.fromtimestamp(refresh['exp'], timezone.utc)
        access_exp = datetime.fromtimestamp(access['exp'], timezone.utc)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'refresh_exp': refresh_exp,
            'access_exp': access_exp,
        }
    except ObjectDoesNotExist:
        return {
            'refresh': None,
            'access': None,
            'refresh_exp': None,
            'access_exp': None,
        }


def get_user_id_from_refresh_token(request, key):
    try:
        refresh_token = request.COOKIES['refresh']
        refresh_payload = jwt.decode(refresh_token, key, algorithms='HS256')
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


def get_variable(variable_name, source_request):
    """
    Function for parse variable from url.
    variable_name: name of variable in url.
    source_request: django request object.
    RETURN: variable value or None.
    """
    try:
        variable = source_request.GET[variable_name]
        return variable
    except MultiValueDictKeyError:
        return None
    except Exception as e:
        return None


def login_password_creator(name, id_):
    """
    Фамилия Имя, строка, в которой ученик находится на вход
    Логин и пароль на выход
    """
    trans = translit(name, 'ru', reversed=True).split()
    if id_ < 10:
        login = trans[0][0] + trans[1][0] + '0' + str(id_)
    else:
        login = trans[0][0] + trans[1][0] + str(id_)
    password = str(random.randint(10000, 99999))
    return id_, login, password


def password_creator():
    password = str(random.randint(10000, 99999))
    return password


def is_trusted(request, id_):
    try:
        if request.user.is_admin or id_ == request.user.id:
            return True
        return False
    except:
        return False


