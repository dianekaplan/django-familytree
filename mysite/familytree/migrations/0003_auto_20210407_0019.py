# Generated by Django 3.0.3 on 2021-04-07 00:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('familytree', '0002_person_living'),
    ]

    operations = [
        migrations.RenameField(
            model_name='person',
            old_name='resting_place',
            new_name='death_place',
        ),
    ]