from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from kpm.apps.logs.models import Log
from kpm.apps.homeworks.models import *
import json
from django.db.models import Sum, Q, Count
from kpm.apps.users.permissions import IsAdmin
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.homeworks.docs import *
from kpm.apps.homeworks.functions import *
from django.utils import timezone


@swagger_auto_schema(method='POST', operation_summary="Создание домашней работы.",
                     request_body=create_homework_request_body,
                     responses=create_homework_responses)
@api_view(["POST"])
@permission_classes([IsAdmin])
def create_homework(request):
    try:
        if request.POST or request.FILES:
            data = request.POST
            files = request.FILES
        else:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=400)
        author = User.objects.get(id=request.user.id)
        title = data["title"]
        score = data["score"]
        if not is_number_float(score):
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Некорректное значение score.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=404)
        text = data["text"]
        if data["class"] not in ['4', '5', '6', 4, 5, 6]:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        class_ = data["class"]
        users = data.getlist("users")
        answers = data.getlist("answers")
        answers_string = '_._'.join(answers)
        fields = len(answers)
        files = files.getlist('files')
        for file in files:
            if (file.content_type == 'application/pdf') or 'image' in file.content_type:
                return HttpResponse(
                    json.dumps({'state': 'error', 'message': 'Недопустимый файл.', 'details': {},
                                'instance': request.path},
                               ensure_ascii=False), status=404)
        homework = Homework(author=author, title=title, text=text, score=score, answers=answers_string, fields=fields,
                            school_class=class_)
        homework.save()
        for file in files:
            ext = file.content_type.split('/')[1]
            homework_file = HomeworkFile(homework=homework, file=file, ext=ext)
            homework_file.save()
        users = User.objects.filter(id__in=users)
        for user in users:
            if user.school_class != homework.school_class:
                pass
            fields = ['#'] * homework.fields
            answers = '_._'.join(fields)
            homework_user = HomeworkUsers(homework=homework, user=user, answers=answers)
            homework_user.save()
        homework.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Пользователь не существует.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='DELETE', operation_summary="Удаление работы.",
                     manual_parameters=[id_param],
                     responses=delete_homework_responses)
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_homework(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        homework = Homework.objects.get(id=id_)
        homework.delete()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Работа не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получение работы(админка).",
                     manual_parameters=[id_param],
                     responses=get_homework_responses)
@api_view(["GET"])
@permission_classes([IsAdmin])
def get_homework(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        homework = Homework.objects.get(id=id_)
        files = HomeworkFile.objects.filter(homework=homework)
        files_list = []
        for file in files:
            link = file.file.name
            name = link.split('/')[1]
            files_list.append({'id': file.id, 'link': link, 'name': name, 'ext': file.ext})
        homework_users = HomeworkUsers.objects.filter(homework=homework)
        users_list = []
        for user in homework_users:
            users_list.append({'id': user.user.id, 'name': user.user.name})
        return HttpResponse(json.dumps({
            'id': homework.id,
            'title': homework.title,
            'text': homework.text,
            'score': homework.score,
            'fields': homework.fields,
            'answers': homework.answers.split("_._"),
            'files': files_list,
            'class': homework.school_class,
            'users': users_list,
            'created_at': str(homework.created_at)
        }, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Работа не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='PATCH', operation_summary="Изменение работы(админка).",
                     request_body=update_homework_request_body,
                     responses=update_homework_responses)
@api_view(["PATCH"])
@permission_classes([IsAdmin])
def update_homework(request):
    try:
        if request.POST or request.FILES:
            data = request.POST
            files = request.FILES
        else:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=400)
        homework = Homework.objects.get(id=data['id'])
        if 'title' in data:
            title = data["title"]
            homework.title = title
        if 'score' in data:
            score = data["score"]
            if not is_number_float(score):
                return HttpResponse(
                    json.dumps({'state': 'error', 'message': 'Некорректное значение score.', 'details': {},
                                'instance': request.path},
                               ensure_ascii=False), status=404)
            homework.score = score
        if 'text' in data:
            text = data["text"]
            homework.text = text
        if 'answer' in data:
            cell = data['cell']
            value = data['answer']
            if cell >= homework.fields:
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Неверное поле ответа.', 'details': {}, 'instance': request.path},
                        ensure_ascii=False), status=400)
            current_answers = homework.answers.split('_._')
            current_answers[int(cell)] = value
            answers = '_._'.join(current_answers)
            homework.answers = answers
        if 'files' in files:
            files = files.getlist('files')
            for file in files:
                if (file.content_type == 'application/pdf') or 'image' in file.content_type:
                    return HttpResponse(
                        json.dumps({'state': 'error', 'message': 'Недопустимый файл.', 'details': {},
                                    'instance': request.path},
                                   ensure_ascii=False), status=404)
                ext = file.content_type.split('/')[1]
                homework_file = HomeworkFile(homework=homework, file=file, ext=ext)
                homework_file.save()
        homework.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Работа не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='PATCH', operation_summary="Удаление файла у работы.",
                     manual_parameters=[file_param],
                     responses=delete_file_from_homework_responses)
