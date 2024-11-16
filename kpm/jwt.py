from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response and response.status_code != 200:
        detail = response.data['detail']
        if detail == 'Учетные данные не были предоставлены.':
            response.data = {'state': 'error', 'message': f'Пользователь не аутентифицирован.', 'details': {},
                             'instance': context['request'].path}
        if detail == 'Данный токен недействителен для любого типа токена':
            response.data = {'state': 'error', 'message': f'Недействительный токен.', 'details': {},
                             'instance': context['request'].path}
        if detail == 'У вас недостаточно прав для выполнения данного действия.':
            response.data = {'state': 'error', 'message': f'У вас недостаточно прав для выполнения данного действия.', 'details': {},
                             'instance': context['request'].path}
    return response