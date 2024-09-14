import time
from collections import defaultdict
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from kpm.apps.works.models import *
from kpm.apps.themes.models import Theme
from kpm.apps.grades.models import Grade, Mana
import json
from django.db.models import Sum, Case, When, IntegerField, Count, Q
from kpm.apps.users.permissions import *
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.works.docs import *
from kpm.apps.works.functions import *
from django.utils import timezone
import os
from django.conf import settings
from kpm.apps.grades.functions import validate_grade
from kpm.apps.groups.models import GroupUser, GroupWorkFile, Group, GroupWorkDate
from datetime import datetime
from kpm.apps.grades.functions import is_number_float, mana_generation
from kpm.apps.users.docs import permissions_operation_description
from kpm.apps.works.validators import *
from django.core.files import File
from kpm.apps.users.functions import is_trusted


HOST = settings.MEDIA_HOST_PATH
LOGGER = settings.LOGGER


@swagger_auto_schema(method='GET', operation_summary="Получение списка домашних(пользователь).",
                     responses=get_my_homeworks_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAuthenticated']}")
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEnabled])
def get_my_homeworks(request):
    try:
        student = User.objects.get(id=request.user.id)
        work_user = WorkUser.objects.filter(Q(user=student) & Q(is_closed=False) & ~Q(work__type__in=[2, 10, 11])).select_related('work').order_by('work__created_at').values('work_id', 'work__name', 'is_done', 'is_checked', 'work__exercises', 'status', 'work__course')
        works_list = {}
        for work in work_user:
            works_list[work['work_id']] = {
                'name': work['work__name'],
                'course': work['work__course'],
                'fields': work['work__exercises'],
                'status': work['status'],
                'is_done': work['is_done'],
                'is_checked': work['is_checked'],
                'green': 0,
                'blue': 0
            }
        grades = Grade.objects.filter(work_id__in=list(works_list.keys()), work__is_homework=True, user=student).select_related(
            'work').values('score', 'max_score', 'work_id', 'work__max_score')
        manas = Mana.objects.filter(work_id__in=list(works_list.keys()), user=student).values('work_id', 'color', 'is_given')
        for grade in grades:
            if grade['max_score']:
                works_list[grade['work_id']]['max_score'] = grade['max_score']
            else:
                works_list[grade['work_id']]['max_score'] = grade['work__max_score']
            works_list[grade['work_id']]['score'] = grade['score']
        for mana in manas:
            if mana['work_id'] in works_list:
                works_list[mana['work_id']][mana['color']] += 1
        homeworks_list = []
        for homework in works_list:
            result = {
                'id': homework,
                'name': works_list[homework]['name'],
                'fields': works_list[homework]['fields'],
                'status': works_list[homework]['status'],
                'course': works_list[homework]['course'],
                'is_done': works_list[homework]['is_done'],
                'is_checked': works_list[homework]['is_checked']
            }
            if works_list[homework]['is_checked']:
                result['score'] = works_list[homework]['score']
                result['max_score'] = works_list[homework]['max_score']
                result['blue'] = works_list[homework]['blue']
                result['green'] = works_list[homework]['green']
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


