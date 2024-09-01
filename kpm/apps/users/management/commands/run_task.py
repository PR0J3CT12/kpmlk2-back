from django.core.management.base import BaseCommand
from kpm.apps.works.tasks import works_deadlines, open_homeworks


class Command(BaseCommand):
    help = 'Update experience | python manage.py run_task id'

    def add_arguments(self, parser):
        parser.add_argument('id', type=int, help='Task id')

    def handle(self, *args, **kwargs):
        try:
            id_ = kwargs['id']
            if id_ == 1:
                open_homeworks.delay()
                self.stdout.write(f'Выполнена open_homeworks.')
            elif id_ == 2:
                works_deadlines.delay()
                self.stdout.write(f'Выполнена works_deadlines.')
            else:
                self.stdout.write(f'Некорректный id.')
        except Exception as e:
            self.stdout.write(f'Произошла ошибка | {str(e)}')