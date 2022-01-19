from django.db import models
from Users.models import *
from random import choice
from django.core.exceptions import ObjectDoesNotExist
import random

# Create your models here.

class LaDoExperiment(models.Model):

    EXPERIMENT_TYPE_IN_CHOICE = [
        ('primal', 'primal'),
        ('lado', 'lado'),
        ('webgazing', 'webgazing'),
        ('sentence translation', 'sentence translation'),
        ('de compound', 'de compound'),
    ]

    experiment_name = models.CharField('experiment name', max_length=100, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    last_changed_on = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True)
    has_audio = models.NullBooleanField(default=False)
    experiment_description = models.CharField(max_length=400, null=True)
    publish = models.BooleanField(default=True)
    experiment_type = models.CharField(max_length=100, choices=EXPERIMENT_TYPE_IN_CHOICE, default='lado')
    experiment_language = models.CharField(max_length=100, null=True, blank=True, default=None)




class LaDoExperimentIntro(models.Model):
    experiment = models.ForeignKey(LaDoExperiment, null=True)
    Intro_line = models.TextField(null=True)
    line_number = models.IntegerField(null=True)
    is_active = models.NullBooleanField(default=True)




class LadoProlificUser(models.Model):

    prolific_id = models.CharField(max_length=100, null=True, default=None)
    created_on = models.DateTimeField(auto_now_add=True, null=True)

    gender = models.ForeignKey(Gender, null=True, blank=True, default=None, on_delete=models.CASCADE)
    age = models.IntegerField(null=True, blank=True, default=None)
    location = models.ForeignKey(Country, null=True, blank=True, default=None, on_delete=models.CASCADE)
    languages = models.ForeignKey(Language, null=True, default=None, on_delete=models.CASCADE)
    is_active = models.NullBooleanField(default=True)
    is_delete = models.NullBooleanField(default=False)
    try_count = models.IntegerField(default=0)
    other_languages = models.TextField(null=True, blank=True, default='')
    first_language = models.TextField(null=True, blank=True, default='')



class CloseTestExperiment(models.Model):

    EXPERIMENT_TYPE_IN_CHOICE = [
        ('round1', 'round1')
    ]

    close_test_experiment_id = models.AutoField(primary_key=True)
    experiment_name = models.CharField('experiment name', max_length=100, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    last_changed_on = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True)
    has_audio = models.NullBooleanField(default=False)
    experiment_description = models.CharField(max_length=400, null=True)
    publish = models.BooleanField(default=True)
    experiment_type = models.CharField(max_length=100, choices=EXPERIMENT_TYPE_IN_CHOICE, default='round1')

    experiment_native_language = models.ForeignKey(Language, related_name="close_test_native_language", null=True)
    experiment_foreign_language = models.ForeignKey(Language, related_name="close_test_foreign_language", null=True)


    @staticmethod
    def getAvailableCloseTestExperiments(userInfo):

        try:
            participation_objs = CloseTestExperimentParticipation.objects.filter(user=userInfo)
            completed_exp_list = []

            for obj in participation_objs:
                # print(obj.experiment.close_test_experiment_id, obj.user_id)
                if obj.completed_on == None:
                    # print("Existing: ", obj.experiment.close_test_experiment_id)
                    return obj.experiment.close_test_experiment_id

                completed_exp_list.append(obj.experiment.close_test_experiment_id)


            user_native_languages = [x.language_code for x in userInfo.getNativeLanguages()][0]
            exp_list = CloseTestExperiment.objects.filter(is_active=True,
                                                          experiment_native_language__language_code=user_native_languages).values_list('close_test_experiment_id', flat=True)

            remaining_exp = list(set(exp_list) - set(completed_exp_list))
            print("Remaining: ", remaining_exp)
            print("Total: ", exp_list)
            print("completed: ", completed_exp_list)
            if len(remaining_exp) > 0:
                # print("New experiment: ")
                return random.choice(remaining_exp)
            else:
                return None

        except Exception as E:
            print(E)
            return 0
# close test

class CloseTestExperimentQuestion(models.Model):

    question_id = models.AutoField(primary_key=True)
    experiment = models.ForeignKey(CloseTestExperiment, null=True)
    full_fragment = models.TextField(null=True)
    sentence_block_text = models.TextField(null=True)
    sentence_block_audio = models.TextField(null=True)
    sentence_block_translation = models.TextField(null=True)
    group = models.IntegerField(default=1)
    block = models.IntegerField(null=True, default=None)
    is_active = models.NullBooleanField(default=True)
    is_delete = models.NullBooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    last_changed_on = models.DateTimeField(auto_now=True, null=True)


    def total_time(self):

        # return total time in sec
        return 60


