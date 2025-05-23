# Generated by Django 5.2 on 2025-04-30 08:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_add_subcategory_and_quote_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="BackgroundImage",
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
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                (
                    "image_url",
                    models.URLField(
                        help_text="Google Drive or other hosted image URL (1080x1080 px)"
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.RemoveField(
            model_name="quote",
            name="background_image_1",
        ),
        migrations.RemoveField(
            model_name="quote",
            name="background_image_2",
        ),
        migrations.RemoveField(
            model_name="quote",
            name="background_image_3",
        ),
        migrations.RemoveField(
            model_name="quote",
            name="background_image_4",
        ),
        migrations.RemoveField(
            model_name="quote",
            name="background_image_5",
        ),
        migrations.AddField(
            model_name="quote",
            name="custom_x_position",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="X position in pixels (only used with CUSTOM position)",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="quote",
            name="custom_y_position",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Y position in pixels (only used with CUSTOM position)",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="quote",
            name="default_font_color",
            field=models.CharField(default="#FFFFFF", max_length=7),
        ),
        migrations.AddField(
            model_name="quote",
            name="default_font_size",
            field=models.PositiveIntegerField(default=36),
        ),
        migrations.AddField(
            model_name="quote",
            name="default_font_style",
            field=models.CharField(
                choices=[
                    ("ARIAL", "Arial"),
                    ("TIMES", "Times New Roman"),
                    ("ROBOTO", "Roboto"),
                    ("MONTSERRAT", "Montserrat"),
                    ("OPENSANS", "Open Sans"),
                ],
                default="ARIAL",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="quote",
            name="default_text_position",
            field=models.CharField(
                choices=[
                    ("CENTER", "Center"),
                    ("TOP", "Top"),
                    ("BOTTOM", "Bottom"),
                    ("CUSTOM", "Custom"),
                ],
                default="CENTER",
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="quote",
            name="default_background",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="quotes",
                to="core.backgroundimage",
            ),
        ),
    ]
