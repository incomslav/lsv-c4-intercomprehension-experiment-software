# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0009_auto_20180206_1532'),
    ]

    operations = [
        migrations.CreateModel(
            name='LanguageScriptRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isActive', models.NullBooleanField()),
                ('isDelete', models.NullBooleanField()),
                ('language', models.ForeignKey(to='Users.Language')),
            ],
        ),
        migrations.CreateModel(
            name='Script',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('script_name', models.CharField(max_length=400)),
                ('script_code', models.CharField(default=None, null=True, max_length=50, blank=True)),
                ('isActive', models.NullBooleanField()),
                ('isDelete', models.NullBooleanField()),
            ],
        ),
        migrations.AddField(
            model_name='languagescriptrelation',
            name='script',
            field=models.ForeignKey(to='Users.Script'),
        ),
    ]
