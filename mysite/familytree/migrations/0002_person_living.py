# Generated by Django 3.0.3 on 2021-04-03 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("familytree", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="person",
            name="living",
            field=models.BooleanField(default=False, null=True),
        )
    ]