@api_view(["PATCH"])
@permission_classes([IsAdmin])
def delete_file_from_homework(request):
    try:
        file_id = get_variable("file", request)
        if (file_id is None) or (file_id == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id файла.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        homework_file = HomeworkFile.objects.get(id=file_id)
        homework_file.delete()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Файл не существует.', 'details': {},
                        'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='PATCH', operation_summary="Добавление работы ученику.",
                     manual_parameters=[id_param, student_param],
                     responses=add_to_homework_responses)
@api_view(["PATCH"])
@permission_classes([IsAdmin])
def add_to_homework(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        student_id = get_variable("student", request)
        if (student_id is None) or (student_id == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        homework = Homework.objects.get(id=id_)
        student = User.objects.get(id=student_id)
        if student.school_class != homework.school_class:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Класс ученика не соответствует классу работы.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        fields = ['#'] * homework.fields
        answers = '_._'.join(fields)
        homework_user = HomeworkUsers(homework=homework, user=student, answers=answers)
        homework_user.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Работа или пользователь не существует.', 'details': {},
                        'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='PATCH', operation_summary="Удаление работы у ученика.",
                     manual_parameters=[id_param, student_param],
                     responses=delete_from_homework_responses)
@api_view(["PATCH"])
@permission_classes([IsAdmin])
def delete_from_homework(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        student_id = get_variable("student", request)
        if (student_id is None) or (student_id == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        homework = Homework.objects.get(id=id_)
        student = User.objects.get(id=student_id)
        homework_user = HomeworkUsers.objects.filter(homework=homework, user=student)
        if homework_user:
            homework_user[0].delete()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Работа или пользователь не существует.', 'details': {},
                        'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получение работы(пользователь).",
                     manual_parameters=[id_param],
                     responses=get_user_homework_responses)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_homework(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        homework = Homework.objects.get(id=id_)
        student = User.objects.get(id=request.user.id)
        homework_user = HomeworkUsers.objects.filter(user=student, homework=homework)
        if not homework_user:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        homework_user = homework_user[0]
        files = HomeworkFile.objects.filter(homework=homework)
        files_list = []
        for file in files:
            link = file.file.name
            name = link.split('/')[1]
            files_list.append({'link': link, 'name': name, 'ext': file.ext})
        response = {
            'id': homework.id,
            'title': homework.title,
            'text': homework.text,
            'max_score': homework.score,
            'fields': homework.fields,
            'files': files_list,
            'class': homework.school_class,
            'is_done': homework_user.is_done,
            'is_checked': homework_user.is_checked,
            'created_at': str(homework.created_at)
        }
        if homework_user.is_done:
            response['answers'] = homework.answers.split("_._")
            response['user_answers'] = homework_user.answers.split("_._")
            user_files = HomeworkUsersFile.objects.filter(link=homework_user)
            user_files_list = []
            for file in user_files:
                link = file.file.name
                name = link.split('/')[1]
                user_files_list.append({'link': link, 'name': name, 'ext': file.ext})
            response['user_files'] = user_files_list
            response['answered_at'] = str(homework_user.answered_at)
        if homework_user.is_checked:
            response['user_score'] = homework_user.score
        response['comment'] = homework_user.comment
        return HttpResponse(json.dumps(response, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Работа не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='POST', operation_summary="Ответ на домашнюю работу.",
                     request_body=create_response_request_body,
                     responses=create_response_responses)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_response(request):
    try:
        if request.POST or request.FILES:
            data = request.POST
            files = request.FILES
        else:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Body запроса пустое.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=400)
        id_ = data['id']
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        homework = Homework.objects.get(id=id_)
        student = User.objects.get(id=request.user.id)
        homework_user = HomeworkUsers.objects.filter(user=student, homework=homework)
        if not homework_user:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        homework_user = homework_user[0]
        answers = data.getlist("answers")
        for answer in answers:
            if '_._' in answer:
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Некорректный ответ.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=403)
        answers_string = '_._'.join(answers)
        fields = len(answers)
        if fields != homework.fields:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Некорректное количество ответов.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=403)
        files = files.getlist('files')
        for file in files:
            if (file.content_type == 'application/pdf') or 'image' in file.content_type:
                return HttpResponse(
                    json.dumps({'state': 'error', 'message': 'Недопустимый файл.', 'details': {},
                                'instance': request.path},
                               ensure_ascii=False), status=404)
        homework_user.is_done = True
        homework_user.answers = answers_string
        homework_user.answered_at = timezone.now()
        for file in files:
            ext = file.content_type.split('/')[1]
            homework_file = HomeworkUsersFile(link=homework_user, file=file, ext=ext)
            homework_file.save()
        homework_user.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Работа не существует.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='PATCH', operation_summary="Проверка домашней работы(админка).",
                     request_body=check_user_homework_request_body,
                     responses=check_user_homework_responses)
