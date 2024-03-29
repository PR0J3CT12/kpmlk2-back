from drf_yasg import openapi

id_param = openapi.Parameter("id", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                             operation_description='ID пользователя.', example=1)
id_param_group = openapi.Parameter("id", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                   operation_description='ID группы.', example=1)
class_param = openapi.Parameter("class", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                operation_description='Класс учеников.', example=4)
group_param = openapi.Parameter("group", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                operation_description='ID группы.', example=1)
user_param = openapi.Parameter("student", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                               operation_description='ID ученика.', example=1)
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
create_group_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                           required=['name', 'class'],
                                           properties={
                                               'name': openapi.Schema(type=openapi.TYPE_STRING, example="Группа1"),
                                               'class': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                               'marker': openapi.Schema(type=openapi.TYPE_INTEGER, example=0),
                                           },
                                           operation_description='Создание группы')
operation_description = "Marker: 0 - #ff8282, 1 - #ffb875, 2 - #fdff96, 3 - #93ff91, 4 - #78ffef, 5 - #7776d6, 6 - #bfa0de"
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
                                                                           "group_id": openapi.Schema(
                                                                               type=openapi.TYPE_INTEGER, example=1),
                                                                           "group_name": openapi.Schema(
                                                                               type=openapi.TYPE_INTEGER, example="Название группы"),
                                                                           "color": openapi.Schema(
                                                                               type=openapi.TYPE_STRING, example="#bfa0de"),
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
                                           "admin_tier": openapi.Schema(type=openapi.TYPE_INTEGER, example=2),
                                       })
get_groups_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                         properties={
                                             "groups": openapi.Schema(
                                                      type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                                                                          "id": openapi.Schema(
                                                                              type=openapi.TYPE_INTEGER, example=1),
                                                                          "name": openapi.Schema(
                                                                              type=openapi.TYPE_STRING,
                                                                              example="Группа 1"),
                                                                          "marker": openapi.Schema(
                                                                              type=openapi.TYPE_INTEGER,
                                                                              example=0),
                                                                          "students": openapi.Schema(
                                                                              type=openapi.TYPE_ARRAY,
                                                                              items=openapi.Schema(
                                                                                  type=openapi.TYPE_OBJECT,
                                                                                  properties={
                                                                                      "id": openapi.Schema(
                                                                                          type=openapi.TYPE_INTEGER,
                                                                                          example=1),
                                                                                      "name": openapi.Schema(
                                                                                          type=openapi.TYPE_STRING,
                                                                                          example="Левин Михаил"),
                                                                                  }))
                                                                      }))

                                         })
get_all_logons_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                             properties={
                                                 "logons": openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                          properties={
                                                                              "date": openapi.Schema(
                                                                                  type=openapi.TYPE_STRING,
                                                                                  example="14.08.2023"),
                                                                              "hour": openapi.Schema(
                                                                                  type=openapi.TYPE_STRING,
                                                                                  example="16:00"),
                                                                              "datetime": openapi.Schema(
                                                                                  type=openapi.TYPE_STRING,
                                                                                  example="2023-08-14 16:33:11.402593+03"),
                                                                          }),

                                             })
logout_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_users_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_user_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
create_user_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
change_password_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
create_group_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_group_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
add_to_group_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_from_group_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
logout_responses = {200: logout_response_200}
login_responses = {200: login_response_200}
delete_users_responses = {200: delete_users_response_200}
delete_user_responses = {200: delete_user_response_200}
create_user_responses = {200: create_user_response_200}
get_user_responses = {200: get_user_response_200}
get_users_responses = {200: get_users_response_200}
change_password_responses = {200: change_password_response_200}
create_group_responses = {200: create_group_response_200}
delete_group_responses = {200: delete_group_response_200}
add_to_group_responses = {200: add_to_group_response_200}
delete_from_group_responses = {200: delete_from_group_response_200}
get_groups_responses = {200: get_groups_response_200}
get_all_logons_responses = {200: get_all_logons_response_200}
