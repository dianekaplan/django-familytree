# Generated by Django 3.2 on 2021-08-14 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("familytree", "0026_profile_limited")]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="timezone",
            field=models.CharField(default="US/Eastern", max_length=100, null=True),
        )
    ]
