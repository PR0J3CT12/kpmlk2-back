from django.db import models
from django.utils import timezone
import datetime


class Student(models.Model):
    id = models.IntegerField('student id', primary_key=True, editable=False)
    name = models.CharField('student name', max_length=20)
    login = models.CharField('student login', max_length=20)
    password = models.CharField('student password', max_length=20)
    experience = models.IntegerField('student experience', default=1)
    mana_earned = models.IntegerField('mana earned by student', default=0)
    last_homework_id = models.IntegerField('last homework id', default=1)
    last_classwork_id = models.IntegerField('last classwork id', default=1)
    is_admin = models.BooleanField('is this account is admin', default=0)
    school_class = models.IntegerField('student class', default=None, null=True, blank=True)

    def __str__(self):
        return f'{str(self.id)}'

    class Meta:
        db_table = 'students'


class Admin(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    permissions = models.IntegerField('admin permissions', default=0)

    def __str__(self):
        return f'{str(self.id)}'

    class Meta:
        db_table = 'admins'


class Theme(models.Model):
    name = models.CharField('theme name', max_length=20)
    type = models.IntegerField('theme type')
    school_class = models.IntegerField('student class', default=4)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        db_table = 'themes'


class Work(models.Model):
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


class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    mana = models.IntegerField('mana', default=0)
    score = models.FloatField('score', default=0)
    max_score = models.FloatField('max_score', default=0)
    grades = models.CharField('grades string', default=None, max_length=200)
    exercises = models.IntegerField('amount of exercises(current student)')

    class Meta:
        db_table = 'grades'


class Mana(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    color = models.CharField('mana color(green or blue)', max_length=5)
    is_given = models.BooleanField('is mana given', default=0)

    class Meta:
        db_table = 'mana'


class Message(models.Model):
    text = models.TextField('text of message')
    date_time = models.DateTimeField('message date', default=timezone.localtime(timezone.now()))

    def __str__(self):
        return f'{self.id}'

