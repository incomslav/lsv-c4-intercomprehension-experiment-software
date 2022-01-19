# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('LanguageGameExperiment', '0010_auto_20200423_0203'),
    ]

    operations = [
        migrations.AddField(
            model_name='primalexperimentuseranswer',
            name='running_avg_time',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='primalexperimentuseranswer',
            name='running_correct',
            field=models.IntegerField(default=0),
        ),
    ]