class CloseTestExperimentParticipation(models.Model):

    EXPERIMENT_PARTICIPATION_TYPE_IN_CHOICE = [
        ('audio', 'audio'),
        ('text', 'text')
    ]

    user = models.ForeignKey(UserInfo, null=True, blank=True, default=None)
    experiment = models.ForeignKey(CloseTestExperiment, null=True)
    started_on = models.DateTimeField(auto_now=True)
    completed_on = models.DateTimeField(null=True)
    retry_count = models.IntegerField(default=0)
    is_active = models.NullBooleanField(default=True)
    is_delete = models.NullBooleanField(default=False)
    allocated_group = models.IntegerField(null=True, default=1)
    total_time_taken = models.CharField(max_length=100, null=True) #time in seconds

    exp_participation_type = models.CharField(max_length=100, choices=EXPERIMENT_PARTICIPATION_TYPE_IN_CHOICE,
                                              default='text')

    lado_prolific_user = models.ForeignKey(LadoProlificUser, null=True, blank=True, default=None)

    def getAllUserAnswerQuestions(self):

        return self.close_test_exp_given_answers.all().order_by('answer_order')


    def getExperimentStatistics(self):
        experiment_language = self.experiment.experiment_foreign_language.language_name
        total_correct = 0
        user_answer_list = self.getAllUserAnswerQuestions()

        ua_answer_list = []
        question_anwer_list = []
        for ua in user_answer_list:
            ua_answer_list.append(ua.answer)
            question_anwer_list.append(ua.question.sentence_block_text)
            if ua.answer.strip() == ua.question.sentence_block_text.strip():
                # print("match", ua.answer)
                total_correct += 1

        total_question = len(user_answer_list)
        accuracy = float(total_correct / total_question)
        time_taken = self.total_time_taken

        return (experiment_language, total_question, total_correct, time_taken, accuracy, ua_answer_list, question_anwer_list)


    # def checkCompletion(self):
    #     """ Checks if all questions have been answered"""
    #     if self.close_test_exp_given_answers.filter(completed_answered=False).exists():
    #         return False
    #     else:
    #         return True
    #
    #
    # # return answer in self.trans_game_given_answers.filter(is_answered=False).exists()
    #
    # #
    # def getNextUserAnswerID(self, chunk=1, is_random=False):
    #     """ Returns (the ID of) another UserAnswer for the participating user. The UserAnswer (and thus the question) is selected at random from the as-of-yet-unanswered questions. """
    #     ids = self.decompound_exp_given_answers.filter(completed_answered=False, is_active=True).order_by('id').values_list('id', flat=True)
    #     print(ids)
    #     if not ids:
    #         return None
    #     else:
    #         return ids[0]
    #
    # def getRunningStatistics(self):
    #     ans_objs = self.decompound_exp_given_answers.filter(completed_answered=True, is_active=True)
    #     block_list = []
    #     total_task_time = 0.0
    #     completed_task = 0
    #     total_blocks = 12
    #     total_tasks = 300
    #     for ans in ans_objs:
    #         if ans.question.block not in block_list:
    #             block_list.append(ans.question.block)
    #         total_task_time += float(ans.total_time_taken)
    #         completed_task += 1
    #     completed_block = len(block_list)
    #     avg_time_task = float(round((total_task_time / (1000 * completed_task)),2))
    #     avg_time_block = float(round((total_task_time / (1000 * completed_block * 60)),2))
    #     total_time = float(round((total_task_time / (1000 * 60)), 2))
    #
    #     return avg_time_task, avg_time_block, total_time, total_blocks, total_tasks, completed_block, completed_task
    #
    #


