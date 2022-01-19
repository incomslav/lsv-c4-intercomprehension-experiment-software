from django.core.management.base import BaseCommand, CommandError

from ExperimentBasics.models import *
from ExperimentBasics.ParticipatingUsersExporter import *

class Command(BaseCommand):
    help = 'Exports participating user files for all experiments'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for E in Experiment.objects.all():
            exp_id = E.id
            try:
                makeParticipatingUsersCSVFileForExperiment(exp_id)

            except Experiment.DoesNotExist as e:
                raise CommandError('Experiment "%s" does not exist.' % exp_id)
