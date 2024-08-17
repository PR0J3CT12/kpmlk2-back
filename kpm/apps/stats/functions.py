from django.utils.datastructures import MultiValueDictKeyError


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


def is_number_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


GRAPH_CONFIG_THEMES = {
    'default': {
        'min': 0,
        'max': 100
    },
    '1': {
        'bad': 0.9,
        'normal': 2.4,
        'good': 3,
        'min': 0,
        'max': 3
    },
    '8': {
        'border': 9,
        'min': 0,
        'max': 18
    },
    '9': {
        'bad': 2.5,
        'normal': 3.5,
        'good': 6,
        'min': 0,
        'max': 6
    }
}

GRAPH_CONFIG_TYPES = {
    'default': {
        'min': 0,
        'max': 100
    }
}
