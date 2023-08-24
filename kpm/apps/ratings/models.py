from django.db import models
from kpm.apps.users.models import User


class League(models.Model):
    id = models.AutoField('league id', primary_key=True, editable=False)
    name = models.CharField('league name', max_length=100, unique=True)
    school_class = models.IntegerField('student class', default=4)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        db_table = 'leagues'


class LeagueUser(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        db_table = 'leagues_users'