class CloseTestUserAnswer(models.Model):

    answering_user = models.ForeignKey(UserInfo, related_name='close_test_given_answers', null=True, blank=True, default=None)
    participation = models.ForeignKey(CloseTestExperimentParticipation, related_name='close_test_exp_given_answers', null=True)
    question = models.ForeignKey(CloseTestExperimentQuestion, related_name='close_test_exp_answers', null=True)
    answer = models.TextField(null=True, blank=True, default=None)
    time_taken = models.CharField(null=True, max_length=200) # time in seconds to answer per question
    created_time = models.DateTimeField(auto_now=True)
    updated_time = models.DateTimeField(null=True)
    answer_order = models.IntegerField(null=True, default=1)

    def getTotalAllocatedTime(self):

        question_section = self.question.full_fragment.split(' ')
        total_words = len(question_section) - 1
        total_time = total_words * 3 + 10 # 3 seconds per words and 10 seconds for 1 gap

        return int(total_time)

# end close test





class DECompoundExperimentQuestion(models.Model):
    experiment = models.ForeignKey(LaDoExperiment, null=True, default=12)
    defination_ru = models.TextField(null=True)
    compound_word_de = models.TextField(null=True)
    supportive_defination_ru = models.NullBooleanField(default=True)
    neutral_defination_ru = models.NullBooleanField(default=True)
    group = models.IntegerField(default=1)
    block = models.IntegerField(default=1)
    participant_languages = models.TextField(null=True, default='ru_de')
    is_active = models.NullBooleanField(default=True)
    is_delete = models.NullBooleanField(default=False)


class DECompoundExperimentParticipation(models.Model):
    user = models.ForeignKey(UserInfo, null=True, blank=True, default=None)
    experiment = models.ForeignKey(LaDoExperiment, null=True)
    started_on = models.DateTimeField(auto_now=True)
    completed_on = models.DateTimeField(null=True)
    retry_count = models.IntegerField(default=0)
    is_active = models.NullBooleanField(default=True)
    is_delete = models.NullBooleanField(default=False)
    allocated_group = models.IntegerField(null=True, default=1)
    allocated_blocks = models.TextField(null=True)
    answered_blocks = models.TextField(null=True, default=None)
    current_block = models.IntegerField(null=True, default=1)

    lado_prolific_user = models.ForeignKey(LadoProlificUser, null=True, blank=True, default=None)

    def getTotalNumberOfBlockQuestions(self):
        """ Returns the total number of questions for this Participation. """
        return self.decompound_exp_given_answers.filter(question__block=self.current_block).count()


    def getNumberOfBlockAnsweredQuestions(self):
        """ Returns the number of answered questions so far. """
        return self.decompound_exp_given_answers.filter(question__block=self.current_block, completed_answered=True).count()

    def checkCompletion(self):
        """ Checks if all questions have been answered"""
        if self.decompound_exp_given_answers.filter(completed_answered=False).exists():
            return False
        else:
            return True


    # return answer in self.trans_game_given_answers.filter(is_answered=False).exists()

    #
    def getNextUserAnswerID(self, chunk=1, is_random=False):
        """ Returns (the ID of) another UserAnswer for the participating user. The UserAnswer (and thus the question) is selected at random from the as-of-yet-unanswered questions. """
        ids = self.decompound_exp_given_answers.filter(completed_answered=False, is_active=True).order_by('id').values_list('id', flat=True)
        print(ids)
        if not ids:
            return None
        else:
            return ids[0]

    def getRunningStatistics(self):
        ans_objs = self.decompound_exp_given_answers.filter(completed_answered=True, is_active=True)
        block_list = []
        total_task_time = 0.0
        completed_task = 0
        total_blocks = 12
        total_tasks = 300
        for ans in ans_objs:
            if ans.question.block not in block_list:
                block_list.append(ans.question.block)
            total_task_time += float(ans.total_time_taken)
            completed_task += 1
        completed_block = len(block_list)
        avg_time_task = float(round((total_task_time / (1000 * completed_task)),2))
        avg_time_block = float(round((total_task_time / (1000 * completed_block * 60)),2))
        total_time = float(round((total_task_time / (1000 * 60)), 2))

        return avg_time_task, avg_time_block, total_time, total_blocks, total_tasks, completed_block, completed_task


