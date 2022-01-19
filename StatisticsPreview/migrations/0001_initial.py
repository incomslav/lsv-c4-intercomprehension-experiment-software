# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ResultMenu',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('menu_name', models.CharField(max_length=150)),
                ('is_root', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('parent_id', models.ForeignKey(null=True, to='StatisticsPreview.ResultMenu')),
            ],
        ),
    ]
