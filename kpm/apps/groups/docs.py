from drf_yasg import openapi

id_group_param = openapi.Parameter("id", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                   operation_description='ID группы.', example=1)
class_param = openapi.Parameter("class", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                operation_description='Класс учеников.', example=4)

create_group_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                           required=['name', 'class'],
                                           properties={
                                               'name': openapi.Schema(type=openapi.TYPE_STRING, example="Группа1"),
                                               'class': openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                               'marker': openapi.Schema(type=openapi.TYPE_INTEGER, example=0),
                                               'students': openapi.Schema(
                                                   type=openapi.TYPE_ARRAY,
                                                   items=openapi.Schema(
                                                       type=openapi.TYPE_INTEGER,
                                                       example=2)),
                                           },
                                           operation_description='Создание группы')
add_to_group_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                           required=['id', 'students'],
                                           properties={
                                               "id": openapi.Schema(
                                                   type=openapi.TYPE_INTEGER, example=4),
                                               'students': openapi.Schema(
                                                   type=openapi.TYPE_ARRAY,
                                                   items=openapi.Schema(
                                                       type=openapi.TYPE_INTEGER,
                                                       example=2)),
                                           })
delete_from_group_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                required=['students'],
                                                properties={
                                                    'students': openapi.Schema(
                                                        type=openapi.TYPE_ARRAY,
                                                        items=openapi.Schema(
                                                            type=openapi.TYPE_INTEGER,
                                                            example=2)),
                                                })
update_group_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                           required=['id'],
                                           properties={
                                               'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=2),
                                               'name': openapi.Schema(type=openapi.TYPE_STRING, example="Группа1"),
                                               'marker': openapi.Schema(type=openapi.TYPE_INTEGER, example=0),
                                               'students': openapi.Schema(
                                                   type=openapi.TYPE_ARRAY,
                                                   items=openapi.Schema(
                                                       type=openapi.TYPE_INTEGER,
                                                       example=2)),
                                           },
                                           operation_description='Обновление группы')

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
get_group_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                        properties={
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
                                        })

create_group_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_group_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
add_to_group_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_from_group_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
update_group_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
create_group_responses = {200: create_group_response_200}
update_group_responses = {200: update_group_response_200}
delete_group_responses = {200: delete_group_response_200}
add_to_group_responses = {200: add_to_group_response_200}
delete_from_group_responses = {200: delete_from_group_response_200}
get_groups_responses = {200: get_groups_response_200}
get_group_responses = {200: get_group_response_200}