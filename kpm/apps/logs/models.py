from django.db import models
from django.utils import timezone
import datetime


class Log(models.Model):
    operation = models.CharField('event operation', max_length=30)
    from_table = models.CharField('event table', max_length=30)
    date_time = models.DateTimeField('event date', auto_now_add=True)
    details = models.TextField('event details', default=None)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        db_table = 'logs'