# Generated by Django 5.0.6 on 2024-08-17 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='league',
            name='description',
            field=models.CharField(blank=True, default=None, max_length=1000, null=True, verbose_name='league description'),
        ),
    ]