@swagger_auto_schema(method='GET', operation_summary="Получение списка домашних работ.",
                     manual_parameters=[class_param, theme_param, type_param, course_param],
                     responses=get_homeworks_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']} | {operation_description}")
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_all_homeworks(request):
    try:
        class_ = get_variable("class", request)
        theme = get_variable("theme", request)
        type_ = get_variable("type", request)
        course = get_variable("course", request)
        if class_ not in ['4', '5', '6', '7']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан класс учеников.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=400)
        if course not in [None, '', '0', '1', '2', '3', '4']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неверно указан курс работы.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=400)
        works = Work.objects.filter(is_homework=True, school_class=int(class_)).exclude(type__in=[1, 2, 3, 4, 7, 8, 9]).select_related("theme").order_by('-created_at')
        works_users = WorkUser.objects.filter(work__in=works).select_related('user').values('work_id', 'user_id', 'is_checked', 'is_done')
        works_users_dict = {}
        for wu in works_users:
            if wu['work_id'] not in works_users_dict:
                works_users_dict[wu['work_id']] = {
                    'amount': 0,
                    'not_checked': 0
                }
            works_users_dict[wu['work_id']]['amount'] += 1
            if wu['is_done'] and not wu['is_checked']:
                works_users_dict[wu['work_id']]['not_checked'] += 1
        if (theme is not None) and (theme != ''):
            works = works.filter(theme_id=theme)
        if type_ in ['0', '5', '6']:
            works = works.filter(type=type_)
        if course in ['0', '1', '2', '3', '4']:
            works = works.filter(course=course)
        works = works.values('id', 'name', 'grades', 'max_score', 'exercises', 'theme__id', 'theme__name', 'type',
                             'is_homework', 'course')
        works_list = []
        for work in works:
            if work['id'] in works_users_dict:
                amount = works_users_dict[work['id']]['amount']
                not_checked = works_users_dict[work['id']]['not_checked']
            else:
                amount = 0
                not_checked = 0
            works_list.append({
                "id": work['id'],
                "name": work['name'],
                "course": work['course'],
                "grades": work['grades'],
                "max_score": work['max_score'],
                "exercises": work['exercises'],
                "theme_id": work['theme__id'],
                "theme_name": work['theme__name'],
                "work_type": work['type'],
                "is_homework": work['is_homework'],
                "amount": amount,
                "not_checked": not_checked,
            })
        return HttpResponse(json.dumps({'works': works_list}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='PATCH', operation_summary="Проверка домашней работы(админка).",
                     request_body=check_user_homework_request_body,
                     responses=check_user_homework_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']}")
@api_view(["PATCH"])
@permission_classes([IsAdmin, IsEnabled])
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
        work = Work.objects.get(Q(id=id_) & ~Q(type__in=[2, 10, 11]))
        student = User.objects.get(id=student_id)
        admin = User.objects.get(id=request.user.id)
        work_user = WorkUser.objects.filter(user=student, work=work)
        if not work_user:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        work_user = work_user[0]
        if work_user.status not in [1, 5]:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Работа не нуждается в проверке.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        grade_row = Grade.objects.get(user=student, work=work)
        work_grades = list(map(float, work.grades))
        new_grades = grade_row.grades
        grades = request_body["grades"]
        old_score = grade_row.score
        score = 0
        max_score = 0
        exercises = 0
        is_empty = True
        for i, value in enumerate(grades):
            if ',' in value:
                value = value.replace(',', '.')
            if not validate_grade(value):
                return HttpResponse(
                    json.dumps({'state': 'error', 'message': 'Некорректное значение оценки.', 'details': {},
                                'instance': request.path},
                               ensure_ascii=False), status=400)
            if value == '-':
                is_empty = False
                pass
            elif value == '#':
                exercises += 1
                max_score += work_grades[i]
            else:
                is_empty = False
                exercises += 1
                max_score += work_grades[i]
                score += float(value)
            if score > work.max_score:
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': 'Некорректное значение оценок. Сумма вышла больше максимума.',
                         'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=404)
            if is_empty:
                exercises = 0
                max_score = 0
                score = 0
                work_user.is_checked = False
                work_user.checked_at = None
                work_user.is_done = False
                work_user.checker = None
            else:
                work_user.is_checked = True
                work_user.checked_at = timezone.now()
                work_user.is_done = True
                work_user.checker = admin
            new_grades[i] = value
        grade_row.score = score
        grade_row.exercises = exercises
        grade_row.max_score = max_score
        grade_row.grades = new_grades
        grade_row.save()
        if 'comment' in request_body.keys():
            comment = request_body['comment']
            work_user.comment = comment
        if work_user.status == 1:
            work_user.status = 2
        else:
            work_user.status = 6
        if student.last_homework_id is None:
            student.last_homework_id = work.id
        else:
            try:
                last_homework = Work.objects.get(id=student.last_homework_id)
                if work.created_at > last_homework.created_at:
                    student.last_homework_id = work.id
            except ObjectDoesNotExist:
                student.last_homework_id = work.id
        work_user.save()
        student.save()
        if work_user.status == 2:
            if score != old_score:
                manas_delete = Mana.objects.filter(Q(user=student) & Q(work=work))
                manas_delete.delete()
            if work.type == 6:
                count = 0
                for grade_ in new_grades:
                    if is_number_float(grade_):
                        if float(grade_) > 0:
                            count += 1
                green, blue = mana_generation(int(work.type), count, 0)
            else:
                green, blue = mana_generation(int(work.type), score, max_score)
            if score != old_score:
                for i in range(0, green):
                    mana = Mana(user=student, work=work, color='green')
                    mana.save()
                for i in range(0, blue):
                    mana = Mana(user=student, work=work, color='blue')
                    mana.save()
            if student.school_class == 4:
                aggregated_data = Grade.objects.filter(
                    user=student,
                    work__type__in=[0, 5, 6]
                ).aggregate(
                    total_experience=Sum('score'),
                    exam_experience=Sum(
                        Case(
                            When(work__type=5, then='score'),
                            default=0,
                            output_field=IntegerField(),
                        )
                    ),
                    oral_exam_experience=Sum(
                        Case(
                            When(work__type=6, then='score'),
                            default=0,
                            output_field=IntegerField(),
                        )
                    )
                )
                experience = aggregated_data['total_experience'] if aggregated_data else 0
                exam_experience = aggregated_data['exam_experience'] if aggregated_data else 0
                oral_exam_experience = aggregated_data['oral_exam_experience'] if aggregated_data else 0
                student.experience = experience
                student.exam_experience = exam_experience
                student.oral_exam_experience = oral_exam_experience
            else:
                aggregated_data = Grade.objects.filter(
                    user=student,
                    work__type__in=[0, 10, 11]
                ).aggregate(
                    total_experience=Sum('score'),
                )
                experience = aggregated_data['total_experience'] if aggregated_data else 0
                student.experience = experience
            student.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Работа или пользователь не существует.', 'details': {},
                        'instance': request.path},
                       ensure_ascii=False), status=404)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='POST', operation_summary="Ответ на домашнюю работу.",
                     request_body=create_response_request_body,
                     responses=create_response_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAuthenticated']}")
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsEnabled])
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
        work = Work.objects.get(Q(id=id_) & ~Q(type__in=[2, 10, 11]))
        student = User.objects.get(id=request.user.id)
        work_user = WorkUser.objects.filter(user=student, work=work)
        if not work_user:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        work_user = work_user[0]
        if work_user.is_closed:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Работа закрыта.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        if work_user.status not in [0, 3, 4]:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Работа не нуждается в сдачи.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        answers = data.getlist("answers")
        fields = len(answers)
        if fields != work.exercises:
            answers = answers[:work.exercises]
            #return HttpResponse(
            #    json.dumps(
            #        {'state': 'error', 'message': f'Некорректное количество ответов.', 'details': {},
            #         'instance': request.path},
            #        ensure_ascii=False), status=403)
        files = files.getlist('files')
        if not files:
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Не указаны файлы.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=400)
        for file in files:
            if 'image' in str(file.content_type):
                pass
            elif file.content_type in ('application/pdf', 'application/octet-stream'):
                pass
            else:
                return HttpResponse(
                    json.dumps({'state': 'error', 'message': 'Недопустимый файл.', 'details': {'ct': file.content_type},
                                'instance': request.path},
                               ensure_ascii=False), status=404)
        work_user.is_done = True
        work_user.answers = answers
        work_user.answered_at = timezone.now()
        for file in files:
            ext = file.name.split('.')[-1]
            if file.name.lower().endswith('.heif') or file.name.lower().endswith('.heic'):
                temp_path = f'/tmp/{file.name}'
                with open(temp_path, 'wb+') as temp_file:
                    for chunk in file.chunks():
                        temp_file.write(chunk)
                new_path = heif_to_jpeg(temp_path)
                if new_path:
                    with open(new_path, 'rb') as jpeg_file:
                        django_file = File(jpeg_file, name=os.path.basename(new_path))
                        homework_file = WorkUserFile(link=work_user, file=django_file, ext='jpeg')
                        homework_file.save()
                    os.remove(temp_path)
                    if new_path:
                        os.remove(new_path)
                else:
                    continue
            else:
                homework_file = WorkUserFile(link=work_user, file=file, ext=ext)
                homework_file.save()
        if work_user.status in [0, 3]:
            work_user.status = 1
        else:
            work_user.status = 5
        work_user.save()
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


