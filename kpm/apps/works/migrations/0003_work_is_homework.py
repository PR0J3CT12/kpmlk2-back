# Generated by Django 4.2 on 2023-08-19 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('works', '0002_alter_work_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='work',
            name='is_homework',
            field=models.BooleanField(default=0, verbose_name='is homework'),
        ),
    ]