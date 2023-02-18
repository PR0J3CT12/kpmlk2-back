from django.db import connection
from django.utils.datastructures import MultiValueDictKeyError
from transliterate import translit
import random


def get_lvl(exp: float):
    """
    Function for get lvl from experience
    :param exp: experience
    :return: lvl
    """
    if exp < 0:
        return 0
    elif exp < 50:
        return 1
    elif 50 <= exp < 110:
        return 2
    elif 110 <= exp < 180:
        return 3
    elif 180 <= exp < 260:
        return 4
    elif 260 <= exp < 350:
        return 5
    elif 350 <= exp < 450:
        return 6
    elif 450 <= exp < 560:
        return 7
    elif 560 <= exp < 680:
        return 8
    elif 680 <= exp < 810:
        return 9
    elif 810 <= exp < 950:
        return 10
    elif 950 <= exp < 1100:
        return 11
    else:
        return 12


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


def execute_sql(query: str, params: list):
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchall()

        return result
    except Exception as e:
        print(e)


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


if __name__ == '__main__':
    pass
