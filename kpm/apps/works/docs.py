from drf_yasg import openapi

id_param = openapi.Parameter("id", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                             operation_description='ID работы.', example=1)
group_param = openapi.Parameter("group", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                operation_description='ID группы.', example=1)
work_param = openapi.Parameter("work", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
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
course_param = openapi.Parameter("course", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                 operation_description='ID курса.', example=1)

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
                                                  required=['id', 'student', 'grades'],
                                                  properties={
                                                      'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                                      'student': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                                      'grades': openapi.Schema(
                                                          type=openapi.TYPE_ARRAY,
                                                          items=openapi.Schema(
                                                              type=openapi.TYPE_OBJECT,
                                                              example=["5", "5", "5", "10", "15"])),
                                                      'comment': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                example="Комментарий преподавателя"),
                                                  },
                                                  operation_description='Проверка домашней работы(админка).')
check_user_individual_work_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                         required=['id', 'student', 'grades'],
                                                         properties={
                                                             'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                                             'student': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                       example=4),
                                                             'grades': openapi.Schema(
                                                                 type=openapi.TYPE_ARRAY,
                                                                 items=openapi.Schema(
                                                                     type=openapi.TYPE_OBJECT,
                                                                     example=["1", "1", "1", "1", "1"])),
                                                             'comment': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                       example="Комментарий преподавателя"),
                                                         },
                                                         operation_description='Проверка домашней работы(админка).')
return_user_homework_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                   required=['id', 'student', 'comment'],
                                                   properties={
                                                       'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                                       'student': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                                       'comment': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                 example="Комментарий преподавателя"),
                                                   },
                                                   operation_description='Вернуть домашнюю работу с комментарием(админка).')
return_user_individual_work_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                          required=['id', 'student', 'comment'],
                                                          properties={
                                                              'id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                   example=4),
                                                              'student': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                        example=4),
                                                              'comment': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                        example="Комментарий преподавателя"),
                                                          },
                                                          operation_description='Вернуть самостоятельную работу с комментарием(админка).')
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
                                                        "course": openapi.Schema(
                                                            type=openapi.TYPE_INTEGER, example=3),
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
                                               example=True),
                                           "groups": openapi.Schema(
                                               type=openapi.TYPE_ARRAY,
                                               items=openapi.Schema(
                                                   type=openapi.TYPE_OBJECT,
                                                   properties={
                                                       "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=3),
                                                       "name": openapi.Schema(type=openapi.TYPE_STRING,
                                                                              example="Название группы"),
                                                       "color": openapi.Schema(type=openapi.TYPE_STRING,
                                                                               example="#FFFFFF"),
                                                       "type": openapi.Schema(type=openapi.TYPE_INTEGER, example=3),
                                                       "date": openapi.Schema(type=openapi.TYPE_STRING, example=None),
                                                   })
                                           )
                                       })
get_homeworks_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                            properties={
                                                "id": openapi.Schema(
                                                    type=openapi.TYPE_INTEGER, example=3),
                                                "name": openapi.Schema(
                                                    type=openapi.TYPE_STRING,
                                                    example="Классная работа 1"),
                                                "course": openapi.Schema(
                                                    type=openapi.TYPE_INTEGER, example=3),
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
                                                    example=True),
                                                "amount": openapi.Schema(
                                                    type=openapi.TYPE_INTEGER,
                                                    example=25),
                                                "not_checked": openapi.Schema(
                                                    type=openapi.TYPE_INTEGER,
                                                    example=5),
                                            })
create_work_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                          required=['grades', 'name', 'class', 'type'],
                                          properties={
                                              'theme_id': openapi.Schema(type=openapi.TYPE_INTEGER, example=0),
                                              'class': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                              'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                     example="Домашняя работа 1"),
                                              'type': openapi.Schema(type=openapi.TYPE_INTEGER, example=0),
                                              'course': openapi.Schema(type=openapi.TYPE_INTEGER, example=0),
                                              "grades": openapi.Schema(type=openapi.TYPE_ARRAY,
                                                                       items=openapi.TYPE_STRING,
                                                                       example=["5", "5", "5", "10", "15"]),
                                              "has_attachments": openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                                example=True),
                                              "text": openapi.Schema(type=openapi.TYPE_STRING,
                                                                     example="Описание работы."),
                                              "exercises": openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                          example=11),
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
set_homework_date_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                required=['group', 'work', 'date'],
                                                properties={
                                                    'group': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                                    'work': openapi.Schema(type=openapi.TYPE_INTEGER, example=2),
                                                    'date': openapi.Schema(type=openapi.TYPE_STRING,
                                                                           example='01.01.2024'),
                                                },
                                                operation_description='Установка даты проведения домашней работы для группы.')