@swagger_auto_schema(method='GET', operation_summary="Получение домашней работы(пользователь).",
                     manual_parameters=[id_param, student_param],
                     responses=get_user_homework_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAuthenticated']}")
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEnabled])
def get_user_homework(request):
    try:
        id_ = get_variable("id", request)
        student_id = get_variable("student", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        work = Work.objects.get(Q(id=id_) & ~Q(type__in=[2, 10, 11]))
        if student_id is None:
            student_id = request.user.id
        if not is_trusted(request, student_id):
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': f'Отказано в доступе', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=401)
        user = User.objects.get(id=request.user.id)
        if user.is_admin:
            student = User.objects.get(id=student_id)
        else:
            student = user
        work_user = WorkUser.objects.filter(user=student, work=work)
        if not work_user:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        work_user = work_user[0]
        files = WorkFile.objects.filter(work=work)
        files_list = []
        host = HOST
        for file in files:
            link = file.file.name
            name = link.split('/')[-1]
            ext = name.split('.')[-1]
            files_list.append({'link': f'{host}/{link}', 'name': name, 'ext': ext})
        response = {
            'id': work.id,
            'name': work.name,
            'course': work.course,
            'text': work.text,
            'fields': work.exercises,
            'files': files_list,
            'class': work.school_class,
            'status': work_user.status,
            'is_done': work_user.is_done,
            'is_checked': work_user.is_checked,
            'created_at': str(work.created_at)
        }
        grade = Grade.objects.get(work=work, user=student)
        max_score = grade.max_score
        score = grade.score
        if work_user.is_done:
            response['user_answers'] = work_user.answers
            response['answers'] = work.answers
            user_files = WorkUserFile.objects.filter(link=work_user)
            user_files_list = []
            for file in user_files:
                link = file.file.name
                name = link.split('/')[-1]
                user_files_list.append({'link': f'{host}/{link}', 'name': name, 'ext': file.ext})
            response['user_files'] = user_files_list
            response['answered_at'] = str(work_user.answered_at)
        if work_user.is_checked:
            response['score'] = score
            response['max_score'] = max_score
        response['comment'] = work_user.comment
        manas = Mana.objects.filter(work=work, user=student).values('color')
        green = 0
        blue = 0
        for mana in manas:
            if mana['color'] == 'green':
                green += 1
            if mana['color'] == 'blue':
                blue += 1
        response['green'] = green
        response['blue'] = blue
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


@swagger_auto_schema(method='PATCH', operation_summary="Открыть доступ к домашней работе ученику.",
                     manual_parameters=[id_param, student_param],
                     responses=add_to_homework_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierOne']}")
@api_view(["PATCH"])
@permission_classes([IsTierOne, IsEnabled])
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
        work = Work.objects.get(Q(id=id_) & ~Q(type__in=[2, 10, 11]))
        student = User.objects.get(id=student_id)
        student_types = GroupUser.objects.filter(user=student).values_list('group__type', flat=True)
        student_types = set(student_types)
        if work.type == 10:
            if 0 not in student_types:
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Несоответствие типа группы ученика и типа работы.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=400)
        if work.type == 11:
            if (1 not in student_types) or (2 not in student_types) or (3 not in student_types):
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Несоответствие типа группы ученика и типа работы.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=400)
        if student.school_class != work.school_class:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Класс ученика не соответствует классу работы.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=404)
        answers = ['#'] * work.exercises
        work_user = WorkUser.objects.filter(work=work, user=student)
        if work_user:
            work_user = work_user[0]
            work_user.is_closed = False
        else:
            work_user = WorkUser(work=work, user=student, answers=answers)
        work_user.save()
        LOGGER.info(f'Added student {student_id} to work {id_} by user {request.user.id}.')
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


