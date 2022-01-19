# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0010_auto_20180606_0002'),
        ('LanguageGameExperiment', '0004_ladoquestion_experiment'),
    ]

    operations = [
        migrations.AddField(
            model_name='ladouseranswer',
            name='answered_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='ladouseranswer',
            name='answering_user',
            field=models.ForeignKey(related_name='lado_given_answers', null=True, to='Users.UserInfo'),
        ),
        migrations.AlterField(
            model_name='ladouseranswer',
            name='participation',
            field=models.ForeignKey(related_name='lado_given_answers', null=True, to='LanguageGameExperiment.LaDoExperimentParticipation'),
        ),
        migrations.AlterField(
            model_name='ladouseranswer',
            name='question',
            field=models.ForeignKey(related_name='lado_answers', null=True, to='LanguageGameExperiment.LaDoQuestion'),
        ),
    ]
