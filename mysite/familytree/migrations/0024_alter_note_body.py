# Generated by Django 3.2 on 2021-07-25 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("familytree", "0023_story_branches")]

    operations = [
        migrations.AlterField(
            model_name="note", name="body", field=models.CharField(max_length=3000)
        )
    ]
