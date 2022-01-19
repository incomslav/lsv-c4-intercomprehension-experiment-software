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

from SentenceTranslationExperiment.models import *

import json

from io import BytesIO


def getTimes(json_data):
    changes = json.loads(json_data)
    out = []
    timestamps = []
    states = []
    
    if len(changes) >= 2:
        hesitation_time = float(changes[1][0]) - float(changes[0][0])
        time_spent_typing = float(changes[-1][0]) - float(changes[0][0])
    else:
        hesitation_time = float("inf")
        time_spent_typing = float("inf")

    return hesitation_time, time_spent_typing

class ExportSentenceTranslationAnswersPreviewView(View):
    def get(self, request):
        
        headers = ["Experiment_ID", "Experiment_Name", "Question_ID", "Question"]
        
        num_exp = 0
        num_users = 0
        num_participations = 0
        
        #output = BytesIO()
        #wb = Workbook(output, {'in_memory': True})
        data = [("Experiment ID", "Experiment Name", "Question ID", "Question Word", "# Answers", "Avg time spent", "Avg hesitation time", "Avg typing time")]
        common = [num_exp]
        
        for experiment in SentenceTranslationExperiment.objects.all():
            num_exp += 1
            questions = []
            total_times = defaultdict(lambda:[])
            hesitation_times = defaultdict(lambda:[])
            typing_times = defaultdict(lambda:[])
            
            """
            ws = wb.add_worksheet('UserExperimentData')
            header = wb.add_format({
                'bold': True,
                'font_size': 12
            })
            bold = wb.add_format({
                'bold': True
            })
            row_num = 1

            ws.write(0, 1, "Experiment ID", header)
            ws.write(0, 2, "Experiment Name", header)
            ws.write(0, 3, "Question ID", header)
            ws.write(0, 4, "Question Word", header)
            ws.write(0, 5, "Answers", header)
            ws.write(0, 6, "# Correct", header)
            ws.write(0, 7, "# Incorrect", header)
            ws.write(0, 8, "% Correct", header)
            ws.write(0, 9, "% Incorrect", header)
            ws.write(0, 10, "Avg time", header)
            ws.write(0, 11, "Avg time correct", header)
            ws.write(0, 12, "Avg time incorrect", header)
            ws.write(0, 13, "Avg hesitation time", header)
            ws.write(0, 14, "Avg hesitation time correct", header)
            ws.write(0, 15, "Avg hesitation time incorrect", header)
            ws.write(0, 16, "Avg typing time", header)
            ws.write(0, 17, "Avg typing time correct", header)
            ws.write(0, 18, "Avg typing time incorrect", header)
            """
            
            # get all participations in this experiment
            for question in experiment.experiment_questions.select_subclasses():
                questions.append((experiment.id, experiment.experiment_name, question.id, question.stimulus_sentence))
                
                num_answers = 0
                for user_answer in UserAnswer.objects.filter(answered_question=question).select_subclasses():
                    user = user_answer.answering_user
                    if user_answer.answer_given:
                        num_answers += 1
                        
                        data.append((experiment.id, experiment.experiment_name, question.id, question.stimulus_sentence, user.id, user.user.email, user_answer.translated_sentence, user_answer.result_changes))
                        #hesitation_time, typing_time = getTimes(user_answer.result_changes)
                        hesitation_time = 0.0
                        typing_time = 0.0

                        total_time = user_answer.time_spent
                        
                        hesitation_times[question.id].append(hesitation_time)
                        typing_times[question.id].append(typing_time)
                        total_times[question.id].append(total_time)
                
                if num_answers > 0:
                    avg_total_time = sum(total_times[question.id]) / num_answers
                    avg_hesitation_time = sum(hesitation_times[question.id]) / num_answers
                    avg_typing_time = sum(typing_times[question.id]) / num_answers

                else:
                    avg_total_time = "N/A"
                    avg_hesitation_time = "N/A"
                    avg_typing_time = "N/A"

                data.append((experiment.id, experiment.experiment_name, question.id, question.stimulus_sentence, num_answers, avg_total_time, avg_hesitation_time, avg_typing_time))
                
        
        """
                ws.write(row_num, 0, str(row_num))
                ws.write(row_num, 1, experiment.id)
                ws.write(row_num, 2, experiment.experiment_name)
                ws.write(row_num, 3, question.id)
                ws.write(row_num, 4, question.stimulus_sentence)
                ws.write(row_num, 5, num_answers)
                ws.write(row_num, 6, correct_answers[question.id])
                ws.write(row_num, 7, incorrect_answers[question.id])
                ws.write(row_num, 8, perc_correct)
                ws.write(row_num, 9, perc_incorrect)
                ws.write(row_num, 10, avg_total_time)
                ws.write(row_num, 11, avg_total_time_cor)
                ws.write(row_num, 12, avg_total_time_incor)
                ws.write(row_num, 13, avg_hesitation_time)
                ws.write(row_num, 14, avg_hesitation_time_cor)
                ws.write(row_num, 15, avg_hesitation_time_incor)
                ws.write(row_num, 16, avg_typing_time)
                ws.write(row_num, 17, avg_typing_time_cor)
                ws.write(row_num, 18, avg_typing_time_incor)
                
                row_num += 1
           



        
        wb.close()
        output.seek(0)
        response = HttpResponse(output.read(),
                                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = "attachment; filename=UserExperimentData.xlsx"

        return response
        """
        return render(request, "adminpanel/ListAnswers.html", {'common_data': common, 'data': data })
