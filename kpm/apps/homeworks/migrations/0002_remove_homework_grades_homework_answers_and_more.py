# Generated by Django 4.2 on 2023-08-28 00:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homeworks', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='homework',
            name='grades',
        ),
        migrations.AddField(
            model_name='homework',
            name='answers',
            field=models.CharField(default='', max_length=1000, verbose_name='Форма с ответами'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='homeworkfile',
            name='ext',
            field=models.CharField(default='', max_length=10, verbose_name='Расширение файла'),
            preserve_default=False,
        ),
    ]