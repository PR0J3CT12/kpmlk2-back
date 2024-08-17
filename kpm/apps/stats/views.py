from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from kpm.apps.users.permissions import *
from kpm.apps.users.functions import is_trusted
from kpm.apps.stats.functions import *
from kpm.apps.stats.docs import *
from kpm.apps.ratings.functions import count_lvl
from kpm.apps.works.models import Work
from kpm.apps.grades.models import Grade, Mana
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import json
from django.db.models import Sum, Q, Count, F, Avg, ExpressionWrapper, FloatField
from drf_yasg.utils import swagger_auto_schema
from kpm.apps.users.docs import *
from django.conf import settings
from kpm.apps.users.docs import permissions_operation_description

LOGGER = settings.LOGGER


@swagger_auto_schema(method='GET', operation_summary="Получить персональную статистику ученика.",
                     manual_parameters=[id_param],
                     responses=get_stats_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAuthenticated']}")
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEnabled])
def get_stats(request):
    try:
        id_ = get_variable('id', request)
        if not is_trusted(request, id_):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        student = User.objects.get(id=id_, is_admin=False)

        if student.last_homework_id is None:
            last_homework_current = None
            last_homework_others = None
        else:
            try:
                last_homework_work = Work.objects.get(id=student.last_homework_id)
                last_homework = Grade.objects.filter(work=last_homework_work)
                last_homework_current = last_homework.filter(user=student)
                last_homework_others = last_homework.exclude(user=student)
            except ObjectDoesNotExist:
                last_homework_current = None
                last_homework_others = None
        if not last_homework_current:
            last_homework_perc_current = None
        else:
            last_homework_current = last_homework_current[0]
            if last_homework_current.max_score != 0:
                last_homework_perc_current = round(last_homework_current.score / last_homework_current.max_score * 100)
            else:
                last_homework_perc_current = 0
        if not last_homework_others:
            last_homework_perc_others = None
        else:
            total = 0
            total_perc = 0
            for student_ in last_homework_others:
                if student_.max_score <= 0:
                    continue
                total_perc += round(student_.score / student_.max_score * 100)
                total += 1
            if total > 0:
                last_homework_perc_others = total_perc // total
            else:
                last_homework_perc_others = None

        if student.last_classwork_id is None:
            last_classwork = None
        else:
            try:
                last_classwork_work = Work.objects.get(id=student.last_classwork_id)
                last_classwork = Grade.objects.filter(work=last_classwork_work, user=student)
            except ObjectDoesNotExist:
                last_classwork = None
        if not last_classwork:
            last_classwork_perc = None
        else:
            last_classwork = last_classwork[0]
            if last_classwork.max_score != 0:
                last_classwork_perc = round(last_classwork.score / last_classwork.max_score * 100)
            else:
                last_classwork_perc = 0

        homeworks = Grade.objects.filter(user=student, work__type__in=[0, 5, 6]).values('score', 'max_score')
        if not homeworks:
            homeworks_perc = None
        else:
            total = 0
            total_perc = 0
            for homework in homeworks:
                if homework['max_score'] <= 0:
                    continue
                homework_perc = round(homework['score'] / homework['max_score'] * 100)
                total_perc += homework_perc
                total += 1
            if total > 0:
                homeworks_perc = total_perc // total
            else:
                homeworks_perc = None

        classworks = Grade.objects.filter(work__is_homework=False, user=student).values('score', 'max_score')
        if not classworks:
            classworks_perc = None
        else:
            total = 0
            total_perc = 0
            for classwork in classworks:
                if classwork['max_score'] <= 0:
                    continue
                classwork_perc = round(classwork['score'] / classwork['max_score'] * 100)
                total_perc += classwork_perc
                total += 1
            if total > 0:
                classworks_perc = total_perc // total
            else:
                classworks_perc = None

        manas = Mana.objects.filter(Q(user=student) & Q(is_given=0))
        green = manas.filter(color='green').aggregate(Count('id'))["id__count"]
        blue = manas.filter(color='blue').aggregate(Count('id'))["id__count"]

        total_exp = student.experience
        lvl, exp, base_exp = count_lvl(total_exp)

        return HttpResponse(json.dumps({
            'last_homework_current': last_homework_perc_current,
            'last_homework_others': last_homework_perc_others,
            'last_classwork': last_classwork_perc,
            'homeworks': homeworks_perc,
            'classworks': classworks_perc,
            'green': green,
            'blue': blue,
            'lvl': lvl,
            'exp': exp,
            'base_exp': base_exp,
            'total_exp': total_exp
        }, ensure_ascii=False), status=200)
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


