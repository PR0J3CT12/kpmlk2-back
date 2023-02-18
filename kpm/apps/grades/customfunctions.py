from django.db import connection
from django.utils.datastructures import MultiValueDictKeyError
from transliterate import translit
import random


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


if __name__ == '__main__':
    pass
