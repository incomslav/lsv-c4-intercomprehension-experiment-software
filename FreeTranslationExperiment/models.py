__author__ = 'A. K. Fischer'

from django.db import models

from ExperimentBasics.models import *
from django.core.urlresolvers import reverse

from FreeTranslationExperiment.variables import *
from Common.constants import *

from django.utils.translation import ugettext as _

from math import ceil
from Common.common_utils import removeDiacritics

from ExperimentBasics.definitions import *

class FreeTranslationExperiment(Experiment):
    """ Free Translation Experiment class. Used to represent a single data set
    to be used in a word-based free translation experiment. Has an associated
    native language, which a potential user must have, and an associated
    foreign language, which a potential user must not have."""
    free_translation_experiment_id = models.AutoField(primary_key=True)
    native_language = models.ForeignKey(Language, related_name="FreeTranslation_native_language", null=True)
    foreign_language = models.ForeignKey(Language, related_name="FreeTranslation_foreign_language", null=True)
    # stimuli_file = models.CharField(max_length='800', null=True, blank=True) #Added by Hasan on 2018-05-28

    def getAllocatedTimePerQuestion(self):
        """ Returns, in seconds, the time allocated to each individual question. """
        return 10

    def getExperimentNameForUser(self):
        """ Gets the Experiment's name. """
        return "Free Translation "+self.native_language.language_code+"-"+self.foreign_language.language_code

    def getRedirectURL(self):
        """ The URL this experiment links to for its actual questions. """
        return reverse("FreeTranslationQuestions")

    def getExperimentNameForExperimentMedalsPage(self):
        lang_labels = {}
        lang_labels["fromLangLabel"] = _("EXPERIMENT_FROM_LANGUAGE_LABEL")
        lang_labels["fromLangName"] = _(self.foreign_language.language_name)
        lang_labels["fromLangCode"] = self.foreign_language.language_code
        lang_labels["toLangLabel"] = _("EXPERIMENT_TO_LANGUAGE_LABEL")
        lang_labels["toLangName"] = _(self.native_language.language_name)
        lang_labels["toLangCode"] = self.native_language.language_code

        language_table = """
        <table class="table table-responsive table-bordered from-to-language-container" style="width: 100%">
            <tr>
                <td>
                    {fromLangLabel}
                </td>
                <td>
                    <img src="/static/images/flags/{fromLangCode}.png" style="width: 30px; padding-right:5px;"> {fromLangName}
                </td>
                <td>
                        {toLangLabel}
                </td>
                <td>
                    <img src="/static/images/flags/{toLangCode}.png" style="width: 30px; padding-right:5px;">{toLangName}
                </td>
            </tr>
        </table>
        """.format(**lang_labels)
        experimentName = _("FREE_TRANSLATION_EXPERIMENT")
        return experimentName, language_table

    def getWelcomeTemplateStrings(self):
        """ Returns strings for this experiment to be used in the Experiment Welcome template. """
        strings = {}
        strings['EXPERIMENT_WELCOME_HEADER'] = _("FREE_TRANSLATION_EXPERIMENT_WELCOME_HEADER") + " #"+str(self.free_translation_experiment_id)
       
        lang_labels = {}
        lang_labels["fromLangLabel"] = _("EXPERIMENT_FROM_LANGUAGE_LABEL")
        lang_labels["fromLangName"] = _(self.foreign_language.language_name)
        lang_labels["fromLangCode"] = self.foreign_language.language_code
        
        lang_labels["toLangLabel"] = _("EXPERIMENT_TO_LANGUAGE_LABEL")
        lang_labels["toLangName"] = _(self.native_language.language_name)
        lang_labels["toLangCode"] = self.native_language.language_code

        language_table = """
        <table class="table table-responsive table-bordered from-to-language-container" style="width: 50%">
            <tr>
                <td>
                    {fromLangLabel}
                </td>
                <td>
                    <img src="/static/images/flags/{fromLangCode}.png" style="width: 30px; padding-right:5px;"> {fromLangName}
                </td>
                <td>
                        {toLangLabel}
                </td>
                <td>
                    <img src="/static/images/flags/{toLangCode}.png" style="width: 30px; padding-right:5px;">{toLangName}
                </td>
            </tr>
        </table>
        """.format(**lang_labels)
        
        strings['EXPERIMENT_INSTRUCTIONS'] = language_table

        strings['EXPERIMENT_INSTRUCTIONS'] += "<p>"+_("FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_TOTAL_WORDS_TEXT").format(self.getNumberOfQuestions())+ "</p>"
        strings['EXPERIMENT_INSTRUCTIONS'] += "<p>"+_("FREE_TRANSLATION_TRANSLATE_WORD_TEXT")+"</p>"
        keyboard_text = _("FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_SET_KEYBOARD_LANGUAGE_TEXT")
        if not keyboard_text.endswith("."):
            keyboard_text += " " + lang_labels["toLangName"] + "." 
        
        strings['EXPERIMENT_INSTRUCTIONS'] += "<p><b>" + keyboard_text + "</b></p>"

        strings['EXPERIMENT_INSTRUCTIONS'] += "<p>" + _("FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_CLOSE_BROWSER_WINDOWS_TEXT") + "</p>"
        strings['EXPERIMENT_INSTRUCTIONS'] += "<p>" + _("FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_TIME_ESTIMATE_TEXT").format(ceil(self.getNumberOfQuestions()*self.getAllocatedTimePerQuestion()/60))+"</p>"
        strings['EXPERIMENT_INSTRUCTIONS'] += "<p>" + _("FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_START_WHEN_READY_TEXT") +"</p>"
        #+ FreeTranslationWelcomePageConstants.FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_CLOSE_BROWSER_WINDOWS_TEXT + "</p>"
        
        # if RETRY_AUDIO_EXPERIMENT in request.session:
        #     strings['EXPERIMENT_INSTRUCTIONS'] += "<p><b>" + "Please Make sure system speaker is working properly." + "</b></p>"
        #     strings['EXPERIMENT_INSTRUCTIONS'] += "<p><b>" + "Only Use Google Chrome browser for audio experiments." + "</b></p>"

        strings['EXPERIMENT_INSTRUCTIONS'] += """<marquee onmouseover="this.stop();" onmouseout="this.start();">
                   <h4 style=""> {} <img src="/static/images/smilely.png" style="width: 30px;"></h4>
       </marquee>""".format(_("FREE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_HOW_FAST_ARE_YOU_TEXT"))
        
        """<p>You will be presented <b>{} words in {}</b>, which will appear <b>one by one</b>.<br>
        Your task is to <b>translate each word into {} without using any help from other people, a dictionary, or the internet</b>.<br>
        You have a maximum of 10 seconds to translate each word. Try to be as fast and accurate as you can!</p>

        <p>Please <b>adjust your keyboard settings for {}</b> and <b>close all other browser windows</b>.</p>

        <p>When you are ready, check 'I am ready' and click on the 'start experiment' button to proceed.<p>""".format(str(self.getNumberOfQuestions()), self.foreign_language.language_name, self.native_language.language_name, self.native_language.language_name)
        
        return strings


    def RetryMakeNewParticipation(self, userInfo, retryCount):

        newParticipation, created = RetryExperimentParticipation.objects.get_or_create(
            experiment = self,
            user = userInfo,
            retry_count = retryCount)

        if created:
            for question in self.experiment_questions.all():
                A = RetryFreeTranslationUserAnswer()
                A.re_answering_user = userInfo
                A.re_answered_question = question
                A.re_experiment_participation = newParticipation
                A.save()

        return newParticipation


    def makeNewParticipation(self, userInfo, expType='text'):
        """ Returns a new experiment participation object for this experiment. """
        newParticipation = ExperimentParticipation()
        newParticipation.experiment = self
        newParticipation.user = userInfo
        newParticipation.experiment_type = expType
        newParticipation.save()

        for question in self.experiment_questions.all():
            # make new FreeTranslationUserAnswer for this participation
            A = FreeTranslationUserAnswer()
            A.answering_user = userInfo
            A.answered_question = question
            A.experiment_participation = newParticipation
            A.save()

        return newParticipation

