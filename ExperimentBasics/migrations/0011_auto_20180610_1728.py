# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ExperimentBasics', '0010_experiment_folder_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='foreign_script',
            field=models.CharField(null=True, blank=True, max_length='100', default=None),
        ),
        migrations.AddField(
            model_name='experiment',
            name='native_script',
            field=models.CharField(null=True, blank=True, max_length='100', default=None),
        ),
    ]