@api_view(["PATCH"])
@permission_classes([IsAdmin])
def check_user_homework(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        id_ = request_body['id']
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        student_id = request_body['student']
        if (student_id is None) or (student_id == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        homework = Homework.objects.get(id=id_)
        student = User.objects.get(id=student_id)
        homework_user = HomeworkUsers.objects.filter(user=student, homework=homework)
        if not homework_user:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        homework_user = homework_user[0]
        if 'score' in request_body.keys():
            score = request_body['score']
            if not is_number_float(score):
                return HttpResponse(
                    json.dumps({'state': 'error', 'message': 'Некорректное значение score.', 'details': {},
                                'instance': request.path},
                               ensure_ascii=False), status=404)
            if (float(score) < 0) or (float(score) > homework.score):
                return HttpResponse(
                    json.dumps({'state': 'error', 'message': 'Некорректное значение score.', 'details': {},
                                'instance': request.path},
                               ensure_ascii=False), status=404)
            homework_user.is_checked = True
            homework_user.score = int(score)
        if 'comment' in request_body.keys():
            comment = request_body['comment']
            homework_user.comment = comment
        homework_user.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Работа или пользователь не существует.', 'details': {},
                        'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получение списка домашних(пользователь).",
                     responses=get_my_homeworks_responses)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_my_homeworks(request):
    try:
        student = User.objects.get(id=request.user.id)
        homework_user = HomeworkUsers.objects.filter(user=student)
        homeworks_list = []
        for homework_ in homework_user:
            result = {
                'id': homework_.homework.id,
                'name': homework_.homework.title,
                'is_done': homework_.is_done,
                'is_checked': homework_.is_checked
            }
            if homework_.is_checked:
                result['score'] = homework_.score
                result['max_score'] = homework_.homework.score
            homeworks_list.append(result)
        return HttpResponse(json.dumps({'homeworks': homeworks_list}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Работа или пользователь не существует.', 'details': {},
                        'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получение списка всех работ(админка).",
                     manual_parameters=[class_param],
                     responses=get_all_homeworks_responses)
@api_view(["GET"])
@permission_classes([IsAdmin])
def get_all_homeworks(request):
    try:
        class_ = get_variable("class", request)
        if not class_:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан класс ученика.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        else:
            if class_ not in ['4', '5', '6', 4, 5, 6]:
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Неверно указан класс ученика.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=404)
        homeworks = Homework.objects.filter(school_class=class_).order_by('-created_at')
        homeworks_list = []
        for homework_ in homeworks:
            homeworks_users = HomeworkUsers.objects.filter(homework=homework_)
            amount = len(homeworks_users)
            homeworks_list.append(
                {
                    'id': homework_.id,
                    'name': homework_.title,
                    'amount': amount,
                    'created_at': str(homework_.created_at)
                }
            )
        return HttpResponse(json.dumps({'homeworks': homeworks_list}, ensure_ascii=False), status=200)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получение ответов на работу(для таблицы).",
                     manual_parameters=[id_param],
                     responses=get_all_answers_responses)
@api_view(["GET"])
@permission_classes([IsAdmin])
def get_all_answers(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        homework = Homework.objects.get(id=id_)
        response = {'id': homework.id, 'title': homework.title, 'answers': homework.answers.split("_._"),
                    'students': [], 'max_score': homework.score}
        homework_users = HomeworkUsers.objects.filter(homework=homework).order_by('user_id').select_related('user')
        students_list = []
        for homework_user in homework_users:
            student_data = {'id': homework_user.user.id, 'name': homework_user.user.name, 'answers': [], 'files': []}
            if homework_user.is_done:
                answers_list = homework_user.answers.split('_._')
                files = HomeworkUsersFile.objects.filter(link=homework_user)
                if files:
                    for file in files:
                        link = file.file.name
                        name = link.split('/')[1]
                        student_data['files'].append({'link': link, 'name': name, 'ext': file.ext})
            else:
                answers_list = [''] * homework.fields
            if homework_user.is_checked:
                score = homework_user.score
            else:
                score = None
            comment = homework_user.comment
            student_data['answers'] = answers_list
            student_data['score'] = score
            student_data['comment'] = comment
            students_list.append(student_data)
        response['students'] = students_list
        return HttpResponse(json.dumps(response, ensure_ascii=False), status=200)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)
