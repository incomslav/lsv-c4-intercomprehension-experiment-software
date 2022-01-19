# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('LanguageGameExperiment', '0013_auto_20200603_2300'),
    ]

    operations = [
        migrations.AddField(
            model_name='primalexperimentparticipation',
            name='primal_prolific_user',
            field=models.ForeignKey(blank=True, null=True, default=None, to='LanguageGameExperiment.LadoProlificUser'),
        ),
        migrations.AlterField(
            model_name='ladouseranswer',
            name='answering_user',
            field=models.ForeignKey(blank=True, null=True, default=None, related_name='lado_given_answers', to='Users.UserInfo'),
        ),
        migrations.AlterField(
            model_name='primalexperimentparticipation',
            name='user',
            field=models.ForeignKey(blank=True, null=True, default=None, to='Users.UserInfo'),
        ),
    ]
