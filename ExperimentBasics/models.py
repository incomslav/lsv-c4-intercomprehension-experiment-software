__author__ = 'A. K. Fischer'
from datetime import datetime
from random import choice
from itertools import groupby

from PIL import Image

import os

from Incomslav.settings import *

from django.conf import settings

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator
# from polymorphic.models import PolymorphicModel

from model_utils.managers import InheritanceManager

from ExperimentBasics.definitions import *

from Users.models import *

from django.core.files.storage import FileSystemStorage

import logging
logger = logging.getLogger("ayan")

fs = FileSystemStorage(location=settings.EXPERIMENT_MEDAL_FOLDER, base_url=settings.EXPERIMENT_MEDAL_URL)

"""
class RelatedParent(PolymorphicModel):
    name = models.CharField('related parent name', max_length=100, null=True)

class RelatedA(RelatedParent):
    field_A = models.IntegerField()

class RelatedB(RelatedParent):
    field_B = models.CharField('related parent name', max_length=100, null=True)

class Parent(PolymorphicModel):
    name = models.CharField('parent name', max_length=100, null=True)
    related = models.ForeignKey(RelatedParent, null=True)
    
class ChildA(Parent):
    additional_A = models.IntegerField()
    
class ChildB(Parent):
    additional_B = models.IntegerField()
"""

""" START BASIC EXPERIMENT """


