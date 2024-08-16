from django.db import models
from kpm.apps.themes.models import Theme
from django.utils.deconstruct import deconstructible
import os
from kpm.apps.users.models import User
from django.core.exceptions import ValidationError


@deconstructible
class PathRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        return os.path.join(self.path, filename)


path_and_rename = PathRename("homeworks/")


class Work(models.Model):
    TYPE_CHOICES = (
        (0, 'Домашняя работа'),
        (1, 'Классная работа'),
        (2, 'Блиц'),
        (3, 'Письменный экзамен классный'),
        (4, 'Устный экзамен классный'),
        (5, 'Письменный экзамен домашний'),
        (6, 'Устный экзамен домашний'),
        (7, 'Письменный экзамен домашний(баллы 2007)'),
        (8, 'Письменный экзамен классный(баллы 2007)'),
        (9, 'Вне статистики'),
        (10, 'Зачет'),
        (11, 'Проверка на рептилоида'),
    )
    id = models.AutoField('work id', primary_key=True, editable=False)
    name = models.CharField('work name', max_length=100)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    school_class = models.IntegerField('student class', default=4)
    is_homework = models.BooleanField('is homework')
    type = models.IntegerField('theme type', choices=TYPE_CHOICES, default=0)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='author', default=None)

    # Grades fields
    grades = models.JSONField('work grades')
    max_score = models.FloatField('max score')
    exercises = models.IntegerField('amount of exercises')

    # Object fields
    has_attachments = models.BooleanField('has attachments', default=False)
    text = models.TextField('Текст домашней работы', default=None, null=True, blank=True)
    answers = models.JSONField('Форма с ответами', null=True, blank=True)
    is_closed = models.BooleanField('Работа закрыта', default=False)

    # Date fields
    created_at = models.DateTimeField('Дата создания работы', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления работы', auto_now_add=True)

    def clean(self):
        if self.work.school_class != self.theme.school_class:
            raise ValidationError(f"Работа {self.work.id} не соответствует классу темы '{self.theme.id}'.")
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

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


class WorkFile(models.Model):
    id = models.AutoField('id файла', primary_key=True, editable=False)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    file = models.FileField('Файл работы', upload_to=path_and_rename)
    ext = models.CharField('Расширение файла', max_length=100)

    def __str__(self):
        return f'{str(self.id)}'

    class Meta:
        db_table = 'works_files'


class WorkUser(models.Model):
    id = models.AutoField('id связи', primary_key=True, editable=False)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_done = models.BooleanField('Сдал ли работу ученик', default=False)
    comment = models.TextField('Комментарий преподавателя', default="")
    is_checked = models.BooleanField('Проверена ли работа', default=False)
    checker = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='checker', null=True)
    answers = models.JSONField('Форма с ответами')
    is_closed = models.BooleanField('Закрыта ли работа', default=False)

    answered_at = models.DateTimeField('Дата ответа', default=None, null=True)
    checked_at = models.DateTimeField('Дата проверки', default=None, null=True)
    added_at = models.DateTimeField('Дата выдачи работы', null=True, auto_now_add=True)

    def clean(self):
        if self.user.school_class != self.work.school_class:
            raise ValidationError(f"Ученик {self.user.id} не соответствует классу работы '{self.work.id}'.")
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{str(self.id)}'

    class Meta:
        db_table = 'works_users'
        unique_together = ('work', 'user')


class WorkUserFile(models.Model):
    id = models.AutoField('id файла пользователя', primary_key=True, editable=False)
    link = models.ForeignKey(WorkUser, on_delete=models.CASCADE)
    file = models.FileField('Файл работы', upload_to=path_and_rename)
    ext = models.CharField('Расширение файла', max_length=100)

    def __str__(self):
        return f'{str(self.id)}'

    class Meta:
        db_table = 'works_users_files'
