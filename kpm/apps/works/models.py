from django.db import models
from kpm.apps.themes.models import Theme


class Work(models.Model):
    id = models.AutoField('work id', primary_key=True, editable=False)
    name = models.CharField('work name', max_length=100)
    grades = models.CharField('work grades', max_length=100)
    max_score = models.FloatField('max score')
    exercises = models.IntegerField('amount of exercises')
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    school_class = models.IntegerField('student class', default=4)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        db_table = 'works'
