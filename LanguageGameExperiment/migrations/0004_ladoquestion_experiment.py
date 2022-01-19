# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('LanguageGameExperiment', '0003_auto_20191124_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='ladoquestion',
            name='experiment',
            field=models.ForeignKey(to='LanguageGameExperiment.LaDoExperiment', null=True, default=1),
        ),
    ]
