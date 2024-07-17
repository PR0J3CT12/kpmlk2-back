from django.db import models
from kpm.apps.works.models import Work
from kpm.apps.users.models import User


class Group(models.Model):
    id = models.AutoField('id группы', primary_key=True, editable=False)
    name = models.CharField('Название группы', max_length=100)
    marker = models.CharField('Цвет группы', default=None, null=True, max_length=7)
    school_class = models.IntegerField('student class', default=None, null=True, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        db_table = 'groups'


class GroupUser(models.Model):
    id = models.AutoField('id пары группа - ученик', primary_key=True, editable=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'groups_users'


class GroupWorkDate(models.Model):
    id = models.AutoField('id тройки группа - дата - работа', primary_key=True, editable=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    work = models.OneToOneField(Work, on_delete=models.CASCADE)
    date = models.DateField('Дата выполнения работы')

    class Meta:
        db_table = 'groups_works_dates'