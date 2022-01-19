# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StatisticsPreview', '0003_auto_20190828_1128'),
    ]

    operations = [
        migrations.CreateModel(
            name='ColumnName',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('full_name', models.CharField(max_length=300)),
                ('abbvr_name', models.CharField(max_length=40)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
    ]
