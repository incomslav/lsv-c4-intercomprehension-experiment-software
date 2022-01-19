from collections import defaultdict

from Common.constants import *
from Common.Enums import *
from Users.enums import *

from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.core.files.storage import FileSystemStorage

from PhraseTranslationExperiment.models import *

import json

from io import BytesIO


def getTimes(json_data):
    changes = json.loads(json_data)
    out = []
    timestamps = []
    states = []
    
    if len(changes) >= 2:
        hesitation_time = float(changes[1][1]) - float(changes[0][1])
    else:
        hesitation_time = float("inf")
        
    if len(changes) >= 3:
        time_spent_typing = float(changes[-1][1]) - float(changes[0][1])
    else:
        time_spent_typing = float("inf")

    return hesitation_time, time_spent_typing


class ExportAnswersPreviewView(View):
    def get(self, request):
        
        headers = ["Experiment_ID", "Experiment_Name", "Question_ID", "Question"]
        
        num_exp = 0
        num_users = 0
        num_participations = 0

        data = [("Experiment ID", "Experiment Name", "Question ID", "Question Word", "# Total", "# No Answer", "# Correct", "# Incorrect", "% Correct", "% Incorrect", "Avg time spent", "Avg time spent correct", "Avg time spent incorrect", "Avg hesitation time", "Avg hesitation time correct", "Avg hesitation time incorrect", "Avg typing time correct", "Avg typing time incorrect")]
        common = [num_exp]
        
        for experiment in PhraseTranslationExperiment.objects.all():
            num_exp += 1
            questions = []
            no_answers = defaultdict(lambda: 0)
            correct_answers = defaultdict(lambda:0)
            incorrect_answers = defaultdict(lambda:0)
            total_times_no_answer = defaultdict(lambda:[])
            total_times_correct = defaultdict(lambda:[])
            total_times_incorrect = defaultdict(lambda:[])
            hesitation_times_no_answer = defaultdict(lambda:[])
            hesitation_times_correct = defaultdict(lambda:[])
            hesitation_times_incorrect = defaultdict(lambda:[])
            typing_times_no_answer = defaultdict(lambda:[])
            typing_times_correct = defaultdict(lambda:[])
            typing_times_incorrect = defaultdict(lambda:[])

            
            # get all participations in this experiment
            for question in experiment.experiment_questions.select_subclasses():
                questions.append((experiment.id, experiment.experiment_name, question.id, question.foreign_word))
                
                num_answers = 0
                for user_answer in UserAnswer.objects.filter(answered_question=question).select_subclasses():
                    user = user_answer.answering_user
                    if user_answer.answer_given:
                        num_answers += 1
                        
                        data.append((experiment.id, experiment.experiment_name, question.id, question.foreign_word, user.id, user.user.email, user_answer.native_word, user_answer.isCorrectAnswer()))
                        hesitation_time, typing_time = getTimes(user_answer.result_changes)

                        total_time = user_answer.time_spent
                        
                        if user_answer.native_word:
                            no_answers[question.id] += 1
                            hesitation_times_no_answer[question.id].append(hesitation_time)
                            typing_times_no_answer[question.id].append(typing_time)
                            total_times_no_answer[question.id].append(total_time)
                        
                        else:
                            if user_answer.isCorrectAnswer():
                                correct_answers[question.id] += 1
                                hesitation_times_correct[question.id].append(hesitation_time)
                                typing_times_correct[question.id].append(typing_time)
                                total_times_correct[question.id].append(total_time)
                            else:
                                incorrect_answers[question.id] += 1
                                hesitation_times_incorrect[question.id].append(hesitation_time)
                                typing_times_incorrect[question.id].append(typing_time)
                                total_times_incorrect[question.id].append(total_time)
                
                if num_answers > 0:
                    perc_no_answer = no_answers[question.id]/num_answers
                    perc_correct = correct_answers[question.id]/num_answers
                    perc_incorrect = incorrect_answers[question.id]/num_answers
                    
                    avg_total_time = (sum(total_times_correct[question.id]) + sum(total_times_incorrect[question.id])) / num_answers
                    avg_hesitation_time = (sum(hesitation_times_correct[question.id]) + sum(hesitation_times_incorrect[question.id])) / num_answers
                    avg_typing_time = (sum(typing_times_correct[question.id]) + sum(typing_times_incorrect[question.id])) / num_answers
                    
                    if total_times_no_answer[question.id]:
                        avg_total_time_no_answer = (sum(total_times_no_answer[question.id])) / len(total_times_no_answer[question.id])
                        avg_hesitation_time_no_answer = (sum(hesitation_times_no_answer[question.id])) / len(hesitation_times_no_answer[question.id])
                        avg_typing_time_no_answer = (sum(typing_times_no_answer[question.id])) / len(typing_times_no_answer[question.id])

                else:
                    perc_no_answer = "N/A"
                    perc_correct = "N/A"
                    perc_incorrect = "N/A"
                    
                    avg_total_time = "N/A"
                    avg_hesitation_time = "N/A"
                    avg_typing_time = "N/A"

                    avg_total_time_no_answer = "N/A"
                    avg_hesitation_time_no_answer = "N/A"
                    avg_typing_time_no_answer = "N/A"
                
                if correct_answers[question.id] > 0:
                    avg_total_time_cor = sum(total_times_correct[question.id]) / correct_answers[question.id]
                    avg_hesitation_time_cor = sum(hesitation_times_correct[question.id]) / correct_answers[question.id]
                    avg_typing_time_cor = sum(typing_times_correct[question.id]) / correct_answers[question.id]
                
                else:
                    avg_total_time_cor = "N/A"
                    avg_hesitation_time_cor = "N/A"
                    avg_typing_time_cor = "N/A"

                if incorrect_answers[question.id] > 0:
                    avg_total_time_incor = sum(total_times_incorrect[question.id]) / incorrect_answers[question.id]
                    avg_hesitation_time_incor = sum(hesitation_times_incorrect[question.id]) / incorrect_answers[question.id]
                    avg_typing_time_incor = sum(typing_times_incorrect[question.id]) / incorrect_answers[question.id]
                
                else:
                    avg_total_time_incor = "N/A"
                    avg_hesitation_time_incor = "N/A"
                    avg_typing_time_incor = "N/A"
                
                data.append((experiment.id, experiment.experiment_name, question.id, question.foreign_word, num_answers, no_answers[question.id], correct_answers[question.id], incorrect_answers[question.id], perc_no_answer, perc_correct, perc_incorrect, avg_total_time, avg_total_time_no_answer, avg_total_time_cor, avg_total_time_incor, avg_hesitation_time_no_answer, avg_hesitation_time, avg_hesitation_time_cor, avg_hesitation_time_incor, avg_typing_time, avg_typing_time_no_answer, avg_typing_time_cor, avg_typing_time_incor))

        return render(request, "adminpanel/ListAnswers.html", {'common_data': common, 'data': data })
