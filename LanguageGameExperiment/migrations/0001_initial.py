# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LaDoExperiment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('experiment_name', models.CharField(max_length=100, null=True, verbose_name='experiment name')),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_changed_on', models.DateTimeField(auto_now=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='LaDoQuestion',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('file_name', models.CharField(max_length=500)),
                ('correct_answer', models.CharField(max_length=100)),
            ],
        ),
    ]
