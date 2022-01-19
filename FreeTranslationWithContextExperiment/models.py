
from ExperimentBasics.models import *
from django.core.urlresolvers import reverse
from Common.constants import *
from django.utils.translation import ugettext as _
from django.db import models
from math import ceil
from Common.common_utils import removeDiacritics

class FreeTranslationWithContextExperiment(Experiment):
    """
    Free Translation with Context Experiment class
    """
    free_translation_with_context_experiment_id = models.AutoField(primary_key=True)
    native_language = models.ForeignKey(Language, related_name="FreeTranslationWithContext_native_language", null=True)
    foreign_language = models.ForeignKey(Language, related_name="FreeTranslationWithContext_foreign_language", null=True)

    # def getAllocatedTimePerQuestion(self):
    #     """ Returns, in seconds, the time allocated to each individual question. """
    #     return 10

    def getAllocatedTimeForAllQuestions(self):
        """ Returns, in seconds, the time allocated to all questions. """
        time=0
        for question in self.experiment_questions.select_subclasses():
            time+= question.question_answer_time
        return time

    def getExperimentNameForUser(self):
        """ Gets the Experiment's name. """
        return "Free Translation with Context "+self.native_language.language_code+"-"+self.foreign_language.language_code

    def getRedirectURL(self):
        """ The URL this experiment links to for its actual questions. """
        return reverse("FreeTranslationWithContextQuestions")

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
        experimentName = _("FREE_TRANSLATION_WITH_CONTEXT_EXPERIMENT")
        return experimentName, language_table

    def getWelcomeTemplateStrings(self):
        """ Returns strings for this experiment to be used in the Experiment Welcome template. """
        strings = {}
        strings['EXPERIMENT_WELCOME_HEADER'] = _("FREE_TRANSLATION_WITH_CONTEXT_EXPERIMENT_WELCOME_HEADER") + " #"+str(self.free_translation_with_context_experiment_id)

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

        strings['EXPERIMENT_INSTRUCTIONS'] += "<p>"+_("FREE_TRANSLATION_WITH_CONTEXT_EXPERIMENT_WELCOME_PAGE_TOTAL_QUESTIONS_TEXT").format(self.getNumberOfQuestions())+ "</p>"
        strings['EXPERIMENT_INSTRUCTIONS'] += "<p>"+_("FREE_TRANSLATION_WITH_CONTEXT_SENTENCE_TEXT").format(self.getNumberOfQuestions())+"</p>"
        keyboard_text = _("FREE_TRANSLATION_WITH_CONTEXT_EXPERIMENT_WELCOME_PAGE_SET_KEYBOARD_LANGUAGE_TEXT")
        if not keyboard_text.endswith("."):
            keyboard_text += " " + lang_labels["toLangName"] + "."

        strings['EXPERIMENT_INSTRUCTIONS'] += "<p><b>" + keyboard_text + "</b></p>"
        strings['EXPERIMENT_INSTRUCTIONS'] += "<p>" + _("FREE_TRANSLATION_WITH_CONTEXT_EXPERIMENT_WELCOME_PAGE_CLOSE_BROWSER_WINDOWS_TEXT") + "</p>"
        strings['EXPERIMENT_INSTRUCTIONS'] += "<p>" + _("FREE_TRANSLATION_WITH_CONTEXT_EXPERIMENT_WELCOME_PAGE_TIME_ESTIMATE_TEXT").format(ceil(self.getAllocatedTimeForAllQuestions()/60))+"</p>"
        strings['EXPERIMENT_INSTRUCTIONS'] += "<p>" + _("FREE_TRANSLATION_WITH_CONTEXT_EXPERIMENT_WELCOME_PAGE_START_WHEN_READY_TEXT") +"</p>"

        strings['EXPERIMENT_INSTRUCTIONS'] += """<marquee onmouseover="this.stop();" onmouseout="this.start();">
                   <h4 style=""> {} <img src="/static/images/smilely.png" style="width: 30px;"></h4>
       </marquee>""".format(_("FREE_TRANSLATION_WITH_CONTEXT_EXPERIMENT_WELCOME_PAGE_HOW_FAST_ARE_YOU_TEXT"))

        """<p>You will be presented <b>{} sentences in {}</b>, which will appear <b>one by one</b>.<br>
        Your task is to <b>enter appropriate word for the gap in {} without using any help from other people, a dictionary, or the internet</b>.<br>
        Try to be as fast and accurate as you can!</p>

        <p>Please <b>adjust your keyboard settings for {}</b> and <b>close all other browser windows</b>.</p>

        <p>When you are ready, check 'I am ready' and click on the 'start experiment' button to proceed.<p>""".format(str(self.getNumberOfQuestions()), self.foreign_language.language_name, self.native_language.language_name, self.native_language.language_name)

        return strings


    def makeNewParticipation(self, userInfo):
        """ Returns a new experiment participation object for this experiment. """
        try:
            newParticipation = ExperimentParticipation()
            newParticipation.experiment = self
            newParticipation.user = userInfo
            newParticipation.save()

            for question in self.experiment_questions.all():
                # make new FreeTranslationWithContextUserAnswer for this participation
                A = FreeTranslationWithContextUserAnswer()
                A.answering_user = userInfo
                A.answered_question = question
                A.experiment_participation = newParticipation
                A.save()

            return newParticipation
        except Exception as e:
            print(str(e))
            return None

