# Generated by Django 3.2 on 2021-09-14 11:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("familytree", "0029_image_parents_only")]

    operations = [
        migrations.RenameField(
            model_name="image", old_name="parents_only", new_name="spouses_only"
        )
    ]