@swagger_auto_schema(method='PATCH', operation_summary="Закрыть доступ к домашней работе ученику.",
                     manual_parameters=[id_param, student_param],
                     responses=delete_from_homework_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierOne']}")
@api_view(["PATCH"])
@permission_classes([IsTierOne, IsEnabled])
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
        work = Work.objects.get(Q(id=id_) & ~Q(type__in=[2, 10, 11]))
        student = User.objects.get(id=student_id)
        work_user = WorkUser.objects.filter(work=work, user=student)
        if work_user:
            work_user = work_user[0]
            work_user.is_closed = True
            work_user.save()
            LOGGER.info(f'Deleted student {student_id} from work {id_} by user {request.user.id}.')
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps(
                {'state': 'error', 'message': f'Работа или пользователь не существует или у пользователя нет доступа к этой работе.', 'details': {},
                 'instance': request.path},
                ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='PATCH', operation_summary="Вернуть домашнюю работу с комментариями(админка).",
                     request_body=return_user_homework_request_body,
                     responses=return_user_homework_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierTwo']}")
@api_view(["PATCH"])
@permission_classes([IsTierTwo, IsEnabled])
def return_user_homework(request):
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
        work = Work.objects.get(Q(id=id_) & ~Q(type__in=[2, 10, 11]))
        student = User.objects.get(id=student_id)
        admin = User.objects.get(id=request.user.id)
        work_user = WorkUser.objects.filter(user=student, work=work)
        if not work_user:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        work_user = work_user[0]
        if work_user.status != 1:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Работа не ожидает проверки.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        comment = request_body["comment"]
        work_user.checker = admin
        work_user.is_done = False
        work_user.status = 3
        work_user.comment = comment
        work_user.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Работа или пользователь не существует.', 'details': {},
                        'instance': request.path},
                       ensure_ascii=False), status=404)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='POST', operation_summary="Установить дату проведения домашней работы для группы.",
                     request_body=set_homework_date_request_body,
                     responses=set_homework_date_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierOne']}")
