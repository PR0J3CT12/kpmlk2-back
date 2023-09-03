from django.db import models
from kpm.apps.users.models import User
from uuid import uuid4
import os
from django.utils.deconstruct import deconstructible


@deconstructible
class PathRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        return os.path.join(self.path, filename)


path_and_rename = PathRename("homeworks/")


class Homework(models.Model):
    id = models.AutoField('id домашней работы', primary_key=True, editable=False)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='author')
    title = models.CharField('Заголовок домашней работы', max_length=200)
    text = models.TextField('Текст домашней работы')
    score = models.IntegerField('Максимальный балл за работу')
    answers = models.CharField('Форма с ответами', max_length=5000)
    fields = models.IntegerField('Количество полей в форме')
    school_class = models.IntegerField('Класс работы', default=4)
    created_at = models.DateTimeField('Дата создания домашней работы', auto_now_add=True)
    is_closed = models.BooleanField('Домашняя работа закрыта', default=False)

    def __str__(self):
        return f'{str(self.id)}'

    class Meta:
        db_table = 'homeworks'


class HomeworkFile(models.Model):
    id = models.AutoField('id файла', primary_key=True, editable=False)
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE)
    file = models.FileField('Файл новости', upload_to=path_and_rename)
    ext = models.CharField('Расширение файла', max_length=10)

    def __str__(self):
        return f'{str(self.id)}'

    class Meta:
        db_table = 'homeworks_files'


class HomeworkUsers(models.Model):
    id = models.AutoField('id связи', primary_key=True, editable=False)
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_done = models.BooleanField('Сдал ли работу ученик', default=False)
    comment = models.TextField('Комментарий преподавателя', default=None, null=True)
    is_checked = models.BooleanField('Проверена ли работа', default=False)
    score = models.IntegerField('Оценка за работу', default=0)
    answers = models.CharField('Форма с ответами', max_length=5000)
    answered_at = models.DateTimeField('Дата ответа', default=None, null=True)

    def __str__(self):
        return f'{str(self.id)}'

    class Meta:
        db_table = 'homeworks_users'
        unique_together = ('homework', 'user',)


class HomeworkUsersFile(models.Model):
    id = models.AutoField('id файла пользователя', primary_key=True, editable=False)
    link = models.ForeignKey(HomeworkUsers, on_delete=models.CASCADE)
    file = models.FileField('Файл новости', upload_to=path_and_rename)
    ext = models.CharField('Расширение файла', max_length=10)

    def __str__(self):
        return f'{str(self.id)}'

    class Meta:
        db_table = 'homeworks_users_files'