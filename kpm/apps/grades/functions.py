from django.db import connection
from django.utils.datastructures import MultiValueDictKeyError
from transliterate import translit
import random
import math


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


def mana_generation(type_, is_homework, score, max_score):
    if not is_homework:
        return 0, 0
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
    elif type_ == 7:
        mana = math.ceil(float(score) / float(max_score) * 4)
    elif type_ == 6:
        if score >= 4:
            mana = 4
        else:
            mana = score
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
        green = random.randint(1, 2)
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


def is_number_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def custom_distinct(array):
    new_array = []
    for element in array:
        if element not in new_array:
            new_array.append(element)
    return new_array


def borders_lvl(score):
    homework_lvl = 0
    if 50 <= score < 110:
        homework_lvl = 1
    elif 110 <= score < 180:
        homework_lvl = 2
    elif 180 <= score < 260:
        homework_lvl = 3
    elif 260 <= score < 350:
        homework_lvl = 4
    elif 350 <= score < 450:
        homework_lvl = 5
    elif 450 <= score < 560:
        homework_lvl = 6
    elif 560 <= score < 680:
        homework_lvl = 7
    elif 680 <= score < 810:
        homework_lvl = 8
    elif 810 <= score < 950:
        homework_lvl = 9
    elif 950 <= score < 1100:
        homework_lvl = 10
    elif score >= 1100:
        homework_lvl = 10
    return homework_lvl


if __name__ == '__main__':
    pass
