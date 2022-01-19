# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0011_auto_20200422_2227'),
        ('LanguageGameExperiment', '0012_ladoquestion_question_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='LadoProlificUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('prolific_id', models.CharField(max_length=100, null=True, default=None)),
                ('created_on', models.DateTimeField(null=True, auto_now_add=True)),
                ('age', models.IntegerField(blank=True, null=True, default=None)),
                ('is_active', models.NullBooleanField(default=True)),
                ('is_delete', models.NullBooleanField(default=False)),
                ('try_count', models.IntegerField(default=0)),
                ('gender', models.ForeignKey(blank=True, null=True, default=None, to='Users.Gender')),
                ('languages', models.ForeignKey(null=True, default=None, to='Users.Language')),
                ('location', models.ForeignKey(blank=True, null=True, default=None, to='Users.Country')),
            ],
        ),
        migrations.AlterField(
            model_name='ladoexperimentparticipation',
            name='user',
            field=models.ForeignKey(blank=True, null=True, default=None, to='Users.UserInfo'),
        ),
        migrations.AddField(
            model_name='ladoexperimentparticipation',
            name='lado_prolific_user',
            field=models.ForeignKey(blank=True, null=True, default=None, to='LanguageGameExperiment.LadoProlificUser'),
        ),
    ]