class DECompoundExperimentUserAnswer(models.Model):

    ANSWER_1_IN_CHOICES = [
        (1, 'very bad'),
        (2, 'rather bad'),
        (3, 'rather good'),
        (4, 'very good')
    ]

    ANSWER_2_IN_CHOICES = [
        (1, 'first part'),
        (2, 'second part'),
        (3, 'both'),
        (4, 'none')
    ]


    answering_user = models.ForeignKey(UserInfo, related_name='decompound_exp_given_answers', null=True, blank=True, default=None)
    participation = models.ForeignKey(DECompoundExperimentParticipation, related_name='decompound_exp_given_answers', null=True)
    question = models.ForeignKey(DECompoundExperimentQuestion, related_name='decompound_exp_answers', null=True)
    user_answer1 = models.IntegerField(null=True, blank=True, default=None, choices=ANSWER_1_IN_CHOICES)
    user_answer2 = models.IntegerField(null=True, blank=True, default=None, choices=ANSWER_2_IN_CHOICES)
    answer1_time = models.CharField(null=True, max_length=200) # time in miliseconds
    answer2_time = models.CharField(null=True, max_length=200) # time in milisecond
    is_answered_1 = models.NullBooleanField(default=False)
    is_answered_2 = models.NullBooleanField(default=False)
    completed_answered = models.NullBooleanField(default=False)
    is_active = models.NullBooleanField(default=True)
    answered_time = models.DateTimeField(null=True)
    total_time_taken = models.CharField(null=True, max_length=200)  # in miliseconds
    created_time = models.DateTimeField(auto_now=True)
    updated_time = models.DateTimeField(null=True)
    answer_order = models.IntegerField(null=True, default=1)



class TranslationGameQuestion(models.Model):

    experiment = models.ForeignKey(LaDoExperiment, null=True, default=5)
    line1 = models.TextField(null=True)
    line2 = models.TextField(null=True)
    language = models.ForeignKey(Language, null=True, default=None, on_delete=models.CASCADE)
    is_active = models.NullBooleanField(default=True)
    is_delete = models.NullBooleanField(default=False)


# this is a general experiment participation for prolific experiments
class TranslationGameExperimentParticipation(models.Model):
    user = models.ForeignKey(UserInfo, null=True, blank=True, default=None)
    experiment = models.ForeignKey(LaDoExperiment, null=True)
    started_on = models.DateTimeField(auto_now=True)
    completed_on = models.DateTimeField(null=True)
    retry_count = models.IntegerField(default=0)
    is_active = models.NullBooleanField(default=True)
    is_delete = models.NullBooleanField(default=False)

    lado_prolific_user = models.ForeignKey(LadoProlificUser, null=True, blank=True, default=None)

    def getTotalNumberOfQuestions(self):
        """ Returns the total number of questions for this Participation. """
        return self.trans_game_given_answers.count()

    def getNumberOfAnsweredQuestions(self):
        """ Returns the number of answered questions so far. """
        return self.trans_game_given_answers.filter(is_answered=True).count()

    def checkCompletion(self):
        """ Checks if all questions have been answered"""
        if self.trans_game_given_answers.filter(is_answered=False).exists():
            return False
        else:
            return True

    # return answer in self.trans_game_given_answers.filter(is_answered=False).exists()

    #
    def getNextUserAnswerID(self, chunk=5, is_random=False):
        """ Returns (the ID of) another UserAnswer for the participating user. The UserAnswer (and thus the question) is selected at random from the as-of-yet-unanswered questions. """
        ids = self.trans_game_given_answers.filter(is_answered=False, is_active=True).order_by('id').values_list('id', flat=True)
        print(ids)
        if not ids:
            return None

        elif len(ids) < chunk:
            print(type(ids))
            return list(ids)
        else:
            # C = choice(ids)
            return ids[:chunk]



class TranslationGameUserAnswer(models.Model):
    answering_user = models.ForeignKey(UserInfo, related_name='trans_game_given_answers', null=True, blank=True, default=None)
    participation = models.ForeignKey(TranslationGameExperimentParticipation, related_name='trans_game_given_answers', null=True)
    question = models.ForeignKey(TranslationGameQuestion, related_name='trans_game_answers', null=True)
    user_answer = models.TextField(null=True)
    is_answered = models.NullBooleanField(default=False)
    is_active = models.NullBooleanField(default=True)
    answered_time = models.DateTimeField(null=True)
    time_taken = models.CharField(null=True, max_length=200)  # in miliseconds




