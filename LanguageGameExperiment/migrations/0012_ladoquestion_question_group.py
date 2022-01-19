# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('LanguageGameExperiment', '0011_auto_20200423_0843'),
    ]

    operations = [
        migrations.AddField(
            model_name='ladoquestion',
            name='question_group',
            field=models.IntegerField(null=True, default=1),
        ),
    ]
