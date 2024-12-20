# Generated by Django 5.1.3 on 2024-11-20 21:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Area",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("notes", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="Consumable",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("notes", models.TextField(blank=True)),
                ("unit", models.CharField(max_length=25)),
                ("quantity", models.PositiveIntegerField()),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("notes", models.TextField(blank=True)),
                ("duration", models.DurationField(blank=True, null=True)),
                ("interval", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "frequency",
                    models.CharField(
                        choices=[
                            ("days", "Days"),
                            ("weeks", "Weeks"),
                            ("months", "Months"),
                        ],
                        default="months",
                        max_length=10,
                    ),
                ),
                (
                    "area",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tasks",
                        to="core.area",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Schedule",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("due_date", models.DateField()),
                ("completion_date", models.DateField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.task",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TaskConsumable",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.PositiveIntegerField(default=1)),
                (
                    "consumable",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.consumable",
                    ),
                ),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.task",
                    ),
                ),
            ],
            options={
                "unique_together": {("task", "consumable")},
            },
        ),
        migrations.AddField(
            model_name="consumable",
            name="tasks",
            field=models.ManyToManyField(
                related_name="consumables",
                through="core.TaskConsumable",
                to="core.task",
            ),
        ),
    ]
