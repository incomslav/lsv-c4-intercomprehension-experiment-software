# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('PrimalTaskExperiment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrimalTaskExperiment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('experiment_name', models.CharField(verbose_name='experiment name', max_length=100, null=True)),
                ('created_on', models.DateTimeField(null=True, auto_now_add=True)),
                ('last_changed_on', models.DateTimeField(null=True, auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('has_audio', models.NullBooleanField(default=False)),
                ('experiment_description', models.CharField(max_length=400, null=True)),
            ],
        ),
    ]
