from drf_yasg import openapi

class_param = openapi.Parameter("class", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                operation_description='Класс учеников.', example=4)
id_param = openapi.Parameter("id", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                             operation_description='ID работы.', example=1)
file_param = openapi.Parameter("file", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                               operation_description='ID файла.', example=1)
student_param = openapi.Parameter("student", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                  operation_description='ID ученика.', example=1)
create_homework_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                              required=['title', 'class', 'score', 'text', 'answers'],
                                              properties={
                                                  'title': openapi.Schema(type=openapi.TYPE_STRING,
                                                                          example="Домашняя работа 1"),
                                                  'class': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                                  'score': openapi.Schema(type=openapi.TYPE_INTEGER, example=100),
                                                  'text': openapi.Schema(type=openapi.TYPE_STRING,
                                                                         example="Условие домашней работы"),
                                                  'files': openapi.Schema(
                                                      type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(
                                                          type=openapi.TYPE_STRING)
                                                  ),
                                                  "answers": openapi.Schema(
                                                      type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(
                                                          type=openapi.TYPE_STRING)
                                                  ),
                                                  "users": openapi.Schema(
                                                      type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(
                                                          type=openapi.TYPE_INTEGER)
                                                  )
                                              },
                                              operation_description='Создание домашней работы.')
update_homework_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                              required=['id'],
                                              properties={
                                                  'title': openapi.Schema(type=openapi.TYPE_STRING,
                                                                          example="Домашняя работа 1"),
                                                  'score': openapi.Schema(type=openapi.TYPE_INTEGER, example=100),
                                                  'text': openapi.Schema(type=openapi.TYPE_STRING,
                                                                         example="Условие домашней работы"),
                                                  'files': openapi.Schema(
                                                      type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(
                                                          type=openapi.TYPE_STRING)
                                                  ),
                                                  "answer": openapi.Schema(
                                                      type=openapi.TYPE_STRING, example="Ответ"
                                                  ),
                                                  "cell": openapi.Schema(
                                                      type=openapi.TYPE_INTEGER, example=0
                                                  ),
                                              },
                                              operation_description='Изменение домашней работы.')
get_homework_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                           properties={
                                               'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                               'title': openapi.Schema(type=openapi.TYPE_STRING,
                                                                       example="Домашняя работа 1"),
                                               'text': openapi.Schema(type=openapi.TYPE_STRING,
                                                                      example="Условие домашней работы"),
                                               'score': openapi.Schema(type=openapi.TYPE_INTEGER, example=100),
                                               'fields': openapi.Schema(type=openapi.TYPE_INTEGER, example=6),
                                               "answers": openapi.Schema(
                                                   type=openapi.TYPE_ARRAY,
                                                   items=openapi.Schema(
                                                       type=openapi.TYPE_STRING)
                                               ),
                                               'files': openapi.Schema(
                                                   type=openapi.TYPE_ARRAY,
                                                   items=openapi.Schema(
                                                       type=openapi.TYPE_OBJECT,
                                                       properties={
                                                           "id": openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                example=0),
                                                           "name": openapi.Schema(type=openapi.TYPE_STRING,
                                                                                  example="Название файла"),
                                                           "link": openapi.Schema(type=openapi.TYPE_STRING,
                                                                                  example="Путь до файла"),
                                                           "ext": openapi.Schema(type=openapi.TYPE_STRING,
                                                                                 example="Расширение файла"),
                                                       }
                                                   )
                                               ),
                                               'class': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                               'users': openapi.Schema(
                                                   type=openapi.TYPE_ARRAY,
                                                   items=openapi.Schema(
                                                       type=openapi.TYPE_OBJECT,
                                                       properties={
                                                           "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                                           "name": openapi.Schema(type=openapi.TYPE_STRING,
                                                                                  example="Имя Фамилия"),
                                                       }
                                                   )
                                               ),
                                               'created_at': openapi.Schema(type=openapi.TYPE_STRING,
                                                                            example="2023-08-21 16:40:19.337147+03"),
                                           },
                                           operation_description='Получение домашней работы(админка).')
