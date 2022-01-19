from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User

from datetime import datetime

class Language(models.Model):
    language_id = models.AutoField('language id', primary_key=True)
    language_code = models.CharField('language code', max_length=15, null=False)
    language_name = models.CharField('language', max_length=30, null=False)

    class Meta:
        db_table = "language"
   
    def __str__(self):
        return self.language_name

    def __repr__(self):
        return str(self)

class Script(models.Model):
    script_name = models.CharField(max_length=400)
    script_code = models.CharField(max_length=50, null=True, blank=True, default=None)
    isActive = models.NullBooleanField()
    isDelete = models.NullBooleanField()
    # insertUser = models.CharField(max_length=50, null=True, blank=True)
    # updateUser = models.CharField(max_length=50, null=True, blank=True)
    # insertDate = models.DateTimeField(null=True, blank=True)
    # updateDate = models.DateTimeField(null=True, blank=True)


class LanguageScriptRelation(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    script = models.ForeignKey(Script, on_delete=models.CASCADE)
    isActive = models.NullBooleanField()
    isDelete = models.NullBooleanField()
    # insertUser = models.CharField(max_length=50, null=True, blank=True)
    # updateUser = models.CharField(max_length=50, null=True, blank=True)
    # insertDate = models.DateTimeField(null=True, blank=True)
    # updateDate = models.DateTimeField(null=True, blank=True)    


class EducationDegree(models.Model):
    """ Model for user education degrees. """
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)


class Gender(models.Model):
    """ Gender model. Made into model to allow for later extension
    for diverse genders. """
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=16)
   
    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

class Country(models.Model):
    """ Class representing a country. """
    country_id = models.AutoField('country id', primary_key=True)
    country_code = models.CharField('country code', max_length=15)
    country_name = models.CharField('country name', max_length=70)
   
    def __str__(self):
        return self.country_name

    def __repr__(self):
        return str(self)



