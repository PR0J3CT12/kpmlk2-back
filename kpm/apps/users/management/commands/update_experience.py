from django.core.management.base import BaseCommand
from kpm.apps.users.models import User, Admin
from kpm.apps.grades.models import Grade
from django.conf import settings
from django.db.models import Sum, Case, When, IntegerField


class Command(BaseCommand):
    help = 'Update experience | python manage.py update_experience'

    def handle(self, *args, **kwargs):
        try:
            students = User.objects.filter(is_admin=False)
            for student in students:
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
                student.save()
            self.stdout.write(f'Опыт пользователей обновлён.')
        except Exception as e:
            self.stdout.write(f'Произошла ошибка | {str(e)}')