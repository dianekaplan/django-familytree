# Generated by Django 3.2 on 2021-06-22 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('familytree', '0015_auto_20210523_1349'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='external_author',
            field=models.BooleanField(default=False, null=True),
        ),
    ]