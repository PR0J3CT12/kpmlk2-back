# Generated by Django 4.2 on 2023-08-30 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homeworks', '0012_remove_homeworkusers_answers_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='homeworkusers',
            name='answers',
            field=models.CharField(default='', max_length=5000, verbose_name='Форма с ответами'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='homeworkusers',
            name='is_done',
            field=models.BooleanField(default=False, verbose_name='Сдал ли работу ученик'),
        ),
    ]