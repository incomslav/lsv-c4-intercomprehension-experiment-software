from ExperimentBasics.models import *
from django.core.urlresolvers import reverse
from Common.constants import *
from django.utils.translation import ugettext as _
from django.db import models
from math import ceil
from Common.common_utils import removeDiacritics


class MixedLanguagesGapFillingExperiment(Experiment):
    """
    Mixed Languages Gap Filling Experiment class
    """
    mixed_gap_filling_experiment_id = models.AutoField(primary_key=True)
    native_language = models.ForeignKey(Language, related_name="MixedLanguagesGapFilling_native_language", null=True)
    # foreign_language = models.ForeignKey(Language, related_name="MixedLanguagesGapFilling_foreign_language", null=True)
    foreign_language = models.TextField(null=True)

    # def getAllocatedTimePerQuestion(self):
    # """ Returns, in seconds, the time allocated to each individual question. """
    # return 10

    def getAllocatedTimeForAllQuestions(self):
        """ Returns, in seconds, the time allocated to all questions. """
        time = 0
        for question in self.experiment_questions.select_subclasses():
            time += question.question_answer_time
        return time

    def getExperimentNameForUser(self):
        """ Gets the Experiment's name. """
        return "Gap Filling " + self.native_language.language_code + "-" + self.foreign_language

    def getRedirectURL(self):
        """ The URL this experiment links to for its actual questions. """
        return reverse("MixedLanguagesGapFillingQuestions")

    def getExperimentNameForExperimentMedalsPage(self):
        lang_labels = {}
        lang_labels["fromLangLabel"] = _("EXPERIMENT_FROM_LANGUAGE_LABEL")
        lang_labels["fromLangName"] = _("GAP_FILLING_SLAVIC_LANGUAGES_TEXT")
        lang_labels["fromLangCode"] = self.foreign_language
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
        experimentName = _("GAP_FILLING_EXPERIMENT")
        return experimentName, language_table

    def getWelcomeTemplateStrings(self):
        """ Returns strings for this experiment to be used in the Experiment Welcome template. """
        try:
            strings = {}
            strings['EXPERIMENT_WELCOME_HEADER'] = _("GAP_FILLING_EXPERIMENT_WELCOME_HEADER") + " #" + str(
                self.mixed_gap_filling_experiment_id)

            lang_labels = {}
            lang_labels["fromLangLabel"] = _("EXPERIMENT_FROM_LANGUAGE_LABEL")
            lang_labels["fromLangName"] = _("GAP_FILLING_WELCOME_PAGE_SLAVIC_LANGUAGES_TEXT")
            lang_labels["fromLangCode"] = self.foreign_language

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

            strings['EXPERIMENT_INSTRUCTIONS'] += "<p>" + _(
                "GAP_FILLING_EXPERIMENT_WELCOME_PAGE_TOTAL_WORDS_TEXT").format(self.getNumberOfQuestions()) + "</p>"
            strings['EXPERIMENT_INSTRUCTIONS'] += "<p>" + _("GAP_FILLING_SENTENCE_TEXT") + "</p>"
            strings['EXPERIMENT_INSTRUCTIONS'] += "<p>" + _("GAP_FILLING_EXPERIMENT_EXAMPLE_TEXT") + "</p>"
            # adding video
            strings[
                'EXPERIMENT_INSTRUCTIONS'] += "<p> <video width='100%' height='' controls>  <source src='/static/media/demo_gapfilling_PL_for_CS_readers.mp4' type='video/mp4'> Your browser does not support the video tag.</video> </p>"

            keyboard_text = _("GAP_FILLING_EXPERIMENT_WELCOME_PAGE_SET_KEYBOARD_LANGUAGE_TEXT")
            if not keyboard_text.endswith("."):
                keyboard_text += " " + lang_labels["toLangName"] + "."

            strings['EXPERIMENT_INSTRUCTIONS'] += "<p><b>" + keyboard_text + "</b></p>"
            strings['EXPERIMENT_INSTRUCTIONS'] += "<p>" + _(
                "GAP_FILLING_EXPERIMENT_WELCOME_PAGE_CLOSE_BROWSER_WINDOWS_TEXT") + "</p>"
            strings['EXPERIMENT_INSTRUCTIONS'] += "<p>" + _(
                "GAP_FILLING_EXPERIMENT_WELCOME_PAGE_TIME_ESTIMATE_TEXT").format(
                ceil(self.getAllocatedTimeForAllQuestions() / 60)) + "</p>"
            # strings['EXPERIMENT_INSTRUCTIONS'] += "<p>" + _("GAP_FILLING_EXPERIMENT_WELCOME_PAGE_TIME_ESTIMATE_TEXT").format(ceil(self.getNumberOfQuestions()*self.getAllocatedTimePerQuestion()/60))+"</p>"
            strings['EXPERIMENT_INSTRUCTIONS'] += "<p>" + _(
                "GAP_FILLING_EXPERIMENT_WELCOME_PAGE_START_WHEN_READY_TEXT") + "</p>"

            strings['EXPERIMENT_INSTRUCTIONS'] += """<marquee onmouseover="this.stop();" onmouseout="this.start();">
                       <h4 style=""> {} <img src="/static/images/smilely.png" style="width: 30px;"></h4>
           </marquee>""".format(_("GAP_FILLING_EXPERIMENT_WELCOME_PAGE_HOW_FAST_ARE_YOU_TEXT"))

            """<p>You will be presented <b>{} sentences in {}</b>, which will appear <b>one by one</b>.<br>
            Your task is to <b>select appropriate word for each gap in {} without using any help from other people, a dictionary, or the internet</b>.<br>
            Try to be as fast and accurate as you can!</p>

            <p>Please <b>adjust your keyboard settings for {}</b> and <b>close all other browser windows</b>.</p>

            <p>When you are ready, check 'I am ready' and click on the 'start experiment' button to proceed.<p>""".format(
                str(self.getNumberOfQuestions()), self.foreign_language,
                self.native_language.language_name, self.native_language.language_name)

            return strings
        except Exception as ex:
            print(str(ex))
            return ex

    def makeNewParticipation(self, userInfo):
        """ Returns a new experiment participation object for this experiment. """
        try:
            newParticipation = ExperimentParticipation()
            newParticipation.experiment = self
            newParticipation.user = userInfo
            newParticipation.save()

            for question in self.experiment_questions.all():
                # make new GapFillingUserAnswer for this participation
                A = MixedLanguagesGapFillingUserAnswer()
                A.answering_user = userInfo
                A.answered_question = question
                A.experiment_participation = newParticipation
                A.save()

            return newParticipation
        except Exception as e:
            print(str(e))
            return None


