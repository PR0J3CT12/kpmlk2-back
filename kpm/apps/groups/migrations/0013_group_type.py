# Generated by Django 5.0.6 on 2024-08-16 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0012_groupworkdate_is_given'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='type',
            field=models.IntegerField(default=None, null=True, verbose_name='Тип группы'),
        ),
    ]