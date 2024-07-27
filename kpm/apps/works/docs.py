from drf_yasg import openapi

id_param = openapi.Parameter("id", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                             operation_description='ID работы.', example=1)
class_param = openapi.Parameter("class", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                operation_description='Класс учеников.', example=4)
theme_param = openapi.Parameter("theme", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                operation_description='ID темы.', example=4)
type_param = openapi.Parameter("type", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                               operation_description='Тип работы', example=4)
file_param = openapi.Parameter("file", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                               operation_description='ID файла.', example=1)
student_param = openapi.Parameter("student", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                  operation_description='ID ученика.', example=1)

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
                                                  required=['id', 'student'],
                                                  properties={
                                                      'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                                      'student': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                                      'value': openapi.Schema(type=openapi.TYPE_STRING, example='-'),
                                                      'cell': openapi.Schema(type=openapi.TYPE_INTEGER, example=0),
                                                      'comment': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                example="Комментарий преподавателя"),
                                                  },
                                                  operation_description='Проверка домашней работы(админка).')
apply_files_to_classwork_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                       required=['group', 'work', 'files'],
                                                       properties={
                                                           'group': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                   example=4),
                                                           'work': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                                           'files': openapi.Schema(
                                                               type=openapi.TYPE_ARRAY,
                                                               items=openapi.Schema(
                                                                   type=openapi.TYPE_FILE
                                                               )
                                                           ),
                                                       },
                                                       operation_description='Отправление файла классной работы для группы(FormData).')

get_works_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                        properties={
                                            "works": openapi.Schema(
                                                type=openapi.TYPE_ARRAY,
                                                items=openapi.Schema(
                                                    type=openapi.TYPE_OBJECT,
                                                    properties={
                                                        "id": openapi.Schema(
                                                            type=openapi.TYPE_INTEGER, example=3),
                                                        "name": openapi.Schema(
                                                            type=openapi.TYPE_STRING,
                                                            example="Классная работа 1"),
                                                        "grades": openapi.Schema(
                                                            type=openapi.TYPE_ARRAY,
                                                            items=openapi.Schema(
                                                                type=openapi.TYPE_OBJECT,
                                                                example=["5", "5", "5", "10", "15"])),
                                                        "max_score": openapi.Schema(
                                                            type=openapi.TYPE_INTEGER, example=40),
                                                        "exercises": openapi.Schema(
                                                            type=openapi.TYPE_INTEGER, example=5),
                                                        "theme_id": openapi.Schema(
                                                            type=openapi.TYPE_INTEGER, example=1),
                                                        "theme_name": openapi.Schema(
                                                            type=openapi.TYPE_STRING,
                                                            example="Площадь"),
                                                        "type": openapi.Schema(
                                                            type=openapi.TYPE_INTEGER, example=0),
                                                        "is_homework": openapi.Schema(
                                                            type=openapi.TYPE_BOOLEAN,
                                                            example=True)
                                                    }))

                                        })
get_work_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                       properties={
                                           "id": openapi.Schema(
                                               type=openapi.TYPE_INTEGER, example=3),
                                           "name": openapi.Schema(
                                               type=openapi.TYPE_STRING,
                                               example="Классная работа 1"),
                                           "grades": openapi.Schema(
                                               type=openapi.TYPE_ARRAY,
                                               items=openapi.Schema(
                                                   type=openapi.TYPE_OBJECT,
                                                   example=["5", "5", "5", "10", "15"])),
                                           "max_score": openapi.Schema(
                                               type=openapi.TYPE_INTEGER, example=40),
                                           "exercises": openapi.Schema(
                                               type=openapi.TYPE_INTEGER, example=5),
                                           "theme_id": openapi.Schema(
                                               type=openapi.TYPE_INTEGER, example=1),
                                           "theme_name": openapi.Schema(
                                               type=openapi.TYPE_STRING, example="Площадь"),
                                           "type": openapi.Schema(
                                               type=openapi.TYPE_INTEGER, example=0),
                                           "is_homework": openapi.Schema(
                                               type=openapi.TYPE_BOOLEAN,
                                               example=True)

                                       })
create_work_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                          required=['grades', 'name', 'theme_id', 'class', 'type'],
                                          properties={
                                              'theme_id': openapi.Schema(type=openapi.TYPE_INTEGER, example=0),
                                              'class': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                              'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                     example="Домашняя работа 1"),
                                              'type': openapi.Schema(type=openapi.TYPE_INTEGER, example=0),
                                              "grades": openapi.Schema(type=openapi.TYPE_ARRAY,
                                                                       items=openapi.TYPE_STRING,
                                                                       example=["5", "5", "5", "10", "15"]),
                                              "has_attachments": openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                                example=True),
                                              "text": openapi.Schema(type=openapi.TYPE_STRING,
                                                                     example="Описание работы."),
                                              "answers": openapi.Schema(type=openapi.TYPE_ARRAY,
                                                                        items=openapi.TYPE_STRING,
                                                                        example=["Ответ1", "Ответ2", "Ответ3", "Ответ4",
                                                                                 "Ответ5"]),
                                              "files": openapi.Schema(type=openapi.TYPE_ARRAY,
                                                                      items=openapi.TYPE_STRING,
                                                                      example=["File1", "File2"]),
                                          },
                                          operation_description='Создание работы.')
