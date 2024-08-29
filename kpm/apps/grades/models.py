from django.db import models
from kpm.apps.works.models import Work
from kpm.apps.users.models import User


class Grade(models.Model):
    id = models.AutoField('grade id', primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    score = models.FloatField('score', default=0)
    max_score = models.FloatField('max_score', default=0)
    grades = models.JSONField('grades string', default=None)
    exercises = models.IntegerField('amount of exercises(current student)')

    class Meta:
        db_table = 'grades'


class Mana(models.Model):
    id = models.AutoField('mana id', primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    color = models.CharField('mana color(green or blue)', max_length=5)
    is_given = models.BooleanField('is mana given', default=0)
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mana'
