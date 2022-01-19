from django.core.management.base import BaseCommand, CommandError

from ExperimentBasics.models import *
from ExperimentBasics.ParticipatingUsersExporter import *

class Command(BaseCommand):
    help = 'Exports participating user files for a given experiment'

    def add_arguments(self, parser):
        parser.add_argument('exp_id', nargs='+', type=int)

    def handle(self, *args, **options):
        for exp_id in options["exp_id"]:
            try:
                makeParticipatingUsersCSVFileForExperiment(exp_id)

            except Experiment.DoesNotExist as e:
                raise CommandError('Experiment "%s" does not exist.' % exp_id)
