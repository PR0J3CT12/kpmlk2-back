# Generated by Django 5.0.6 on 2024-07-17 12:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='group',
        ),
    ]