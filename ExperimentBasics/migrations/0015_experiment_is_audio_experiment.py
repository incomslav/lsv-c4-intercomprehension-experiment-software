# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2019-05-02 09:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ExperimentBasics', '0014_retryexperimentstatistics'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='is_audio_experiment',
            field=models.BooleanField(default=False),
        ),
    ]
