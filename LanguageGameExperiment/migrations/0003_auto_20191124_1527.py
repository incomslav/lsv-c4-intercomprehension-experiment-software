# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('LanguageGameExperiment', '0002_ladoexperimentparticipation_ladoexperimentstatistics_ladouseranswer'),
    ]

    operations = [
        migrations.CreateModel(
            name='LaDoExperimentIntro',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('Intro_line', models.TextField(null=True)),
                ('line_number', models.IntegerField(null=True)),
                ('is_active', models.NullBooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name='ladoexperiment',
            name='experiment_description',
            field=models.CharField(null=True, max_length=400),
        ),
        migrations.AddField(
            model_name='ladoexperiment',
            name='has_audio',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ladoexperimentintro',
            name='experiment',
            field=models.ForeignKey(null=True, to='LanguageGameExperiment.LaDoExperiment'),
        ),
    ]
