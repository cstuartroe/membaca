# Generated by Django 5.0.7 on 2024-11-17 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spaced_repetition', '0021_word_occurrences'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sentence',
            name='format_level',
            field=models.CharField(choices=[('h1', 'h1'), ('h2', 'h2'), ('h3', 'h3'), ('p', 'p'), ('ns', 'new section'), ('in', 'indented')], default='p', max_length=2),
        ),
    ]
