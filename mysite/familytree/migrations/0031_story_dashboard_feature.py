# Generated by Django 3.2 on 2021-09-14 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("familytree", "0030_rename_parents_only_image_spouses_only")]

    operations = [
        migrations.AddField(
            model_name="story",
            name="dashboard_feature",
            field=models.BooleanField(default=True, null=True),
        )
    ]
