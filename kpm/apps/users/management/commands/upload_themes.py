from django.core.management.base import BaseCommand
from kpm.apps.themes.models import Theme
from django.conf import settings


class Command(BaseCommand):
    help = 'Upload themes | python manage.py upload_themes'

    def handle(self, *args, **kwargs):
        try:
            themes = Theme.objects.all()
            if not themes:
                Theme.objects.create(name="Блицы", school_class=4)
                Theme.objects.create(name="Площадь", school_class=4)
                Theme.objects.create(name="Части", school_class=4)
                Theme.objects.create(name="Движение", school_class=4)
                Theme.objects.create(name="Совместная работа", school_class=4)
                Theme.objects.create(name="Обратный ход", school_class=4)
                Theme.objects.create(name="Головы и ноги", school_class=4)
                Theme.objects.create(name="Экзамен письменный", school_class=4)
                Theme.objects.create(name="Экзамен устный", school_class=4)
                Theme.objects.create(name="5 класс", school_class=5)
                Theme.objects.create(name="6 класс", school_class=6)
                Theme.objects.create(name="7 класс", school_class=7)
            self.stdout.write(f'Темы добавлены.')
        except Exception as e:
            self.stdout.write(f'Произошла ошибка | {str(e)}')