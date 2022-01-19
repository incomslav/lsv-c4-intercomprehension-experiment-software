from django.core.management.base import BaseCommand, CommandError

from ExperimentBasics.models import *
from FreeTranslationExperiment.models import *
from ExperimentBasics.UserAnswerExporter import *

class Command(BaseCommand):
    help = 'Migrates languages from individual classes (renamed old_foreign_language and old_native_language) into Experiment fields'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for E in FreeTranslationExperiment.objects.all():
            try:
                old_flang = E.old_foreign_language
                old_nlang = E.old_native_language
                E.foreign_language = old_flang
                E.native_language = old_nlang

            except Exception as e:
                raise CommandError('Error: '+str(e))