get_user_homework_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                properties={
                                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                                    'title': openapi.Schema(type=openapi.TYPE_STRING,
                                                                            example="Домашняя работа 1"),
                                                    'text': openapi.Schema(type=openapi.TYPE_STRING,
                                                                           example="Условие домашней работы"),
                                                    'max_score': openapi.Schema(type=openapi.TYPE_INTEGER, example=100),
                                                    'fields': openapi.Schema(type=openapi.TYPE_INTEGER, example=6),
                                                    'files': openapi.Schema(
                                                        type=openapi.TYPE_ARRAY,
                                                        items=openapi.Schema(
                                                            type=openapi.TYPE_OBJECT,
                                                            properties={
                                                                "name": openapi.Schema(type=openapi.TYPE_STRING,
                                                                                       example="Название файла"),
                                                                "link": openapi.Schema(type=openapi.TYPE_STRING,
                                                                                       example="Путь до файла"),
                                                                "ext": openapi.Schema(type=openapi.TYPE_STRING,
                                                                                      example="Расширение файла"),
                                                            }
                                                        )
                                                    ),
                                                    'class': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                                    'is_done': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                                                    'is_checked': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                                 example=True),
                                                    'comment': openapi.Schema(type=openapi.TYPE_STRING,
                                                                              example="Комментарий преподавателя"),
                                                    'created_at': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                 example="2023-08-21 16:40:19.337147+03"),
                                                    "answers": openapi.Schema(
                                                        type=openapi.TYPE_ARRAY,
                                                        items=openapi.Schema(
                                                            type=openapi.TYPE_STRING)
                                                    ),
                                                    "user_answers": openapi.Schema(
                                                        type=openapi.TYPE_ARRAY,
                                                        items=openapi.Schema(
                                                            type=openapi.TYPE_STRING)
                                                    ),
                                                    'user_files': openapi.Schema(
                                                        type=openapi.TYPE_ARRAY,
                                                        items=openapi.Schema(
                                                            type=openapi.TYPE_OBJECT,
                                                            properties={
                                                                "name": openapi.Schema(type=openapi.TYPE_STRING,
                                                                                       example="Название файла"),
                                                                "link": openapi.Schema(type=openapi.TYPE_STRING,
                                                                                       example="Путь до файла"),
                                                                "ext": openapi.Schema(type=openapi.TYPE_STRING,
                                                                                      example="Расширение файла"),
                                                            }
                                                        )
                                                    ),
                                                    'answered_at': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                  example="2023-08-21 16:40:19.337147+03"),
                                                    'user_score': openapi.Schema(type=openapi.TYPE_INTEGER, example=100)
                                                },
                                                operation_description='Получение домашней работы(пользователь).')
create_response_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                              required=['id', 'answers'],
                                              properties={
                                                  'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                                  "answers": openapi.Schema(
                                                      type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(
                                                          type=openapi.TYPE_STRING)
                                                  ),
                                                  'files': openapi.Schema(
                                                      type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(
                                                          type=openapi.TYPE_STRING)
                                                  ),
                                              },
                                              operation_description='Создание ответа на домашнюю работу.')
check_user_homework_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                  required=['id', 'student', 'score'],
                                                  properties={
                                                      'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                                      'student': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                                      'score': openapi.Schema(type=openapi.TYPE_INTEGER, example=100),
                                                      'comment': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                example="Комментарий преподавателя"),
                                                  },
                                                  operation_description='Проверка домашней работы(админка).')
get_my_homeworks_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                               properties={
                                                   "homeworks": openapi.Schema(
                                                       type=openapi.TYPE_ARRAY,
                                                       items=openapi.Schema(
                                                           type=openapi.TYPE_OBJECT,
                                                           properties={
                                                               "id": openapi.Schema(
                                                                   type=openapi.TYPE_INTEGER, example=3),
                                                               "name": openapi.Schema(
                                                                   type=openapi.TYPE_STRING,
                                                                   example="Домашняя работа 1"),
                                                               "is_done": openapi.Schema(
                                                                   type=openapi.TYPE_BOOLEAN,
                                                                   example=True),
                                                               "is_checked": openapi.Schema(
                                                                   type=openapi.TYPE_BOOLEAN,
                                                                   example=True),
                                                               'score': openapi.Schema(
                                                                   type=openapi.TYPE_INTEGER,
                                                                   example=100),
                                                               'max_score': openapi.Schema(
                                                                   type=openapi.TYPE_INTEGER,
                                                                   example=100),
                                                           }))

                                               })
