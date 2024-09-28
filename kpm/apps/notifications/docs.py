from drf_yasg import openapi

id_param = openapi.Parameter("id", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                             operation_description='ID пользователя.', example=1)
class_param = openapi.Parameter("class", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                operation_description='Класс учеников.', example=4)
get_notifications_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                                properties={
                                                    "messages": openapi.Schema(type=openapi.TYPE_INTEGER, example=3),
                                                    "works": openapi.Schema(type=openapi.TYPE_INTEGER, example=2),
                                                })

get_notifications_responses = {200: get_notifications_response_200}
