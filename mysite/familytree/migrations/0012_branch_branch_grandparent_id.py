# Generated by Django 3.2 on 2021-04-25 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("familytree", "0011_auto_20210421_1321")]

    operations = [
        migrations.AddField(
            model_name="branch",
            name="branch_grandparent_id",
            field=models.IntegerField(blank=True, null=True),
        )
    ]