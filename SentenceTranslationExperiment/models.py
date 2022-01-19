__author__ = 'A. K. Fischer'

from django.db import models

from ExperimentBasics.models import *
from django.core.urlresolvers import reverse

from SentenceTranslationExperiment.variables import *
from Common.constants import *

from django.utils.translation import ugettext as _

from math import ceil

from Common.common_utils import removeDiacritics

class SentenceTranslationExperiment(Experiment):
    """ Sentence Translation Experiment class. Used to represent a single data set
    to be used in a sentence-based free translation experiment. Has an associated
    native language, which a potential user must have, and an associated
    foreign language, which a potential user must not have."""
    sentence_translation_experiment_id = models.AutoField(primary_key=True)
    native_language = models.ForeignKey(Language, related_name="SentenceTranslation_native_language", null=True)
    foreign_language = models.ForeignKey(Language, related_name="SentenceTranslation_foreign_language", null=True)

    def getAllocatedTimePerQuestion(self):
        """ Returns, in seconds, the time allocated to each individual question. """
        return 120

    def getExperimentNameForUser(self):
        """ Gets the Experiment's name. """
        return "Sentence Translation "+self.native_language.language_code+"-"+self.foreign_language.language_code

    def getRedirectURL(self):
        """ The URL this experiment links to for its actual questions. """
        return reverse("SentenceTranslationQuestions")

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
        experimentName = _("SENTENCE_TRANSLATION_EXPERIMENT")
        return experimentName, language_table

    def getWelcomeTemplateStrings(self):
        """ Returns strings for this experiment to be used in the Experiment Welcome template. """
        strings = {}
        strings['EXPERIMENT_WELCOME_HEADER'] = _("SENTENCE_TRANSLATION_EXPERIMENT_WELCOME_HEADER") + " #"+str(self.sentence_translation_experiment_id)
       
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

        strings['EXPERIMENT_INSTRUCTIONS'] += "<p>"+_("SENTENCE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_TOTAL_WORDS_TEXT").format(self.getNumberOfQuestions())+ "</p>"
        strings['EXPERIMENT_INSTRUCTIONS'] += "<p>"+_("SENTENCE_TRANSLATION_TRANSLATE_WORD_TEXT")+"</p>"
        keyboard_text = _("SENTENCE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_SET_KEYBOARD_LANGUAGE_TEXT")
        if not keyboard_text.endswith("."):
            keyboard_text += " " + lang_labels["toLangName"] + "." 
        
        strings['EXPERIMENT_INSTRUCTIONS'] += "<p><b>" + keyboard_text + "</b></p>"
        strings['EXPERIMENT_INSTRUCTIONS'] += "<p>" + _("SENTENCE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_CLOSE_BROWSER_WINDOWS_TEXT") + "</p>"
        strings['EXPERIMENT_INSTRUCTIONS'] += "<p>" + _("SENTENCE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_TIME_ESTIMATE_TEXT").format(ceil(self.getNumberOfQuestions()*self.getAllocatedTimePerQuestion()/60))+"</p>"
        strings['EXPERIMENT_INSTRUCTIONS'] += "<p>" + _("SENTENCE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_START_WHEN_READY_TEXT") +"</p>"
        #+ SentenceTranslationWelcomePageConstants.SENTENCE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_CLOSE_BROWSER_WINDOWS_TEXT + "</p>"
                
        strings['EXPERIMENT_INSTRUCTIONS'] += """<marquee onmouseover="this.stop();" onmouseout="this.start();">
                   <h4 style=""> {} <img src="/static/images/smilely.png" style="width: 30px;"></h4>
       </marquee>""".format(_("SENTENCE_TRANSLATION_EXPERIMENT_WELCOME_PAGE_HOW_FAST_ARE_YOU_TEXT"))
        
        """<p>You will be presented <b>{} sentences in {}</b>, which will appear <b>one by one</b>.<br>
        Your task is to <b>translate each sentence into {} without using any help from other people, a dictionary, or the internet</b>.<br>
        You have a maximum of 5 minutes to translate each word. Try to be as fast and accurate as you can!</p>

        <p>Please <b>adjust your keyboard settings for {}</b> and <b>close all other browser windows</b>.</p>

        <p>When you are ready, check 'I am ready' and click on the 'start experiment' button to proceed.<p>""".format(str(self.getNumberOfQuestions()), self.foreign_language.language_name, self.native_language.language_name, self.native_language.language_name)
        
        return strings


    def makeNewParticipation(self, userInfo):
        """ Returns a new experiment participation object for this experiment. """
        newParticipation = ExperimentParticipation()
        newParticipation.experiment = self
        newParticipation.user = userInfo
        newParticipation.save()

        for question in self.experiment_questions.all():
            # make new SentenceTranslationUserAnswer for this participation
            A = SentenceTranslationUserAnswer()
            A.answering_user = userInfo
            A.answered_question = question
            A.experiment_participation = newParticipation
            A.save()

        return newParticipation


class SentenceTranslationAnswer(models.Model):
    """ Model for any answer in Sentence Translation task.
    Stores the answered string in the native language. """
    sentence_translation_answer_id = models.AutoField(primary_key=True)
    translated_sentence = models.CharField(max_length = 512, null=True)

    def __eq__(self, other):
        """ Convenience method to compare to other answers. """
        return self.translated_sentence == other.translated_sentence

    def isCorrectAnswer(self):
        return True # Returns True for now, should later be extended to compare against set of sentences
    

class SentenceTranslationCorrectAnswer(SentenceTranslationAnswer):
    """ Model for a correct answer in the Sentence Translation task.
    Empty shell to allow for convenient handling. Associated with
    SentenceTranslationQuestion. """
    sentence_translation_correct_answer_id = models.AutoField(primary_key=True)


class SentenceTranslationUserAnswer(UserAnswer, SentenceTranslationAnswer):
    """ A Sentence Translation user answer. Stores the final reply and a 
    JSON-encoded log of the input reply's changes and (millisecond) 
    times of change."""
    sentence_translation_user_answer_id = models.AutoField(primary_key=True)
    result_changes = models.TextField(null=True)

    def recomputeNormalizedCorrectness(self):
        """ Go through all the correct answers associated with the answered question and see if one matches with normalized form of this one. """
        AQ = SentenceTranslationUserAnswer.objects.get(id=self.answered_question.id)
        for correct_answer in AQ.correct_answers.all():
            if removeDiacritics(self.translated_sentence.lower().strip()) == removeDiacritics(correct_answer.translated_sentence.lower().strip()):
                return True
        return False

    def recomputeExactCorrectness(self):
        """
        check if provided answer is absolutely correct or not
        """
        AQ = SentenceTranslationUserAnswer.objects.get(id=self.answered_question.id)
        for correct_answer in AQ.correct_answers.all():
            if self.translated_sentence.lower().strip() == correct_answer.translated_sentence.lower().strip():
                return True

        return False


class SentenceTranslationQuestion(Question):
    """ Model for questions in the Sentence Translation task.
    Contain the presented foreign word and a list of 
    acceptable answers. """
    sentence_translation_question_id = models.AutoField(primary_key=True)
    stimulus_sentence = models.CharField(max_length = 512)

    def __str__(self):
        return self.stimulus_sentence

