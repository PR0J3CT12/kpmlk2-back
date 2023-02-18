from django.db import models


class Theme(models.Model):
    name = models.CharField('theme name', max_length=20)
    type = models.IntegerField('theme type')
    school_class = models.IntegerField('student class', default=4)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        db_table = 'themes'