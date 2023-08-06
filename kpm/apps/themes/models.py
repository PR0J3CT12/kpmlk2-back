from django.db import models


class Theme(models.Model):
    TYPE_CHOICES = (
        (0, 'Домашняя работа'),
        (1, 'Классная работа'),
        (2, 'Блиц'),
        (3, 'Домашний письменный экзамен'),
        (4, 'Домашний устный экзамен'),
        (5, 'Письменный экзамен'),
        (6, 'Устный экзамен'),
        (7, 'Вне статистики'),
    )
    id = models.AutoField('theme id', primary_key=True, editable=False)
    name = models.CharField('theme name', max_length=20)
    type = models.IntegerField('theme type', choices=TYPE_CHOICES)
    is_homework = models.BooleanField('is homework')
    school_class = models.IntegerField('student class', default=4)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        db_table = 'themes'