# Generated by Django 5.0.3 on 2024-03-26 03:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spaced_repetition', '0003_alter_wordinsentence_lemma'),
    ]

    operations = [
        migrations.AlterField(
            model_name='substring',
            name='word',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='substrings', to='spaced_repetition.wordinsentence'),
        ),
    ]