# Generated by Django 3.2 on 2021-05-23 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("familytree", "0014_auto_20210510_1116")]

    operations = [
        migrations.AlterField(
            model_name="person",
            name="notes1",
            field=models.CharField(blank=True, default="", max_length=1200, null=True),
        ),
        migrations.AlterField(
            model_name="person",
            name="notes2",
            field=models.CharField(blank=True, default="", max_length=1200, null=True),
        ),
        migrations.AlterField(
            model_name="person",
            name="notes3",
            field=models.CharField(blank=True, default="", max_length=1200, null=True),
        ),
    ]