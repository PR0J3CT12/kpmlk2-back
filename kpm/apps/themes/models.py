from django.db import models


class Theme(models.Model):
    id = models.AutoField('theme id', primary_key=True, editable=False)
    name = models.CharField('theme name', max_length=20)
    school_class = models.IntegerField('student class', default=4)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        db_table = 'themes'