set_individual_work_date_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                       required=['group', 'work', 'date'],
                                                       properties={
                                                           'group': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                   example=1),
                                                           'work': openapi.Schema(type=openapi.TYPE_INTEGER, example=2),
                                                           'date': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                  example='01.01.2024'),
                                                       },
                                                       operation_description='Установка даты проведения самостоятельной работы для группы.')
insert_classwork_grade_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                     required=['work', 'user', 'cell', 'value'],
                                                     properties={
                                                         'work': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                example=1),
                                                         'user': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                example=1),
                                                         'cell': openapi.Schema(type=openapi.TYPE_INTEGER, example=2),
                                                         'value': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                                 example=True),
                                                     },
                                                     operation_description='Установка оценки за номер в классной работе.')
get_user_homework_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                properties={
                                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                                    'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                           example="Домашняя работа 1"),
                                                    'user_name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                example="Иван Иванов"),
                                                    'course': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                                    'text': openapi.Schema(type=openapi.TYPE_STRING,
                                                                           example="Условие домашней работы"),
                                                    'fields': openapi.Schema(type=openapi.TYPE_INTEGER, example=6),
                                                    'status': openapi.Schema(type=openapi.TYPE_INTEGER, example=0),
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
                                                    'user_grades': openapi.Schema(
                                                        type=openapi.TYPE_ARRAY,
                                                        items=openapi.Schema(
                                                            type=openapi.TYPE_STRING)),
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
                                                    'score': openapi.Schema(type=openapi.TYPE_INTEGER, example=85),
                                                    'max_score': openapi.Schema(type=openapi.TYPE_INTEGER, example=125),
                                                    'green': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                                    'blue': openapi.Schema(type=openapi.TYPE_INTEGER, example=2),
                                                },
                                                operation_description='Получение домашней работы(пользователь).')
get_user_individual_work_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                       properties={
                                                           'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                                           'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                  example="Блиц 1"),
                                                           'user_name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                       example="Иван Иванов"),
                                                           'course': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                    example=4),
                                                           'text': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                  example="Условие блица"),
                                                           'fields': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                    example=6),
                                                           'status': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                    example=0),
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
                                                           'class': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                   example=4),
                                                           'is_done': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                                     example=True),
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
                                                           'user_grades': openapi.Schema(
                                                               type=openapi.TYPE_ARRAY,
                                                               items=openapi.Schema(
                                                                   type=openapi.TYPE_STRING)),
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
                                                           'score': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                   example=85),
                                                           'max_score': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                       example=125),
                                                           'green': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                   example=1),
                                                           'blue': openapi.Schema(type=openapi.TYPE_INTEGER, example=2),
                                                       },
                                                       operation_description='Получение индивидуальной работы(пользователь).')
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
                                                               "fields": openapi.Schema(
                                                                   type=openapi.TYPE_INTEGER, example=3),
                                                               "status": openapi.Schema(
                                                                   type=openapi.TYPE_INTEGER, example=0),
                                                               "course": openapi.Schema(
                                                                   type=openapi.TYPE_INTEGER, example=0),
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
                                                               'blue': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                      example=0),
                                                               'green': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                       example=3),
                                                           }))})
