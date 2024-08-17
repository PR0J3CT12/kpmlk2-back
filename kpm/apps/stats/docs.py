from drf_yasg import openapi

id_param = openapi.Parameter("id", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                             operation_description='ID ученика.', example=1)
theme_param = openapi.Parameter("theme", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                operation_description='ID темы.', example=1)
type_param = openapi.Parameter("type", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                               operation_description='ID типа работы.', example=1)

get_graph_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
get_stats_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                        properties={
                                            "last_homework_current": openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                    example=10),
                                            "last_homework_others": openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                   example=10),
                                            "last_classwork": openapi.Schema(type=openapi.TYPE_INTEGER, example=10),
                                            "homeworks": openapi.Schema(type=openapi.TYPE_INTEGER, example=10),
                                            "classworks": openapi.Schema(type=openapi.TYPE_INTEGER, example=10),
                                            "green": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                            "blue": openapi.Schema(type=openapi.TYPE_INTEGER, example=2),
                                            "lvl": openapi.Schema(type=openapi.TYPE_INTEGER, example=2),
                                            "exp": openapi.Schema(type=openapi.TYPE_INTEGER, example=20),
                                            "base_exp": openapi.Schema(type=openapi.TYPE_INTEGER, example=100),
                                            "total_exp": openapi.Schema(type=openapi.TYPE_INTEGER, example=120),
                                        })
get_stats_responses = {200: get_stats_response_200}
get_graph_responses = {200: get_graph_response_200}
