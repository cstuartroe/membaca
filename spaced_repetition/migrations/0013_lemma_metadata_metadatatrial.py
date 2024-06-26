# Generated by Django 5.0.3 on 2024-04-07 21:25

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spaced_repetition', '0012_alter_sentence_text_alter_sentence_translation'),
    ]

    operations = [
        migrations.AddField(
            model_name='lemma',
            name='metadata',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.CreateModel(
            name='MetadataTrial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_created', models.DateTimeField()),
                ('metadata_field', models.CharField(max_length=16)),
                ('choices', models.CharField(max_length=256)),
                ('choice', models.CharField(max_length=128)),
                ('correct', models.BooleanField()),
                ('easiness', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)])),
                ('lemma_add', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spaced_repetition.lemmaadd')),
            ],
        ),
    ]