# # Extended class for retry freetranslation
class RetryFreeTranslationAnswer(models.Model):

    """ Model for any answer in Free Translation task.
    Stores the answered string in the native language. """
    retry_free_translation_answer_id = models.AutoField(primary_key=True)
    native_word = models.CharField(max_length = 512, null=True)

    def __eq__(self, other):
        """ Convenience method to compare to other answers. """
        return self.native_word == other.native_word

class FreeTranslationAnswer(models.Model):
    """ Model for any answer in Free Translation task.
    Stores the answered string in the native language. """
    free_translation_answer_id = models.AutoField(primary_key=True)
    native_word = models.CharField(max_length = 512, null=True)

    def __eq__(self, other):
        """ Convenience method to compare to other answers. """
        return self.native_word == other.native_word


class FreeTranslationCorrectAnswer(FreeTranslationAnswer):
    """ Model for a correct answer in the Free Translation task.
    Empty shell to allow for convenient handling. Associated with
    FreeTranslationQuestion. """
    free_translation_correct_answer_id = models.AutoField(primary_key=True)


class FreeTranslationUserAnswer(UserAnswer, FreeTranslationAnswer):
    """ A Free Translation user answer. Stores the final reply and a 
    JSON-encoded log of the input reply's changes and (millisecond) 
    times of change."""
    free_translation_user_answer_id = models.AutoField(primary_key=True)
    result_changes = models.TextField(null=True)

    def recomputeNormalizedCorrectness(self):
        """ Go through all the correct answers associated with the answered question and see if one matches with normalized form of this one. """
        if self.normalized_form_is_correct is None and not self.native_word is None:
            AQ = FreeTranslationQuestion.objects.get(id=self.answered_question.id)
            for correct_answer in AQ.correct_answers.all():
                # Need to add code to build in tolerance for multiple spaces.
                self.native_word = " ".join(self.native_word.lower().strip().split())
                correct_answer.native_word = " ".join(correct_answer.native_word.lower().strip().split())
                if removeDiacritics(self.native_word.lower().strip()) == removeDiacritics(correct_answer.native_word.lower().strip()):
                    self.normalized_form_is_correct = True
                    break
        else:
            self.normalized_form_is_correct = False
    
        return self.normalized_form_is_correct

    def recomputeExactCorrectness(self):
        """
        check if provided answer is absolutely correct or not
        """
        if not self.native_word is None:
            AQ = FreeTranslationQuestion.objects.get(id=self.answered_question.id)
            for correct_answer in AQ.correct_answers.all():
                # Added code for space tolerance
                self.native_word = " ".join(self.native_word.lower().strip().split())
                correct_answer.native_word = " ".join(correct_answer.native_word.lower().strip().split())
                if self.native_word.lower().strip() == correct_answer.native_word.lower().strip():
                    return True

        return False