@api_view(["POST"])
@permission_classes([IsTierOne, IsEnabled])
def set_homework_date(request):
    try:
        if request.body:
            request_body = json.loads(request.body)
        else:
            return HttpResponse(json.dumps(
                {'state': 'error', 'message': 'Body запроса пустое.', 'details': {}, 'instance': request.path},
                ensure_ascii=False), status=400)
        group_id = request_body['group']
        work_id = request_body['work']
        date = request_body['date']
        if date is None:
            date = str(datetime.today())
        if date:
            date = datetime.strptime(date, '%d.%m.%Y')
        group = Group.objects.get(id=group_id)
        work = Work.objects.get(Q(id=work_id) & ~Q(type__in=[2, 10, 11]))
        if not validate_work_type_for_group_type(work.type, group.type):
            return HttpResponse(
                json.dumps({'state': 'error', 'message': 'Тип работы не подходит для этого типа группы.', 'details': {},
                            'instance': request.path},
                           ensure_ascii=False), status=400)
        row = GroupWorkDate.objects.filter(work=work, group=group)
        if row:
            row = row[0]
            row.date = date
        else:
            row = GroupWorkDate(work=work, group=group, date=date)
        if date <= datetime.today():
            row.is_given = True
            answers = ['#'] * work.exercises
            students = GroupUser.objects.filter(group=group).select_related('user')
            for student in students:
                user = student.user
                try:
                    if user.school_class == work.school_class:
                        work_user = WorkUser(user=user, work=work, answers=answers)
                        work_user.save()
                except Exception as e:
                    pass
        row.save()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except KeyError as e:
        return HttpResponse(
            json.dumps({'state': 'error', 'message': f'Не указано поле {e}.', 'details': {}, 'instance': request.path},
                       ensure_ascii=False), status=404)
    except ObjectDoesNotExist as e:
        return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Группа или работа не существует.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='DELETE', operation_summary="Удалить дату проведения домашней работы для группы.",
                     manual_parameters=[work_param, group_param],
                     responses=delete_homework_date_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsTierOne']}")
