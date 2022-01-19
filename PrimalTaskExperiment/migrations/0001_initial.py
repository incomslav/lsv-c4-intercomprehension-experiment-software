# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PrimalTaskQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('stimuli1_location', models.CharField(max_length=500)),
                ('stimuli2_location', models.CharField(max_length=500)),
                ('right_response', models.CharField(max_length=100, default='l')),
            ],
        ),
    ]
