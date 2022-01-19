
from modeltranslation.translator import translator, TranslationOptions
from ExperimentBasics.models import *


class NewsTranslationOptions(TranslationOptions):
    fields = ('news_description',)

translator.register(News,NewsTranslationOptions)


class ExperimentInfoTranslationOptions(TranslationOptions):
    fields = ('experiment_info',)

translator.register(ExperimentInfo,ExperimentInfoTranslationOptions)


class InformedConsentTranslationOptions(TranslationOptions):
    fields = ('consent_description',)

translator.register(InformedConsent,InformedConsentTranslationOptions)