get_my_individual_works_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
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
                                                                          example="Блиц 1"),
                                                                      "fields": openapi.Schema(
                                                                          type=openapi.TYPE_INTEGER, example=3),
                                                                      "status": openapi.Schema(
                                                                          type=openapi.TYPE_INTEGER, example=0),
                                                                      "course": openapi.Schema(
                                                                          type=openapi.TYPE_INTEGER, example=0),
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
                                                                      'blue': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                             example=0),
                                                                      'green': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                              example=3),
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
                                                                "course": openapi.Schema(
                                                                    type=openapi.TYPE_INTEGER,
                                                                    example=0),
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
                                                                  "group_type": openapi.Schema(
                                                                      type=openapi.TYPE_INTEGER,
                                                                      example=1),
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
get_homeworks_dates_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                  properties={
                                                      "groups_works_dates": openapi.Schema(
                                                          type=openapi.TYPE_ARRAY,
                                                          items=openapi.Schema(
                                                              type=openapi.TYPE_OBJECT,
                                                              properties={
                                                                  "group_id": openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                             example=1),
                                                                  "work_id": openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                            example=2),
                                                                  "date": openapi.Schema(type=openapi.TYPE_STRING,
                                                                                         example='01.01.2024'),
                                                              }
                                                          )
                                                      )
                                                  })
get_individual_works_dates_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                         properties={
                                                             "groups_works_dates": openapi.Schema(
                                                                 type=openapi.TYPE_ARRAY,
                                                                 items=openapi.Schema(
                                                                     type=openapi.TYPE_OBJECT,
                                                                     properties={
                                                                         "group_id": openapi.Schema(
                                                                             type=openapi.TYPE_INTEGER,
                                                                             example=1),
                                                                         "work_id": openapi.Schema(
                                                                             type=openapi.TYPE_INTEGER,
                                                                             example=2),
                                                                         "date": openapi.Schema(
                                                                             type=openapi.TYPE_STRING,
                                                                             example='01.01.2024'),
                                                                     }
                                                                 )
                                                             )
                                                         })
get_all_answers_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                              properties={
                                                  'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                                  'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                         example="Домашняя работа 1"),
                                                  "answers": openapi.Schema(
                                                      type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(
                                                          type=openapi.TYPE_STRING)
                                                  ),
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
                                                                      type=openapi.TYPE_STRING, example=["1", "2", "3"])
                                                              ),
                                                              'groups': openapi.Schema(
                                                                  type=openapi.TYPE_ARRAY,
                                                                  items=openapi.Schema(
                                                                      type=openapi.TYPE_OBJECT,
                                                                      properties={
                                                                          "id": openapi.Schema(
                                                                              type=openapi.TYPE_INTEGER,
                                                                              example=1),
                                                                          "name": openapi.Schema(
                                                                              type=openapi.TYPE_STRING,
                                                                              example="Группа 1"),
                                                                          "color": openapi.Schema(
                                                                              type=openapi.TYPE_STRING,
                                                                              example="#FFFFFF"),
                                                                          "type": openapi.Schema(
                                                                              type=openapi.TYPE_INTEGER,
                                                                              example=1),
                                                                      }
                                                                  )
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
                                                                  type=openapi.TYPE_INTEGER, example=80),
                                                              'max_score': openapi.Schema(
                                                                  type=openapi.TYPE_INTEGER, example=125),
                                                              'comment': openapi.Schema(
                                                                  type=openapi.TYPE_STRING,
                                                                  example="Комментарий от преподавателя"),
                                                              'checker': openapi.Schema(
                                                                  type=openapi.TYPE_STRING,
                                                                  example="Имя Фамилия преподавателя"),
                                                              'checked_at': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                           example=None),
                                                              'is_done': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                                        example=True),
                                                              'is_checked': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                                           example=True),
                                                              'is_closed': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                                          example=True),
                                                              'green': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                      example=1),
                                                              'blue': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                     example=2),
                                                              'answered_at': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                            example="2023-09-08 17:21:45.279285+03"),
                                                              'added_at': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                         example="2023-09-08 17:21:45.279285+03"),
                                                          }))})
