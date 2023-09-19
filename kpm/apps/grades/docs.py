from drf_yasg import openapi

id_param = openapi.Parameter("id", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                             operation_description='ID ученика.', example=1)
class_param = openapi.Parameter("class", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                operation_description='Класс учеников.', example=4)
theme_param = openapi.Parameter("theme", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                operation_description='ID темы.', example=4)
type_param = openapi.Parameter("type", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                               operation_description='Тип темы.', example=4)
group_param = openapi.Parameter("group", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                                operation_description='ID группы.', example=0)
insert_grades_request_body = openapi.Schema(type=openapi.TYPE_OBJECT,
                                            required=['changes'],
                                            properties={
                                                "work_id": openapi.Schema(
                                                    type=openapi.TYPE_INTEGER, example=1),
                                                "user_id": openapi.Schema(
                                                    type=openapi.TYPE_INTEGER, example=1),
                                                "cell_number": openapi.Schema(
                                                    type=openapi.TYPE_INTEGER, example=1),
                                                "value": openapi.Schema(
                                                    type=openapi.TYPE_STRING,
                                                    example="15.0"),
                                            })
get_mana_waiters_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                               properties={
                                                   "waiters": openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                             properties={
                                                                                 "id": openapi.Schema(
                                                                                     type=openapi.TYPE_INTEGER,
                                                                                     example=3),
                                                                                 "name": openapi.Schema(
                                                                                     type=openapi.TYPE_STRING,
                                                                                     example="Левин Михаил"),
                                                                                 "green": openapi.Schema(
                                                                                     type=openapi.TYPE_INTEGER,
                                                                                     example=5),
                                                                                 "blue": openapi.Schema(
                                                                                     type=openapi.TYPE_INTEGER,
                                                                                     example=8),
                                                                                 "color": openapi.Schema(
                                                                                     type=openapi.TYPE_STRING,
                                                                                     example='#bfa0de'),
                                                                             })})
get_grades_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT,
                                         properties={
                                             "works": openapi.Schema(
                                                 type=openapi.TYPE_ARRAY,
                                                 items=openapi.Schema(
                                                     type=openapi.TYPE_OBJECT,
                                                     example=[
                                                         {
                                                             'id': 1,
                                                             'name': 'Контрольная работа 1',
                                                             'max_score': 40,
                                                             'grades': [5, 5, 5, 10, 15]
                                                         }
                                                     ])),
                                             "students": openapi.Schema(
                                                 type=openapi.TYPE_ARRAY,
                                                 items=openapi.Schema(
                                                     type=openapi.TYPE_OBJECT,
                                                     example=[
                                                         {
                                                             'id': 1,
                                                             'name': 'Левин Михаил',
                                                             'experience': 100,
                                                             'percentage_full_score': 85.5,
                                                             'grades': [
                                                                 {
                                                                     'work_id': 1,
                                                                     'grades': [5, 5, 5, 10, 15],
                                                                     'score': 40,
                                                                     'percentage': 100
                                                                 }
                                                             ],
                                                             'color': '#bfa0de'
                                                         }
                                                     ])),
                                         })
insert_grades_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
give_mana_response_200 = openapi.Schema(type=openapi.TYPE_OBJECT)
insert_grades_responses = {200: insert_grades_response_200}
get_mana_waiters_responses = {200: get_mana_waiters_response_200}
give_mana_responses = {200: give_mana_response_200}
get_grades_responses = {200: get_grades_response_200}
