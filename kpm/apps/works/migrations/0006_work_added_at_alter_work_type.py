# Generated by Django 4.2 on 2023-08-19 22:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('works', '0005_work_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='work',
            name='added_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата создания работы'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='work',
            name='type',
            field=models.IntegerField(choices=[(0, 'Домашняя работа'), (1, 'Классная работа'), (2, 'Блиц'), (3, 'Письменный экзамен'), (4, 'Устный экзамен'), (5, 'Вне статистики')], default=0, verbose_name='theme type'),
        ),
    ]