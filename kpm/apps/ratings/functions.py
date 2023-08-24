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


def count_lvl(exp):
    try:
        exp = int(exp)
        base_exp = 50
        exp_per_level = 5

        level = 1
        while exp >= base_exp:
            exp -= base_exp
            base_exp += exp_per_level
            level += 1
        return level, exp, base_exp
    except Exception as e:
        return None, None, None