# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('ExperimentBasics', '0007_auto_20180215_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='user_medal',
            field=models.ImageField(blank=True, null=True, width_field='medal_width', height_field='medal_height', upload_to='/srv/C4-django/c4-django-webexperiments/Incomslav/static/media//medals/', storage=django.core.files.storage.FileSystemStorage(base_url='/media//medals/', location='/srv/C4-django/c4-django-webexperiments/Incomslav/static/media//medals/')),
        ),
    ]
