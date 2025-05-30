# Generated by Django 5.2 on 2025-05-26 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_alter_quote_default_font_style"),
    ]

    operations = [
        migrations.AlterField(
            model_name="quote",
            name="default_font_style",
            field=models.CharField(
                choices=[
                    ("ARIAL", "Arial"),
                    ("TIMES", "Times New Roman"),
                    ("DAILYQUOTES", "Daily Quotes"),
                    ("LATO-BOLD", "Lato Bold"),
                    ("LATO-ITALIC", "Lato Italic"),
                    ("LATO-REGULAR", "Lato Regular"),
                    ("POPPINS-ITALIC", "Poppins Italic"),
                    ("POPPINS-REGULAR", "Poppins Regular"),
                    ("POPPINS-THIN", "Poppins Thin"),
                    ("QUOTE", "Quote"),
                ],
                default="ARIAL",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="quote",
            name="default_text_position",
            field=models.CharField(
                choices=[
                    ("CENTER", "Center"),
                    ("TOP", "Top"),
                    ("BOTTOM", "Bottom"),
                    ("LEFT", "Left"),
                    ("RIGHT", "Right"),
                    ("CUSTOM", "Custom"),
                ],
                default="CENTER",
                max_length=10,
            ),
        ),
    ]
