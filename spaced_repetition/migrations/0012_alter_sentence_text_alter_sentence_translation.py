# Generated by Django 5.0.3 on 2024-04-01 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spaced_repetition', '0011_sentence_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sentence',
            name='text',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='sentence',
            name='translation',
            field=models.TextField(),
        ),
    ]
