from drf_yasg import openapi

id_param = openapi.Parameter("id", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                             operation_description='ID сообщения.', example=1)
id_user_param = openapi.Parameter("id", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                  operation_description='ID ученика.', example=1)
send_message_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                           required=['user_to', 'text'],
                                           properties={
                                               "user_to": [1, 2, 3, 4, 5],
                                               "title": openapi.Schema(type=openapi.TYPE_STRING,
                                                                       example='Тема сообщения'),
                                               "text": openapi.Schema(type=openapi.TYPE_STRING,
                                                                      example='Текст сообщения'),
                                           })
get_message_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                          properties={
                                              "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                              'user_to': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                        example=1),
                                              'user_to_name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                             example="Имя Фамилия"),
                                              'user_from': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                          example=2),
                                              'user_from_name': openapi.Schema(
                                                  type=openapi.TYPE_STRING,
                                                  example="Имя Фамилия"),
                                              'title': openapi.Schema(type=openapi.TYPE_STRING,
                                                                      example="Тема сообщения"),
                                              'text': openapi.Schema(type=openapi.TYPE_STRING,
                                                                     example="Текст сообщения"),
                                              'is_viewed': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                                              'viewed_at': openapi.Schema(type=openapi.TYPE_STRING,
                                                                          example="2023-08-14 16:33:11.402593+03"),
                                              'datetime': openapi.Schema(type=openapi.FORMAT_DATETIME,
                                                                         example="2023-03-31 17:31:59.612927+03"),
                                              'files': openapi.Schema(
                                                  type=openapi.TYPE_ARRAY,
                                                  items=openapi.Schema(
                                                      type=openapi.TYPE_STRING)
                                              ),
                                          })
get_messages_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                           properties={
                                               "messages": openapi.Schema(
                                                   type=openapi.TYPE_ARRAY,
                                                   items=openapi.Schema(
                                                       type=openapi.TYPE_OBJECT,
                                                       properties=
                                                       {
                                                           "id": openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                example=1),
                                                           'user_to': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                     example=1),
                                                           'user_to_name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                          example="Имя Фамилия"),
                                                           'user_from': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                       example=2),
                                                           'user_from_name': openapi.Schema(
                                                               type=openapi.TYPE_STRING,
                                                               example="Имя Фамилия"),
                                                           "title": openapi.Schema(type=openapi.TYPE_STRING,
                                                                                   example='Тема сообщения'),
                                                           'text': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                  example="Текст сообщения"),
                                                           'is_viewed': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                                       example=False),
                                                           'viewed_at': openapi.Schema(
                                                               type=openapi.TYPE_STRING,
                                                               example="2023-08-14 16:33:11.402593+03"),
                                                           'datetime': openapi.Schema(type=openapi.FORMAT_DATETIME,
                                                                                      example="2023-03-31 17:31:59.612927+03"),
                                                       }
                                                   )),
                                           })

get_sent_messages_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                properties={
                                                    "messages": openapi.Schema(
                                                        type=openapi.TYPE_ARRAY,
                                                        items=openapi.Schema(
                                                            type=openapi.TYPE_OBJECT,
                                                            properties=
                                                            {
                                                                "id": openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                     example=1),
                                                                'user_from': openapi.Schema(
                                                                    type=openapi.TYPE_INTEGER,
                                                                    example=2),
                                                                'user_from_name': openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    example="Имя Фамилия"),
                                                                "title": openapi.Schema(type=openapi.TYPE_STRING,
                                                                                        example='Тема сообщения'),
                                                                'text': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                       example="Текст сообщения"),
                                                                'is_viewed': openapi.Schema(
                                                                    type=openapi.TYPE_BOOLEAN,
                                                                    example=False),
                                                                'datetime': openapi.Schema(
                                                                    type=openapi.FORMAT_DATETIME,
                                                                    example="2023-03-31 17:31:59.612927+03"),
                                                                'recipients': openapi.Schema(
                                                                    type=openapi.TYPE_ARRAY,
                                                                    items=openapi.Schema(
                                                                        type=openapi.TYPE_OBJECT,
                                                                        properties=
                                                                        {
                                                                            'user_to': openapi.Schema(
                                                                                type=openapi.TYPE_INTEGER,
                                                                                example=1),
                                                                            'user_to_name': openapi.Schema(
                                                                                type=openapi.TYPE_STRING,
                                                                                example="Имя Фамилия"),
                                                                            'is_viewed': openapi.Schema(
                                                                                type=openapi.TYPE_BOOLEAN,
                                                                                example=False),
                                                                            'viewed_at': openapi.Schema(
                                                                                type=openapi.TYPE_STRING,
                                                                                example="2023-08-14 16:33:11.402593+03"),
                                                                        })),
                                                                'files': openapi.Schema(
                                                                    type=openapi.TYPE_ARRAY,
                                                                    items=openapi.Schema(
                                                                        type=openapi.TYPE_STRING)
                                                                ),
                                                            }
                                                        )),
                                                })

read_message_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
read_message_responses = {200: read_message_response_200}
send_message_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
send_message_responses = {200: send_message_response_200}
get_message_responses = {200: get_message_response_200}
get_messages_responses = {200: get_messages_response_200}
get_sent_messages_responses = {200: get_sent_messages_response_200}
delete_message_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_message_responses = {200: delete_message_response_200}
