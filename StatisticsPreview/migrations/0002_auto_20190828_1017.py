# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StatisticsPreview', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resultmenu',
            name='parent_id',
            field=models.ForeignKey(to='StatisticsPreview.ResultMenu', blank=True, null=True),
        ),
    ]
