# Generated by Django 3.2 on 2021-09-15 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("familytree", "0031_story_dashboard_feature")]

    operations = [
        migrations.AlterField(
            model_name="family",
            name="display_name",
            field=models.CharField(blank=True, max_length=75),
        ),
        migrations.AlterField(
            model_name="person",
            name="birthplace",
            field=models.CharField(blank=True, default="", max_length=80, null=True),
        ),
    ]
