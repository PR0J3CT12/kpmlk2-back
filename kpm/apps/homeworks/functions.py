from django.utils.datastructures import MultiValueDictKeyError
from PIL import Image
from pillow_heif import register_heif_opener


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


def heif_to_jpeg(path):
    try:
        register_heif_opener()
        image = Image.open(path)
        path_wo_ext, ext = path.split('.')
        new_path = f'{path_wo_ext}.jpeg'
        image.convert('RGB').save(f'{path_wo_ext}.jpeg')
        return new_path
    except Exception:
        return None


if __name__ == "__main__":
    heif_to_jpeg('C:/PythonProjects/kpm/media/homeworks/123.heic')
