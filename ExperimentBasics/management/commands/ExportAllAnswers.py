from django.core.management.base import BaseCommand, CommandError

from ExperimentBasics.models import *
from FreeTranslationExperiment.models import *
from ExperimentBasics.UserAnswerExporter import *

class Command(BaseCommand):
    help = 'Exports user answer files for all experiments'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for E in FreeTranslationExperiment.objects.all():
            exp_id = E.id
            try:
                makeUserAnswersCSVFileForExperiment(exp_id)

            except Experiment.DoesNotExist as e:
                raise CommandError('Experiment "%s" does not exist.' % exp_id)
