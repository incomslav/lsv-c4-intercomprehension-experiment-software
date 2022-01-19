# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StatisticsPreview', '0002_auto_20190828_1017'),
    ]

    operations = [
        migrations.AddField(
            model_name='resultmenu',
            name='has_child',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='resultmenu',
            name='menu_url',
            field=models.CharField(max_length=350, default=''),
        ),
    ]
