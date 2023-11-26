from django.db import models
from kpm.apps.themes.models import Theme


class Work(models.Model):
    TYPE_CHOICES = (
        (0, 'Домашняя работа'),
        (1, 'Классная работа'),
        (2, 'Блиц'),
        (3, 'Письменный экзамен'),
        (4, 'Устный экзамен'),
        (5, 'Письменный экзамен дз'),
        (6, 'Устный экзамен дз'),
        (7, 'Письменный экзамен дз(баллы 2007)'),
        (8, 'Письменный экзамен(баллы 2007)'),
        (9, 'Вне статистики'),
    )
    id = models.AutoField('work id', primary_key=True, editable=False)
    name = models.CharField('work name', max_length=100)
    grades = models.CharField('work grades', max_length=100)
    max_score = models.FloatField('max score')
    exercises = models.IntegerField('amount of exercises')
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    school_class = models.IntegerField('student class', default=4)
    is_homework = models.BooleanField('is homework')
    type = models.IntegerField('theme type', choices=TYPE_CHOICES, default=0)
    added_at = models.DateTimeField('Дата создания работы', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления работы', auto_now_add=True)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        db_table = 'works'


class Exam(models.Model):
    id = models.AutoField('link id', primary_key=True, editable=False)
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='work')
    work_2007 = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='work_2007')

    def __str__(self):
        return f'{self.id}'

    class Meta:
        db_table = 'exam_links'
