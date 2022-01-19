# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('LanguageGameExperiment', '0007_auto_20200414_1324'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrimalExperimentQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('token1_name', models.CharField(max_length=150, null=True)),
                ('token1_gloss', models.CharField(max_length=150, null=True)),
                ('token1_language', models.CharField(max_length=100, null=True)),
                ('token1_filename', models.TextField(null=True)),
                ('token2_name', models.CharField(max_length=150, null=True)),
                ('token2_gloss', models.CharField(max_length=150, null=True)),
                ('token2_filename', models.TextField(null=True)),
                ('token2_language', models.CharField(max_length=100, null=True)),
                ('native_language', models.CharField(max_length=100, null=True)),
                ('priming_type', models.CharField(max_length=100, null=True, default='unknown', choices=[('phonetic', 'phonetic'), ('cognate', 'cognate'), ('filler', 'filler'), ('unknown', 'unknown')])),
                ('correct_response', models.CharField(max_length=100, choices=[('a', 'word'), ('l', 'non-word')])),
                ('phonetic_distance', models.FloatField(null=True)),
                ('csv_file_path', models.TextField(null=True)),
                ('csv_file_name', models.CharField(max_length=200, null=True)),
                ('experiment', models.ForeignKey(null=True, default=0, to='LanguageGameExperiment.LaDoExperiment')),
            ],
        ),
    ]
