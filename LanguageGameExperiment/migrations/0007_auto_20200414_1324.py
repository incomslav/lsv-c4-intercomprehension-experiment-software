# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('LanguageGameExperiment', '0006_auto_20191125_1822'),
    ]

    operations = [
        migrations.AddField(
            model_name='ladoexperiment',
            name='experiment_type',
            field=models.CharField(max_length=100, default='lado', choices=[('primal', 'primal'), ('lado', 'lado')]),
        ),
        migrations.AddField(
            model_name='ladoexperiment',
            name='publish',
            field=models.BooleanField(default=True),
        ),
    ]
