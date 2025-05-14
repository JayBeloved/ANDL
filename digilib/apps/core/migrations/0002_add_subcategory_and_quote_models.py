# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, help_text='Category image for display in cards', null=True, upload_to='categories/'),
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('slug', models.SlugField(editable=False, unique=True)),
                ('image', models.ImageField(blank=True, help_text='Subcategory image for display in cards', null=True, upload_to='subcategories/')),
                ('parent_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='core.category')),
            ],
            options={
                'verbose_name': 'Sub Category',
                'verbose_name_plural': 'Sub Categories',
                'ordering': ['name'],
                'unique_together': {('name', 'parent_category')},
            },
        ),
        migrations.AddField(
            model_name='content',
            name='subcategory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contents', to='core.subcategory'),
        ),
        migrations.AlterField(
            model_name='content',
            name='content_type',
            field=models.CharField(choices=[('SERMON', 'Sermon'), ('BOOK', 'Book'), ('WRITE_UP', 'Write-Up'), ('QUOTE', 'Quote')], default='WRITE_UP', max_length=20),
        ),
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quote_text', models.TextField()),
                ('default_background', models.CharField(choices=[('BG1', 'Background 1'), ('BG2', 'Background 2'), ('BG3', 'Background 3'), ('BG4', 'Background 4'), ('BG5', 'Background 5')], default='BG1', max_length=3)),
                ('background_image_1', models.ImageField(blank=True, null=True, upload_to='quotes/backgrounds/')),
                ('background_image_2', models.ImageField(blank=True, null=True, upload_to='quotes/backgrounds/')),
                ('background_image_3', models.ImageField(blank=True, null=True, upload_to='quotes/backgrounds/')),
                ('background_image_4', models.ImageField(blank=True, null=True, upload_to='quotes/backgrounds/')),
                ('background_image_5', models.ImageField(blank=True, null=True, upload_to='quotes/backgrounds/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('shares_count', models.PositiveIntegerField(default=0)),
                ('content', models.ForeignKey(limit_choices_to={'content_type': 'QUOTE'}, on_delete=django.db.models.deletion.CASCADE, related_name='quotes', to='core.content')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]