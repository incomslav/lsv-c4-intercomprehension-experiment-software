# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ExperimentBasics', '0008_auto_20180508_1444'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='stimuli_file',
            field=models.CharField(blank=True, null=True, max_length='1000'),
        ),
    ]