# Hasan 
# Added for Mulitple try experiment

class RetryFreeTranslationUserAnswer(RetryUserAnswer, RetryFreeTranslationAnswer):
    """ A Free Translation user answer. Stores the final reply and a 
    JSON-encoded log of the input reply's changes and (millisecond) 
    times of change."""
    retry_free_translation_user_answer_id = models.AutoField(primary_key=True)
    result_changes = models.TextField(null=True)

    def recomputeNormalizedCorrectness(self):
        """ Go through all the correct answers associated with the answered question and see if one matches with normalized form of this one. """
        if self.re_normalized_form_is_correct is None and not self.native_word is None:
            AQ = FreeTranslationQuestion.objects.get(id=self.re_answered_question.id)
            for correct_answer in AQ.correct_answers.all():
                self.native_word = " ".join(self.native_word.lower().strip().split())
                correct_answer.native_word = " ".join(correct_answer.native_word.lower().strip().split())
                if removeDiacritics(self.native_word.lower().strip()) == removeDiacritics(correct_answer.native_word.lower().strip()):
                    self.re_normalized_form_is_correct = True
                    break
        else:
            self.re_normalized_form_is_correct = False
    
        return self.re_normalized_form_is_correct

    def recomputeExactCorrectness(self):
        """
        check if provided answer is absolutely correct or not
        """
        if not self.native_word is None:
            AQ = FreeTranslationQuestion.objects.get(id=self.re_answered_question.id)
            for correct_answer in AQ.correct_answers.all():
               self.native_word = " ".join(self.native_word.lower().strip().split())
               correct_answer.native_word = " ".join(correct_answer.native_word.lower().strip().split())
               if self.native_word.lower().strip() == correct_answer.native_word.lower().strip():
                    return True

        return False




class FreeTranslationQuestion(Question):
    """ Model for questions in the Free Translation task.
    Contain the presented foreign word and a list of 
    acceptable answers. """
    free_translation_question_id = models.AutoField(primary_key=True)
    foreign_word = models.CharField(max_length = 512)
    correct_answers = models.ManyToManyField(FreeTranslationCorrectAnswer, related_name="associated_question")
    has_audio = models.NullBooleanField(default=None)
    audio_path = models.CharField(max_length= 1200, default=None, null=True)
    audio_file = models.FileField(upload_to='FreeTranslationQuestionAudio/', blank=True, null=True)
    # audio_upload_time = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.foreign_word

    def answerCorrect(self, given_answer):
        """ Checks if the given answer is acceptable. """
        for correct_answer in self.correct_answers:
            if correct_answer == given_answer:
                return True
        return False