@api_view(["DELETE"])
@permission_classes([IsTierOne, IsEnabled])
def delete_homework_dates(request):
    try:
        group_id = get_variable("group", request)
        if not group_id:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id группы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=400)
        work_id = get_variable("work", request)
        if not work_id:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=400)
        group = Group.objects.get(id=group_id)
        work = Work.objects.get(Q(id=work_id) & ~Q(type__in=[2, 10, 11]))
        row = GroupWorkDate.objects.filter(work=work, group=group)
        if row:
            row = row[0]
            row.delete()
        return HttpResponse(json.dumps({}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Группа или работа не существует.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получить даты проведения домашних работ для группы, либо для домашней работы получить даты проведения в группах.",
                     manual_parameters=[work_param, group_param],
                     responses=get_homeworks_dates_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']}")
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_homeworks_dates(request):
    try:
        group_filter = False
        work_filter = False
        group_id = get_variable("group", request)
        if group_id not in [None, '']:
            group_filter = True
        work_id = get_variable("work", request)
        if work_id not in [None, '']:
            group_filter = False
            work_filter = True

        result = []
        if group_filter:
            group = Group.objects.get(id=group_id)
            rows = GroupWorkDate.objects.filter(Q(group=group) & ~Q(work__type__in=[2, 10, 11])).values('work_id', 'date')
            for row in rows:
                result.append({
                    'work_id': row['work_id'],
                    'group_id': group_id,
                    'date': row['date'].strftime('%d.%m.%Y'),
                })
        elif work_filter:
            work = Work.objects.get(id=work_id)
            rows = GroupWorkDate.objects.filter(work=work).values('group_id', 'date')
            for row in rows:
                result.append({
                    'work_id': row['work_id'],
                    'group_id': group_id,
                    'date': row['date'].strftime('%d.%m.%Y'),
                })
        else:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Необходимо указать либо work, либо group.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        return HttpResponse(json.dumps({'groups_works_dates': result}, ensure_ascii=False), status=200)
    except ObjectDoesNotExist as e:
        return HttpResponse(
                json.dumps({'state': 'error', 'message': f'Группа или работа не существует.', 'details': {}, 'instance': request.path},
                           ensure_ascii=False), status=404)
    except Exception as e:
        return HttpResponse(json.dumps(
            {'state': 'error', 'message': f'Произошла странная ошибка.', 'details': {'error': str(e)},
             'instance': request.path},
            ensure_ascii=False), status=404)


@swagger_auto_schema(method='GET', operation_summary="Получение ответов на домашнюю работу(для таблицы).",
                     manual_parameters=[id_param],
                     responses=get_all_answers_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAdmin']}")
@api_view(["GET"])
@permission_classes([IsAdmin, IsEnabled])
def get_all_answers(request):
    try:
        id_ = get_variable("id", request)
        if (id_ is None) or (id_ == ''):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Не указан id работы.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=404)
        admin = Admin.objects.get(user_id=request.user.id)
        work = Work.objects.get(Q(id=id_) & ~Q(type__in=[2, 10, 11]))
        grades = Grade.objects.filter(work=work).values('user_id', 'score', 'max_score')
        grades_dict = {}
        for grade in grades:
            if grade['user_id'] not in grades_dict:
                grades_dict[grade['user_id']] = {'score': 0,'max_score': 0, 'green': 0, 'blue': 0}
            grades_dict[grade['user_id']]['score'] = grade['score']
            grades_dict[grade['user_id']]['max_score'] = grade['max_score'] if grade['max_score'] else work.max_score
        manas = Mana.objects.filter(work=work, is_given=False).values('user_id', 'color')
        for mana in manas:
            if mana['color'] == 'blue':
                grades_dict[mana['user_id']]['blue'] += 1
            if mana['color'] == 'green':
                grades_dict[mana['user_id']]['green'] += 1
        response = {'id': work.id, 'name': work.name, 'answers': work.answers,
                    'students': []}
        work_users = WorkUser.objects.filter(work=work).order_by('user_id').select_related('user', 'checker').values(
            'id', 'user_id', 'user__name', 'is_done', 'is_checked', 'comment', 'checker_id', 'checker__name',
            'checked_at', 'added_at', 'answered_at', 'answers', 'is_closed'
        )
        groups_users = GroupUser.objects.filter(group__school_class=4).select_related('group').values('user_id', 'group_id', 'group__marker', 'group__name', 'group__type')
        user_groups_dict = {}
        for gu in groups_users:
            if gu['user_id'] not in user_groups_dict:
                user_groups_dict[gu['user_id']] = []
            user_groups_dict[gu['user_id']].append({
                'id': gu['group_id'],
                'color': gu['group__marker'],
                'name': gu['group__name'],
                'type': gu['group__type']
            })
        work_user_files = WorkUserFile.objects.filter(link__work=work).values('link', 'file', 'ext')
        files_dict = {}
        for user_file in work_user_files:
            if user_file['link'] not in files_dict:
                files_dict[user_file['link']] = []
            files_dict[user_file['link']].append({
                'file': user_file['file'],
                'ext': user_file['ext']
            })
        students_list = []
        host = HOST
        for wu in work_users:
            student_data = {'id': wu['user_id'], 'name': wu['user__name'], 'answers': [], 'files': [], 'groups': []}
            if wu['user_id'] in user_groups_dict:
                student_data['groups'] = user_groups_dict[wu['user_id']]
            if wu['is_done']:
                answers_list = wu['answers']
                if wu['id'] in files_dict:
                    files = files_dict[wu['id']]
                    for file in files:
                        name = file['file'].split('/')[-1]
                        link = f"{host}/{file['file']}"
                        ext = file['ext']
                        student_data['files'].append({'link': link, 'name': name, 'ext': ext})
            else:
                answers_list = [''] * len(work.answers)
            if wu['is_checked']:
                score = grades_dict[wu['user_id']]['score']
                max_score = grades_dict[wu['user_id']]['max_score']
                green = grades_dict[wu['user_id']]['green']
                blue = grades_dict[wu['user_id']]['blue']
            else:
                score = None
                max_score = None
                green = None
                blue = None
            if wu['checker_id']:
                if admin.user_id == wu['checker_id']:
                    checker = wu['checker__name']
                elif admin.tier == 0:
                    checker = ""
                else:
                    checker = wu['checker__name']
            else:
                checker = ""
            comment = wu['comment']
            student_data['answers'] = answers_list
            student_data['score'] = score
            student_data['max_score'] = max_score
            student_data['comment'] = comment
            student_data['checker'] = checker
            student_data['is_done'] = wu['is_done']
            student_data['is_checked'] = wu['is_checked']
            student_data['is_closed'] = wu['is_closed']
            student_data['green'] = green
            student_data['blue'] = blue
            if wu['checked_at']:
                checked_at = str(wu['checked_at'])
            else:
                checked_at = None
            if wu['answered_at']:
                answered_at = str(wu['answered_at'])
            else:
                answered_at = None
            if wu['added_at']:
                added_at = str(wu['added_at'])
            else:
                added_at = None
            student_data['checked_at'] = checked_at
            student_data['answered_at'] = answered_at
            student_data['added_at'] = added_at
            students_list.append(student_data)
        response['students'] = students_list
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