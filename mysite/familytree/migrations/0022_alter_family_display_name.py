# Generated by Django 3.2 on 2021-07-11 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('familytree', '0021_auto_20210711_1016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='display_name',
            field=models.CharField(blank=True, max_length=60),
        ),
    ]
