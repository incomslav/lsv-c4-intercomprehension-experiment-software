# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0011_auto_20200422_2227'),
        ('LanguageGameExperiment', '0008_primalexperimentquestion'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrimalExperimentParticipation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('started_on', models.DateTimeField(auto_now=True)),
                ('completed_on', models.DateTimeField(null=True)),
                ('retry_count', models.IntegerField(default=0)),
                ('is_active', models.NullBooleanField(default=True)),
                ('is_delete', models.NullBooleanField(default=False)),
                ('experiment', models.ForeignKey(null=True, to='LanguageGameExperiment.LaDoExperiment')),
                ('user', models.ForeignKey(null=True, to='Users.UserInfo')),
            ],
        ),
        migrations.CreateModel(
            name='PrimalExperimentStatistics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('total_question', models.IntegerField(default=0)),
                ('total_correct', models.IntegerField(default=0)),
                ('total_time_in_min', models.FloatField(default=0)),
                ('avg_time_in_sec', models.FloatField(default=0)),
                ('completed_on', models.DateTimeField(null=True)),
                ('inserted_on', models.DateTimeField(auto_now=True)),
                ('is_active', models.NullBooleanField(default=True)),
                ('is_delete', models.NullBooleanField(default=False)),
                ('participation', models.ForeignKey(null=True, to='LanguageGameExperiment.PrimalExperimentParticipation')),
            ],
        ),
        migrations.CreateModel(
            name='PrimalExperimentUserAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('question_play_order', models.IntegerField(default=0)),
                ('user_answer', models.CharField(max_length=150, null=True)),
                ('is_answered', models.NullBooleanField(default=False)),
                ('is_active', models.NullBooleanField(default=True)),
                ('answered_time', models.DateTimeField(null=True)),
                ('time_taken', models.CharField(max_length=200, null=True)),
                ('audio_listen_count', models.IntegerField(null=True, default=1)),
                ('answering_user', models.ForeignKey(null=True, related_name='primal_given_answers', to='Users.UserInfo')),
                ('participation', models.ForeignKey(null=True, related_name='primal_given_answers', to='LanguageGameExperiment.LaDoExperimentParticipation')),
                ('question', models.ForeignKey(null=True, related_name='primal_answers', to='LanguageGameExperiment.PrimalExperimentQuestion')),
            ],
        ),
    ]
