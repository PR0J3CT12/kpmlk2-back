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


def mana_generation(type_, score, max_score):
    if type_ == 0:
        percentage = float(score) / float(max_score) * 100
        if 0 < percentage <= 25:
            mana = 1
        elif 25 < percentage <= 50:
            mana = 2
        elif 50 < percentage <= 75:
            mana = 3
        elif 75 < percentage <= 100:
            mana = 4
        else:
            mana = 0
    elif type_ == 2:
        score_ = float(score)
        if 0 <= score_ < 0.9:
            mana = 0
        elif 0.9 <= score_ < 2.4:
            mana = 1
        elif 2.4 <= score_ <= 3:
            mana = 2
        else:
            mana = 0
    elif type_ == 3:
        score_ = float(score)
        if score_ == 1:
            mana = 1
        elif score_ == 2:
            mana = 2
        elif score_ == 3:
            mana = 3
        elif score_ >= 4:
            mana = 4
        else:
            mana = 0
    else:
        mana = 0
    if mana == 4:
        seed = random.randint(0, 1)
        if seed:
            green = 4
            blue = 0
        else:
            green = 0
            blue = 4
    elif mana == 3:
        green = random.randint(0, 3)
        blue = mana - green
    elif mana == 2:
        if type_ == 2:
            seed = random.randint(0, 1)
            if seed:
                green = 2
                blue = 0
            else:
                green = 0
                blue = 2
        else:
            green = random.randint(0, 2)
            blue = mana - green
    elif mana == 1:
        green = random.randint(0, 1)
        blue = mana - green
    else:
        green = 0
        blue = 0
    return green, blue


def is_number(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    pass
