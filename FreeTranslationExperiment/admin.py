from django.contrib import admin

from ExperimentBasics.models import *
from FreeTranslationExperiment.models import *

"""
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin
@admin.register(FreeTranslationExperiment)
class FreeTranslationExperimentAdmin(PolymorphicChildModelAdmin):
    base_model = FreeTranslationExperiment

    base_form = ...
    base_fieldsets = (
        ...
    )

@admin.register(FreeTranslationQuestion)
class QuestionAdmin(PolymorphicChildModelAdmin):
    base_model = FreeTranslationQuestion
"""


# Register your models here.