class UserInfo(models.Model):
    """ Class for holding relevant user information. """
    user = models.OneToOneField(User, unique=True)
    gender = models.ForeignKey(Gender, null=True, blank=True, default=None)
    age = models.IntegerField(null=True, blank=True, default=None)
    location = models.ForeignKey(Country, null=True, blank=True)
    location_living_duration = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    grew_up_multilingually = models.BooleanField(default=False)
    living_countries = models.ManyToManyField(Country, through="LivingCountryStay", related_name="living_countries")
    education_countries = models.ManyToManyField(Country, through="EducationCountryStay", related_name="education_countries")
    languages = models.ManyToManyField(Language, through="UserLanguageSkill", related_name="user_language_skill")
    highest_education_degree = models.ForeignKey(EducationDegree, null=True, blank=True,default=None)
    degree_in_linguistics = models.BooleanField(default=False)

    created_on = models.DateTimeField(default=datetime.now)
    requested_signup_for_newsletter = models.BooleanField(default=False)
    confirmed_signup_for_newsletter = models.BooleanField(default=False)
    prolific_id = models.CharField('prolific id', max_length=64, null=True,blank=True)

    def checkEnteredInfo(self):
        """ Checks and returns whether this user has entered individual parts of participation-relevant information,
        EXCLUDING setting language skills levels, in order to participate in experiments. """
        # age given
        A = not self.age is None
        # gender given
        G = not self.gender is None
        # location given
        L = not self.location is None
        # location living duration given
        LD = not self.location_living_duration is None
        # at least one native language given
        N = False
        # at least one language in spoken in home country given
        H = False
        for language_skill in self.getAllLanguageSkills():
            if language_skill.is_native_language:
                N = True
            if language_skill.used_at_home:
                H = True
            if language_skill.spoken_at_user_location:
                L = True
        # at least one education country given
        E = self.education_countries.count() > 0

        # user has specified their highest education degree
        # DG = not self.highest_education_degree is None
        DG = True
        return (A, G, L, LD, N, H, E, DG)

    def enteredAllInfo(self):
        """ Checks and returns whether this user has entered all relevant information,
        EXCLUDING setting language skills levels, in order to participate in experiments. """
        return all(self.checkEnteredInfo())

    def getEnteredInformationErrors(self):
        """ Constructs a dictionary of aspects -> booleans to use in the UserInfoForm view, for displaying validation errors. """
        D = {}
        A, G, L, LD, N, H, E,DG = self.checkEnteredInfo()
        if not A:
            D["age_missing"] = True
        if not G:
            D["gender_missing"] = True
        if not L:
            D["location_language_missing"] = True
        if not LD:
            D["location_living_duration_missing"] = True
        if not N:
            D["native_language_missing"] = True
        if not H:
            D["home_language_missing"] = True
        if not E:
            D["education_missing"] = True
        # if not ES:
        #     D["education_duration_missing"] = True
        if not DG:
            D["degree_missing"] = True
        
        return D

    def clearedForExperiments(self):
        """ Checks and returns whether this user can participate in experiments.
        User must have entered all relevant information for this. """
        ALL_LANG_SET = True
        for language_skill in self.getAllLanguageSkills():
            if not language_skill.skillLevelsSet():
                ALL_LANG_SET = False
        return self.enteredAllInfo() and ALL_LANG_SET

    def clearedForDECompoundRUContextExperiment(self):

        """check availability for lado decompound ru context experiment
            This checks only for ru native and de speakers
        """
        is_native_ru = False
        is_de_speaker = False
        for language_skill in self.getAllLanguageSkills():
            if language_skill.is_native_language and language_skill.language.language_code == 'ru':
                is_native_ru = True
            if language_skill.is_native_language == False and language_skill.language.language_code == 'de':
                is_de_speaker = True

        if is_native_ru and is_de_speaker:
            return True
        else:
            return False


    def isSignedUpForNewsletter(self):
        """ Used to check if a user is signed up for the newsletter.
        User must have confirmed newsletter signup to prevent spam to
        mail addressed used untruthfully. """
        return self.confirmed_signup_for_newsletter

    def getAllLanguageSkills(self):
        """ Convenience method for getting all language skills of this user. """
        return UserLanguageSkill.objects.filter(user=self).all()

    def getAllLanguages(self):
        """ Convenience method for getting languages of this user. """
        for lang_skill in UserLanguageSkill.objects.filter(user=self).all():
            yield lang_skill.language

    def getNativeLanguages(self):
        for lang_skill in UserLanguageSkill.objects.filter(user=self, is_native_language=True).all():
            yield lang_skill.language

    def hasNativeLanguage(self, language):
        """ Used for checking if a user has a certain native language. """
        return UserLanguageSkill.objects.filter(user=self, language=language, is_native_language=True).exists()

    def getNativeLanguageSkills(self):
        """ Convenience method for getting the native language skills of this user. """
        return UserLanguageSkill.objects.filter(user=self, is_native_language=True).all()

    # def getNativeLanguages(self):
    #     for lang_skill in UserLanguageSkill.objects.filter(user=self, is_native_language=True).all():
    #         yield lang_skill.language

    def getEducationCountryStays(self):
        """ Convenience for getting education country stays. """
        return EducationCountryStay.objects.filter(user=self).all()

    def getHomeLanguageSkills(self):
        """ Convenience method for getting the user skills at the languages this user uses at home. """
        return UserLanguageSkill.objects.filter(user=self, used_at_home=True).all()
    
    def getHomeLanguages(self):
        for lang_skill in UserLanguageSkill.objects.filter(user=self, used_at_home=True).all():
            yield lang_skill.language

    def getLocationLanguageSkills(self):
        """ Convenience method for getting the user skills at the languages this user uses at home. """
        return UserLanguageSkill.objects.filter(user=self, spoken_at_user_location=True).all()
    
    def getLocationLanguages(self):
        for lang_skill in UserLanguageSkill.objects.filter(user=self, spoken_at_user_location=True).all():
            yield lang_skill.language

    def getLanguageSkillsExposedToByLiving(self):
        """ Convenience method for getting the user skills at the languages this user uses at home. """
        return UserLanguageSkill.objects.filter(user=self, exposure_through_living__isnull=False).all()
    
    def getLanguagesExposedToByLiving(self):
        for lang_skill in UserLanguageSkill.objects.filter(user=self, exposure_through_living__isnull=False).all():
            yield lang_skill.language

    def getLearnedLanguageSkills(self):
        """ Convenience method for getting the user skills at the languages this user uses at home. """
        return UserLanguageSkill.objects.filter(user=self, exposure_through_learning__isnull=False).all()
    
    def getLearnedLanguages(self):
        for lang_skill in UserLanguageSkill.objects.filter(user=self, exposure_through_learning__isnull=False).all():
            yield lang_skill.language
    
    def hasLivedInAnotherArea(self):
        """ Convenience method for checking whether any exposure through living (beyond current location) is present. """
        return UserLanguageSkill.objects.filter(user=self, exposure_through_living__isnull=False).count() > 0

class UserLanguageSkill(models.Model):
    """ Class storing a user's skill levels in a specific language."""
    user = models.ForeignKey(UserInfo)
    language = models.ForeignKey(Language)
    reading_level = models.IntegerField('reading level', null=True)
    writing_level = models.IntegerField('writing level', null=True)
    listening_level = models.IntegerField('listening level', null=True)
    speaking_level = models.IntegerField('speaking level', null=True)
    is_native_language = models.BooleanField(default=False)
    used_at_home = models.BooleanField(default=False)
    exposure_through_learning = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    exposure_through_living = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    spoken_at_user_location = models.BooleanField(default=False)

    class Meta:
        unique_together = (("user", "language"))

    def skillLevelsSet(self):
        """ Checks and returns if all individual skill levels are non-null. """
        return not self.reading_level is None and not self.writing_level is None and not self.listening_level is None and not self.speaking_level is None

    def eligibleForDeletion(self):
        """ Check if this language skill can be deleted. """
        return not self.is_native_language and not self.used_at_home and self.exposure_through_learning is None and self.exposure_through_learning is None and not self.spoken_at_user_location

    def save_or_delete(self):
        if self.eligibleForDeletion():
            self.delete()
        else:
            self.save()

class CountryStay(models.Model):
    """ Class modeling a user's stay in a country. Used to relate UserInfo with Countries as intermediary model. """
    user = models.ForeignKey(UserInfo)
    country = models.ForeignKey(Country)
    duration = models.DecimalField(decimal_places=2, max_digits=6, null=True)

class LivingCountryStay(CountryStay):
    """ Intermediary model for the countries a user has lived in. """
    pass

class EducationCountryStay(CountryStay):
    """ Intermediary model for the countries a user has been educated in. """
    pass
