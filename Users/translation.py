
from modeltranslation.translator import translator, TranslationOptions
from Users.models import *

class LanguageTranslationOptions(TranslationOptions):
    fields = ('language_name',)

translator.register(Language, LanguageTranslationOptions)


class GenderTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(Gender, GenderTranslationOptions)


class CountryTranslationOptions(TranslationOptions):
    fields = ('country_name',)

translator.register(Country, CountryTranslationOptions)

class EducationDegreeTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(EducationDegree,EducationDegreeTranslationOptions)
