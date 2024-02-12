from drf_yasg import openapi

id_param = openapi.Parameter("id", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                             operation_description='ID рейтинга.', example=1)
user_param = openapi.Parameter("student", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                               operation_description='ID ученика.', example=1)
class_param = openapi.Parameter("class", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                operation_description='Класс учеников.', example=4)
create_rating_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                            required=['name', 'class'],
                                            properties={
                                                "name": openapi.Schema(
                                                    type=openapi.TYPE_STRING, example="Лига сентябрь"),
                                                "class": openapi.Schema(
                                                    type=openapi.TYPE_INTEGER, example=4),
                                                "type": openapi.Schema(
                                                    type=openapi.TYPE_INTEGER, example=0),
                                                "description": openapi.Schema(
                                                    type=openapi.TYPE_STRING, example="Описание рейтинга"),
                                            })
get_ratings_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                          properties={
                                              'ratings': openapi.Schema(
                                                  type=openapi.TYPE_ARRAY,
                                                  items=openapi.Schema(
                                                      type=openapi.TYPE_OBJECT,
                                                      properties={
                                                          'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                                          'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                 example="Лига сентябрь"),
                                                          'description': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                        example="Описание рейтинга"),
                                                          'type': openapi.Schema(type=openapi.TYPE_INTEGER, example=0),
                                                          'students': openapi.Schema(type=openapi.TYPE_INTEGER, example=35),
                                                      })),
                                          })
get_rating_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                         properties={
                                             'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                             'name': openapi.Schema(type=openapi.TYPE_STRING, example="Лига сентябрь"),
                                             'description': openapi.Schema(type=openapi.TYPE_STRING,
                                                                           example="Описание рейтинга"),
                                             'type': openapi.Schema(type=openapi.TYPE_INTEGER, example=0),
                                             'students': openapi.Schema(
                                                 type=openapi.TYPE_ARRAY,
                                                 items=openapi.Schema(
                                                     type=openapi.TYPE_OBJECT,
                                                     properties={
                                                         'id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                              example=2),
                                                         'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                example="Левин Михаил"),
                                                         'lvl': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                               example=3),
                                                         'exp': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                               example=59),
                                                         'base_exp': openapi.Schema(
                                                             type=openapi.TYPE_INTEGER,
                                                             example=60),
                                                         'total_exp': openapi.Schema(
                                                             type=openapi.TYPE_INTEGER,
                                                             example=164),
                                                     }))
                                         })
get_user_rating_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                              properties={
                                                  'id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                       example=1),
                                                  'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                         example="Лига сентябрь"),
                                                  'description': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                example="Описание рейтинга"),
                                                  'type': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                         example=0),
                                                  'students': openapi.Schema(
                                                      type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(
                                                          type=openapi.TYPE_OBJECT,
                                                          properties={
                                                              'id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                   example=1),
                                                              'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                     example="Левин Михаил"),
                                                              'lvl': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                    example=3),
                                                              'exp': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                    example=59),
                                                              'base_exp': openapi.Schema(
                                                                  type=openapi.TYPE_INTEGER,
                                                                  example=60),
                                                              'total_exp': openapi.Schema(
                                                                  type=openapi.TYPE_INTEGER,
                                                                  example=164),
                                                          }))
                                              })
get_user_ratings_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                               properties={
                                                   'ratings': openapi.Schema(
                                                       type=openapi.TYPE_ARRAY,
                                                       items=openapi.Schema(
                                                           type=openapi.TYPE_OBJECT,
                                                           properties={
                                                               'id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                    example=1),
                                                               'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                      example="Лига сентябрь"),
                                                               'description': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                             example="Описание рейтинга"),
                                                               'type': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                      example=0),
                                                           }))
                                               })
create_rating_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_rating_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_from_rating_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
add_to_rating_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
create_rating_responses = {200: create_rating_response_200}
delete_rating_responses = {200: delete_rating_response_200}
delete_from_rating_responses = {200: delete_from_rating_response_200}
add_to_rating_responses = {200: add_to_rating_response_200}
get_ratings_responses = {200: get_ratings_response_200}
get_rating_responses = {200: get_rating_response_200}
get_user_ratings_responses = {200: get_user_ratings_response_200}
get_user_rating_responses = {200: get_user_rating_response_200}
