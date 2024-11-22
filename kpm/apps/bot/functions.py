from django.utils.datastructures import MultiValueDictKeyError
import subprocess


def get_vda2_usage():
    # Выполняем команду df -h
    result = subprocess.run(['df', '-h'], stdout=subprocess.PIPE, text=True)

    # Разделяем вывод на строки
    lines = result.stdout.splitlines()

    # Ищем строку с /dev/vda2
    for line in lines:
        if '/dev/vda2' in line:
            return line
    return "Раздел /dev/vda2 не найден"


def get_variable(variable_name, source_request):
    try:
        variable = source_request.GET[variable_name]
        return variable
    except MultiValueDictKeyError:
        return None
    except Exception as e:
        return None
