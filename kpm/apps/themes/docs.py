from drf_yasg import openapi

id_param = openapi.Parameter("id", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                             operation_description='ID темы.', example=1)
class_param = openapi.Parameter("class", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                operation_description='Класс учеников.', example=4)
get_themes_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                         properties={
                                             "themes": openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                      properties={
                                                                          "id": openapi.Schema(
                                                                              type=openapi.TYPE_INTEGER, example=3),
                                                                          "name": openapi.Schema(
                                                                              type=openapi.TYPE_STRING,
                                                                              example="Площадь"),
                                                                          "school_class": openapi.Schema(
                                                                              type=openapi.TYPE_INTEGER, example=4)
                                                                      })

                                         })
get_theme_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                        properties={
                                            "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=3),
                                            "name": openapi.Schema(type=openapi.TYPE_STRING, example="Площадь"),
                                            "school_class": openapi.Schema(type=openapi.TYPE_INTEGER, example=4)
                                        })
create_theme_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                           required=['name', 'class'],
                                           properties={
                                               'class': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                               'name': openapi.Schema(type=openapi.TYPE_STRING, example="Площадь")
                                           },
                                           operation_description='Создание темы')
create_theme_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_theme_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_themes_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
get_theme_responses = {200: get_theme_response_200}
get_themes_responses = {200: get_themes_response_200}
delete_themes_responses = {200: delete_themes_response_200}
delete_theme_responses = {200: delete_theme_response_200}
create_theme_responses = {200: create_theme_response_200}
