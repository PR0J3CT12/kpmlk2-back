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


if __name__ == '__main__':
    pass
