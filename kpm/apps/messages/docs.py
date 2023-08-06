from drf_yasg import openapi

id_param = openapi.Parameter("id", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                             operation_description='ID сообщения.', example=1)
id_user_param = openapi.Parameter("id", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                  operation_description='ID ученика.', example=1)
send_message_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                           required=['user_to', 'text'],
                                           properties={
                                               "user_to": openapi.Schema(
                                                   type=openapi.TYPE_INTEGER, example=1),
                                               "text": openapi.Schema(
                                                   type=openapi.TYPE_STRING, example='Текст сообщения'),
                                           })
get_message_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                          properties={
                                              "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                              'user_to': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                              'user_from': openapi.Schema(type=openapi.TYPE_INTEGER, example=2),
                                              'text': openapi.Schema(type=openapi.TYPE_STRING,
                                                                     example="Текст сообщения"),
                                              'is_viewed': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                                              'datetime': openapi.Schema(type=openapi.FORMAT_DATETIME,
                                                                         example="2023-03-31 17:31:59.612927+03"),
                                          })
get_messages_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                           properties={
                                               "messages": openapi.Schema(
                                                   type=openapi.TYPE_ARRAY,
                                                   items=openapi.Schema(
                                                       type=openapi.TYPE_OBJECT,
                                                       example=[
                                                           {
                                                               "id": 1,
                                                               'user_to': 1,
                                                               'user_from': 2,
                                                               'text': "Текст сообщения",
                                                               'is_viewed': False,
                                                               'datetime': "2023-03-31 17:31:59.612927+03",
                                                           }
                                                       ])),
                                           })

read_message_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
read_message_responses = {200: read_message_response_200}
send_message_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
send_message_responses = {200: send_message_response_200}
get_message_responses = {200: get_message_response_200}
get_messages_responses = {200: get_messages_response_200}
delete_message_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
delete_message_responses = {200: delete_message_response_200}
