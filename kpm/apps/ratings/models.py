from django.db import models
from kpm.apps.users.models import User


class League(models.Model):
    TYPE_CHOICES = (
        (0, 'Общий рейтинг'),
        (1, 'Рейтинг письменного экзамена'),
        (2, 'Рейтинг устного экзамена'),
        (3, 'Рейтинг репетиций'),
        (4, 'Другой рейтинг'),
    )
    id = models.AutoField('league id', primary_key=True, editable=False)
    name = models.CharField('league name', max_length=100)
    description = models.CharField('league description', max_length=1000, null=True, default=None)
    school_class = models.IntegerField('student class', default=4)
    rating_type = models.IntegerField('rating type', choices=TYPE_CHOICES, default=0)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        db_table = 'leagues'