class LaDoExperimentParticipation(models.Model):
    user = models.ForeignKey(UserInfo, null=True, blank=True, default=None)
    experiment = models.ForeignKey(LaDoExperiment, null=True)
    started_on = models.DateTimeField(auto_now=True)
    completed_on = models.DateTimeField(null=True)
    retry_count = models.IntegerField(default=0)
    is_active = models.NullBooleanField(default=True)
    is_delete = models.NullBooleanField(default=False)

    lado_prolific_user = models.ForeignKey(LadoProlificUser, null=True, blank=True, default=None)

    def getTotalNumberOfQuestions(self):
        """ Returns the total number of questions for this Participation. """
        return self.lado_given_answers.count()

    def getNumberOfAnsweredQuestions(self):
        """ Returns the number of answered questions so far. """
        return self.lado_given_answers.filter(is_answered=True).count()

    def checkCompletion(self):
        """ Checks if all questions have been answered"""
        if self.lado_given_answers.filter(is_answered=False).exists():
            return False
        else:
            return True

    # return answer in self.lado_given_answers.filter(is_answered=False).exists()

    #
    def getNextUserAnswerID(self):
        """ Returns (the ID of) another UserAnswer for the participating user. The UserAnswer (and thus the question) is selected at random from the as-of-yet-unanswered questions. """
        ids = self.lado_given_answers.filter(is_answered=False, question__question_group=1).values('id')
        if not ids:
            return None
        else:
            C = choice(ids)
            return C["id"]

    def getNextUserAnswerID_group2(self):
        """ Returns (the ID of) another UserAnswer for the participating user. The UserAnswer (and thus the question) is selected at random from the as-of-yet-unanswered questions. """
        ids = self.lado_given_answers.filter(is_answered=False, question__question_group=2).values('id')
        if not ids:
            return None
        else:
            C = choice(ids)
            return C["id"]



class LaDoQuestion(models.Model):
    experiment = models.ForeignKey(LaDoExperiment, null=True, default=1)
    file_name = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=100)
    question_group = models.IntegerField(default=1, null=True)


class LaDoUserAnswer(models.Model):
    answering_user = models.ForeignKey(UserInfo, related_name='lado_given_answers', null=True, blank=True, default=None)
    participation = models.ForeignKey(LaDoExperimentParticipation, related_name='lado_given_answers', null=True)
    question = models.ForeignKey(LaDoQuestion, related_name='lado_answers', null=True)
    user_answer = models.CharField(max_length=150, null=True)
    answer_confidence = models.IntegerField(default=0, null=True)
    is_answered = models.NullBooleanField(default=False)
    is_active = models.NullBooleanField(default=True)
    answered_time = models.DateTimeField(null=True)
    time_taken = models.CharField(null=True, max_length=200)  # in miliseconds
    audio_listen_count = models.IntegerField(default=1, null=True)


class LaDoExperimentStatistics(models.Model):
    participation = models.ForeignKey(LaDoExperimentParticipation, null=True)
    total_question = models.IntegerField(default=0)
    total_correct = models.IntegerField(default=0)
    total_time_in_min = models.FloatField(default=0)
    avg_time_in_sec = models.FloatField(default=0)
    completed_on = models.DateTimeField(null=True)
    inserted_on = models.DateTimeField(auto_now=True)
    is_active = models.NullBooleanField(default=True)
    is_delete = models.NullBooleanField(default=False)


class PrimalExperimentQuestion(models.Model):
    PRIMING_TYPE_IN_CHOICE = [
        ('phonetic', 'phonetic'),
        ('cognate', 'cognate'),
        ('filler', 'filler'),
        ('unknown', 'unknown')
    ]

    RESPONSE_IN_CHOICE = [
        ('a', 'word'),
        ('l', 'non-word')
    ]
    experiment = models.ForeignKey(LaDoExperiment, null=True, default=0)

    token1_name = models.CharField(max_length=150, null=True)
    token1_gloss = models.CharField(max_length=150, null=True)
    token1_language = models.CharField(max_length=100, null=True)
    token1_filename = models.TextField(null=True)

    token2_name = models.CharField(max_length=150, null=True)
    token2_gloss = models.CharField(max_length=150, null=True)
    token2_filename = models.TextField(null=True)
    token2_language = models.CharField(max_length=100, null=True)

    native_language = models.CharField(max_length=100, null=True)
    priming_type = models.CharField(max_length=100, null=True, choices=PRIMING_TYPE_IN_CHOICE, default='unknown')
    correct_response = models.CharField(max_length=100, choices=RESPONSE_IN_CHOICE)
    phonetic_distance = models.FloatField(null=True)

    csv_file_path = models.TextField(null=True)
    csv_file_name = models.CharField(max_length=200, null=True)