get_all_answers_individuals_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                          properties={
                                                              'id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                   example=4),
                                                              'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                     example="Домашняя работа 1"),
                                                              "answers": openapi.Schema(
                                                                  type=openapi.TYPE_ARRAY,
                                                                  items=openapi.Schema(
                                                                      type=openapi.TYPE_STRING)
                                                              ),
                                                              'students': openapi.Schema(
                                                                  type=openapi.TYPE_ARRAY,
                                                                  items=openapi.Schema(
                                                                      type=openapi.TYPE_OBJECT,
                                                                      properties={
                                                                          "id": openapi.Schema(
                                                                              type=openapi.TYPE_INTEGER, example=3),
                                                                          'name': openapi.Schema(
                                                                              type=openapi.TYPE_STRING,
                                                                              example="Иван Иванов"),
                                                                          'answers': openapi.Schema(
                                                                              type=openapi.TYPE_ARRAY,
                                                                              items=openapi.Schema(
                                                                                  type=openapi.TYPE_STRING,
                                                                                  example=["1", "2", "3"])
                                                                          ),
                                                                          'groups': openapi.Schema(
                                                                              type=openapi.TYPE_ARRAY,
                                                                              items=openapi.Schema(
                                                                                  type=openapi.TYPE_OBJECT,
                                                                                  properties={
                                                                                      "id": openapi.Schema(
                                                                                          type=openapi.TYPE_INTEGER,
                                                                                          example=1),
                                                                                      "name": openapi.Schema(
                                                                                          type=openapi.TYPE_STRING,
                                                                                          example="Группа 1"),
                                                                                      "color": openapi.Schema(
                                                                                          type=openapi.TYPE_STRING,
                                                                                          example="#FFFFFF"),
                                                                                      "type": openapi.Schema(
                                                                                          type=openapi.TYPE_INTEGER,
                                                                                          example=1),
                                                                                  }
                                                                              )
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
                                                                              type=openapi.TYPE_INTEGER, example=80),
                                                                          'max_score': openapi.Schema(
                                                                              type=openapi.TYPE_INTEGER, example=125),
                                                                          'comment': openapi.Schema(
                                                                              type=openapi.TYPE_STRING,
                                                                              example="Комментарий от преподавателя"),
                                                                          'checker': openapi.Schema(
                                                                              type=openapi.TYPE_STRING,
                                                                              example="Имя Фамилия преподавателя"),
                                                                          'checked_at': openapi.Schema(
                                                                              type=openapi.TYPE_STRING,
                                                                              example=None),
                                                                          'is_done': openapi.Schema(
                                                                              type=openapi.TYPE_BOOLEAN,
                                                                              example=True),
                                                                          'is_checked': openapi.Schema(
                                                                              type=openapi.TYPE_BOOLEAN,
                                                                              example=True),
                                                                          'is_closed': openapi.Schema(
                                                                              type=openapi.TYPE_BOOLEAN,
                                                                              example=True),
                                                                          'green': openapi.Schema(
                                                                              type=openapi.TYPE_INTEGER,
                                                                              example=1),
                                                                          'blue': openapi.Schema(
                                                                              type=openapi.TYPE_INTEGER,
                                                                              example=2),
                                                                          'answered_at': openapi.Schema(
                                                                              type=openapi.TYPE_STRING,
                                                                              example="2023-09-08 17:21:45.279285+03"),
                                                                          'added_at': openapi.Schema(
                                                                              type=openapi.TYPE_STRING,
                                                                              example="2023-09-08 17:21:45.279285+03"),
                                                                      }))})
get_all_individual_works_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
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
                                                                           example="Зачет 1"),
                                                                       "course": openapi.Schema(
                                                                           type=openapi.TYPE_INTEGER, example=3),
                                                                       "grades": openapi.Schema(
                                                                           type=openapi.TYPE_ARRAY,
                                                                           items=openapi.Schema(
                                                                               type=openapi.TYPE_OBJECT,
                                                                               example=["1", "1", "1", "1", "1"])),
                                                                       "max_score": openapi.Schema(
                                                                           type=openapi.TYPE_INTEGER, example=5),
                                                                       "exercises": openapi.Schema(
                                                                           type=openapi.TYPE_INTEGER, example=5),
                                                                       "type": openapi.Schema(
                                                                           type=openapi.TYPE_INTEGER, example=0),
                                                                       "is_homework": openapi.Schema(
                                                                           type=openapi.TYPE_BOOLEAN,
                                                                           example=True)
                                                                   }))

                                                       })
