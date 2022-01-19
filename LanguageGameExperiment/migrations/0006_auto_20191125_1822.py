# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('LanguageGameExperiment', '0005_auto_20191125_0121'),
    ]

    operations = [
        migrations.AddField(
            model_name='ladouseranswer',
            name='audio_listen_count',
            field=models.IntegerField(default=1, null=True),
        ),
        migrations.AddField(
            model_name='ladouseranswer',
            name='time_taken',
            field=models.CharField(null=True, max_length=200),
        ),
    ]
