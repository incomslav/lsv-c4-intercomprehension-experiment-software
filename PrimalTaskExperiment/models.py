from django.db import models

# Create your models here.


class PrimalTaskExperiment(models.Model):
    experiment_name = models.CharField('experiment name', max_length=100, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    last_changed_on = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True)
    has_audio = models.NullBooleanField(default=False)
    experiment_description = models.CharField(max_length=400, null=True)


class PrimalTaskQuestion(models.Model):
    # experiment = models.ForeignKey(LaDoExperiment, null=True, default=1)
    stimuli1_location = models.CharField(max_length=500)
    stimuli2_location = models.CharField(max_length=500)
    right_response = models.CharField(max_length=100, default='l')
