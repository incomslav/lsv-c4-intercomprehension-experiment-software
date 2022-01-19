# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0010_auto_20180606_0002'),
        ('LanguageGameExperiment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LaDoExperimentParticipation',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('started_on', models.DateTimeField(auto_now=True)),
                ('completed_on', models.DateTimeField(null=True)),
                ('retry_count', models.IntegerField(default=0)),
                ('is_active', models.NullBooleanField(default=True)),
                ('is_delete', models.NullBooleanField(default=False)),
                ('experiment', models.ForeignKey(to='LanguageGameExperiment.LaDoExperiment', null=True)),
                ('user', models.ForeignKey(to='Users.UserInfo', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LaDoExperimentStatistics',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('total_question', models.IntegerField(default=0)),
                ('total_correct', models.IntegerField(default=0)),
                ('total_time_in_min', models.FloatField(default=0)),
                ('avg_time_in_sec', models.FloatField(default=0)),
                ('completed_on', models.DateTimeField(null=True)),
                ('inserted_on', models.DateTimeField(auto_now=True)),
                ('is_active', models.NullBooleanField(default=True)),
                ('is_delete', models.NullBooleanField(default=False)),
                ('participation', models.ForeignKey(to='LanguageGameExperiment.LaDoExperimentParticipation', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LaDoUserAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('user_answer', models.CharField(null=True, max_length=150)),
                ('answer_confidence', models.IntegerField(default=0, null=True)),
                ('is_answered', models.NullBooleanField(default=False)),
                ('is_active', models.NullBooleanField(default=True)),
                ('participation', models.ForeignKey(to='LanguageGameExperiment.LaDoExperimentParticipation', null=True)),
                ('question', models.ForeignKey(to='LanguageGameExperiment.LaDoQuestion', null=True)),
            ],
        ),
    ]