update_work_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                          required=['id'],
                                          properties={
                                              'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                              'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                     example="Классная работа 1"),
                                              "grades": openapi.Schema(
                                                  type=openapi.TYPE_ARRAY,
                                                  items=openapi.Schema(type=openapi.TYPE_STRING),
                                                  example=["5", "5", "5", "10", "15"]),
                                              "has_attachments": openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                                example=True),
                                              "text": openapi.Schema(type=openapi.TYPE_STRING,
                                                                     example="Описание работы."),
                                              "answers": openapi.Schema(type=openapi.TYPE_ARRAY,
                                                                        items=openapi.TYPE_STRING,
                                                                        example=["Ответ1", "Ответ2", "Ответ3", "Ответ4",
                                                                                 "Ответ5"]),
                                              "files": openapi.Schema(type=openapi.TYPE_ARRAY,
                                                                      items=openapi.TYPE_STRING,
                                                                      example=["File1", "File2"]),
                                          },
                                          operation_description='Изменение работы.')
set_homeworks_dates_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                  required=['groups'],
                                                  properties={
                                                      "groups": openapi.Schema(
                                                          type=openapi.TYPE_ARRAY,
                                                          items=openapi.Schema(
                                                              type=openapi.TYPE_OBJECT,
                                                              required=['group_id', 'work_dates'],
                                                              properties={
                                                                  "group_id": openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                             example=1),
                                                                  "work_dates": openapi.Schema(
                                                                      type=openapi.TYPE_ARRAY,
                                                                      items=openapi.Schema(
                                                                          type=openapi.TYPE_OBJECT,
                                                                          properties={
                                                                              "work_id": openapi.Schema(
                                                                                  type=openapi.TYPE_INTEGER,
                                                                                  example=1),
                                                                              "date": openapi.Schema(
                                                                                  type=openapi.TYPE_STRING,
                                                                                  example="2024-01-01"),
                                                                          }
                                                                      ),
                                                                  )
                                                              }
                                                          ))
                                                  },
                                                  operation_description='Установка дат проведения домашних работ.')

get_user_homework_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                properties={
                                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                                    'name': openapi.Schema(type=openapi.TYPE_STRING,
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
                                                           }))})
get_my_classworks_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                properties={
                                                    "classworks": openapi.Schema(
                                                        type=openapi.TYPE_ARRAY,
                                                        items=openapi.Schema(
                                                            type=openapi.TYPE_OBJECT,
                                                            properties={
                                                                "name": openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    example="Классная работа 1"),
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
                                                            }))})
get_classwork_files_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                  properties={
                                                      "groups": openapi.Schema(
                                                          type=openapi.TYPE_ARRAY,
                                                          items=openapi.Schema(
                                                              type=openapi.TYPE_OBJECT,
                                                              properties={
                                                                  "group_id": openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                             example=1),
                                                                  "group_name": openapi.Schema(
                                                                      type=openapi.TYPE_STRING,
                                                                      example="Группа 1"),
                                                                  "group_marker": openapi.Schema(
                                                                      type=openapi.TYPE_STRING,
                                                                      example="#FFFFFF"),
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
                                                              }))})
create_work_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_work_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
update_work_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_file_from_homework_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
add_to_homework_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_from_homework_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
create_response_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
check_user_homework_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
apply_files_to_classwork_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_file_from_classwork_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
set_homeworks_dates_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
get_works_responses = {200: get_works_response_200}
get_work_responses = {200: get_work_response_200}
create_work_responses = {200: create_work_response_200}
delete_work_responses = {200: delete_work_response_200}
update_work_responses = {200: update_work_response_200}
delete_file_from_homework_responses = {200: delete_file_from_homework_response_200}
add_to_homework_responses = {200: add_to_homework_response_200}
delete_from_homework_responses = {200: delete_from_homework_response_200}
get_user_homework_responses = {200: get_user_homework_response_200}
create_response_responses = {200: create_response_response_200}
check_user_homework_responses = {200: check_user_homework_response_200}
get_my_homeworks_responses = {200: get_my_homeworks_response_200}
get_my_classworks_responses = {200: get_my_classworks_response_200}
apply_files_to_classwork_responses = {200: apply_files_to_classwork_response_200}
delete_file_from_classwork_responses = {200: delete_file_from_classwork_response_200}
get_classwork_files_responses = {200: get_classwork_files_response_200}
set_homeworks_dates_responses = {200: set_homeworks_dates_response_200}
operation_description = "Type: 0 - Домашняя работа, 1 - Классная работа, 2 - Блиц, 3 - Письменный экзамен, 4 - Устный экзамен, 5 - Письменный экзамен дз, 6 - Устный экзамен дз, 7 - Письменный экзамен дз(баллы 2007), 8 - Вне статистики"
