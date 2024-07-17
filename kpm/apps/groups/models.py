from django.db import models
from kpm.apps.works.models import Work
from kpm.apps.users.models import User


class Group(models.Model):
    MARKER_CHOICES = (
        (0, '#ff8282'),
        (1, '#ffb875'),
        (2, '#fdff96'),
        (3, '#93ff91'),
        (4, '#78ffef'),
        (5, '#7776d6'),
        (6, '#bfa0de'),
        (7, None)
    )
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)

    class Meta:
        db_table = 'groups_users'


class Subgroup(models.Model):
    id = models.AutoField('id подгруппы', primary_key=True, editable=False)
    name = models.CharField('Название подгруппы', max_length=100)
    marker = models.CharField('Цвет подгруппы', default=None, null=True, max_length=7)
    school_class = models.IntegerField('student class', default=None, null=True, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        db_table = 'subgroups'


class SubgroupUser(models.Model):
    id = models.AutoField('id пары подгруппа - ученик', primary_key=True, editable=False)
    subgroup = models.ForeignKey(Subgroup, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'subgroups_users'
        unique_together = (('subgroup', 'user'),)


class SubgroupWorkDates(models.Model):
    id = models.AutoField('id даты выдачи работы', primary_key=True, editable=False)
    subgroup = models.ForeignKey(Subgroup, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    date = models.DateField('Дата выдачи работы')

    class Meta:
        db_table = 'subgroup_dates'
        unique_together = (('subgroup', 'work', 'date'),)