class FreeTranslationWithContextAnswer(models.Model):
    """ Model for any answer in Free Translation with Context task.
     """
    free_translation_with_context_answer_id = models.AutoField(primary_key=True)
    gap_answer = models.CharField(max_length = 1024, null=True)

    def __eq__(self, other):
        """ Convenience method to compare to other answers. """
        return self.gap_answer == other.gap_answer


class FreeTranslationWithContextCorrectAnswer(FreeTranslationWithContextAnswer):
    """ Model for a correct answer in the Free Translation With Context task.
    Empty shell to allow for convenient handling. Associated with
    FreeTranslationWithContextQuestion. """
    free_translation_with_context_correct_answer_id = models.AutoField(primary_key=True)


class FreeTranslationWithContextQuestion(Question):
    """ Model for questions in the Free Translation With Context task.
    Contain the presented sentence and a list of
    acceptable answers. """
    free_translation_with_context_question_id = models.AutoField(primary_key=True)
    sentence = models.CharField(max_length = 1024)
    question_answer_time = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    correct_answers = models.ManyToManyField(FreeTranslationWithContextCorrectAnswer, related_name="associated_question")

    def __str__(self):
        return self.sentence

    def answerCorrect(self, given_answer):
        """ Checks if the given answer is acceptable. """
        for correct_answer in self.correct_answers:
            if correct_answer == given_answer:
                return True
        return False


class FreeTranslationWithContextUserAnswer(UserAnswer, FreeTranslationWithContextAnswer):
    """ A Free Translation With Context user answer. Stores the final reply and a
    JSON-encoded log of the input changes and (millisecond)
    times of change."""
    free_translation_with_context_user_answer_id = models.AutoField(primary_key=True)
    result_changes = models.TextField(null=True)
    words_click_time = models.TextField(null=True)

    def recomputeNormalizedCorrectness(self):
        """ Go through all the correct answers associated with the answered question and see if one matches with normalized form of this one. """
        if self.normalized_form_is_correct is None and not self.gap_answer is None:
            AQ = FreeTranslationWithContextQuestion.objects.get(id=self.answered_question.id)
            for correct_answer in AQ.correct_answers.all():
                if removeDiacritics(self.gap_answer.lower().strip()) == removeDiacritics(correct_answer.gap_answer.lower().strip()):
                    self.normalized_form_is_correct = True
                    break
        else:
            self.normalized_form_is_correct = False

        return self.normalized_form_is_correct
        return self.recomputeExactCorrectness()

    def recomputeExactCorrectness(self):
        """
        check if provided answer is absolutely correct or not
        """
        if not self.gap_answer is None:
            AQ = FreeTranslationWithContextQuestion.objects.get(id=self.answered_question.id)
            for correct_answer in AQ.correct_answers.all():
                if self.gap_answer.strip().casefold() == correct_answer.gap_answer.strip().casefold():
                    return True

        return False