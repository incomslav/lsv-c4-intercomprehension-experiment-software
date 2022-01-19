# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('LanguageGameExperiment', '0009_primalexperimentparticipation_primalexperimentstatistics_primalexperimentuseranswer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='primalexperimentuseranswer',
            name='participation',
            field=models.ForeignKey(null=True, related_name='primal_given_answers', to='LanguageGameExperiment.PrimalExperimentParticipation'),
        ),
    ]
