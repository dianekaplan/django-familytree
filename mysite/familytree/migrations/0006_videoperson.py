# Generated by Django 3.2 on 2021-04-20 12:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("familytree", "0005_auto_20210417_1452")]

    operations = [
        migrations.CreateModel(
            name="VideoPerson",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(blank=True, null=True)),
                (
                    "person",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="vid_person_id",
                        to="familytree.person",
                    ),
                ),
                (
                    "video",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="video_id",
                        to="familytree.video",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "VideoPerson records",
                "db_table": "video_person",
            },
        )
    ]