class ExperimentPrerequisite(models.Model):
    """ Abstract prerequisite class. A user is eligible for an experiment only 
    if she/he fulfills all prerequisites associated with that experiment."""

    objects = InheritanceManager()

    def fulfilledByUser(self, user):
        """ Method to determine if given user fulfills this prerequisite."""
        raise NotImplemented()

    def __str__(self):
        return "AbstractPrerequisite #" + str(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __le__(self, other):
        return self.id < other.id

    class Meta:
        ordering = ["id"]


class Question(models.Model):
    """ Abstract question model to allow to get all questions for experiment easily."""
    objects = InheritanceManager()

    def getNumbersOfAnswers(self):
        correct = 0
        incorrect = 0
        for UA in UserAnswer.objects.filter(answered_question=self).select_subclasses():
            if UA.isCorrectAnswer():
                correct += 1
            else:
                incorrect += 1

        return correct, incorrect


class Experiment(models.Model):
    """ Base class for Experiments. One experiment is associated with exactly one set of questions. """
    objects = InheritanceManager()

    experiment_name = models.CharField('experiment name', max_length=100, null=True)

    priority = models.IntegerField('experiment priority', choices=[(i, i) for i in range(101)], default=0, null=True)

    user_prerequisites = models.ManyToManyField(ExperimentPrerequisite)

    experiment_questions = models.ManyToManyField(Question, related_name="question_to_experiment_assignment")

    is_active = models.BooleanField(default=False)
    meta = models.CharField('meta', max_length=1024, null=True)

    user_medal = models.ImageField(upload_to=settings.EXPERIMENT_MEDAL_FOLDER, storage=fs, width_field="medal_width",
                                   height_field="medal_height", null=True, blank=True)
    medal_width = models.PositiveIntegerField(default=0)
    medal_height = models.PositiveIntegerField(default=0)

    created_on = models.DateTimeField(auto_now_add=True, null=True)
    last_changed_on = models.DateTimeField(auto_now=True, null=True)

    stimuli_file = models.CharField(max_length=1000, null=True, blank=True) #Added by Hasan on 2018-05-28
    folder_name = models.CharField(max_length=500, null=True, blank=True) #Added by Hasan on 2018-05-28

    native_script = models.CharField(max_length=100, null=True, blank=True, default=None) #Added by Hasan on 2018-05-28
    foreign_script = models.CharField(max_length=100, null=True, blank=True, default=None)    #Added by Hasan on 2018-05-28
    # Flag for availability of Audio Experiment
    is_audio_experiment = models.BooleanField(default=False)

    text_experiment = models.BooleanField(default=True)
    audio_experiment = models.BooleanField(default=False)

    """
    def save(self):
        super(Experiment, self).save()
        print(self.user_medal.path, self.user_medal.url)
        img = Image.open(self.user_medal.path)
        width = self.user_medal.width
        height = self.user_medal.height
        size = (100,100)
        img = img.resize(size, Image.ANTIALIAS)
        img.save(self.user_medal.path)
    """

    def __str__(self):
        if self.experiment_name is None:
            return "Experiment %d" % (self.id)

        else:
            return self.experiment_name

    def __repr__(self):
        return str(self)


    def getNumbersOfCollectedAnswers(self):
        """ Returns a dictionary containing the number of answers for each rank this experiment has answers for. """
        num_at_rank = {}
        for answer in ExperimentParticipation.objects.filter(experiment=self, completed_on__isnull=False).order_by(
                "user", "completed_on").distinct("user"):
            R = answer.getAnswerRank()
            if not R in num_at_rank:
                num_at_rank[R] = 0

            num_at_rank[R] += 1

        return num_at_rank

    #AYAN: Audio Answers
    def getNumbersOfCollectedAnswersForAudio(self):
        """ Returns a dictionary containing the number of answers for each rank this experiment has answers for. """
        num_at_rank = {}
        for answer in ExperimentParticipation.objects.filter(experiment=self, experiment_type="audio", completed_on__isnull=False).order_by(
                "user", "completed_on").distinct("user"):
            R = answer.getAnswerRank()
            if not R in num_at_rank:
                num_at_rank[R] = 0

            num_at_rank[R] += 1

        return num_at_rank


    @staticmethod
    def getExperimentsCompletedByUser(userInfo):
        """ Fetches all experiments the given user has completed, in order of completion. """
        experiments = []
        for ep in ExperimentParticipation.objects.filter(user=userInfo, completed_on__isnull=False).distinct(
                "experiment"):
            experiments.append((ep.experiment, ep.completed_on))
        return sorted(experiments, key=lambda x: x[-1])

    @staticmethod
    def getExperimentsAvailableToUser(userInfo):
        """ Fetches all experiments that the user can still complete, if he or she continues participating in experiments.
        Experiments are in descending order by priority. """
        # print('ok1')
        user_native_languages= [x.language_code for x in userInfo.getNativeLanguages()]
        user_all_languages = list(userInfo.getAllLanguages())
        print(user_native_languages)
        user_languages= [x.language_code for x in user_all_languages]

        # if user does not know any cyrillic language then don't show any experiment in cyrillic languages
        # Commented by Hasan
        # is_cyrillic = False
        # ls_cyrillic_languages = ['bg','sr','ru','uk','be','mk']
        # print('Calling')
        # for ul in user_languages:
        #     if ul in ls_cyrillic_languages:
        #         is_cyrillic = True
        #         break

        # Added by Hasan on 10_06_2018
        for l in user_all_languages:
            print(l.language_name)
        user_scripts = LanguageScriptRelation.objects.filter(language__in=user_all_languages).distinct('script__script_name')
        for s in user_scripts:
            print(s.script.script_name, s.language.language_name)

        script_code = [x.script.script_code for x in user_scripts]
        # print(script_code)

        experiments = []
        for exp in Experiment.objects.filter(is_active=True).select_subclasses():

            if exp.userFulfillsPrerequisites(userInfo):
                if not ExperimentParticipation.objects.filter(experiment=exp, user=userInfo,
                                                              completed_on__isnull=False).exists():

                    # here add logic for non-cyrillic users
                    print("here1")
                    print(type(exp))
                    foreign_lang = exp.foreign_language
                    print("here2")
                    native_language = exp.native_language

                    #Commented by Hasan 

                    # # exclude experiments related to cyrillic language
                    # if not is_cyrillic:
                    #     if foreign_lang.language_code in ls_cyrillic_languages or native_language.language_code in ls_cyrillic_languages:
                    #         # return the control to the beginning of the experiment for loop
                    #         continue

                    # We need to do for native language also

                    if exp.foreign_script is not None:
                        print(exp.foreign_script, script_code)
                        if exp.foreign_script not in script_code:
                            # print('continued')
                            continue

                        foreign_lang_script = LanguageScriptRelation.objects.filter(language=foreign_lang)
                        continue_flag = False
                        for cs in foreign_lang_script:
                            if cs.script.script_code in script_code:
                                continue_flag = True
                                continue

                        if continue_flag is True:
                            continue
                        # print(exp)
                    else:
                        foreign_lang_script = LanguageScriptRelation.objects.filter(language=foreign_lang)
                        continue_flag = True
                        for cs in foreign_lang_script:
                             
                            if cs.script.script_code in script_code:
                                continue_flag = False

                        if continue_flag is True:
                            continue

                    


                    # here add logic for cz users
                    # if they know pl exclude pl for cz, if they know bg exclude bg for cz etc.
                    foreign_lang = exp.foreign_language
                    if 'cs' in user_native_languages:
                        if foreign_lang not in user_all_languages:
                            experiments.append(exp)
                    else:
                        experiments.append(exp)


        return sorted(experiments, key=lambda x: x.priority, reverse=True)

    @staticmethod
    def getExperimentIDsWithSharedPrerequisites():
        """ This static method yields lists with IDs of Experiments grouped by their prerequisites.
        Each group of prerequisites results in one list of Experiment IDs which share the same prerequisites.
        The prerequisites themselves are not included in the output. """
        EXPS = Experiment.objects.all()
        L = []
        for E in EXPS:
            U = []
            for req in E.user_prerequisites.all():
                U.append(req.id)
            L.append((E.id, U))
        for preq, exps in groupby(sorted(L, key=lambda x: x[-1]), lambda x: x[-1]):
            yield list(map(lambda x: x[0], exps))

    def userHasCompletedExperiment(self, userInfo):
        """ Method to determine if a user has completed this experiment before. """
        # user has not completed experiment if no completed ExperimentParticipation can be found.
        return ExperimentParticipation.objects.filter(user=userInfo, experiment=self,
                                                      completed_on__isnull=False).exists()


    def getLastParticipationForUser(self, userInfo):
        """ Fetches the last ExperimentParticipation object associated with this experiment for a given user. """
        try:
            latestParticipation = ExperimentParticipation.objects.filter(user=userInfo, experiment=self).latest(
                'started_on')
            return latestParticipation

        except ObjectDoesNotExist as e:
            return None

    def retryGetActiveParticipationForUser(self, userInfo):

        try:
            re_latestParticipation = RetryExperimentParticipation.objects.filter(user=userInfo, experiment=self).latest('started_on')

            if re_latestParticipation.completed_on is None:
                return re_latestParticipation

            new_retry_count = re_latestParticipation.retry_count + 1
            MAX_RETRY = 5

            if new_retry_count > MAX_RETRY:
                return 'MAXED'

            return self.RetryMakeNewParticipation(userInfo, new_retry_count)

        except:
            pass

        return self.RetryMakeNewParticipation(userInfo, 1)


    def getActiveParticipationForUser(self, userInfo, expType='text'):
        """ Get the last incomplete participation for the user, or create a new one. """
        try:
            latestParticipation = ExperimentParticipation.objects.filter(user=userInfo, experiment=self).latest(
                'started_on')
            if latestParticipation.completed_on is None:
                return latestParticipation  # return the last existing participation object if it is not completed yet

        except ObjectDoesNotExist as e:
            pass  #pass through to the end case, where a new participation is created and returned

        if expType == 'audio':
            return self.makeNewParticipation(userInfo, expType)
            
        return self.makeNewParticipation(userInfo)

    def deactivate(self):
        """ Deactivate this experiment to be no longer shown to users."""
        self.is_active = False
        self.save()

    def activate(self):
        """ Activate this experiment to be shown to users."""
        self.is_active = True
        self.save()

    def userFulfillsPrerequisites(self, user):
        """ Checks if the given user fulfills all associated prerequisites."""
        for user_prerequisite in self.user_prerequisites.select_subclasses():
            if not user_prerequisite.fulfilledByUser(user):
                return False

        return True

    def getNumberOfQuestions(self):
        """ Returns the total number of questions associated with this experiment. """
        return self.experiment_questions.count()

    class Meta:
        managed = True
        db_table = 'experiments'
        app_label = 'ExperimentBasics'
        ordering = (("-priority"),)


# Modified class of 'ExperimentParticipation' for experiment retry
# Added by Hasan

class RetryExperimentParticipation(models.Model):
    user = models.ForeignKey(UserInfo, null=True)
    experiment = models.ForeignKey(Experiment, null=True)
    started_on = models.DateTimeField(auto_now=True)
    completed_on = models.DateTimeField(null=True)
    retry_count = models.IntegerField(default=0)
    is_active = models.NullBooleanField(default=True)
    is_delete = models.NullBooleanField(default=False)

    def getUserAnswerForQuestionID(self, questionID):
        """ Picks out the UserAnswer for the question with the given question ID. """
        return UserAnswer.objects.get(answered_question__id=questionID, experiment_participation=self)

    def checkAndSetCompletion(self):
        """ Checks if all questions have been answered and subsequently registers this experiment participation as completed if it hadn't been before. """
        comp = self.checkCompletion()
        if comp and self.completed_on is None:
            self.completed_on = datetime()
            self.save()
        return comp

    def getTotalNumberOfQuestions(self):
        """ Returns the total number of questions for this Participation. """
        return self.re_given_answers.count()

    def getNumberOfAnsweredQuestions(self):
        """ Returns the number of answered questions so far. """
        return self.re_given_answers.filter(re_answer_given=True).count()

    def getResults(self):
        """ Returns the number of correct and incorrect answers along with their mean completion time. """
        logger.error("%%% getResults")
        try:
            total_time = 0.0
            num_correct = 0
            num_incorrect = 0
            num_not_answered = 0
            for answer in self.re_given_answers.all():
                if not answer.re_answer_given:
                    num_not_answered += 1
                else:
                    Aset = RetryUserAnswer.objects.filter(id=answer.id).select_subclasses()
                    for A in Aset:
                        total_time += A.re_time_spent
                        if A.isCorrectAnswer():
                            num_correct += 1
                        else:
                            num_incorrect += 1

            num_total = num_correct + num_incorrect + num_not_answered
            return num_total, num_correct, num_incorrect, num_not_answered, total_time
        except Exception as ex:
            return ex

    def getResultsForGapFilling(self):
        """ Returns the number of correct and incorrect answers along with their mean completion time. """
        logger.error("### getResultsGapFilling") 
        try:
            total_time = 0.0
            num_correct = 0
            num_incorrect = 0
            num_not_answered = 0

            num_correct_gaps = 0
            num_incorrect_gaps = 0
            num_not_answered_gaps = 0
            total_gaps =0

            for answer in self.re_given_answers.all():
                if not answer.re_answer_given:
                    num_not_answered += 1
                else:
                    Aset = RetryUserAnswer.objects.filter(id=answer.id).select_subclasses()
                    for A in Aset:
                        total_time += A.re_time_spent
                        # ---------gaps answers-----------
                        total_gaps += len(A.gaps_answers.split(','))

                        gaps_ans_dict = A.recomputeNormalizedCorrectness()
                        if gaps_ans_dict:
                            logger.error("### getResultsGapFilling... "+str(gaps_ans_dict)) 
                            if False in gaps_ans_dict.values():
                                num_incorrect += 1
                            else:
                                num_correct+=1

                            for g in gaps_ans_dict:
                                if gaps_ans_dict[g] == False:
                                    num_incorrect_gaps += 1
                                else:
                                    num_correct_gaps += 1
                        else:
                            num_incorrect += 1

                            # if A.isCorrectAnswer():
                            #     num_correct += 1
                            # else:
                            #     num_incorrect += 1

            num_total = num_correct + num_incorrect + num_not_answered
            return num_total, num_correct, num_incorrect, num_not_answered, total_time, total_gaps, num_correct_gaps,num_incorrect_gaps
        except Exception as ex:
            return ex

    def checkCompletion(self):
        """ Checks if all questions have been answered"""
        return answer in self.re_given_answers.filter(re_answer_given=False).exists()

    def getNextUserAnswerID(self):
        """ Returns (the ID of) another UserAnswer for the participating user. The UserAnswer (and thus the question) is selected at random from the as-of-yet-unanswered questions. """
        ids = self.re_given_answers.filter(re_answer_given=False).values('id')
        print(ids)
        if not ids:
            return None
        else:
            C = choice(ids)
            return C["id"]

    def getAnswerRank(self):
        """ Returns the rank of this experiment participation object, the information which experiment this was for the user who participated. """
        if self.completed_on is None:
            return None
        else:
            return RetryExperimentParticipation.objects.filter(user=self.user, completed_on__lt=self.completed_on).distinct(
                "experiment").count()
            #TODO: test this!!!


# model to store experiment result statistics
# added by hasan

class RetryExperimentStatistics(models.Model):
    retry_participation = models.ForeignKey(RetryExperimentParticipation, null=True)
    # for audio
    retry_is_audio_experiment = models.NullBooleanField(default=False)
    total_question = models.IntegerField(default=0)
    total_correct = models.IntegerField(default=0)
    total_time_in_min = models.FloatField(default=0)
    avg_time_in_sec = models.FloatField(default=0)
    completed_on = models.DateTimeField(null=True)
    inserted_on = models.DateTimeField(auto_now=True)
    is_active = models.NullBooleanField(default=True)
    is_delete = models.NullBooleanField(default=False)


class ExperimentParticipation(models.Model):
    """ Class modeling a specific user's participation in a specific experiment. """
    user = models.ForeignKey(UserInfo, null=True)
    experiment = models.ForeignKey(Experiment, null=True)
    started_on = models.DateTimeField(auto_now=True)
    completed_on = models.DateTimeField(null=True)
    experiment_type = models.CharField(max_length=20, default="text")

    @staticmethod
    def getUserRank(userInfo):
        """ Returns the number of distinct experiments this user has already completed. """
        return ExperimentParticipation.objects.filter(user=userInfo, completed_on__isnull=False).distinct(
            "experiment").count()

    def getUserAnswerForQuestionID(self, questionID):
        """ Picks out the UserAnswer for the question with the given question ID. """
        return UserAnswer.objects.get(answered_question__id=questionID, experiment_participation=self)

    def checkAndSetCompletion(self):
        """ Checks if all questions have been answered and subsequently registers this experiment participation as completed if it hadn't been before. """
        comp = self.checkCompletion()
        if comp and self.completed_on is None:
            self.completed_on = datetime()
            self.save()
        return comp

    def getTotalNumberOfQuestions(self):
        """ Returns the total number of questions for this Participation. """
        return self.given_answers.count()

    def getNumberOfAnsweredQuestions(self):
        """ Returns the number of answered questions so far. """
        return self.given_answers.filter(answer_given=True).count()

    def getResults(self):
        """ Returns the number of correct and incorrect answers along with their mean completion time. """
        logger.error("### getResults...")
        try:
            total_time = 0.0
            num_correct = 0
            num_incorrect = 0
            num_not_answered = 0
            for answer in self.given_answers.all():
                if not answer.answer_given:
                    num_not_answered += 1
                else:
                    Aset = UserAnswer.objects.filter(id=answer.id).select_subclasses()
                    logger.error("### "+str(Aset))
                    for A in Aset:
                        total_time += A.time_spent
                        if A.isCorrectAnswer():
                            num_correct += 1
                        else:
                            num_incorrect += 1

            num_total = num_correct + num_incorrect + num_not_answered
            return num_total, num_correct, num_incorrect, num_not_answered, total_time
        except Exception as ex:
            return ex

    def getResultsForGapFilling(self):
        """ Returns the number of correct and incorrect answers along with their mean completion time. """
        logger.error("### getResultsGapFill...")
        try:
            total_time = 0.0
            num_correct = 0
            num_incorrect = 0
            num_not_answered = 0

            num_correct_gaps = 0
            num_incorrect_gaps = 0
            num_not_answered_gaps = 0
            total_gaps =0

            for answer in self.given_answers.all():
                if not answer.answer_given:
                    num_not_answered += 1
                else:
                    Aset = UserAnswer.objects.filter(id=answer.id).select_subclasses()
                    for A in Aset:
                        total_time += A.time_spent
                        # ---------gaps answers-----------
                        total_gaps += len(A.gaps_answers.split(','))
                   
                        gaps_ans_dict = A.recomputeNormalizedCorrectness()
                        logger.error("### "+str(gaps_ans_dict))
                        if gaps_ans_dict:
                            if False in gaps_ans_dict.values():
                                num_incorrect += 1
                            else:
                                num_correct+=1

                            for g in gaps_ans_dict:
                                if gaps_ans_dict[g] == False:
                                    num_incorrect_gaps += 1
                                else:
                                    num_correct_gaps += 1
                        else:
                            num_incorrect += 1

                            # if A.isCorrectAnswer():
                            #     num_correct += 1
                            # else:
                            #     num_incorrect += 1

            num_total = num_correct + num_incorrect + num_not_answered
            return num_total, num_correct, num_incorrect, num_not_answered, total_time, total_gaps, num_correct_gaps,num_incorrect_gaps
        except Exception as ex:
            return ex

    def checkCompletion(self):
        """ Checks if all questions have been answered"""
        return answer in self.given_answers.filter(answer_given=False).exists()

    def getNextUserAnswerID(self):
        """ Returns (the ID of) another UserAnswer for the participating user. The UserAnswer (and thus the question) is selected at random from the as-of-yet-unanswered questions. """
        ids = self.given_answers.filter(answer_given=False).values('id')
        if not ids:
            return None
        else:
            C = choice(ids)
            return C["id"]

    def getAnswerRank(self):
        """ Returns the rank of this experiment participation object, the information which experiment this was for the user who participated. """
        if self.completed_on is None:
            return None
        else:
            return ExperimentParticipation.objects.filter(user=self.user, completed_on__lt=self.completed_on).distinct(
                "experiment").count()
            #TODO: test this!!!


class UserAnswer(models.Model):
    """ Abstract user answer model. Specifies which user answered which
    question. """
    objects = InheritanceManager()

    answering_user = models.ForeignKey(UserInfo, related_name="given_answers", null=True)
    answered_question = models.ForeignKey(Question, related_name="answers", null=True)
    experiment_participation = models.ForeignKey(ExperimentParticipation, null=True, related_name="given_answers")
    answer_date = models.DateTimeField(null=True)
    answer_given = models.BooleanField(default=False)

    is_exactly_correct = models.NullBooleanField()
    normalized_form_is_correct = models.NullBooleanField()

    time_spent = models.IntegerField(validators=[MinValueValidator(0)], null=True)

    def isExactlyCorrectAnswer(self):
        """
        return is_exactly_correct bool field if it is Null then recompute via respective answer type
        """
        if not self.is_exactly_correct is None:
            return self.is_exactly_correct
        else:
            return self.recomputeExactCorrectness()

    def isCorrectAnswer(self):
        """
        return normalized_form_is_correct bool field if it is Null then recompute via respective answer type
        """
        if not self.normalized_form_is_correct is None:
            logger.error("^^^ self normalized_form_is_correct")
            return self.normalized_form_is_correct
        else:
            logger.error("^^^ going to compute normalized")
            return self.recomputeNormalizedCorrectness()

    def __str__(self):
        return str(self.id) + "[U=%d, Q=%d, P=%d, G=%s, D=%s]" % (
        self.answering_user.id, self.answered_question.id, self.experiment_participation.id, str(self.answer_given),
        str(self.answer_date))

    class Meta:
        db_table = 'user_answers'
        app_label = 'ExperimentBasics'


# for Retry Experiment
class RetryUserAnswer(models.Model):
    """ Abstract user answer model. Specifies which user answered which
    question. """
    objects = InheritanceManager()

    re_answering_user = models.ForeignKey(UserInfo, related_name="re_given_answers", null=True)
    re_answered_question = models.ForeignKey(Question, related_name="re_answers", null=True)
    re_experiment_participation = models.ForeignKey(RetryExperimentParticipation, null=True, related_name="re_given_answers")
    re_answer_date = models.DateTimeField(null=True)
    re_answer_given = models.BooleanField(default=False)

    re_is_exactly_correct = models.NullBooleanField()
    re_normalized_form_is_correct = models.NullBooleanField()

    re_time_spent = models.IntegerField(validators=[MinValueValidator(0)], null=True)

    def isExactlyCorrectAnswer(self):
        """
        return is_exactly_correct bool field if it is Null then recompute via respective answer type
        """
        if not self.re_is_exactly_correct is None:
            return self.re_is_exactly_correct
        else:
            return self.recomputeExactCorrectness()

    def isCorrectAnswer(self):
        """
        return normalized_form_is_correct bool field if it is Null then recompute via respective answer type
        """
        if not self.re_normalized_form_is_correct is None:
            return self.re_normalized_form_is_correct
        else:
            return self.recomputeNormalizedCorrectness()

    def __str__(self):
        return str(self.id) + "[U=%d, Q=%d, P=%d, G=%s, D=%s]" % (
        self.re_answering_user.id, self.re_answered_question.id, self.re_experiment_participation.id, str(self.re_answer_given),
        str(self.re_answer_date))

    class Meta:
        db_table = 'retry_user_answers'
        app_label = 'ExperimentBasics'



class NativeLanguagePrerequisite(ExperimentPrerequisite):
    """ Prerequisite on native language. Can be positive (user must have native
    language) or negative (user may not have native language)."""
    required_language = models.ForeignKey(Language)
    positive = models.BooleanField("native yes/no")

    def __str__(self):
        if self.positive:
            return self.required_language.language_code + " native"
        else:
            return self.required_language.language_code + " non-native"

    def fulfilledByUser(self, user):
        """ Method to determine if given user fulfills this prerequisite."""
        user_has_native_language = user.hasNativeLanguage(self.required_language)
        if self.positive:
            return user_has_native_language
        else:
            return not user_has_native_language

    class Meta:
        db_table = 'native_language_prerequisites'
        app_label = 'ExperimentBasics'
        unique_together = (("required_language", "positive"), )


class News(models.Model):
    """ News class to handel news section of the website. """

    news_description = models.CharField('news description', max_length=1024, null=True)
    priority = models.IntegerField('news priority', choices=[(i, i) for i in range(11)], default=0, null=True)
    is_active = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(UserInfo, null=True)
    last_changed_on = models.DateTimeField(auto_now=True, null=True)


    def __str__(self):
        if self.news_description is None:
            return "News %d" % (self.id)

        else:
            return self.news_description

    def __repr__(self):
        return str(self)


    class Meta:
        managed = True
        db_table = 'news'
        app_label = 'ExperimentBasics'
        ordering = (("-priority"),)


class InformedConsent(models.Model):
    """ InformedConsent class to handel informed consent page of the website. """

    consent_description = models.CharField('consent description', max_length=1024, null=True)
    priority = models.IntegerField('consent priority', choices=[(i, i) for i in range(11)], default=0, null=True)
    is_active = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(UserInfo, null=True)
    last_changed_on = models.DateTimeField(auto_now=True, null=True)


    def __str__(self):
        if self.consent_description is None:
            return "InformedConsent %d" % (self.id)

        else:
            return self.consent_description

    def __repr__(self):
        return str(self)


    class Meta:
        managed = True
        db_table = 'informed_consent'
        app_label = 'ExperimentBasics'
        ordering = (("-priority"),)


class ExperimentInfo(models.Model):
    """ Experiment info class to handel experiment info section of the website. """

    experiment_info = models.CharField('experiment info', max_length=1024, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(UserInfo, null=True)
    last_changed_on = models.DateTimeField(auto_now=True, null=True)


    def __str__(self):
        if self.experiment_info is None:
            return "Experiment Info %d" % (self.id)

        else:
            return self.experiment_info

    def __repr__(self):
        return str(self)


    class Meta:
        managed = True
        db_table = 'experiment_info'
        app_label = 'ExperimentBasics'