class PrimalExperimentParticipation(models.Model):
    user = models.ForeignKey(UserInfo, null=True, blank=True, default=None)
    experiment = models.ForeignKey(LaDoExperiment, null=True)
    started_on = models.DateTimeField(auto_now=True)
    completed_on = models.DateTimeField(null=True)
    retry_count = models.IntegerField(default=0)
    is_active = models.NullBooleanField(default=True)
    is_delete = models.NullBooleanField(default=False)

    primal_prolific_user = models.ForeignKey(LadoProlificUser, null=True, blank=True, default=None)


    def getTotalNumberOfQuestions(self):
        """ Returns the total number of questions for this Participation. """
        return self.primal_given_answers.count()

    def getNumberOfAnsweredQuestions(self):
        """ Returns the number of answered questions so far. """
        return self.primal_given_answers.filter(is_answered=True).count()

    def checkCompletion(self):
        """ Checks if all questions have been answered"""
        if self.primal_given_answers.filter(is_answered=False).exists():
            return False
        else:
            return True

    # return answer in self.lado_given_answers.filter(is_answered=False).exists()

    #
    def getNextUserAnswerID(self):
        """ Returns (the ID of) another UserAnswer for the participating user. The UserAnswer (and thus the question) is selected at random from the as-of-yet-unanswered questions. """
        ids = self.primal_given_answers.filter(is_answered=False).values('id')
        if not ids:
            return None
        else:
            C = choice(ids)
            return C["id"]


    def getRunningCorrect(self):

        try:
            obj = self.primal_given_answers.filter(is_answered=True).latest('answered_time')
            return obj.running_correct

        except ObjectDoesNotExist as e:
            return -1



class PrimalExperimentUserAnswer(models.Model):
    answering_user = models.ForeignKey(UserInfo, related_name='primal_given_answers', null=True, blank=True, default=None)
    participation = models.ForeignKey(PrimalExperimentParticipation, related_name='primal_given_answers', null=True)
    question = models.ForeignKey(PrimalExperimentQuestion, related_name='primal_answers', null=True)
    question_play_order = models.IntegerField(default=0)
    user_answer = models.CharField(max_length=150, null=True)
    is_answered = models.NullBooleanField(default=False)
    is_active = models.NullBooleanField(default=True)
    answered_time = models.DateTimeField(null=True)
    time_taken = models.CharField(null=True, max_length=200)  # in miliseconds
    audio_listen_count = models.IntegerField(default=1, null=True)
    running_correct = models.IntegerField(default=0)
    running_avg_time = models.FloatField(default=0)


class PrimalExperimentStatistics(models.Model):
    participation = models.ForeignKey(PrimalExperimentParticipation, null=True)
    total_question = models.IntegerField(default=0)
    total_correct = models.IntegerField(default=0)
    total_time_in_min = models.FloatField(default=0)
    avg_time_in_sec = models.FloatField(default=0)
    completed_on = models.DateTimeField(null=True)
    inserted_on = models.DateTimeField(auto_now=True)
    is_active = models.NullBooleanField(default=True)
    is_delete = models.NullBooleanField(default=False)


