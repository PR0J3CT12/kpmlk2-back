from django.db import models
from kpm.apps.works.models import Work
from kpm.apps.users.models import User
from django.utils.deconstruct import deconstructible
from django.core.exceptions import ValidationError
import os


@deconstructible
class PathRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        return os.path.join(self.path, filename)


path_and_rename = PathRename("classworks/")


class Group(models.Model):
    TYPE_CHOICES = (
        (0, 'Продвинутые'),
        (1, 'Углублённые'),
        (2, 'Углублённые алгебра'),
        (3, 'Углублённые геометрия'),
    )
    id = models.AutoField('id группы', primary_key=True, editable=False)
    name = models.CharField('Название группы', max_length=100)
    marker = models.CharField('Цвет группы', default=None, null=True, max_length=7)
    type = models.IntegerField('Тип группы', default=None, null=True)
    school_class = models.IntegerField('student class', default=None, null=True, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        db_table = 'groups'


class GroupUser(models.Model):
    id = models.AutoField('id пары группа - ученик', primary_key=True, editable=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def clean(self):
        if self.user.school_class != self.group.school_class:
            raise ValidationError(f"Ученик {self.user.id} не соответствует классу группы '{self.group.id}'.")
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'groups_users'


class GroupWorkDate(models.Model):
    id = models.AutoField('id тройки группа - дата - работа', primary_key=True, editable=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    work = models.OneToOneField(Work, on_delete=models.CASCADE)
    date = models.DateField('Дата выполнения работы', null=True, blank=True, default=None)
    is_given = models.BooleanField('Отработала ли таска', default=False)

    def clean(self):
        if self.work.school_class != self.group.school_class:
            raise ValidationError(f"Работа {self.work.id} не соответствует классу группы '{self.group.id}'.")
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('group', 'work')
        db_table = 'groups_works_dates'


class GroupWorkFile(models.Model):
    id = models.AutoField('id тройки файла классной работы подгруппы', primary_key=True, editable=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    file = models.FileField('Файл работы', upload_to=path_and_rename)
    ext = models.CharField('Расширение файла', max_length=100)
    added_at = models.DateTimeField('Дата загрузки файла', auto_now_add=True)

    def clean(self):
        if self.work.school_class != self.group.school_class:
            raise ValidationError(f"Работа {self.work.id} не соответствует классу группы '{self.group.id}'.")
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'classworks_files'