get_all_homeworks_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                properties={
                                                    "homeworks": openapi.Schema(
                                                        type=openapi.TYPE_ARRAY,
                                                        items=openapi.Schema(
                                                            type=openapi.TYPE_OBJECT,
                                                            properties={
                                                                "id": openapi.Schema(
                                                                    type=openapi.TYPE_INTEGER, example=3),
                                                                "name": openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    example="Домашняя работа 1"),
                                                                'amount': openapi.Schema(
                                                                    type=openapi.TYPE_INTEGER, example=3),
                                                                "created_at": openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    example="2023-08-21 16:40:19.337147+03"),
                                                            }))

                                                })
get_all_answers_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                              properties={
                                                  'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                                  'title': openapi.Schema(type=openapi.TYPE_STRING,
                                                                          example="Домашняя работа 1"),
                                                  "answers": openapi.Schema(
                                                      type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(
                                                          type=openapi.TYPE_STRING)
                                                  ),
                                                  'max_score': openapi.Schema(
                                                      type=openapi.TYPE_INTEGER, example=100),
                                                  'color': openapi.Schema(
                                                      type=openapi.TYPE_STRING, example="#bfa0de"),
                                                  'students': openapi.Schema(
                                                      type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(
                                                          type=openapi.TYPE_OBJECT,
                                                          properties={
                                                              "id": openapi.Schema(
                                                                  type=openapi.TYPE_INTEGER, example=3),
                                                              'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                     example="Иван Иванов"),
                                                              'answers': openapi.Schema(
                                                                  type=openapi.TYPE_ARRAY,
                                                                  items=openapi.Schema(
                                                                      type=openapi.TYPE_STRING)
                                                              ),
                                                              'files': openapi.Schema(
                                                                  type=openapi.TYPE_ARRAY,
                                                                  items=openapi.Schema(
                                                                      type=openapi.TYPE_OBJECT,
                                                                      properties={
                                                                          "name": openapi.Schema(
                                                                              type=openapi.TYPE_STRING,
                                                                              example="Название файла"),
                                                                          "link": openapi.Schema(
                                                                              type=openapi.TYPE_STRING,
                                                                              example="Путь до файла"),
                                                                          "ext": openapi.Schema(
                                                                              type=openapi.TYPE_STRING,
                                                                              example="Расширение файла"),
                                                                      }
                                                                  )
                                                              ),
                                                              'score': openapi.Schema(
                                                                  type=openapi.TYPE_INTEGER, example=100),
                                                              'comment': openapi.Schema(
                                                                  type=openapi.TYPE_STRING,
                                                                  example="Комментарий от преподавателя"),
                                                              'checker': openapi.Schema(
                                                                  type=openapi.TYPE_STRING,
                                                                  example="Имя Фамилия преподавателя"),
                                                              'checked_at': openapi.Schema(type=openapi.TYPE_STRING, example=None),
                                                              'answered_at': openapi.Schema(type=openapi.TYPE_STRING, example="2023-09-08 17:21:45.279285+03"),
                                                              'added_at': openapi.Schema(type=openapi.TYPE_STRING, example="2023-09-08 17:21:45.279285+03"),
                                                              'row_color': openapi.Schema(type=openapi.TYPE_STRING, example=None),
                                                          }))})
create_homework_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_homework_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
add_to_homework_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
create_response_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
update_homework_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_from_homework_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
check_user_homework_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_file_from_homework_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
create_homework_responses = {200: create_homework_response_200}
delete_homework_responses = {200: delete_homework_response_200}
get_homework_responses = {200: get_homework_response_200}
get_user_homework_responses = {200: get_user_homework_response_200}
add_to_homework_responses = {200: add_to_homework_response_200}
delete_from_homework_responses = {200: delete_from_homework_response_200}
create_response_responses = {200: create_response_response_200}
update_homework_responses = {200: update_homework_response_200}
check_user_homework_responses = {200: check_user_homework_response_200}
get_my_homeworks_responses = {200: get_my_homeworks_response_200}
get_all_homeworks_responses = {200: get_all_homeworks_response_200}
get_all_answers_responses = {200: get_all_answers_response_200}
delete_file_from_homework_responses = {200: delete_file_from_homework_response_200}