class WebGazingExperimentQuestions(models.Model):
    experiment = models.ForeignKey(LaDoExperiment, null=True, default=4)
    question_id = models.AutoField(primary_key=True)
    con = models.IntegerField(null=True, blank=True, default=None)
    stim = models.NullBooleanField(default=None)
    att_check = models.NullBooleanField(default=None)
    decl = models.NullBooleanField(default=None)
    interr = models.NullBooleanField(default=None)
    english_translation = models.CharField(max_length=250, null=True, blank=True, default=None)
    czech_translation = models.CharField(max_length=250, null=True, blank=True, default=None)
    polish_translation = models.CharField(max_length=250, null=True, blank=True, default=None)
    russian_translation = models.CharField(max_length=250, null=True, blank=True, default=None)
    bulgarian_translation = models.CharField(max_length=250, null=True, blank=True, default=None)
    bcs_ijek_translation = models.CharField(max_length=250, null=True, blank=True, default=None)
    czech_audio = models.TextField(null=True)
    polish_audio = models.TextField(null=True)
    bulgarian_audio = models.TextField(null=True)
    russian_audio = models.TextField(null=True)
    visual_target = models.TextField()
    visual_fillers = models.TextField()
    czech_audio_gaze_start = models.FloatField(null=True, blank=True, default=0)
    czech_audio_gaze_end = models.FloatField(null=True, blank=True, default=0)
    polish_audio_gaze_start = models.FloatField(null=True, blank=True, default=0)
    polish_audio_gaze_end = models.FloatField(null=True, blank=True, default=0)
    bulgarian_audio_gaze_start = models.FloatField(null=True, blank=True, default=0)
    bulgarian_audio_gaze_end = models.FloatField(null=True, blank=True, default=0)
    russian_audio_gaze_start = models.FloatField(null=True, blank=True, default=0)
    russian_audio_gaze_end = models.FloatField(null=True, blank=True, default=0)
    inserted_on = models.DateTimeField(auto_now=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_active = models.NullBooleanField(default=True)
    is_delete = models.NullBooleanField(default=False)

    def getAudio(self, lang_code):

        if lang_code == 'ru':
            return '/media/'+self.russian_audio, self.russian_audio_gaze_start, self.russian_audio_gaze_end
        elif lang_code == 'pl':
            return '/media/'+self.polish_audio, self.polish_audio_gaze_start, self.polish_audio_gaze_end
        elif lang_code == 'bg':
            return '/media/'+self.bulgarian_audio, self.bulgarian_audio_gaze_start, self.bulgarian_audio_gaze_end
        elif lang_code == 'cs':
            return '/media/'+self.czech_audio, self.czech_audio_gaze_start, self.czech_audio_gaze_end
        else:
            return 0






class WebGazingExperimentParticipation(models.Model):
    user = models.ForeignKey(UserInfo, null=True, blank=True, default=None)
    experiment = models.ForeignKey(LaDoExperiment, null=True)
    started_on = models.DateTimeField(auto_now=True)
    completed_on = models.DateTimeField(null=True)
    retry_count = models.IntegerField(default=0)
    is_active = models.NullBooleanField(default=True)
    is_delete = models.NullBooleanField(default=False)

    webgazing_prolific_user = models.ForeignKey(LadoProlificUser, null=True, blank=True, default=None)


    def getTotalNumberOfQuestions(self):
        """ Returns the total number of questions for this Participation. """
        return self.webgazing_given_answers.count()

    def getNumberOfAnsweredQuestions(self):
        """ Returns the number of answered questions so far. """
        return self.webgazing_given_answers.filter(is_answered=True).count()

    def checkCompletion(self):
        """ Checks if all questions have been answered"""
        if self.webgazing_given_answers.filter(is_answered=False).exists():
            return False
        else:
            return True

    # return answer in self.lado_given_answers.filter(is_answered=False).exists()

    #
    def getNextUserAnswerID(self):
        """ Returns (the ID of) another UserAnswer for the participating user. The UserAnswer (and thus the question) is selected at random from the as-of-yet-unanswered questions. """
        ids = self.webgazing_given_answers.filter(is_answered=False).values('id')
        if not ids:
            return None
        else:
            C = choice(ids)
            return C["id"]


    def getRunningCorrect(self):

        try:
            obj = self.webgazing_given_answers.filter(is_answered=True).latest('answered_time')
            return obj.running_correct

        except ObjectDoesNotExist as e:
            return -1




class WebGazingExperimentUserAnswer(models.Model):
    answering_user = models.ForeignKey(UserInfo, related_name='webgazing_given_answers', null=True, blank=True, default=None)
    participation = models.ForeignKey(WebGazingExperimentParticipation, related_name='webgazing_given_answers', null=True)
    question = models.ForeignKey(WebGazingExperimentQuestions, related_name='webgazing_answers', null=True)
    question_play_order = models.IntegerField(default=0)
    user_answer = models.CharField(max_length=150, null=True)
    is_answered = models.NullBooleanField(default=False)
    is_active = models.NullBooleanField(default=True)
    answered_time = models.DateTimeField(null=True)
    time_taken = models.CharField(null=True, max_length=200)  # in miliseconds
    audio_listen_count = models.IntegerField(default=1, null=True)
    running_correct = models.IntegerField(default=0)
    running_avg_time = models.FloatField(default=0)

    user_gaze_answer = models.TextField(null=True)
    user_gaze_coordinates = models.TextField(null=True)
    correct_image_coordinates = models.TextField(null=True)
    all_images_name = models.TextField(null=True)
    all_images_coordinates = models.TextField(null=True)





