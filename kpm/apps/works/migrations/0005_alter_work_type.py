# Generated by Django 5.0.6 on 2024-08-16 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('works', '0004_workuser_is_closed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='work',
            name='type',
            field=models.IntegerField(choices=[(0, 'Домашняя работа'), (1, 'Классная работа'), (2, 'Блиц'), (3, 'Письменный экзамен классный'), (4, 'Устный экзамен классный'), (5, 'Письменный экзамен домашний'), (6, 'Устный экзамен домашний'), (7, 'Письменный экзамен домашний(баллы 2007)'), (8, 'Письменный экзамен классный(баллы 2007)'), (9, 'Вне статистики'), (10, 'Зачет'), (11, 'Проверка на рептилоида')], default=0, verbose_name='theme type'),
        ),
    ]