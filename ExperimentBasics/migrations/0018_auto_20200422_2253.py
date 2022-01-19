# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('ExperimentBasics', '0017_experimentparticipation_experiment_type'),
    ]

    operations = [
        # migrations.RemoveField(
        #     model_name='experimentinfo',
        #     name='experiment_info_bg',
        # ),
        # migrations.RemoveField(
        #     model_name='experimentinfo',
        #     name='experiment_info_bs',
        # ),
        # migrations.RemoveField(
        #     model_name='experimentinfo',
        #     name='experiment_info_cs',
        # ),
        # migrations.RemoveField(
        #     model_name='experimentinfo',
        #     name='experiment_info_de',
        # ),
        # migrations.RemoveField(
        #     model_name='experimentinfo',
        #     name='experiment_info_en',
        # ),
        # migrations.RemoveField(
        #     model_name='experimentinfo',
        #     name='experiment_info_hr',
        # ),
        # migrations.RemoveField(
        #     model_name='experimentinfo',
        #     name='experiment_info_mk',
        # ),
        # migrations.RemoveField(
        #     model_name='experimentinfo',
        #     name='experiment_info_pl',
        # ),
        # migrations.RemoveField(
        #     model_name='experimentinfo',
        #     name='experiment_info_ru',
        # ),
        # migrations.RemoveField(
        #     model_name='experimentinfo',
        #     name='experiment_info_sk',
        # ),
        # migrations.RemoveField(
        #     model_name='experimentinfo',
        #     name='experiment_info_sl',
        # ),
        # migrations.RemoveField(
        #     model_name='experimentinfo',
        #     name='experiment_info_sr',
        # ),
        # migrations.RemoveField(
        #     model_name='experimentinfo',
        #     name='experiment_info_uk',
        # ),
        # migrations.RemoveField(
        #     model_name='informedconsent',
        #     name='consent_description_bg',
        # ),
        # migrations.RemoveField(
        #     model_name='informedconsent',
        #     name='consent_description_bs',
        # ),
        # migrations.RemoveField(
        #     model_name='informedconsent',
        #     name='consent_description_cs',
        # ),
        # migrations.RemoveField(
        #     model_name='informedconsent',
        #     name='consent_description_de',
        # ),
        # migrations.RemoveField(
        #     model_name='informedconsent',
        #     name='consent_description_en',
        # ),
        # migrations.RemoveField(
        #     model_name='informedconsent',
        #     name='consent_description_hr',
        # ),
        # migrations.RemoveField(
        #     model_name='informedconsent',
        #     name='consent_description_mk',
        # ),
        # migrations.RemoveField(
        #     model_name='informedconsent',
        #     name='consent_description_pl',
        # ),
        # migrations.RemoveField(
        #     model_name='informedconsent',
        #     name='consent_description_ru',
        # ),
        # migrations.RemoveField(
        #     model_name='informedconsent',
        #     name='consent_description_sk',
        # ),
        # migrations.RemoveField(
        #     model_name='informedconsent',
        #     name='consent_description_sl',
        # ),
        # migrations.RemoveField(
        #     model_name='informedconsent',
        #     name='consent_description_sr',
        # ),
        # migrations.RemoveField(
        #     model_name='informedconsent',
        #     name='consent_description_uk',
        # ),
        # migrations.RemoveField(
        #     model_name='news',
        #     name='news_description_bg',
        # ),
        # migrations.RemoveField(
        #     model_name='news',
        #     name='news_description_bs',
        # ),
        # migrations.RemoveField(
        #     model_name='news',
        #     name='news_description_cs',
        # ),
        # migrations.RemoveField(
        #     model_name='news',
        #     name='news_description_de',
        # ),
        # migrations.RemoveField(
        #     model_name='news',
        #     name='news_description_en',
        # ),
        # migrations.RemoveField(
        #     model_name='news',
        #     name='news_description_hr',
        # ),
        # migrations.RemoveField(
        #     model_name='news',
        #     name='news_description_mk',
        # ),
        # migrations.RemoveField(
        #     model_name='news',
        #     name='news_description_pl',
        # ),
        # migrations.RemoveField(
        #     model_name='news',
        #     name='news_description_ru',
        # ),
        # migrations.RemoveField(
        #     model_name='news',
        #     name='news_description_sk',
        # ),
        # migrations.RemoveField(
        #     model_name='news',
        #     name='news_description_sl',
        # ),
        # migrations.RemoveField(
        #     model_name='news',
        #     name='news_description_sr',
        # ),
        # migrations.RemoveField(
        #     model_name='news',
        #     name='news_description_uk',
        # ),
        migrations.AlterField(
            model_name='experiment',
            name='user_medal',
            field=models.ImageField(blank=True, null=True, upload_to='E:\\MSc\\Hiwi\\LSV HiWi\\lsv-c4-django-webexperiment\\Incomslav/static/media/medals/', storage=django.core.files.storage.FileSystemStorage(location='E:\\MSc\\Hiwi\\LSV HiWi\\lsv-c4-django-webexperiment\\Incomslav/static/media/medals/', base_url='/media//medals/'), width_field='medal_width', height_field='medal_height'),
        ),
    ]
