from django.db import models


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


class Subgroup(models.Model):
    id = models.AutoField('id подгруппы', primary_key=True, editable=False)
    name = models.CharField('Название группы', max_length=100)
    marker = models.CharField('Цвет группы', default=None, null=True, max_length=7)
    school_class = models.IntegerField('student class', default=None, null=True, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        db_table = 'subgroups'