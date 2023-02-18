from django.db import models
from kpm.apps.works.models import Work
from kpm.apps.users.models import User


class Grade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    mana = models.IntegerField('mana', default=0)
    score = models.FloatField('score', default=0)
    max_score = models.FloatField('max_score', default=0)
    grades = models.CharField('grades string', default=None, max_length=200)
    exercises = models.IntegerField('amount of exercises(current student)')

    class Meta:
        db_table = 'grades'


class Mana(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    color = models.CharField('mana color(green or blue)', max_length=5)
    is_given = models.BooleanField('is mana given', default=0)

    class Meta:
        db_table = 'mana'
