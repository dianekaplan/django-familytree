# Generated by Django 3.2 on 2021-09-14 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("familytree", "0027_profile_timezone")]

    operations = [
        migrations.AddField(
            model_name="image",
            name="notes",
            field=models.CharField(blank=True, max_length=500, null=True),
        )
    ]