@swagger_auto_schema(method='GET', operation_summary="Получить персональную статистику ученика.",
                     manual_parameters=[id_param, theme_param, type_param],
                     responses=get_graph_responses,
                     operation_description=f"Уровни доступа: {permissions_operation_description['IsAuthenticated']}")
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEnabled])
def get_graph(request):
    try:
        id_ = get_variable('id', request)
        if not is_trusted(request, id_):
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Отказано в доступе.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=403)
        student = User.objects.get(id=id_, is_admin=False)
        school_class = student.school_class
        theme_id = get_variable('theme', request)
        filter_ = None
        if theme_id not in [None, '', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неправильно указана тема.', 'details': {}, 'instance': request.path},
                    ensure_ascii=False), status=400)
        if theme_id not in [None, '']:
            filter_ = 'theme'
        type_id = get_variable('type', request)
        if type_id not in [None, '', '0', '1', '2', '3', '4', '5', '6', '7', '8', '10', '11']:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Неправильно указан тип работы.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=400)
        if type_id not in [None, '']:
            filter_ = 'type'
        if filter_ is None:
            return HttpResponse(
                json.dumps(
                    {'state': 'error', 'message': f'Необходимо указать хотя бы один фильтр.', 'details': {},
                     'instance': request.path},
                    ensure_ascii=False), status=400)
        if filter_ == 'theme':
            if school_class != 4:
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Фильтрация по теме закрыта для пользователя.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=400)
            if theme_id == '1':
                grades = Grade.objects.filter(work__theme__id=theme_id, max_score__gt=0, work__school_class=school_class)
            elif theme_id == '8':
                grades = Grade.objects.filter(work__theme__id=theme_id, max_score__gt=0, work__type=7, work__school_class=school_class)
            elif theme_id == '9':
                grades = Grade.objects.filter(work__theme__id=theme_id, max_score__gt=0, work__type=6, work__school_class=school_class)
            else:
                grades = Grade.objects.filter(work__is_homework=True, work__theme__id=theme_id, max_score__gt=0, work__school_class=school_class)
            if theme_id in ['1', '8']:
                current = grades.filter(user=student).values('work_id').annotate(avg=Avg('score'))
                others = grades.exclude(user=student).values('work_id').annotate(avg=Avg('score'))
            elif theme_id == '9':
                current = grades.filter(user=student).values('grades', 'work_id')
                current_list = []
                for current_grade in current:
                    grades_ = current_grade['grades']
                    count = 0
                    for grade in grades_:
                        if is_number_float(grade):
                            if float(grade) > 0:
                                count += 1
                    current_list.append({
                        'work_id': current_grade['work_id'],
                        'avg': count
                    })
                current = current_list
                others = grades.exclude(user=student).values('grades', 'work_id')
                others_list = []
                others_dict = {}
                for others_grades in others:
                    if others_grades['work_id'] not in others_dict.keys():
                        others_dict[others_grades['work_id']] = []
                    grades_ = others_grades['grades']
                    count = 0
                    for grade in grades_:
                        if is_number_float(grade):
                            if float(grade) > 0:
                                count += 1
                    others_dict[others_grades['work_id']].append(count)
                for work_ in others_dict:
                    others_list.append({
                        'work_id': work_,
                        'avg': sum(others_dict[work_]) / len(others_dict[work_])
                    })
                others = others_list
            else:
                current = grades.filter(user=student).annotate(
                    percentage=ExpressionWrapper(F('score') * 100 / F('max_score'), output_field=FloatField())).values(
                    'work_id').annotate(avg=Avg('percentage'))
                others = grades.exclude(user=student).annotate(
                    percentage=ExpressionWrapper(F('score') * 100 / F('max_score'), output_field=FloatField())).values(
                    'work_id').annotate(avg=Avg('percentage'))
            current_grades = {}
            for work in current:
                current_grades[work['work_id']] = {'current': round(work['avg'], 1), 'others': 0}
            for work in others:
                if work['work_id'] in current_grades:
                    current_grades[work['work_id']]['others'] = round(work['avg'], 1)
            graph_list = []
            for work in current_grades:
                graph_list.append(current_grades[work])
            if theme_id not in GRAPH_CONFIG_THEMES:
                config = GRAPH_CONFIG_THEMES['default']
            else:
                config = GRAPH_CONFIG_THEMES[theme_id]
            return HttpResponse(json.dumps({
                'works': graph_list,
                'config': config
            }, ensure_ascii=False), status=200)
        else:
            if school_class == 4:
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Фильтрация по типу закрыта для пользователя.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=400)
            if type_id in ['0', '1', '10', '11']:
                grades = Grade.objects.filter(work__type=type_id, max_score__gt=0, work__school_class=school_class)
                current = grades.filter(user=student).annotate(
                    percentage=ExpressionWrapper(F('score') * 100 / F('max_score'), output_field=FloatField())).values(
                    'work_id').annotate(avg=Avg('percentage'))
                others = grades.exclude(user=student).annotate(
                    percentage=ExpressionWrapper(F('score') * 100 / F('max_score'), output_field=FloatField())).values(
                    'work_id').annotate(avg=Avg('percentage'))
                current_grades = {}
                for work in current:
                    current_grades[work['work_id']] = {'current': round(work['avg'], 1), 'others': 0}
                for work in others:
                    if work['work_id'] in current_grades:
                        current_grades[work['work_id']]['others'] = round(work['avg'], 1)
                graph_list = []
                for work in current_grades:
                    graph_list.append(current_grades[work])
                if type_id not in GRAPH_CONFIG_TYPES:
                    config = GRAPH_CONFIG_TYPES['default']
                else:
                    config = GRAPH_CONFIG_TYPES[type_id]
                return HttpResponse(json.dumps({
                    'works': graph_list,
                    'config': config
                }, ensure_ascii=False), status=200)
            else:
                return HttpResponse(
                    json.dumps(
                        {'state': 'error', 'message': f'Для данного типа нет графиков.', 'details': {},
                         'instance': request.path},
                        ensure_ascii=False), status=400)
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
