# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ExperimentBasics', '0009_experiment_stimuli_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='folder_name',
            field=models.CharField(max_length='500', null=True, blank=True),
        ),
    ]