class MixedLanguagesGapFillingAnswer(models.Model):
    """ Model for any answer in Gap Filling task.
    Stores the comma separated gaps in the gaps. """
    mixed_gap_filling_answer_id = models.AutoField(primary_key=True)
    gaps_answers = models.CharField(max_length=1024, null=True)

    def __eq__(self, other):
        """ Convenience method to compare to other answers. """
        return self.gaps_answers == other.gaps_answers


class MixedLanguagesGapFillingCorrectAnswer(MixedLanguagesGapFillingAnswer):
    """ Model for a correct answer in the Gap Filling task.
    Empty shell to allow for convenient handling. Associated with
    GapFillingQuestion. """
    mixed_gap_filling_correct_answer_id = models.AutoField(primary_key=True)


class MixedLanguagesGapFillingQuestion(Question):
    """ Model for questions in the Gap Filling task.
    Contain the presented sentence and a list of
    acceptable answers. """
    mixed_gap_filling_question_id = models.AutoField(primary_key=True)
    sentence = models.CharField(max_length=1024)
    question_answer_time = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    correct_answers = models.ManyToManyField(MixedLanguagesGapFillingCorrectAnswer, related_name="associated_question")

    def __str__(self):
        return self.sentence

    def answerCorrect(self, given_answer):
        """ Checks if the given answer is acceptable. """
        for correct_answer in self.correct_answers:
            if correct_answer == given_answer:
                return True
        return False


class MixedLanguagesGapFillingUserAnswer(UserAnswer, MixedLanguagesGapFillingAnswer):
    """ A Gap Filling user answer. Stores the final reply and a
    JSON-encoded log of the gaps changes and (millisecond)
    times of change."""
    mixed_gap_filling_user_answer_id = models.AutoField(primary_key=True)
    result_changes = models.TextField(null=True)
    words_click_time = models.TextField(null=True)

    def recomputeNormalizedCorrectness(self):
        """ Go through all the correct answers associated with the answered question and see if one matches with normalized form of this one. """
        ## because user has to select from already populated list so, we don't need this
        try:
            if self.normalized_form_is_correct is None and not self.gaps_answers is None:
                answers = self.gaps_answers.split(',')
                AQ = MixedLanguagesGapFillingQuestion.objects.get(id=self.answered_question.id)
                correct_answers = AQ.correct_answers.all()[0].gaps_answers.strip().split(',')
                ca_dict = {}

                userAnsCorrectnessDict = {}
                # making all possible correct answers dictionary
                for ca in correct_answers:
                    k, val = ca.split('_')
                    if k not in ca_dict:
                        ca_dict[k] = [str(removeDiacritics(val.lower())).strip()]
                    else:
                        ca_dict[k].append(str(removeDiacritics(val.lower())).strip())

                # checking user answer for each gap
                for i in range(len(answers)):
                    ans = removeDiacritics(answers[i].lower())
                    k = 'Gap' + str(i)
                    # don't forget to change below
                    ls = ca_dict[k]
                    if ans in ls:
                        userAnsCorrectnessDict[k] = True
                    else:
                        userAnsCorrectnessDict[k] = False
                        # return False

                # return True
                return userAnsCorrectnessDict

            return False
        except Exception as ex:
            return False


    def recomputeExactCorrectness(self):
        """
        check if provided answer is absolutely correct or not
        """
        try:
            if not self.gaps_answers is None:
                answers = self.gaps_answers.split(',')
                AQ = MixedLanguagesGapFillingQuestion.objects.get(id=self.answered_question.id)
                correct_answers = AQ.correct_answers.all()[0].gaps_answers.strip().split(',')
                ca_dict = {}

                userAnsCorrectnessDict = {}
                # making all possible correct answers dictionary
                for ca in correct_answers:
                    k, val = ca.split('_')
                    if k not in ca_dict:
                        ca_dict[k] = [str(val).strip()]
                    else:
                        ca_dict[k].append(str(val).strip())

                # checking user answer for each gap
                for i in range(len(answers)):
                    ans = answers[i]
                    if ans in ca_dict['Gap' + str(i)]:
                        userAnsCorrectnessDict['Gap' + str(i)] = True
                    else:
                        userAnsCorrectnessDict['Gap' + str(i)] = False
                        # return False

                # return True
                return userAnsCorrectnessDict

            return False
        except Exception as ex:
            return False