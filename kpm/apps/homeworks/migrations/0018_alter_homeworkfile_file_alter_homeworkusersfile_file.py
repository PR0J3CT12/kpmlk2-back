# Generated by Django 4.2 on 2023-09-03 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homeworks', '0017_alter_homeworkfile_file_alter_homeworkusersfile_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homeworkfile',
            name='file',
            field=models.FileField(upload_to='', verbose_name='Файл новости'),
        ),
        migrations.AlterField(
            model_name='homeworkusersfile',
            name='file',
            field=models.FileField(upload_to='', verbose_name='Файл новости'),
        ),
    ]