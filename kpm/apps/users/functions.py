from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework_simplejwt.exceptions import TokenError
from transliterate import translit
import random
from kpm.apps.users.models import User
from datetime import datetime, timezone
import jwt
from fuzzywuzzy import process


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
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


def get_new_access_for_refresh_token(request):
    try:
        refresh_token = request.COOKIES['refresh_token']
        refresh_token = RefreshToken(refresh_token)
        new_access_token = refresh_token.access_token
        return str(new_access_token), ''
    except TokenError as e:
        return None, 'Invalid refresh token'
    except Exception as e:
        return None, f'Failed to generate new access token | {str(e)}'


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
