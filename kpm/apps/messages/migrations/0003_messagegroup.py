# Generated by Django 4.2 on 2023-11-30 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messages_', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageGroup',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False, verbose_name='group id')),
                ('datetime', models.DateTimeField(auto_now_add=True, verbose_name='group datetime')),
            ],
            options={
                'db_table': 'messages_groups',
            },
        ),
    ]