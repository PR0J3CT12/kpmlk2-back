from drf_yasg import openapi

id_param = openapi.Parameter("id", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                             operation_description='ID работы.', example=1)
class_param = openapi.Parameter("class", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                operation_description='Класс учеников.', example=4)
theme_param = openapi.Parameter("theme", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                operation_description='ID темы.', example=4)
type_param = openapi.Parameter("type", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                               operation_description='Тип работы', example=4)
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
                                                                     example="Классная работа 1"),
                                              'type': openapi.Schema(type=openapi.TYPE_INTEGER, example=0),
                                              "grades": ["5", "5", "5", "10", "15"],
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
                                                  items=openapi.Schema(
                                                      type=openapi.TYPE_OBJECT,
                                                      example=["5", "5", "5", "10", "15"])),
                                          },
                                          operation_description='Изменение работы.')
create_work_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_work_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
update_work_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
get_works_responses = {200: get_works_response_200}
get_work_responses = {200: get_work_response_200}
create_work_responses = {200: create_work_response_200}
delete_work_responses = {200: delete_work_response_200}
update_work_responses = {200: update_work_response_200}
operation_description = "Type: 0 - Домашняя работа, 1 - Классная работа, 2 - Блиц, 3 - Письменный экзамен, 4 - Устный экзамен, 5 - Письменный экзамен дз, 6 - Устный экзамен дз, 7 - Письменный экзамен дз(баллы 2007), 8 - Вне статистики"