get_classwork_grades_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                   properties={
                                                       "fields": openapi.Schema(type=openapi.TYPE_INTEGER, example=6),
                                                       "students": openapi.Schema(
                                                           type=openapi.TYPE_ARRAY,
                                                           items=openapi.Schema(
                                                               type=openapi.TYPE_OBJECT,
                                                               properties={
                                                                   "id": openapi.Schema(
                                                                       type=openapi.TYPE_INTEGER, example=3),
                                                                   "name": openapi.Schema(
                                                                       type=openapi.TYPE_STRING,
                                                                       example="Иван Иванов"),
                                                                   "grades": openapi.Schema(
                                                                       type=openapi.TYPE_ARRAY,
                                                                       items=openapi.Schema(
                                                                           type=openapi.TYPE_BOOLEAN,
                                                                           example=[True, True, True, True, True,
                                                                                    False]))
                                                               }))

                                                   })
create_work_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_work_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
update_work_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_file_from_homework_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
add_to_homework_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
add_to_individual_work_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_from_homework_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_from_individual_work_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
create_response_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
check_user_homework_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
check_user_individual_work_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
apply_files_to_classwork_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_file_from_classwork_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
set_homework_date_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
set_individual_work_date_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_homework_date_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_individual_work_date_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
return_user_homework_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
return_user_individual_work_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
insert_classwork_grade_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
get_works_responses = {200: get_works_response_200}
get_work_responses = {200: get_work_response_200}
create_work_responses = {200: create_work_response_200}
delete_work_responses = {200: delete_work_response_200}
update_work_responses = {200: update_work_response_200}
delete_file_from_homework_responses = {200: delete_file_from_homework_response_200}
add_to_homework_responses = {200: add_to_homework_response_200}
add_to_individual_work_responses = {200: add_to_individual_work_response_200}
delete_from_homework_responses = {200: delete_from_homework_response_200}
delete_from_individual_work_responses = {200: delete_from_individual_work_response_200}
get_user_individual_work_responses = {200: get_user_individual_work_response_200}
get_user_homework_responses = {200: get_user_homework_response_200}
create_response_responses = {200: create_response_response_200}
check_user_homework_responses = {200: check_user_homework_response_200}
check_user_individual_work_responses = {200: check_user_individual_work_response_200}
get_my_individual_works_responses = {200: get_my_individual_works_response_200}
get_my_homeworks_responses = {200: get_my_homeworks_response_200}
get_my_classworks_responses = {200: get_my_classworks_response_200}
apply_files_to_classwork_responses = {200: apply_files_to_classwork_response_200}
delete_file_from_classwork_responses = {200: delete_file_from_classwork_response_200}
get_classwork_files_responses = {200: get_classwork_files_response_200}
set_homework_date_responses = {200: set_homework_date_response_200}
set_individual_work_date_responses = {200: set_individual_work_date_response_200}
delete_homework_date_responses = {200: delete_homework_date_response_200}
delete_individual_work_date_responses = {200: delete_individual_work_date_response_200}
get_homeworks_dates_responses = {200: get_homeworks_dates_response_200}
get_individual_works_dates_responses = {200: get_individual_works_dates_response_200}
get_homeworks_responses = {200: get_homeworks_response_200}
return_user_homework_responses = {200: return_user_homework_response_200}
return_user_individual_work_responses = {200: return_user_individual_work_response_200}
get_all_answers_responses = {200: get_all_answers_response_200}
get_all_answers_individuals_responses = {200: get_all_answers_individuals_response_200}
get_all_individual_works_responses = {200: get_all_individual_works_response_200}
get_classwork_grades_responses = {200: get_classwork_grades_response_200}
insert_classwork_grade_responses = {200: insert_classwork_grade_response_200}
operation_description = "Type: 0 - Домашняя работа, 1 - Классная работа, 2 - Блиц, 3 - Письменный экзамен классный, 4 - Устный экзамен классный, 5 - Письменный экзамен домашний, 6 - Устный экзамен домашний, 7 - Письменный экзамен домашний(баллы 2007), 7 - Письменный экзамен классный(баллы 2007), 9 - Вне статистики, 10 - Зачет, 11 - Проверка на рептилоида"
