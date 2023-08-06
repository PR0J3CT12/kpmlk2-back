from drf_yasg import openapi

id_param = openapi.Parameter("id", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                             operation_description='ID пользователя.', example=1)
class_param = openapi.Parameter("class", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                operation_description='Класс учеников.', example=4)
login_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                    required=['login', 'password'],
                                    properties={
                                        'login': openapi.Schema(type=openapi.TYPE_STRING, example="LM01"),
                                        'password': openapi.Schema(type=openapi.TYPE_STRING, example="12345")
                                    },
                                    operation_description='Вход пользователя')
create_user_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                          required=['name', 'class'],
                                          properties={
                                              'name': openapi.Schema(type=openapi.TYPE_STRING, example="Левин Михаил"),
                                              'class': openapi.Schema(type=openapi.TYPE_INTEGER, example=4)
                                          },
                                          operation_description='Создание пользователя')
change_password_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                              required=['password'],
                                              properties={
                                                  'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                                  'password': openapi.Schema(type=openapi.TYPE_STRING, example="12345"),
                                                  'refresh': openapi.Schema(type=openapi.TYPE_STRING,
                                                                   example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY3NTA3NjI3MSwianRpIjoiOTg1ZmUyYWViNjBkNDk1MzhjMTRiOGRhY2YwODNjYTkiLCJ1c2VyX2lkIjozfQ.l-KVnS4mKjK7V8bw96qxfePb4H8MfV0EZ-HOoarTpjs"),
                                              },
                                              operation_description='Изменение пароля пользователя')
logout_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                     required=['refresh'],
                                     properties={
                                         'refresh': openapi.Schema(type=openapi.TYPE_STRING,
                                                                   example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY3NTA3NjI3MSwianRpIjoiOTg1ZmUyYWViNjBkNDk1MzhjMTRiOGRhY2YwODNjYTkiLCJ1c2VyX2lkIjozfQ.l-KVnS4mKjK7V8bw96qxfePb4H8MfV0EZ-HOoarTpjs"),
                                     },
                                     operation_description='Выход пользователя')
login_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                    properties={
                                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=3),
                                        'tokens': openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                 properties={
                                                                     'refresh': openapi.Schema(
                                                                         type=openapi.TYPE_STRING,
                                                                         example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY3NTA3NjI3MSwianRpIjoiOTg1ZmUyYWViNjBkNDk1MzhjMTRiOGRhY2YwODNjYTkiLCJ1c2VyX2lkIjozfQ.l-KVnS4mKjK7V8bw96qxfePb4H8MfV0EZ-HOoarTpjs"),
                                                                     'access': openapi.Schema(
                                                                         type=openapi.TYPE_STRING,
                                                                         example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjc0NDc1MDcxLCJqdGkiOiI0YTRjNTY4NTg5YmQ0NTUyOTEzYTgzZDcxYTFkNzE1ZCIsInVzZXJfaWQiOjN9.wqpesDMhcj1uYRk947vqmYtmVjaBgWTchtuh8y1bzgI")
                                                                 }),
                                        'is_default': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),

                                    })
get_users_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                        properties={
                                            "students": openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                       properties={
                                                                           "id": openapi.Schema(
                                                                               type=openapi.TYPE_INTEGER, example=3),
                                                                           "name": openapi.Schema(
                                                                               type=openapi.TYPE_STRING,
                                                                               example="Левин Михаил"),
                                                                           "login": openapi.Schema(
                                                                               type=openapi.TYPE_STRING,
                                                                               example="LM01"),
                                                                           "default_password": openapi.Schema(
                                                                               type=openapi.TYPE_STRING,
                                                                               example="12345"),
                                                                           "experience": openapi.Schema(
                                                                               type=openapi.TYPE_INTEGER,
                                                                               example=12345),
                                                                           "mana_earned": openapi.Schema(
                                                                               type=openapi.TYPE_INTEGER, example=100),
                                                                           "last_homework_id": openapi.Schema(
                                                                               type=openapi.TYPE_INTEGER, example=12),
                                                                           "last_classwork_id": openapi.Schema(
                                                                               type=openapi.TYPE_INTEGER, example=12),
                                                                       }),

                                        })
get_user_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                       properties={
                                           "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=3),
                                           "name": openapi.Schema(type=openapi.TYPE_STRING, example="Левин Михаил"),
                                           "login": openapi.Schema(type=openapi.TYPE_STRING, example="LM01"),
                                           "default_password": openapi.Schema(type=openapi.TYPE_STRING,
                                                                              example="12345"),
                                           "is_default": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                                           "experience": openapi.Schema(type=openapi.TYPE_INTEGER, example=12345),
                                           "mana_earned": openapi.Schema(type=openapi.TYPE_INTEGER, example=100),
                                           "last_homework_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=12),
                                           "last_classwork_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=12),
                                       })
logout_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_users_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_user_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
create_user_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
change_password_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
logout_responses = {200: logout_response_200}
login_responses = {200: login_response_200}
delete_users_responses = {200: delete_users_response_200}
delete_user_responses = {200: delete_user_response_200}
create_user_responses = {200: create_user_response_200}
get_user_responses = {200: get_user_response_200}
get_users_responses = {200: get_users_response_200}
change_password_responses = {200: change_password_response_200}
