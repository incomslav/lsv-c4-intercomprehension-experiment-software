# Name for the request.session field indicating the experiment assigned to a user.
ASSIGNED_EXPERIMENT = 'assignedExperiment'
# Name for the request.session field for the active ExperimentParticipation for the assigned experiment
CURRENT_PARTICIPATION = 'experimentParticipationID'
# Name for the request.session field indicating the experiment completed last
LAST_COMPLETED_EXPERIMENT = 'lastCompletedExperiment'
# Name for the request.session field indicating the last completed experiment participation 
LAST_COMPLETED_PARTICIPATION = 'lastCompletedParticipation'

# Name for request.sessiom field indicating which type of experiment does user selected , text or audio
SELECTED_EXPERIMENT_TYPE = 'SelectedExperimentType'

# Name for the request.session field for retrying completed participation
RETRY_CURRENT_PARTICIPATION = 'RetryexperimentParticipationID'

RETRY_ASSIGNED_EXPERIMENT = 'RetryAssignedExperiment'

RETRY_EXPERIMENT_STATUS = 'experimentStatus'

RETRY_EXP_COUNT = 'RetryExpCount'

RETRY_LAST_COMPLETED_EXPERIMENT = 'retrylastCompletedExperiment'
# Name for the request.session field indicating the last completed experiment participation 
RETRY_LAST_COMPLETED_PARTICIPATION = 'retrylastCompletedParticipation'

RETRY_AUDIO_EXPERIMENT = 'RetryAudioExperiment'


# Choices for Experiment.experiment_type.
FREE_TRANSLATION_EXPERIMENT = "FT"
EXPERIMENT_TYPES = ((FREE_TRANSLATION_EXPERIMENT, "Free Translation Experiment"), )

from django.utils.translation import ugettext_lazy as _


class ExperimentWelcomeScreenConstants:
    # I_AM_READY_CHECKBOX_TEXT = _("I_AM_READY_CHECKBOX")
    #CONTINUE_BUTTON_TEXT = _("START_EXPERIMENT_BUTTON")

    I_AM_READY_CHECKBOX_TEXT = "I am ready."
    CONTINUE_BUTTON_TEXT = "Start experiment"


class EnableJavaScriptMessageConstants:
    """
    enable javascript message constants
    """
    ENABLE_JAVA_SCRIPT_MESSAGE = "You must activate JavaScript in order to participate in our experiments. Please activate JavaScript and reload this page."