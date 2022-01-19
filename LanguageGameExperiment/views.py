from urllib import request

from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.generic import View
from django.core.urlresolvers import reverse
from .models import *
from django.core.exceptions import ObjectDoesNotExist
import csv
import os
from django.contrib.staticfiles.storage import staticfiles_storage
# import datetime
from datetime import datetime
from pathlib import Path
import csv
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import random
from Users.models import *
import json
# import pandas as pd
import sys
import math
from collections import defaultdict
# from sklearn.utils import shuffle
import random
from Common.constants import CloseTestExperimentPageConstants
# from django.utils.translation import gettext as _

# Create your views here.


class CloseTestWelcomePage(View):

    def get(self, request, exp_id):
        context = {}

        try:
            if 'CLOSE_TEST_EXPERIMENT_COMPLETE' in request.session:
                context['experiment_completed']= True
                del request.session['CLOSE_TEST_EXPERIMENT_COMPLETE']

            userInfo = UserInfo.objects.get(user=request.user)

            selected_exp_id = CloseTestExperiment.getAvailableCloseTestExperiments(userInfo)

            # print("User Native Language: ")
            # print(selected_exp_id)

            # if there is experiment
            if selected_exp_id:
                request.session['CLOSE_TEST_SELECTED_EXP'] = selected_exp_id
                context['selected_experiment'] = request.session.get('CLOSE_TEST_SELECTED_EXP')
                print(request.session.get('CLOSE_TEST_SELECTED_EXP'))

                exp_obj = CloseTestExperiment.objects.get(close_test_experiment_id=selected_exp_id)
                context['exp_language'] = exp_obj.experiment_foreign_language.language_name

            else:
                context['finished_all_experiment'] = True


            # get experiments participation objects
            completed_experiments = CloseTestExperimentParticipation.objects.filter(user=userInfo, completed_on__isnull=False).order_by('completed_on')
            completed_exp_list = []
            for exp in completed_experiments:

                completed_exp_list.append(exp.getExperimentStatistics())

            context['completed_exp_list'] = completed_exp_list

            return render(request, 'CloseTestWelcomePage.html', context)

        except Exception as e:
            print("Exception: ", e)
            return render(request, '404_page.html')

        # return render(request, 'CloseTestWelcomePage.html', context)


    def post(self, request, exp_id):

        return HttpResponseRedirect('/LanguageGameExperiment/CloseTestExperimentPage')

# import pandas as pd
class CloseTestExperimentUpload(View):

    def get(self, request):

        return render(request, 'CloseTestExperimentUploadQuestion.html')

    def post(self, request):
        context = {}

        file_root = "E:\\MSc\\Hiwi\\LSV HiWi\\lsv-c4-django-webexperiment\\Incomslav\\static\\media\\close_test_input_files"

        files = os.listdir(file_root)

        for file in files:
            path = os.path.join(file_root, file)
            print(file, path)
            if '~' not in path:
                df = pd.read_excel(os.path.join(file_root, file))

                foreign_language = df.columns[3].split(' ')[-1]
                native_language = df.columns[4].split(' ')[-1]
                experiment_name = str(file).split('.')[0] + 'Group 1'
                experiment_type = 'round1'
                exp_obj, created = CloseTestExperiment.objects.get_or_create(
                    experiment_name = experiment_name,
                    experiment_native_language = Language.objects.get(language_code= native_language.lower()),
                    experiment_foreign_language = Language.objects.get(language_code= foreign_language.lower()),
                    experiment_type = experiment_type,
                    defaults={'is_active': True, 'publish': True},
                )

                if created:
                    count = 0
                    for idx, row in df.iterrows():

                        full_fragment = row[1]
                        start = full_fragment.find("{") + len("{")
                        end = full_fragment.find("}")
                        substring = full_fragment[start:end]
                        sentence_block, translation = substring.split('|')
                        updated_fragments = full_fragment.replace(substring, "")
                        group = str(row[2])

                        q_obj, question_created = CloseTestExperimentQuestion.objects.get_or_create(
                            experiment = exp_obj,
                            full_fragment= updated_fragments,
                            sentence_block_text=sentence_block,
                            sentence_block_translation=translation,
                            group=group,
                            defaults={
                                'block': 1
                            }
                        )

                        if question_created:
                            count += 1

                    print(experiment_name, " Total Question: ", str(count))


        return render(request, 'CloseTestExperimentUploadQuestion.html', context)


class CloseTestExperimentPage(View):

    def get(self, request):
        try:
            context = {}
            userInfo = UserInfo.objects.get(user=request.user)

            selected_experiment = request.session.get('CLOSE_TEST_SELECTED_EXP')
            context['selected_experiment'] = selected_experiment

            # creating closetest participation object
            participation, created = CloseTestExperimentParticipation.objects.get_or_create(experiment_id=selected_experiment,
                                                                                           user=userInfo,
                                                                                           exp_participation_type='text')

            if created:
                questions = CloseTestExperimentQuestion.objects.filter(experiment=participation.experiment).order_by('question_id')
                answer_order = 1
                for ques in questions:
                    answer_obj = CloseTestUserAnswer(answering_user=userInfo, participation=participation,
                                                              question=ques, answer_order=answer_order)
                    answer_order += 1
                    answer_obj.save()



            # questions = CloseTestExperimentQuestion.objects.filter(experiment=participation.experiment)
            request.session['CLOSE_TEST_PARTICIPATION_ID'] = participation.id

            f_frag = ''
            f_drop = []
            f_val = []
            total_time_allocation = 0
            for q in participation.getAllUserAnswerQuestions():

                f_frag += q.question.full_fragment
                f_val.append(q.question.sentence_block_text)
                f_drop.append([q.question.sentence_block_text, q.question.sentence_block_translation])

                #get time
                total_time_allocation += q.getTotalAllocatedTime()

            random.shuffle(f_val)
            # context['dropdown_list'] = dropdown_list
            # context['text'] = new_string
            # # context['values'] = shuffle(values, random_state=0)
            # context['values'] = values
            random.shuffle(f_drop)
            context['dropdown_list'] = f_drop
            context['text'] = f_frag
            # context['values'] = shuffle(values, random_state=0)
            context['values'] = f_val
            context['time_counter'] = total_time_allocation
            context['val'] = str(CloseTestExperimentPageConstants.WRITTEN_CLOZE_TEST_TEXT_EXPERIMENT_PAGE_INSTRUCTION_TIME).format(
                "5 min"
            )


            return render(request, 'CloseTestExperimentPage.html', context)

        except Exception as e:

            return render(request, '404_page.html')

    def post(self, request):

        try:
            time_count = int(request.POST['time_count'])
            total_allocated_time = int(request.POST['total_allocated_time'])
            total_time_taken = total_allocated_time - time_count

            time_per_question = str(float(total_time_taken) / 7)
            participation_id = request.session.get('CLOSE_TEST_PARTICIPATION_ID')
            participation_obj = CloseTestExperimentParticipation.objects.get(id=participation_id)

            for idx, q in enumerate(participation_obj.getAllUserAnswerQuestions()):
                option = request.POST['cloze_dropdown_' + str(idx+1)]
                print("The option is: ", option)
                print(q.question.full_fragment)
                q.answer = option
                q.time_taken = time_per_question
                q.updated_time = datetime.now()
                q.save()

            participation_obj.total_time_taken = str(total_time_taken)
            participation_obj.completed_on = datetime.now()
            participation_obj.save()

            if 'CLOSE_TEST_PARTICIPATION_ID' in request.session:
                del request.session['CLOSE_TEST_PARTICIPATION_ID']

            if 'CLOSE_TEST_SELECTED_EXP' in request.session:
                del request.session['CLOSE_TEST_SELECTED_EXP']

            request.session['CLOSE_TEST_EXPERIMENT_COMPLETE'] = True

            return HttpResponseRedirect('/LanguageGameExperiment/8/CloseTestWelcomePage')
        except:
            return render(request, '404_page.html')



class CloseTestExportAnswers(View):

    def get(self, request):
        context = {}

        close_test_exp_list = CloseTestExperiment.objects.all()
        context['exp_list'] = close_test_exp_list

        return render(request, 'CloseTestExportAnswers.html', context)


def export_close_test_results_csv(request, lang_id):


    try:

        user_answer_list = CloseTestUserAnswer.objects.filter(participation__completed_on__isnull=False,
                                                              participation__experiment__experiment_native_language__language_code='ru').order_by('answering_user', 'participation')

        response = HttpResponse(content_type='text/csv')
        csv_out_file = 'CloseTest_' + 'RU' + "_UserAnswers.csv"
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(csv_out_file)

        writer = csv.writer(response)



        headers = ['participant_id', 'participant_language', 'experiment_native_language',
                   'experiment_foreign_language', 'experiment_order', 'correct_response', 'user_response',
                   'is Correct', 'time_taken (sec)', 'answer_order', 'started_on', 'completed_on',
                   'User Age', 'User Gender', 'User Living Location', 'User Living Duration (years)']

        additional_headers1 = ['User Has Language RU', 'RU spoken where user lives', 'RU native', 'RU Used at Home',
                              'RU Learning Duration (years)', 'RU Exposer Through Living (years)', 'RU Reading',
                              'RU Writing', 'RU Listening', 'RU Speaking']

        additional_headers2 = ['User Has Language DE', 'DE spoken where user lives', 'DE native', 'DE Used at Home',
                               'DE Learning Duration (years)', 'DE Exposer Through Living (years)', 'DE Reading',
                               'DE Writing', 'DE Listening', 'DE Speaking']

        total_headers = headers + additional_headers1
        writer.writerow(total_headers)

        user_count = 0
        lang_list = ''
        curr_part_id = 0
        curr_exp_id = 0
        exp_count = 0

        total_lang_weight = defaultdict(lambda: 0)
        total_country_weight = defaultdict(lambda: 0)

        for data in user_answer_list:
            # print(data)

            part_id = data.participation.user.user_id
            if curr_part_id is not part_id:

                user_languages = data.participation.user.getAllLanguages()
                lang_list = ''
                for lang in user_languages:
                    lang_list += lang.language_code + ','

                curr_lang = 'ru'
                for skill in UserLanguageSkill.objects.filter(user=data.participation.user,
                                                              language__language_code__in=['ru']).order_by('language__language_code'):
                    curr_lang = skill.language.language_code
                    native = 0
                    if skill.is_native_language:
                        # native = "NATIVE1"
                        native = 1

                    # home = "HOME0"
                    home = 0
                    if skill.used_at_home:
                        # home = "HOME1"
                        home = 1

                    # location_lang = "LOC0"
                    location_lang = 0
                    if skill.spoken_at_user_location:
                        # location_lang = "LOC1"
                        location_lang = 1

                    if not skill.reading_level is None:
                        total_lang_weight[
                            skill.language.language_name] += skill.reading_level + skill.writing_level + skill.listening_level + skill.speaking_level

                    exp_living = 0
                    if not skill.exposure_through_living is None:
                        exp_living = skill.exposure_through_living

                    exp_learning = 0
                    if not skill.exposure_through_learning is None:
                        exp_learning = skill.exposure_through_learning

                    ru_lang_info = [1, location_lang, native, home, exp_learning, exp_living,
                                    skill.reading_level, skill.writing_level, skill.listening_level,
                                    skill.speaking_level]
                    #
                    # if curr_lang == 'ru':
                    #     ru_lang_info = [1, location_lang, native, home, exp_learning, exp_living,
                    #                     skill.reading_level, skill.writing_level, skill.listening_level, skill.speaking_level]
                    # else:
                    #     de_lang_info = [1, location_lang, native, home, exp_learning, exp_living,
                    #                     skill.reading_level, skill.writing_level, skill.listening_level,
                    #                     skill.speaking_level]



                curr_part_id = part_id
                exp_count = 0
                curr_exp_id = 0

            if curr_exp_id is not data.participation.experiment.close_test_experiment_id:
                exp_count += 1
                curr_exp_id = data.participation.experiment.close_test_experiment_id

            exp_native_lang = data.participation.experiment.experiment_native_language.language_code
            exp_foreign_lang = data.participation.experiment.experiment_foreign_language.language_code
            user_response = data.answer.strip()
            correct_response = data.question.sentence_block_text.strip()
            is_correct = 0
            if user_response == correct_response:
                is_correct = 1
            time_taken_per_ans = data.time_taken
            answer_order = data.answer_order
            started_on = data.participation.started_on
            completed_on = data.participation.completed_on

            age = data.participation.user.age
            gender = data.participation.user.gender
            country_name = data.participation.user.location.country_name
            living_duration = data.participation.user.location_living_duration

            writer.writerow(
                [part_id, lang_list, exp_native_lang, exp_foreign_lang, exp_count, correct_response,
                 user_response, is_correct, time_taken_per_ans, answer_order, started_on, completed_on,
                 age, gender, country_name, living_duration] + ru_lang_info
            )
            # writer.writerow(
            #     [part_id, lang_list, group, block, ru_def, de_com, su, ns, ans1, ans1_time,
            #      ans2, ans2_time, total_time, ans_order, started_on, completed_on,
            #      age, gender, country_name, living_duration] + ru_lang_info + de_lang_info)

        return response

    except Exception as e:
        return HttpResponse(e)



def LanguageGameExp(request):

    if request.is_ajax():
        message = 'This is ajax'
        print("Working")

        return JsonResponse(message, safe=False)

        return render(request, 'LanguageGameExperimentPage.html')


class UploadDECompoundQuestion(View):

    def get(self, request, exp_id):

        context = {}
        exp_obj = LaDoExperiment.objects.get(id=exp_id)
        context['exp_obj'] = exp_obj

        media_path = settings.MEDIA_ROOT
        folder_path = os.path.join(media_path, 'DECompoundRU')
        myfiles = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        context['myfiles'] = myfiles

        return render(request, 'DECompoundUploadQuestion.html', context)

    def post(self, request, exp_id):

        file_path = 'E:\\MSc\\Hiwi\\LSV HiWi\\lsv-c4-django-webexperiment\\Incomslav\\static\\media\\\DECompoundRU\\' + "RU definition DE compound group 1 group 2.xlsx"
        root = 'demo_webgazer/TTS_VWP_RU/'

        xls_file = pd.read_excel(file_path, header=0, sheet_name=1)

        q_list = []
        count = 0
        for idx, row in xls_file.iterrows():
            definition_ru = row[0]
            compound_de = row[1]
            su = row[2]
            ns = row[3]
            group = 2
            block = int(row[4].split(' ')[1])
            print(definition_ru, compound_de, su, ns, group, block)
            # count += 1
            obj, created = DECompoundExperimentQuestion.objects.get_or_create(experiment_id=exp_id,
                                                                              defination_ru=definition_ru,
                                                                              compound_word_de=compound_de,
                                                                              supportive_defination_ru=su,
                                                                              neutral_defination_ru=ns,
                                                                              group=group,
                                                                              block=block
                                                                              )

            if created:
                count += 1
        print(count)
            # sentence = str(row[0]).split('_')
            # q_id = sentence[0].strip()
            # audio_file_name = sentence[-1].strip()
            # q_list.append(int(q_id))
            #
            # question_obj = WebGazingExperimentQuestions.objects.get(question_id=q_id)
            # question_obj.russian_audio = root + row[0]
            # question_obj.russian_audio_gaze_start = row[1]
            # question_obj.russian_audio_gaze_end = row[2]
            # # question_obj.save()
            #
            # print(q_id, question_obj.bulgarian_audio, question_obj.bulgarian_audio_gaze_start,
            #       question_obj.bulgarian_audio_gaze_end)

        # print(sorted(q_list), len(q_list))

        return render(request, 'DECompoundUploadQuestion.html')


class DECompoundExperimentPage(View):

    def get(self, request):
        context = {}
        try:
            selected_exp = request.session.get('DECOMP_SELECTED_EXP')
            selcted_participation_id = request.session.get('DECOMP_SELECTED_EXP_PARTICIPATION')

            exp_obj = LaDoExperiment.objects.get(id=selected_exp, experiment_type='de compound', is_active=True)
            context['exp_obj'] = exp_obj

        except Exception as e:
            return render(request, '404_page.html')

        return render(request, 'DECompoundExperimentPage.html', context)


    def post(self, request):

        if request.is_ajax():

            try:
                selected_exp = request.session.get('DECOMP_SELECTED_EXP')
                selcted_participation_id = request.session.get('DECOMP_SELECTED_EXP_PARTICIPATION')
                selected_user_id = request.session.get('DECOMP_SELECTED_USER')

                # prolific_id = request.session.get('ST_PROLIFIC_ID')
                # print(selected_exp, prolific_id)

                type = int(request.POST['type'])

                if type == 0:
                    data = {}
                    participation_obj = DECompoundExperimentParticipation.objects.get(user_id=selected_user_id,
                                                                                     experiment_id=selected_exp)
                    if participation_obj.checkCompletion() == False:
                        next_question_id = participation_obj.getNextUserAnswerID(chunk=1)

                        print("starting ids:", next_question_id)
                        answer_obj = DECompoundExperimentUserAnswer.objects.get(id=next_question_id)
                        data['current_block'] = answer_obj.question.block

                        data['ru_def'] = answer_obj.question.defination_ru
                        data['de_com'] = answer_obj.question.compound_word_de
                        data['count'] = answer_obj.id  # change here
                        print(data['ru_def'])

                        data['total_ques'] = participation_obj.getTotalNumberOfBlockQuestions()
                        data['answered_ques'] = participation_obj.getNumberOfBlockAnsweredQuestions()
                        data['percentage'] = int((data['answered_ques'] / data['total_ques']) * 100)
                        data['completed'] = 'no'

                    else:

                        data['completed'] = 'yes'
                        avg_time_task, avg_time_block, total_time, total_blocks, total_tasks, completed_block, completed_task = participation_obj.getRunningStatistics()
                        data['avg_time_task'] = avg_time_task
                        data['avg_time_block'] = avg_time_block
                        data['total_time'] = total_time
                        data['total_blocks'] = total_blocks
                        data['total_tasks'] = total_tasks
                        data['completed_block'] = completed_block
                        data['completed_task'] = completed_task

                    return JsonResponse(data, safe=False)

                if type == 1:

                    data = {}
                    old_count = int(request.POST['old_count'])

                    participation_obj = DECompoundExperimentParticipation.objects.get(
                        user_id=selected_user_id,
                        experiment_id=selected_exp)

                    # insert existing translations
                    old_answer_obj = DECompoundExperimentUserAnswer.objects.get(id=old_count)

                    answer1_value = int(request.POST['answer1_value'])
                    checkbox_1_val = int(request.POST['checkbox_1_val'])
                    checkbox_2_val = int(request.POST['checkbox_2_val'])
                    checkbox_3_val = int(request.POST['checkbox_3_val'])

                    answer2_value = 3
                    if checkbox_3_val == 1:
                        answer2_value = 4
                    else:
                        if checkbox_1_val == 1 and checkbox_2_val == 0:
                            answer2_value = 1
                        elif checkbox_1_val == 0 and checkbox_2_val == 1:
                            answer2_value = 2
                        else:
                            answer2_value = 3

                    answer_1_total_time = float(request.POST['answer_1_total_time'])
                    answer_2_total_time = float(request.POST['answer_2_total_time'])

                    old_answer_obj.user_answer1 = answer1_value
                    old_answer_obj.answer1_time = str(answer_1_total_time)
                    old_answer_obj.is_answered_1 = True

                    old_answer_obj.user_answer2 = answer2_value
                    old_answer_obj.answer2_time = str(answer_2_total_time)
                    old_answer_obj.is_answered_2 = True

                    old_answer_obj.answered_time = datetime.now()
                    old_answer_obj.total_time_taken = str(answer_1_total_time + answer_2_total_time)
                    old_answer_obj.updated_time = datetime.now()
                    old_answer_obj.completed_answered = True
                    old_answer_obj.save()
                    print("old answer id:", old_answer_obj.id)


                    if participation_obj.checkCompletion() == False:

                        next_question_id = participation_obj.getNextUserAnswerID(chunk=1)
                        print("starting ids:", next_question_id)
                        answer_obj = DECompoundExperimentUserAnswer.objects.get(id=next_question_id)

                        if answer_obj.question.block is not participation_obj.current_block:

                            if participation_obj.answered_blocks is not None:

                                participation_obj.answered_blocks = participation_obj.answered_blocks + ',' + str(participation_obj.current_block)
                            else:
                                participation_obj.answered_blocks = str(participation_obj.current_block)

                            participation_obj.current_block = answer_obj.question.block
                            participation_obj.save()

                            data['completed'] = 'break'
                            avg_time_task, avg_time_block, total_time, total_blocks, total_tasks, completed_block, completed_task = participation_obj.getRunningStatistics()
                            data['avg_time_task'] = avg_time_task
                            data['avg_time_block'] = avg_time_block
                            data['total_time'] = total_time
                            data['total_blocks'] = total_blocks
                            data['total_tasks'] = total_tasks
                            data['completed_block'] = completed_block
                            data['completed_task'] = completed_task

                            print(avg_time_task, avg_time_block, total_time)
                            return JsonResponse(data, safe=False)


                        data['current_block'] = answer_obj.question.block

                        data['ru_def'] = answer_obj.question.defination_ru
                        data['de_com'] = answer_obj.question.compound_word_de
                        data['count'] = answer_obj.id  # change here
                        print(data['ru_def'])

                        data['total_ques'] = participation_obj.getTotalNumberOfBlockQuestions()
                        data['answered_ques'] = participation_obj.getNumberOfBlockAnsweredQuestions()
                        data['percentage'] = int((data['answered_ques'] / data['total_ques']) * 100)
                        data['completed'] = 'no'

                    else:

                        data['completed'] = 'yes'
                        avg_time_task, avg_time_block, total_time, total_blocks, total_tasks, completed_block, completed_task = participation_obj.getRunningStatistics()
                        data['avg_time_task'] = avg_time_task
                        data['avg_time_block'] = avg_time_block
                        data['total_time'] = total_time
                        data['total_blocks'] = total_blocks
                        data['total_tasks'] = total_tasks
                        data['completed_block'] = completed_block
                        data['completed_task'] = completed_task

                        participation_obj.completed_on = datetime.now()
                        participation_obj.save()


                        if 'DECOMP_SELECTED_EXP' in request.session:
                            del request.session['DECOMP_SELECTED_EXP']
                        if 'DECOMP_SELECTED_EXP_PARTICIPATION' in request.session:
                            del request.session['DECOMP_SELECTED_EXP_PARTICIPATION']
                        if 'DECOMP_SELECTED_USER' in request.session:
                            del request.session['DECOMP_SELECTED_USER']


                        # participation_obj.completed_on = datetime.now()
                        # participation_obj.save()
                        # if participation_obj.lado_prolific_user.languages.language_code == 'ru':
                        #     data['prolific_link'] = 'https://app.prolific.co/submissions/complete?cc=83EEED51'
                        # if participation_obj.lado_prolific_user.languages.language_code == 'cs':
                        #     data['prolific_link'] = 'https://app.prolific.co/submissions/complete?cc=53B32E1D'
                        # if participation_obj.lado_prolific_user.languages.language_code == 'pl':
                        #     data['prolific_link'] = 'https://app.prolific.co/submissions/complete?cc=804C2BE8'
                        # if participation_obj.lado_prolific_user.languages.language_code == 'bg':
                        #     data['prolific_link'] = 'https://app.prolific.co/submissions/complete?cc=3AEBAB00'
                        #
                        #
                        # if 'ST_SELECTED_EXP_PROLIFIC' in request.session:
                        #     del request.session['ST_SELECTED_EXP_PROLIFIC']
                        # if 'ST_PROLIFIC_ID' in request.session:
                        #     del request.session['ST_PROLIFIC_ID']


                    return JsonResponse(data, safe=False)

            except Exception as e:
                print("Coming to exception")
                print(e)
                return HttpResponse(e)

        return render(request, 'DECompoundExperimentPage.html')



class DECompoundWelcomePage(View):
    
    def get(self, request, exp_id):
        context = {}

        try:
            exp_obj = LaDoExperiment.objects.get(id=exp_id, is_active=True)
            context['exp_obj'] = exp_obj
            request.session['DECOMP_SELECTED_EXP'] = exp_obj.id
            user_obj = UserInfo.objects.get(user=request.user)
            #
            # if DECompoundExperimentParticipation.objects.get(user=userInfo, experiment=exp_obj,is_active=True).exist():
            #
            #     participation_obj = DECompoundExperimentParticipation.objects.get(user=userInfo, experiment=exp_obj,is_active=True)

            return render(request, 'DECompoundWelcomePage.html', context)

        except Exception as e:
            print(e)
            return render(request, '404_page.html')
        # request.session['ST_PROLIFIC_ID'] = 11

        # context['exp_obj'] =exp_obj
        # gender_list = Gender.objects.all()
        # context['gender_list'] = gender_list
        # language_list = Language.objects.filter(language_code__in=['ru', 'bg', 'cs', 'pl'])
        # context['language_list'] = language_list

        return render(request, 'DECompoundWelcomePage.html', context)
    

    def post(self, request, exp_id):

        try:
            print("Error 1")
            exp_id = request.session.get('DECOMP_SELECTED_EXP')
            user_obj = UserInfo.objects.get(user=request.user)
            print("Error 2")
            request.session['DECOMP_SELECTED_USER'] = user_obj.id
            print("Error 3")
            group_list = [1,2]
            selected_group = random.choice(group_list)

            block_list = list(range(1,13))
            random.shuffle(block_list)

            print("Error")
            participation_obj, created = DECompoundExperimentParticipation.objects.get_or_create(user=user_obj,
                                                                                                 experiment_id=exp_id,
                                                                                                 is_active=True,
                                                                                                 )

            if created:
                participation_obj.allocated_group = selected_group
                # participation_obj.allocated_blocks =
                answer_order_idx = 1
                block_text_list = []

                for block in block_list:
                    question_list = DECompoundExperimentQuestion.objects.filter(experiment_id=exp_id,
                                                                                group=selected_group,
                                                                                block=block).order_by('id')

                    q_list = list(question_list.values_list('id', flat=True))
                    random.shuffle(q_list)
                    print(q_list)
                    for q in q_list:
                        answer_obj = DECompoundExperimentUserAnswer(answering_user=user_obj, participation=participation_obj,
                                                                    question_id=q, answer_order=answer_order_idx)
                        answer_obj.save()
                        answer_order_idx += 1

                    block_text_list.append(str(block))

                block_text = ','.join(block_text_list)
                participation_obj.allocated_blocks = block_text
                participation_obj.current_block = int(block_text_list[0])
                participation_obj.save()

            request.session['DECOMP_SELECTED_EXP_PARTICIPATION'] = participation_obj.id
            return HttpResponseRedirect('/LanguageGameExperiment/DECompoundExperimentPage/')

        except Exception as e:
            print(e)
            return HttpResponse(e)




class UploadSentenceTranslationQuestion(View):

    def get(self, request, exp_id):

        context = {}
        exp_obj = LaDoExperiment.objects.get(id=exp_id)
        context['exp_obj'] = exp_obj

        media_path = settings.MEDIA_ROOT
        folder_path = os.path.join(media_path, 'SentenceTranslation')
        myfiles = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        context['myfiles'] = myfiles

        return render(request, 'SentenceTranslationUploadQuestion.html', context)

    def post(self, request, exp_id):

        file_path = 'E:\\MSc\\Hiwi\\LSV HiWi\\lsv-c4-django-webexperiment\\Incomslav\\static\\media\\SentenceTranslation\\files\\' + "damon_brown_how_to_choose_your_news_updated.exp.pl_2.xlsx"


        xls_file = pd.read_excel(file_path, header=None)

        q_list = []
        count = 0
        for idx, row in xls_file.iterrows():
            line1 = row[0]
            line2 = row[1]
            print(line1, line2)
            obj, created = TranslationGameQuestion.objects.get_or_create(line1=line1,
                                                                         line2=line2,
                                                                         experiment_id=exp_id,
                                                                         language__language_code='pl')

            if created:
                count += 1
        print(count)
            # sentence = str(row[0]).split('_')
            # q_id = sentence[0].strip()
            # audio_file_name = sentence[-1].strip()
            # q_list.append(int(q_id))
            #
            # question_obj = WebGazingExperimentQuestions.objects.get(question_id=q_id)
            # question_obj.russian_audio = root + row[0]
            # question_obj.russian_audio_gaze_start = row[1]
            # question_obj.russian_audio_gaze_end = row[2]
            # # question_obj.save()
            #
            # print(q_id, question_obj.bulgarian_audio, question_obj.bulgarian_audio_gaze_start,
            #       question_obj.bulgarian_audio_gaze_end)

        # print(sorted(q_list), len(q_list))

        return render(request, 'SentenceTranslationUploadQuestion.html')


class SentenceTranslationWelcomePage(View):

    def get(self, request, exp_id):
        context = {}
        try:
            exp_obj = LaDoExperiment.objects.get(id=exp_id, experiment_type='sentence translation', is_active=True)
            request.session['ST_SELECTED_EXP_PROLIFIC'] = exp_obj.id
        except:
            return render(request, '404_page.html')
        # request.session['ST_PROLIFIC_ID'] = 11

        context['exp_obj'] =exp_obj
        gender_list = Gender.objects.all()
        context['gender_list'] = gender_list
        language_list = Language.objects.filter(language_code__in=['ru', 'bg', 'cs', 'pl'])
        context['language_list'] = language_list

        return render(request, 'SentenceTranslationWelcomePage.html', context)

    def post(self, request, exp_id):
        selected_exp = request.session.get('ST_SELECTED_EXP_PROLIFIC')
        context = {}

        if 'ST_PROLIFIC_ID' in request.session:
            prolific_id = request.session.get('ST_PROLIFIC_ID')
            # prolific_user = LadoProlificUser.objects.get(id=request.session.get('ST_PROLIFIC_ID'))
            print("Current User: ", prolific_id)

        else:
            age = request.POST['age']
            gender = request.POST['gender']
            prolific_id = request.POST['prolific_id']
            first_langauge = request.POST['first_language']
            other_langauge = request.POST['other_langauge']
            print(age, gender, prolific_id, first_langauge, other_langauge)


            # return render(request, 'SentenceTranslationWelcomePage.html', context)

            try:
                prolific_user = LadoProlificUser(gender_id=gender,
                                                 age=age, languages_id=int(first_langauge), try_count=1, prolific_id=prolific_id,
                                                 other_languages=other_langauge, first_language=first_langauge)
                prolific_user.save()
                request.session['ST_PROLIFIC_ID'] = prolific_user.id
                prolific_id = request.session.get('ST_PROLIFIC_ID')
                print("New created user: ", prolific_id)

            except Exception as e:
                print(e)

        participation_obj, created = TranslationGameExperimentParticipation.objects.get_or_create(experiment_id=selected_exp,
                                                                                            lado_prolific_user_id=prolific_id,
                                                                                            retry_count=0,
                                                                                            defaults={'is_active': True}
                                                                                            )

        if created:
            question_list = TranslationGameQuestion.objects.filter(experiment_id=selected_exp,
                                                                        is_active=True).order_by('id')

            for question in question_list:
                answer_obj = TranslationGameUserAnswer(participation=participation_obj,
                                                           question=question)

                answer_obj.save()

        print("coming here")
        return HttpResponseRedirect('/LanguageGameExperiment/SentenceTranslationExperimentPage')


class SentenceTranslationShowResults(View):

    def get(self, request):

        return render(request, 'SentenceTranslationThankYouPage.html')

class SentenceTranslationExperimentPage(View):

    def get(self, request):
        context = {}
        try:
            selected_exp = request.session.get('ST_SELECTED_EXP_PROLIFIC')
            exp_obj = LaDoExperiment.objects.get(id=selected_exp, experiment_type='sentence translation', is_active=True)
            context['exp_obj'] = exp_obj

        except Exception as e:
            return render(request, '404_page.html')

        return render(request, 'SentenceTranslationExperimentPage.html', context)


    def post(self, request):

        if request.is_ajax():

            try:
                selected_exp = request.session.get('ST_SELECTED_EXP_PROLIFIC')
                prolific_id = request.session.get('ST_PROLIFIC_ID')
                print(selected_exp, prolific_id)

                type = int(request.POST['type'])

                if type == 0:
                    data = {}
                    participation_obj = TranslationGameExperimentParticipation.objects.get(lado_prolific_user_id=prolific_id,
                                                                                     experiment_id=selected_exp)
                    if participation_obj.checkCompletion() == False:
                        ids = participation_obj.getNextUserAnswerID(chunk=5)
                        print("starting ids:", ids)
                        answer_obj_list = TranslationGameUserAnswer.objects.filter(participation=participation_obj,
                                                                                   id__in=ids).order_by('question_id')


                        data['question'] = list(answer_obj_list.values('question__line1', 'question__line2'))
                        data['answer_ids'] = ids
                        data['answer_ids_len'] = len(ids)
                        data['completed'] = 'no'
                        print(data['question'])
                    else:

                        data['completed'] = 'yes'



                    # para_div = '<p style="font-size: larger; line-height: 2;">'
                    # for q in question:
                    #     para_div += '<span class="text-primary">' + q.line1 + ' ' + '</span>' + '<span class="text-danger bg-success">' + q.line2 + ' ' + '</span>'
                    #
                    # para_div += '</p>'
                    # data['para_div'] = para_div
                    return JsonResponse(data, safe=False)

                if type == 1:

                    data = {}
                    participation_obj = TranslationGameExperimentParticipation.objects.get(
                        lado_prolific_user_id=prolific_id,
                        experiment_id=selected_exp)
                    # insert existing translations
                    old_answer_ids = request.POST.getlist('user_answer_ids[]', False)
                    answer_total_time = float(request.POST['answer_total_time'])


                    print("old answer id:", old_answer_ids)
                    for i in range(len(old_answer_ids)):
                        id_name = 'answer_' + str(i)
                        line_answer = request.POST[id_name]

                        ans = TranslationGameUserAnswer.objects.get(id=int(old_answer_ids[i]))
                        ans.user_answer = str(line_answer) #chaged the lower
                        ans.time_taken = str(answer_total_time/len(old_answer_ids))
                        ans.is_answered = True
                        ans.save()


                    if participation_obj.checkCompletion() == False:
                        ids = participation_obj.getNextUserAnswerID(chunk=5)
                        print("New ids:", ids)
                        answer_obj_list = TranslationGameUserAnswer.objects.filter(participation=participation_obj,
                                                                                   id__in=ids).order_by('question_id')

                        data['question'] = list(answer_obj_list.values('question__line1', 'question__line2'))
                        data['answer_ids'] = ids
                        data['answer_ids_len'] = len(ids)
                        data['completed'] = 'no'

                    else:

                        data['completed'] = 'yes'
                        participation_obj.completed_on = datetime.now()
                        participation_obj.save()
                        if participation_obj.lado_prolific_user.languages.language_code == 'ru':
                            data['prolific_link'] = 'https://app.prolific.co/submissions/complete?cc=83EEED51'
                        if participation_obj.lado_prolific_user.languages.language_code == 'cs':
                            data['prolific_link'] = 'https://app.prolific.co/submissions/complete?cc=53B32E1D'
                        if participation_obj.lado_prolific_user.languages.language_code == 'pl':
                            data['prolific_link'] = 'https://app.prolific.co/submissions/complete?cc=804C2BE8'
                        if participation_obj.lado_prolific_user.languages.language_code == 'bg':
                            data['prolific_link'] = 'https://app.prolific.co/submissions/complete?cc=3AEBAB00'


                        if 'ST_SELECTED_EXP_PROLIFIC' in request.session:
                            del request.session['ST_SELECTED_EXP_PROLIFIC']
                        if 'ST_PROLIFIC_ID' in request.session:
                            del request.session['ST_PROLIFIC_ID']


                    return JsonResponse(data, safe=False)

            except Exception as e:
                print("Coming to exception")
                print(e)

        return render(request, 'SentenceTranslationExperimentPage.html')



class WebGazingIntro(View):

    def get(self, request):
        request.session['WG_SELECTED_EXP_PROLIFIC'] = 4
        request.session['WG_PROLIFIC_ID'] = 11

        return render(request, 'WebGazingIntro.html')


    def post(self, request):

        prolific_id = request.session.get('WG_PROLIFIC_ID')
        selected_exp = request.session.get('WG_SELECTED_EXP_PROLIFIC')

        participation_obj, created = WebGazingExperimentParticipation.objects.get_or_create(experiment_id=selected_exp,
                                                                                   webgazing_prolific_user_id=prolific_id,
                                                                                   retry_count=0,
                                                                                   defaults={'is_active': True}
                                                                                   )

        if created:
            question_list = WebGazingExperimentQuestions.objects.filter(experiment_id=selected_exp,
                                                                        is_active=True).exclude(visual_fillers=0)

            for question in question_list:
                answer_obj = WebGazingExperimentUserAnswer(participation=participation_obj,
                                                           question=question)

                answer_obj.save()


        return HttpResponseRedirect('/LanguageGameExperiment/demo_webgazer')


def webgazerView(request):

    return render(request, 'demo_webgazer.html')

#helper function
def getCenter(top, left, height, width):
    center_x = left + width / 2
    center_y = top + height / 2

    return (center_x, center_y)


def getNearestDistance(pred_x, pred_y, img1_center, img2_center, img3_center, img4_center):
    img1_dist = math.sqrt((pred_x - img1_center[0]) ** 2 + (pred_y - img1_center[1]) ** 2)
    img2_dist = math.sqrt((pred_x - img2_center[0]) ** 2 + (pred_y - img2_center[1]) ** 2)
    img3_dist = math.sqrt((pred_x - img3_center[0]) ** 2 + (pred_y - img3_center[1]) ** 2)
    img4_dist = math.sqrt((pred_x - img4_center[0]) ** 2 + (pred_y - img4_center[1]) ** 2)

    print(img1_dist, img2_dist, img3_dist, img4_dist)


class DemoWebgazerView(View):

    def get(self, request):
        return render(request, 'demo_webgazer.html')


    def post(self, request):

        if request.is_ajax():

            try:
                p_type = int(request.POST['type'])
                # exp_obj = get_object_or_404(LaDoExperiment, pk=4)


                prolific_user_id = request.session.get('WG_PROLIFIC_ID')
                prolific_user = LadoProlificUser.objects.get(id=prolific_user_id)
                selected_exp_id = request.session.get('WG_SELECTED_EXP_PROLIFIC')

                lang_list = ['ru', 'pl', 'cs', 'bg']
                user_lang = prolific_user.languages.language_code
                lang_list.remove(user_lang)

                if p_type == 1:
                    data = {}
                    data['req_type'] = "1"
                    data['exp_id'] = selected_exp_id
                    data['user_id'] = prolific_user_id


                    print("printing type: ", p_type)
                    q_obj = WebGazingExperimentQuestions.objects.get(question_id=1)
                    participation_obj = WebGazingExperimentParticipation.objects.get(webgazing_prolific_user=prolific_user,
                                                                                  experiment_id=selected_exp_id)

                    if participation_obj.checkCompletion() == False:

                        user_answer_id = participation_obj.getNextUserAnswerID()
                        answer_obj = WebGazingExperimentUserAnswer.objects.get(id=int(user_answer_id))

                        # imaages


                        target = '/media/' + 'demo_webgazer/Images/' + answer_obj.question.visual_target
                        fillers = answer_obj.question.visual_fillers.split(',')
                        images_list = []
                        images_name_list = []
                        images_name_list.append(answer_obj.question.visual_target)
                        # images_list.append(target)
                        for fl in fillers:
                            images_name_list.append(fl.strip())


                        random.shuffle(images_name_list)
                        name_list = ''
                        for img in images_name_list:
                            images_list.append('/media/' + 'demo_webgazer/Images/' + img)
                            if name_list == '':
                                name_list = img
                            else:
                                name_list = name_list + ',' + img

                        data['images_name_list'] = name_list
                        data['images_list'] = images_list
                        print(images_list)

                        # audio

                        audio1_src, audio1_gaze_start, audio1_gaze_end = answer_obj.question.getAudio(lang_code='bg')
                        audio_2_id = answer_obj.question.question_id + 1
                        audio2_src, audio2_gaze_start, audio2_gaze_end = WebGazingExperimentQuestions.objects.get(question_id=audio_2_id).getAudio(lang_code="pl")

                        data["audio1_src"] = audio1_src
                        data["audio2_src"] = audio2_src
                        print(audio1_src)
                        print(audio2_src)
                        print(type(audio2_src))
                        data['req_type'] = '1'
                        data['answer_id'] = answer_obj.id

                        return JsonResponse(data, safe=False)


                if p_type == 2:
                    data = {}

                    # print("image 1", request.POST['img1'])
                    pred_x = float(request.POST.get('prediction_x', False))
                    pred_y = float(request.POST.get('prediction_y', False))
                    img1_top = float(request.POST['img1_top'])
                    img1_left = float(request.POST['img1_left'])
                    img2_top = float(request.POST['img2_top'])
                    img2_left = float(request.POST['img2_left'])
                    img3_top = float(request.POST['img3_top'])
                    img3_left = float(request.POST['img3_left'])
                    img4_top = float(request.POST['img4_top'])
                    img4_left = float(request.POST['img4_left'])
                    x_preds = request.POST.getlist('x_preds[]')
                    print(x_preds)

                    old_images_name_list = request.POST['images_name_list']
                    old_answer_id = int(request.POST['current_answer_id'])

                    old_answer_obj = WebGazingExperimentUserAnswer.objects.get(id=old_answer_id)
                    print("Printing image names:", old_images_name_list)

                    img_height = 150
                    img_width = 150

                    img1_center = getCenter(img1_top, img1_left, img_height, img_width)
                    img2_center = getCenter(img2_top, img2_left, img_height, img_width)
                    img3_center = getCenter(img3_top, img3_left, img_height, img_width)
                    img4_center = getCenter(img4_top, img4_left, img_height, img_width)

                    getNearestDistance(pred_x, pred_y, img1_center, img2_center, img3_center, img4_center)

                    print("predictions:", pred_x, pred_y)
                    print(img1_center[0], img1_center[1])

                    # inserting in old answer object
                    old_answer_obj.all_images_name = old_images_name_list
                    img_names = old_images_name_list.split(',')
                    old_answer_obj.user_gaze_coordinates = 'x:' + str(pred_x) + '_' + 'y:' + str(pred_y)
                    old_answer_obj.all_images_coordinates = 'name:' + str(img_names[0]) + '_' + 'top:' + str(img1_top) + '_' + 'left:' + str(img1_left) + '_' + 'center:' + str(img1_center) + ',' + 'name:' + str(img_names[1]) + '_' +  'top:' + str(img2_top) + '_' + 'left:' + str(img2_left) + '_' + 'center:' + str(img2_center) + ',' + 'name:' + str(img_names[2]) + '_' +  'top:' + str(img3_top) + '_' + 'left:' + str(img3_left) + '_' + 'center:' + str(img3_center) + ',' + 'name:' + str(img_names[3]) + '_' +  'top:' + str(img4_top) + '_' + 'left:' + str(img4_left) + '_' + 'center:' + str(img4_left) + ','

                    print(old_answer_obj.all_images_coordinates)


                    participation_obj = WebGazingExperimentParticipation.objects.get(
                        webgazing_prolific_user=prolific_user,
                        experiment_id=selected_exp_id)

                    if participation_obj.checkCompletion() == False:

                        user_answer_id = participation_obj.getNextUserAnswerID()
                        answer_obj = WebGazingExperimentUserAnswer.objects.get(id=int(user_answer_id))

                        # imaages
                        target = '/media/' + 'demo_webgazer/Images/' + answer_obj.question.visual_target
                        fillers = answer_obj.question.visual_fillers.split(',')
                        # images_list = []
                        # images_list.append(target)
                        # for fl in fillers:
                        #     images_list.append('/media/' + 'demo_webgazer/Images/' + fl.strip())
                        #
                        # random.shuffle(images_list)
                        # data['images_list'] = images_list
                        # print(images_list)

                        images_list = []
                        images_name_list = []
                        images_name_list.append(answer_obj.question.visual_target)
                        # images_list.append(target)
                        for fl in fillers:
                            images_name_list.append(fl.strip())

                        random.shuffle(images_name_list)
                        name_list = ''
                        for img in images_name_list:
                            images_list.append('/media/' + 'demo_webgazer/Images/' + img)
                            if name_list == '':
                                name_list = img
                            else:
                                name_list = name_list + ',' + img

                        data['images_name_list'] = name_list
                        data['images_list'] = images_list
                        print(images_list)

                        # audio

                        audio1_src, audio1_gaze_start, audio1_gaze_end = answer_obj.question.getAudio(lang_code='bg')
                        audio_2_id = answer_obj.question.question_id + 1
                        audio2_src, audio2_gaze_start, audio2_gaze_end = WebGazingExperimentQuestions.objects.get(
                            question_id=audio_2_id).getAudio(lang_code="pl")

                        data["audio1_src"] = audio1_src
                        data["audio2_src"] = audio2_src
                        print(audio1_src)
                        print(audio2_src)
                        print(type(audio2_src))

                        return JsonResponse(data, safe=False)



                data = {}
                pred_x = request.POST.get('prediction_x', False)
                pred_y = request.POST.get('prediction_y', False)
                pred = json.loads(request.POST['prediction'])

                print(pred_x, pred_y)
                print(pred['x'], pred['eyeFeatures']['left']['height'], pred['eyeFeatures']['left']['patch'])
                with open('data.json', 'w', encoding='utf-8') as f:
                    json.dump(pred, f, ensure_ascii=False, indent=4)
                return JsonResponse(data, safe=False)


            except Exception as e:
                print(e)


        return render(request, 'demo_webgazer.html')


class CreateNewLaDoExp(View):

    model = LaDoExperiment
    template_name = 'createNewLaDoExp.html'
    create_message = ''

    def get(self, request):

        data = {}

        experiment_list = self.model.objects.filter(is_active=True)

        data['experiment_list'] = experiment_list
        data['message'] = self.create_message

        return render(request, self.template_name, data)

    def post(self, request):

        obj, created = self.model.objects.get_or_create(
            experiment_name=request.POST['experiment_name'],
            defaults={
                'experiment_type': request.POST['experiment_type'],
                'publish': request.POST['publish']
            }
        )

        if created:
            self.create_message = 'Experiment Created'
        else:
            self.create_message = 'Experiment could not be created'

        return render(request, self.template_name)


def PrimalExperimentQuestionUpload(request, exp_id):

    if request.method == 'POST' and request.FILES['question_file']:

        return None



class PrimalExperimentQuestionView(View):
    def get(self, request, exp_id):

        try:

            data = {}

            exp_obj = LaDoExperiment.objects.get(id=exp_id)
            data['exp_obj'] = exp_obj

            question_list = PrimalExperimentQuestion.objects.filter(experiment=exp_obj)
            data['question_list'] = question_list

            return render(request, 'PrimalExperimentQuestionViewPage.html', data)

        except ObjectDoesNotExist as e:
            return HttpResponse(e)

    def post(self, request, exp_id):

        # data = {}
        #
        # # section for openning file
        # fs = FileSystemStorage()
        # csv_file = request.FILES['question_file']
        # filename = fs.save(csv_file.name, csv_file)
        # uploaded_file_url = fs.url(filename)
        # print(type(uploaded_file_url))
        #
        # # static_path = 'e:\MSc\Hiwi\LSV HiWi\lsv-c4-django-webexperiment\Incomslav\static' + uploaded_file_url
        # static_path = '/srv/C4-django/c4-django-webexperiments/Incomslav/static'
        # # file_path = os.path.join(static_path, uploaded_file_url)
        # file_path = '/srv/C4-django/c4-django-webexperiments/Incomslav/static/media/New Combined Priming Experiment Stimuli.csv'
        # # file_path = 'E:\\MSc\\Hiwi\\LSV HiWi\\lsv-c4-django-webexperiment\\Incomslav\\static\\media\\' + filename
        # # drive_path = 'E:\\MSc\\Hiwi\\LSV HiWi\\lsv-c4-django-webexperiment\\Incomslav\\static\\media\\' + 'PrimalTaskMp3'
        # # folder_name = 'PrimalTaskMp3'
        # print(static_path)
        data = {}
        file_path = '/srv/C4-django/c4-django-webexperiments/Incomslav/static/media/New Combined Priming Experiment Stimuli.csv'
        # file_path = '/home/hasan/Desktop/C4-django-webexperiments/static/media/New Combined Priming Experiment Stimuli.csv'

        #########

        try:
            primal_exp_obj = LaDoExperiment.objects.get(id=exp_id)

            with open(file_path, 'r', encoding='utf-8') as csv_file:
                print('Opened')
                csv_rows = csv.reader(csv_file, delimiter=',')
                firstline = True
                total_entry_count = 0
                for row in csv_rows:
                    if firstline:
                        firstline = False
                        continue

                    token1 = row[0].strip()
                    token1_gloss = row[1].strip()
                    token1_filename = row[2].strip()
                    token1_language = row[3].strip()
                    token2 = row[4].strip()
                    token2_gloss = row[5].strip()
                    token2_filename = row[6].strip()
                    token2_language = row[7].strip()
                    native_language = row[8].strip()
                    priming_type = row[9].strip()
                    correct_response = row[10].strip()
                    phonetic_distance = float(row[11])

                    token1_filepath = 'PrimalTaskMp3/' + token1_language + '/' + token1_filename
                    token2_filepath = 'PrimalTaskMp3/' + token2_language + '/' + token2_filename


                    print(token1, token2, phonetic_distance)

                    obj, created = PrimalExperimentQuestion.objects.get_or_create(
                        experiment=primal_exp_obj,
                        token1_name=token1, token1_gloss=token1_gloss, token1_filename=token1_filepath, token1_language=token1_language,
                        token2_name=token2, token2_gloss=token2_gloss, token2_filename=token2_filepath, token2_language=token2_language,
                        native_language=native_language, priming_type=priming_type, correct_response=correct_response, phonetic_distance=phonetic_distance
                    )

                    if created:
                        total_entry_count += 1


            data['total_entry_count'] = total_entry_count
            data['exp_obj'] = primal_exp_obj

            return render(request, 'PrimalExperimentQuestionViewPage.html', data)
        except Exception as e:
            HttpResponse(e)

class LaDoExperimentQuestionView(View):

    template_name = 'viewLaDoQuestion.html'

    def get(self, request, exp_id):

        try:

            data = {}
            exp_obj = LaDoExperiment.objects.get(id=exp_id)
            question_list = LaDoQuestion.objects.filter(experiment=exp_id)

            # for question in question_list:
            # 	if question.id > 43:
            # 		question.delete()

            # question_list = LaDoQuestion.objects.filter(experiment=exp_id)
            data['exp_obj'] = exp_obj
            data['question_list'] = question_list

            return render(request, self.template_name, data)

        except ObjectDoesNotExist as e:
            return HttpResponse(e)

    def post(self, request, exp_id):

        try:
            data = {}
            exp_obj = LaDoExperiment.objects.get(id=exp_id)

            question_list = LaDoQuestion.objects.filter(experiment=exp_id)
            print(question_list)
            group = int(request.POST['group'])
            if question_list.exists() == False or exp_obj.has_audio == False or group == 2:
                csv_file_path = request.POST['csv_file_path']
                # print(csv_file_path)

                # static_path = '/home/hasan/Desktop/C4-django-webexperiments/static'
                static_path = '/srv/C4-django/c4-django-webexperiments/Incomslav/static'
                # static_path = 'E:/MSc/Hiwi/LSV HiWi/lsv-c4-django-webexperiment/Incomslav/static'
                file_path = os.path.join(static_path, csv_file_path)
                print(file_path)
                if Path(file_path).is_file():
                    print(file_path)
                    # used to upload data
                    with open(file_path, 'r') as csv_file:
                        print("opened")
                        csv_reader = csv.reader(csv_file, delimiter=',')
                        for row in csv_reader:

                            file_name = row[0]
                            answer = str(row[1])
                            answer = answer.strip()
                            group = int(row[2])
                            print(file_name, answer, group)
                            obj = LaDoQuestion(
                                experiment=exp_obj, file_name=file_name, correct_answer=answer, question_group=group)
                            obj.save()
                            # print(row)

                        data['message'] = 'Questions are Uploaded for the Experiment'
                        exp_obj.has_audio = True
                        exp_obj.save()
                        question_list = LaDoQuestion.objects.filter(
                            experiment=exp_id)

                else:
                    data['message'] = 'No file Exists!!!'

            else:
                data['message'] = 'Quetions for the experiment are already exit'

            data['exp_obj'] = exp_obj
            data['question_list'] = question_list

            return render(request, self.template_name, data)

        except ObjectDoesNotExist as e:
            return HttpResponse(e)


class PrimalTaskExperimentTextView(View):

    def get(self, request):
        try:
            context = {}
            if UserInfo.objects.filter(user=request.user).exists():
                userInfo = UserInfo.objects.get(user=request.user)

                # request.session['PRIMAL_EXP_ID'] = 4
                exp_id = request.session.get('PRIMAL_EXP_ID')

                primal_exp = LaDoExperiment.objects.get(id=exp_id)

                # user_language_list = []
                # for l in userInfo.getNativeLanguages():
                #     user_language_list.append(l)
                # print(type(user_language_list[0].language_name))
                # return render(request, 'PrimalTaskExperimentTextPage.html', context)

                lang_list = ['Russian', 'Polish', 'Czech', 'Bulgarian']

                user_language_list = []
                for l in userInfo.getNativeLanguages():
                    user_language_list.append(l)

                context['user_language_list'] = user_language_list
                native_lang_code = user_language_list[0].language_code

                if native_lang_code == 'cs':
                    native_lang = 'Czech'
                elif native_lang_code == 'ru':
                    native_lang = 'Russian'
                elif native_lang_code == 'pl':
                    native_lang = 'Polish'
                elif native_lang_code == 'bg':
                    native_lang = 'Bulgarian'
                else:
                    native_lang = ''
                    return HttpResponseRedirect('/Experiments')

                lang_list.remove(native_lang)


                # create participation object
                experiment_participation, created = PrimalExperimentParticipation.objects.get_or_create(
                    user=userInfo,
                    experiment=primal_exp,
                    retry_count=0,
                    defaults={'is_active': True}
                )

                if created:
                    # creating question object
                    question_list = PrimalExperimentQuestion.objects.filter(experiment=primal_exp)

                    # native_lang = user_language_list[0].language_name

                    print('Coming to created')

                    # native_lang = random.choice(lang_list)

                    type_list = ["phonetic", 'cognate']

                    min_count = 10000
                    selected_questions = []
                    for l2 in lang_list:
                        for t in type_list:
                            count = question_list.filter(token1_language=l2, token2_language=native_lang, priming_type=t).count()
                            if count < min_count:
                                min_count = count

                    if min_count > 9:
                        min_count = 9

                    for l2 in lang_list:
                        for t in type_list:
                            for q in question_list.filter(token1_language=l2, token2_language=native_lang, priming_type=t).order_by('phonetic_distance')[:min_count]:
                                selected_questions.append(q)

                    filler_count = int(len(selected_questions) / 4)
                    filler_list = question_list.filter(native_language=native_lang, priming_type='filler')[:filler_count]
                    for f in filler_list:
                        selected_questions.append(f)


                    total_repeat = 3
                    for i in range(total_repeat):
                        random.shuffle(selected_questions)
                        for s in selected_questions:
                            answer_obj = PrimalExperimentUserAnswer(answering_user=userInfo, participation=experiment_participation,
                                                                    question=s)
                            answer_obj.save()



                complete = experiment_participation.checkCompletion()
                context['complete_status'] = complete

                if complete == False:

                    return render(request, 'PrimalTaskExperimentTextPage.html', context)
                else:
                    return HttpResponseRedirect('/Experiments')

        except Exception as e:
            return HttpResponse(e)


    def post(self, request):

        if request.is_ajax():

            try:
                count = int(request.POST['count'])
                data = {}
                # exp_id = request.session.get('PRIMAL_EXP_ID')
                # exp_obj = LaDoExperiment.objects.get(exp_id)
                # print(exp_obj)

                choices = []
                for i in range(100):
                    choices.append(i)
                id = random.choice(choices)
                print(id)

                question_obj = PrimalExperimentQuestion.objects.get(id=id)
                data['count'] = count+1
                data['token1_filepath'] = '/media/' + question_obj.token1_filename
                data['token2_filepath'] = '/media/' + question_obj.token2_filename
                print(question_obj)
                return JsonResponse(data, safe=False)
            except:
                return HttpResponseRedirect('/Experiments')




# for prolific
class ProlificPrimalTaskExperimentTextView(View):

    def get(self, request):
        context = {}

        request.session['PRIMAL_EXP_ID'] = 3
        accepted_user_lang_code = ['cs', 'ru', 'pl', 'bg']

        language_list = Language.objects.filter(language_code__in=accepted_user_lang_code).order_by('language_name')
        gender_list = Gender.objects.all()

        context['language_list'] = language_list
        context['gender_list'] = gender_list
        return render(request, 'ProlificPrimalTaskExperimentTextPage.html', context)


    def post(self, request):

        if request.is_ajax():

            try:
                count = int(request.POST['count'])
                data = {}
                # exp_id = request.session.get('PRIMAL_EXP_ID')
                # exp_obj = LaDoExperiment.objects.get(exp_id)
                # print(exp_obj)

                choices = []
                for i in range(100):
                    choices.append(i)
                id = random.choice(choices)
                print(id)

                question_obj = PrimalExperimentQuestion.objects.get(id=id)
                data['count'] = count+1
                data['token1_filepath'] = '/media/' + question_obj.token1_filename
                data['token2_filepath'] = '/media/' + question_obj.token2_filename
                print(question_obj)
                return JsonResponse(data, safe=False)
            except:
                return HttpResponseRedirect('/Experiments')

        try:
            context = {}

            age = int(request.POST['age'])
            gender = Gender.objects.get(id=request.POST['gender_id'])
            language = Language.objects.get(language_id=request.POST['language_id'])

            print(age, gender, language)
            print(request.session.get('PRIMAL_EXP_ID'))
            # request.session['PRIMAL_EXP_ID'] = 4
            exp_id = request.session.get('PRIMAL_EXP_ID')
            primal_exp = LaDoExperiment.objects.get(id=exp_id)
            print(request.session.get('PRIMAL_EXP_ID'))
            if 'PROLIFIC_ID' in request.session:
                prolific_user = LadoProlificUser.objects.get(id=request.session.get('PROLIFIC_ID'))
                print("Existing participant")
            else:

                prolific_user = LadoProlificUser(gender=gender, languages=language,
                                                 age=age, try_count=1)
                prolific_user.save()

                request.session['PROLIFIC_ID'] = prolific_user.id
                print(request.session.get('PROLIFIC_ID'))
                print("New Participant")

            # user_language_list = []
            # for l in userInfo.getNativeLanguages():
            #     user_language_list.append(l)
            # print(type(user_language_list[0].language_name))
            # return render(request, 'PrimalTaskExperimentTextPage.html', context)

            lang_list = ['Russian', 'Polish', 'Czech', 'Bulgarian']


            print(prolific_user.languages.language_code)
            context['user_language_list'] = prolific_user.languages.language_name
            native_lang_code = prolific_user.languages.language_code

            if native_lang_code == 'cs':
                native_lang = 'Czech'
            elif native_lang_code == 'ru':
                native_lang = 'Russian'
            elif native_lang_code == 'pl':
                native_lang = 'Polish'
            elif native_lang_code == 'bg':
                native_lang = 'Bulgarian'
            else:
                native_lang = ''
                return HttpResponseRedirect('/Experiments')

            lang_list.remove(native_lang)
            print(lang_list)
            # create participation object
            experiment_participation, created = PrimalExperimentParticipation.objects.get_or_create(
                primal_prolific_user=prolific_user,
                experiment=primal_exp,
                retry_count=0,
                defaults={'is_active': True}
            )

            if created:
                # creating question object
                question_list = PrimalExperimentQuestion.objects.filter(experiment=primal_exp)

                # native_lang = user_language_list[0].language_name

                print('Coming to created')

                # native_lang = random.choice(lang_list)

                type_list = ["phonetic", 'cognate']

                # finding out the minimum quetion count, min or 9 if greater than min
                min_count = 10000
                selected_questions = []
                for l2 in lang_list:
                    for t in type_list:
                        count = question_list.filter(token1_language=l2, token2_language=native_lang,
                                                     priming_type=t).count()
                        if count < min_count:
                            min_count = count

                if min_count > 9:
                    min_count = 9
                print("min count", min_count)
                for l2 in lang_list:
                    for t in type_list:
                        for q in question_list.filter(token1_language=l2, token2_language=native_lang,
                                                      priming_type=t).order_by('phonetic_distance')[:min_count]:
                            selected_questions.append(q)

                filler_count = int(len(selected_questions) / 4)
                filler_list = question_list.filter(native_language=native_lang, priming_type='filler')[
                              :filler_count]
                for f in filler_list:
                    selected_questions.append(f)

                total_repeat = 1
                for i in range(total_repeat):
                    random.shuffle(selected_questions)
                    for s in selected_questions:
                        answer_obj = PrimalExperimentUserAnswer(participation=experiment_participation,
                                                                question=s)
                        answer_obj.save()
                print(len(selected_questions))

            complete = experiment_participation.checkCompletion()
            context['complete_status'] = complete

            if complete == False:

                return HttpResponseRedirect('/LanguageGameExperiment/ProlificPrimalTaskExperiment')
            else:
                return HttpResponseRedirect('/Experiments')

        except Exception as e:
            HttpResponseRedirect(e)



# for prolific
class ProlificPrimalTaskExperimentView(View):

    def get(self, request):

        if 'PRIMAL_EXP_ID' in request.session:

            return render(request, 'ProlificPrimalTaskExperimentPage.html')
        else:
            return HttpResponseRedirect('/LanguageGameExperiment/ProlificPrimalTaskExperimentText')


    def post(self, request):

        if request.is_ajax():

            type = int(request.POST['type'])
            # exp_id = request.session['LADO_SELECTED_EXP']
            exp_id = request.session.get('PRIMAL_EXP_ID')

            try:
                exp_id = request.session.get('PRIMAL_EXP_ID')
                exp_obj = LaDoExperiment.objects.get(id=int(exp_id))
                # userInfo = UserInfo.objects.get(user=request.user)
                prolific_user_id = request.session.get('PROLIFIC_ID')
                prolific_user = LadoProlificUser.objects.get(id=prolific_user_id)

                if type == 0:
                    data = {}
                    participation_obj = PrimalExperimentParticipation.objects.get(primal_prolific_user=prolific_user, experiment_id=exp_id)
                    if participation_obj.checkCompletion() == False:
                        user_answer_id = participation_obj.getNextUserAnswerID()
                        answer_obj = PrimalExperimentUserAnswer.objects.get(id=int(user_answer_id))

                        #for chart
                        total_question = participation_obj.getTotalNumberOfQuestions()
                        total_answered = participation_obj.getNumberOfAnsweredQuestions()

                        remained_count = total_question - total_answered
                        l_list = []
                        label_list = []
                        for l in range(total_question):
                            l_list.append(l+1)

                        running_correct = participation_obj.getRunningCorrect()
                        answer_time_list = []
                        answer_accuracy_list = []
                        if running_correct is not -1:
                            total_answered_obj = PrimalExperimentUserAnswer.objects.filter(participation=participation_obj,
                                                                                           is_answered=True).order_by('question_play_order')

                            for obj in total_answered_obj:
                                answer_time_list.append(round(float(obj.time_taken), 2))
                                current_accuracy = (obj.running_correct / obj.question_play_order) * 100
                                answer_accuracy_list.append(round(current_accuracy, 2))

                        data['completed'] = 'no'
                        data['label_list'] = l_list
                        data['answer_time_list'] = answer_time_list
                        data['answer_accuracy_list'] = answer_accuracy_list
                        data['running_correct'] = running_correct
                        data['answer_id'] = str(answer_obj.id)
                        data['token1_filepath'] = '/media/' + answer_obj.question.token1_filename
                        data['token2_filepath'] = '/media/' + answer_obj.question.token2_filename

                        return JsonResponse(data, safe=False)
                    else:
                        return HttpResponseRedirect('/LanguageGameExperiment/ProlificPrimalTaskExperimentText')

                if type == 1:
                    try:
                        data = {}

                        user_answer = request.POST['user_answer']
                        answer_total_time = request.POST['answer_total_time']
                        last_answer_id = request.POST['answer_id']
                        last_running_correct = int(request.POST['running_correct'])

                        print(user_answer, answer_total_time, last_answer_id, last_running_correct)
                        participation_obj = PrimalExperimentParticipation.objects.get(primal_prolific_user=prolific_user, experiment_id=exp_id)

                        # storing answers
                        last_answered_obj = PrimalExperimentUserAnswer.objects.get(id=int(last_answer_id))
                        last_answered_obj.user_answer = user_answer
                        last_answered_obj.time_taken = answer_total_time
                        last_answered_obj.answered_time = datetime.now()
                        last_answered_obj.is_answered = True
                        last_answered_obj.question_play_order = participation_obj.getNumberOfAnsweredQuestions() + 1

                        if last_running_correct == -1:
                            last_running_correct = 0

                        current_accuracy = 0
                        if last_answered_obj.user_answer == last_answered_obj.question.correct_response:

                            ans_total = participation_obj.getNumberOfAnsweredQuestions() + 1
                            last_running_correct += 1

                            last_answered_obj.running_correct = last_running_correct
                            current_accuracy =(last_running_correct / ans_total) * 100
                            current_accuracy = round(current_accuracy, 2)

                            print(current_accuracy)

                        else:
                            ans_total = participation_obj.getNumberOfAnsweredQuestions() + 1

                            last_answered_obj.running_correct = last_running_correct
                            current_accuracy = (last_running_correct / ans_total) * 100
                            current_accuracy = round(current_accuracy, 2)

                            print(current_accuracy)

                        last_answered_obj.save()


                        data['time_taken'] = round(float(last_answered_obj.time_taken),2)
                        data['current_accuracy'] = current_accuracy
                        data['last_running_currect'] = last_running_correct

                        # data['current_accuracy'] = float()

                        print(last_answered_obj.question_play_order, participation_obj.getRunningCorrect())


                        if participation_obj.checkCompletion() == False:
                            user_answer_id = participation_obj.getNextUserAnswerID()
                            answer_obj = PrimalExperimentUserAnswer.objects.get(id=int(user_answer_id))

                            data['completed'] = 'no'
                            data['answer_id'] = str(answer_obj.id)
                            data['token1_filepath'] = '/media/' + answer_obj.question.token1_filename
                            data['token2_filepath'] = '/media/' + answer_obj.question.token2_filename

                            return JsonResponse(data, safe=False)
                        else:
                            participation_obj.completed_on = datetime.now()
                            participation_obj.save()
                            data['completed'] = 'yes'
                            data['prolific_link'] = 'https://app.prolific.co/submissions/complete?cc=43B6033A'
                            if 'PRIMAL_EXP_ID' in request.session:
                                del request.session['PRIMAL_EXP_ID']
                            if 'PROLIFIC_ID' in request.session:
                                del request.session['PROLIFIC_ID']

                            return JsonResponse(data, safe=False)

                    except:
                        return HttpResponseRedirect('/LanguageGameExperiment/ProlificPrimalTaskExperimentText')



            except Exception as e:
                return HttpResponseRedirect('/LanguageGameExperiment/ProlificPrimalTaskExperimentText')



# end prolific


class PrimalTaskExperimentView(View):

    def get(self, request):

        if 'PRIMAL_EXP_ID' in request.session:

            return render(request, 'PrimalTaskExperimentPage.html')
        else:
            return HttpResponseRedirect('/Experiments')


    def post(self, request):

        if request.is_ajax():

            type = int(request.POST['type'])
            # exp_id = request.session['LADO_SELECTED_EXP']
            exp_id = request.session.get('PRIMAL_EXP_ID')

            try:
                exp_id = request.session.get('PRIMAL_EXP_ID')
                exp_obj = LaDoExperiment.objects.get(id=int(exp_id))
                userInfo = UserInfo.objects.get(user=request.user)

                if type == 0:
                    data = {}
                    participation_obj = PrimalExperimentParticipation.objects.get(user=userInfo, experiment_id=exp_id)
                    if participation_obj.checkCompletion() == False:
                        user_answer_id = participation_obj.getNextUserAnswerID()
                        answer_obj = PrimalExperimentUserAnswer.objects.get(id=int(user_answer_id))

                        #for chart
                        total_question = participation_obj.getTotalNumberOfQuestions()
                        total_answered = participation_obj.getNumberOfAnsweredQuestions()

                        remained_count = total_question - total_answered
                        l_list = []
                        label_list = []
                        for l in range(total_question):
                            l_list.append(l+1)

                        running_correct = participation_obj.getRunningCorrect()
                        answer_time_list = []
                        answer_accuracy_list = []
                        if running_correct is not -1:
                            total_answered_obj = PrimalExperimentUserAnswer.objects.filter(participation=participation_obj,
                                                                                           is_answered=True).order_by('question_play_order')

                            for obj in total_answered_obj:
                                answer_time_list.append(round(float(obj.time_taken), 2))
                                current_accuracy = (obj.running_correct / obj.question_play_order) * 100
                                answer_accuracy_list.append(round(current_accuracy, 2))

                        data['completed'] = 'no'
                        data['label_list'] = l_list
                        data['answer_time_list'] = answer_time_list
                        data['answer_accuracy_list'] = answer_accuracy_list
                        data['running_correct'] = running_correct
                        data['answer_id'] = str(answer_obj.id)
                        data['token1_filepath'] = '/media/' + answer_obj.question.token1_filename
                        data['token2_filepath'] = '/media/' + answer_obj.question.token2_filename

                        return JsonResponse(data, safe=False)
                    else:
                        return HttpResponseRedirect('/Experiments')

                if type == 1:
                    try:
                        data = {}

                        user_answer = request.POST['user_answer']
                        answer_total_time = request.POST['answer_total_time']
                        last_answer_id = request.POST['answer_id']
                        last_running_correct = int(request.POST['running_correct'])

                        print(user_answer, answer_total_time, last_answer_id, last_running_correct)
                        participation_obj = PrimalExperimentParticipation.objects.get(user=userInfo, experiment_id=exp_id)

                        # storing answers
                        last_answered_obj = PrimalExperimentUserAnswer.objects.get(id=int(last_answer_id))
                        last_answered_obj.user_answer = user_answer
                        last_answered_obj.time_taken = answer_total_time
                        last_answered_obj.answered_time = datetime.now()
                        last_answered_obj.is_answered = True
                        last_answered_obj.question_play_order = participation_obj.getNumberOfAnsweredQuestions() + 1

                        if last_running_correct == -1:
                            last_running_correct = 0

                        current_accuracy = 0
                        if last_answered_obj.user_answer == last_answered_obj.question.correct_response:


                            ans_total = participation_obj.getNumberOfAnsweredQuestions() + 1
                            last_running_correct += 1

                            last_answered_obj.running_correct = last_running_correct
                            current_accuracy =(last_running_correct / ans_total) * 100
                            current_accuracy = round(current_accuracy, 2)

                            print(current_accuracy)

                        else:
                            ans_total = participation_obj.getNumberOfAnsweredQuestions() + 1

                            last_answered_obj.running_correct = last_running_correct
                            current_accuracy = (last_running_correct / ans_total) * 100
                            current_accuracy = round(current_accuracy, 2)

                            print(current_accuracy)

                        last_answered_obj.save()


                        data['time_taken'] = round(float(last_answered_obj.time_taken),2)
                        data['current_accuracy'] = current_accuracy
                        data['last_running_currect'] = last_running_correct

                        # data['current_accuracy'] = float()

                        print(last_answered_obj.question_play_order, participation_obj.getRunningCorrect())


                        if participation_obj.checkCompletion() == False:
                            user_answer_id = participation_obj.getNextUserAnswerID()
                            answer_obj = PrimalExperimentUserAnswer.objects.get(id=int(user_answer_id))

                            data['completed'] = 'no'
                            data['answer_id'] = str(answer_obj.id)
                            data['token1_filepath'] = '/media/' + answer_obj.question.token1_filename
                            data['token2_filepath'] = '/media/' + answer_obj.question.token2_filename

                            return JsonResponse(data, safe=False)
                        else:
                            participation_obj.completed_on = datetime.now()
                            participation_obj.save()
                            data['completed'] = 'yes'

                            return JsonResponse(data, safe=False)

                    except:
                        return HttpResponseRedirect('/Experiments')



            except Exception as e:
                print(e)


class LanguageGameExperimentView(View):

    def get(self, request):
        if 'LADO_SELECTED_EXP' in request.session:
            return render(request, 'LanguageGameExperimentPage.html')
        else:
            return HttpResponseRedirect("/Experiments")

    def post(self, request):

        if request.is_ajax():

            type = int(request.POST['type'])

            exp_id = request.session['LADO_SELECTED_EXP']

            try:
                userInfo = UserInfo.objects.get(user=request.user)

                participation_obj = LaDoExperimentParticipation.objects.get(
                    user=userInfo, experiment_id=int(exp_id))

                if type == 0:

                    print('Coming here')
                    data = {}

                    if participation_obj.checkCompletion() == False:
                        user_answer_id = participation_obj.getNextUserAnswerID()
                        print('User answer id ', user_answer_id)
                        answer_obj = LaDoUserAnswer.objects.get(
                            id=int(user_answer_id))
                        print(answer_obj)

                        file_path = '/media/' + answer_obj.question.file_name
                        data['file_path'] = file_path
                        data['question_id'] = str(answer_obj.question.id)
                        data['answer_id'] = str(answer_obj.id)
                        data['total'] = str(
                            participation_obj.getTotalNumberOfQuestions())
                        data['answered'] = str(
                            participation_obj.getNumberOfAnsweredQuestions())

                        return JsonResponse(data, safe=False)

                    else:
                        return HttpResponseRedirect('/Experiments')

                elif type == 1:

                    data = {}

                    user_answer = request.POST['user_answer']
                    answered_id = request.POST['answer_id']

                    conf_val = request.POST['answer_conf']
                    answer_time = request.POST['answer_time']
                    listen_count = request.POST['listen_count']

                    print(user_answer, answered_id, conf_val,
                          answer_time, listen_count)

                    if int(listen_count) == 0:
                        listen_count = 1

                    this_answered_obj = LaDoUserAnswer.objects.get(
                        id=int(answered_id))
                    print(this_answered_obj)

                    # Saving answers
                    this_answered_obj.user_answer = user_answer.lower()
                    this_answered_obj.answer_confidence = conf_val
                    this_answered_obj.time_taken = str(answer_time)
                    this_answered_obj.audio_listen_count = listen_count
                    this_answered_obj.answered_time = datetime.now()
                    this_answered_obj.is_answered = True
                    this_answered_obj.save()

                    if this_answered_obj.question.correct_answer.lower() == this_answered_obj.user_answer.lower():
                        data['answer_status'] = 'Correct'
                    else:
                        data['answer_status'] = 'Incorrect'

                    if participation_obj.checkCompletion() == False:

                        user_answer_id = participation_obj.getNextUserAnswerID()
                        if user_answer_id is None:
                            # for lado2
                            user_answer_id = participation_obj.getNextUserAnswerID_group2()

                        answer_obj = LaDoUserAnswer.objects.get(
                            id=user_answer_id)

                        file_path = '/media/' + answer_obj.question.file_name
                        data['file_path'] = file_path
                        data['question_id'] = str(answer_obj.question.id)
                        data['answer_id'] = str(answer_obj.id)
                        total_ques = participation_obj.getTotalNumberOfQuestions()
                        data['total'] = str(total_ques)
                        total_ans = participation_obj.getNumberOfAnsweredQuestions()
                        data['answered'] = str(total_ans)
                        data['percentage'] = str(
                            int((total_ans * 100) / total_ques))
                        print(data['percentage'])

                        data['given_ans'] = this_answered_obj.user_answer.lower()
                        data['correct_ans'] = this_answered_obj.question.correct_answer.lower()

                        data['completed'] = 'no'
                        data['question_group'] = str(answer_obj.question.question_group)
                        print('COming this block')

                    else:
                        # save completed participation

                        present_time = datetime.now()
                        participation_obj.completed_on = present_time
                        participation_obj.save()

                        user_answers = participation_obj.lado_given_answers.all()
                        total_question = participation_obj.getTotalNumberOfQuestions()
                        total_correct = 0
                        total_time = 0
                        for ans in user_answers:
                            if ans.user_answer.lower() == ans.question.correct_answer:
                                total_correct += 1

                            total_time += float(ans.time_taken)

                        avg_time_sec = float(
                            total_time / (total_question * 1000))
                        total_time = float(total_time / (1000 * 60))

                        stat_obj, created = LaDoExperimentStatistics.objects.get_or_create(
                            participation=participation_obj)
                        if created:
                            stat_obj.total_question = total_question
                            stat_obj.total_correct = total_correct
                            stat_obj.completed_on = present_time
                            stat_obj.avg_time_in_sec = avg_time_sec
                            stat_obj.total_time_in_min = total_time

                            answer_obj = participation_obj.lado_given_answers.all()

                            correct_count = 0
                            for ans in answer_obj:
                                if ans.question.correct_answer.lower() == ans.user_answer.lower():
                                    correct_count += 1

                            stat_obj.total_correct = correct_count
                            stat_obj.save()

                        data['completed'] = 'yes'
                        data['stat_id'] = str(stat_obj.id)

                    print(data)
                    return JsonResponse(data, safe=False)

                elif type == 5:
                    # for result complettion

                    # save completed participation
                    # present_time = datetime.now()
                    # participation_obj.completed_on = present_time
                    # participation_obj.save()
                    #
                    #
                    # user_answers = participation_obj.lado_given_answers.all()
                    # total_question = participation_obj.getTotalNumberOfQuestions()
                    # total_correct = 0
                    # total_time = 0
                    # for ans in user_answers:
                    # 	if ans.user_answer.lower() == ans.question.correct_answer:
                    # 		total_correct += 1
                    #
                    # 	total_time += float(ans.time_taken)
                    #
                    # avg_time_sec = float(total_time /(total_question * 1000))
                    # total_time = float(total_time /(1000 * 60))
                    #
                    # stat_obj = LaDoExperimentStatistics(participation=participation_obj)
                    # stat_obj.total_question = total_question
                    # stat_obj.total_correct = total_correct
                    # stat_obj.completed_on = present_time
                    # stat_obj.avg_time_in_sec = avg_time_sec
                    # stat_obj.total_time_in_min = total_time
                    # stat_obj.save()

                    url = reverse(
                        'LanguageGameExperiment:LaDoShowResult', kwargs={'stat_id': 1})

                    return redirect('/LanguageGameExperiment/LaDoShowResult/1')

            except Exception as e:
                print(e)


        print("coming here")

        return render(request, 'LanguageGameExperimentPage.html')


# this is the call for experiment

class ExperimentTextView(View):

    def get(self, request):

        data = {}

        selected_lado_exp_id = request.session['LADO_SELECTED_EXP']

        data['selected_lado_exp_id'] = selected_lado_exp_id

        return render(request, 'ExperimentTextPage.html', data)

    def post(self, request):

        if request.is_ajax():

            data = {}
            message = 'This is ajax'
            data['message'] = message
            print("Working")

            return JsonResponse(data, safe=False)

        # Ajax part end

        try:
            exp_id = int(request.POST['exp_id'])
            userInfo_obj = UserInfo.objects.get(user=request.user)
            experiment_obj = LaDoExperiment.objects.get(id=exp_id)

            # create participation object
            experiment_participation, created = LaDoExperimentParticipation.objects.get_or_create(
                user=userInfo_obj,
                experiment=experiment_obj,
                retry_count=0,
                defaults={'is_active': True}
            )

            if created:
                # creating question object
                question_list = LaDoQuestion.objects.filter(
                    experiment=experiment_obj)
                print('Participation Object is created')
                for ques in question_list:

                    answer_obj = LaDoUserAnswer(
                        answering_user=userInfo_obj, participation=experiment_participation, question=ques)
                    answer_obj.save()

            complete = experiment_participation.checkCompletion()
            print(complete)
            if complete == False:
                return HttpResponseRedirect('/LanguageGameExperiment/LanguageGameExp')
            else:
                return HttpResponseRedirect('/Experiments')

        except:

            return HttpResponseRedirect('/Experiments')

        return render(request, 'ExperimentTextPage.html')



#### for prolific
class ExperimentTextViewLado1(View):

    def get(self, request):

        data = {}
        # obj = LadoProlificUser.objects.all()
        # print(len(obj))
        language_list = Language.objects.all().order_by('language_name')
        gender_list = Gender.objects.all()

        data['language_list'] = language_list
        data['gender_list'] = gender_list

        # if 'LADO1_SELECTED_EXP_PROLIFIC' in request.session:
        #     del request.session['LADO1_SELECTED_EXP_PROLIFIC']

        request.session['LADO1_SELECTED_EXP_PROLIFIC'] = 1

        selected_lado_exp_id = 1

        data['selected_lado_exp_id'] = selected_lado_exp_id

        return render(request, 'LanguageGame1MainPage.html', data)

    def post(self, request):

        if request.is_ajax():

            data = {}
            message = 'This is ajax'
            data['message'] = message
            print("Working")

            return JsonResponse(data, safe=False)

        # Ajax part end

        try:
            exp_id = int(request.POST['exp_id'])
            age = int(request.POST['age'])
            gender = Gender.objects.get(id=request.POST['gender_id'])

            language = Language.objects.get(language_id= request.POST['language_id'])
            print(exp_id, age, gender, language)

            # userInfo_obj = UserInfo.objects.get(user=request.user)
            experiment_obj = LaDoExperiment.objects.get(id=exp_id)
            print(experiment_obj)
            # del request.session['LADO1_PROLIFIC_ID']
            # try:
            #     print(request.session['LADO1_PROLIFIC_ID'])
            # except KeyError:
            #     print('name variable is not set')

            if 'LADO1_PROLIFIC_ID' in request.session:
                prolific_user = LadoProlificUser.objects.get(id=request.session.get('LADO1_PROLIFIC_ID'))
                print("Existing participant")
            else:

                prolific_user = LadoProlificUser(gender=gender, languages=language,
                                                 age=age, try_count=1)
                prolific_user.save()

                request.session['LADO1_PROLIFIC_ID'] = prolific_user.id
                print(request.session.get('LADO1_PROLIFIC_ID'))
                print("New Participant")

            # create participation object
            experiment_participation, created = LaDoExperimentParticipation.objects.get_or_create(
                lado_prolific_user=prolific_user,
                experiment=experiment_obj,
                retry_count=0,
                defaults={'is_active': True}
            )

            if created:
                # creating question object
                question_list = LaDoQuestion.objects.filter(
                    experiment=experiment_obj)
                print('Participation Object is created')

                for ques in question_list:

                    answer_obj = LaDoUserAnswer(
                        participation=experiment_participation, question=ques)
                    answer_obj.save()


            complete = experiment_participation.checkCompletion()
            print(complete)
            if complete == False:
                return HttpResponseRedirect('/LanguageGameExperiment/Lado1LanguageGameExpPage')
            else:
                return HttpResponseRedirect('/Experiments')

        except:

            return HttpResponseRedirect('/Experiments')

        return render(request, 'ExperimentTextPage.html')

# for prolific lado1
class LanguageGameExperimentViewProlific(View):

    def get(self, request):

        if 'LADO1_SELECTED_EXP_PROLIFIC' in request.session:
            return render(request, 'LanguageGame1QuestionPage.html')
        else:
            return HttpResponseRedirect("/Experiments")

    def post(self, request):

        if request.is_ajax():

            type = int(request.POST['type'])
            print(type)

            exp_id = request.session['LADO1_SELECTED_EXP_PROLIFIC']

            try:
                # userInfo = UserInfo.objects.get(user=request.user)
                prolific_user = request.session.get('LADO1_PROLIFIC_ID')
                participation_obj = LaDoExperimentParticipation.objects.get(
                    lado_prolific_user=prolific_user, experiment_id=int(exp_id))

                if type == 0:

                    print('Coming here')
                    data = {}

                    if participation_obj.checkCompletion() == False:
                        user_answer_id = participation_obj.getNextUserAnswerID()
                        print('User answer id ', user_answer_id)
                        answer_obj = LaDoUserAnswer.objects.get(
                            id=int(user_answer_id))
                        print(answer_obj)

                        file_path = '/media/' + answer_obj.question.file_name
                        data['file_path'] = file_path
                        data['question_id'] = str(answer_obj.question.id)
                        data['answer_id'] = str(answer_obj.id)
                        data['total'] = str(
                            participation_obj.getTotalNumberOfQuestions())
                        data['answered'] = str(
                            participation_obj.getNumberOfAnsweredQuestions())

                        return JsonResponse(data, safe=False)

                    else:
                        return HttpResponseRedirect('/Experiments')

                elif type == 1:

                    data = {}

                    user_answer = request.POST['user_answer']
                    answered_id = request.POST['answer_id']

                    conf_val = request.POST['answer_conf']
                    answer_time = request.POST['answer_time']
                    listen_count = request.POST['listen_count']

                    print(user_answer, answered_id, conf_val,
                          answer_time, listen_count)

                    if int(listen_count) == 0:
                        listen_count = 1

                    this_answered_obj = LaDoUserAnswer.objects.get(
                        id=int(answered_id))
                    print(this_answered_obj)
                    # try:
                    #     print(datetime.datetime.now())
                    # except:
                    #     from datetime import datetime
                    print(datetime.now())
                    # Saving answers
                    this_answered_obj.user_answer = user_answer.lower()
                    this_answered_obj.answer_confidence = conf_val
                    this_answered_obj.time_taken = str(answer_time)
                    this_answered_obj.audio_listen_count = listen_count
                    this_answered_obj.answered_time = datetime.now()
                    this_answered_obj.is_answered = True
                    this_answered_obj.save()

                    if this_answered_obj.question.correct_answer.lower() == this_answered_obj.user_answer.lower():
                        data['answer_status'] = 'Correct'
                    else:
                        data['answer_status'] = 'Incorrect'

                    if participation_obj.checkCompletion() == False:

                        user_answer_id = participation_obj.getNextUserAnswerID()
                        if user_answer_id is None:
                            # for lado2
                            user_answer_id = participation_obj.getNextUserAnswerID_group2()

                        answer_obj = LaDoUserAnswer.objects.get(
                            id=user_answer_id)

                        file_path = '/media/' + answer_obj.question.file_name
                        data['file_path'] = file_path
                        data['question_id'] = str(answer_obj.question.id)
                        data['answer_id'] = str(answer_obj.id)
                        total_ques = participation_obj.getTotalNumberOfQuestions()
                        data['total'] = str(total_ques)
                        total_ans = participation_obj.getNumberOfAnsweredQuestions()
                        data['answered'] = str(total_ans)
                        data['percentage'] = str(
                            int((total_ans * 100) / total_ques))
                        print(data['percentage'])

                        data['given_ans'] = this_answered_obj.user_answer.lower()
                        data['correct_ans'] = this_answered_obj.question.correct_answer.lower()

                        data['completed'] = 'no'
                        data['question_group'] = str(answer_obj.question.question_group)
                        print('COming this block')

                    else:
                        # save completed participation

                        present_time = datetime.now()
                        participation_obj.completed_on = present_time
                        participation_obj.save()

                        user_answers = participation_obj.lado_given_answers.all()
                        total_question = participation_obj.getTotalNumberOfQuestions()
                        total_correct = 0
                        total_time = 0
                        for ans in user_answers:
                            if ans.user_answer.lower() == ans.question.correct_answer:
                                total_correct += 1

                            total_time += float(ans.time_taken)

                        avg_time_sec = float(
                            total_time / (total_question * 1000))
                        total_time = float(total_time / (1000 * 60))

                        stat_obj, created = LaDoExperimentStatistics.objects.get_or_create(
                            participation=participation_obj)
                        if created:
                            stat_obj.total_question = total_question
                            stat_obj.total_correct = total_correct
                            stat_obj.completed_on = present_time
                            stat_obj.avg_time_in_sec = avg_time_sec
                            stat_obj.total_time_in_min = total_time

                            answer_obj = participation_obj.lado_given_answers.all()

                            correct_count = 0
                            for ans in answer_obj:
                                if ans.question.correct_answer.lower() == ans.user_answer.lower():
                                    correct_count += 1

                            stat_obj.total_correct = correct_count
                            stat_obj.save()

                        data['completed'] = 'yes'
                        data['stat_id'] = str(stat_obj.id)

                    print(data)
                    return JsonResponse(data, safe=False)

                elif type == 5:
                    # for result complettion

                    # save completed participation
                    # present_time = datetime.datetime.now()
                    # participation_obj.completed_on = present_time
                    # participation_obj.save()
                    #
                    #
                    # user_answers = participation_obj.lado_given_answers.all()
                    # total_question = participation_obj.getTotalNumberOfQuestions()
                    # total_correct = 0
                    # total_time = 0
                    # for ans in user_answers:
                    # 	if ans.user_answer.lower() == ans.question.correct_answer:
                    # 		total_correct += 1
                    #
                    # 	total_time += float(ans.time_taken)
                    #
                    # avg_time_sec = float(total_time /(total_question * 1000))
                    # total_time = float(total_time /(1000 * 60))
                    #
                    # stat_obj = LaDoExperimentStatistics(participation=participation_obj)
                    # stat_obj.total_question = total_question
                    # stat_obj.total_correct = total_correct
                    # stat_obj.completed_on = present_time
                    # stat_obj.avg_time_in_sec = avg_time_sec
                    # stat_obj.total_time_in_min = total_time
                    # stat_obj.save()

                    url = reverse(
                        'LanguageGameExperiment:LaDoShowResult', kwargs={'stat_id': 1})

                    return redirect('/LanguageGameExperiment/LaDoShowResult/1')

            except Exception as e:
                print(e)


        print("coming here")

        return render(request, 'LanguageGame1QuestionPage.html')



def LaDoShowResult(request, stat_id):

    try:
        data = {}
        # request.session['LADO_SELECTED_EXP'] = 1
        # print(request.session['LADO_SELECTED_EXP'])
        # req_stat_id = request.session['LADO_SELECTED_EXP']
        stat_obj = LaDoExperimentStatistics.objects.get(id=int(stat_id))

        # correct_totatl = stat_obj.participation.lado_given_answers.all()
        c_count = 0
        # for corr in correct_totatl:
        # 	if corr.question.correct_answer.lower() == corr.user_answer.lower():
        # 		c_count += 1
        #
        # stat_obj.total_correct = c_count
        # stat_obj.save()
        # print(stat_obj.total_question)

        data['stat_obj'] = stat_obj
        accuracy = round(
            float((stat_obj.total_correct / stat_obj.total_question) * 100), 2)

        data['accuracy'] = accuracy

        return render(request, 'showLaDoResults.html', data)

    except Exception as e:
        print(e)
        return render(request, 'showLaDoResults.html')


# for Prolific
def LaDoShowResultProlific(request, stat_id):

    try:
        data = {}
        # request.session['LADO_SELECTED_EXP'] = 1
        # print(request.session['LADO_SELECTED_EXP'])
        # req_stat_id = request.session['LADO_SELECTED_EXP']
        stat_obj = LaDoExperimentStatistics.objects.get(id=int(stat_id))

        # correct_totatl = stat_obj.participation.lado_given_answers.all()
        c_count = 0
        # for corr in correct_totatl:
        # 	if corr.question.correct_answer.lower() == corr.user_answer.lower():
        # 		c_count += 1
        #
        # stat_obj.total_correct = c_count
        # stat_obj.save()
        # print(stat_obj.total_question)

        data['stat_obj'] = stat_obj
        accuracy = round(
            float((stat_obj.total_correct / stat_obj.total_question) * 100), 2)

        data['accuracy'] = accuracy

        if 'LADO1_SELECTED_EXP_PROLIFIC' in request.session:
            del request.session['LADO1_SELECTED_EXP_PROLIFIC']
        if 'LADO1_PROLIFIC_ID' in request.session:
            del request.session['LADO1_PROLIFIC_ID']

        return render(request, 'LanguageGame1ShowResultPage.html', data)

    except Exception as e:
        print(e)
        return render(request, 'LanguageGame1ShowResultPage.html')


class AdminLadoResultsView(View):

    def get(self, request, exp_id):

        data = {}

        result_data = LaDoUserAnswer.objects.filter(
            participation__experiment_id=exp_id, participation__completed_on__isnull=False)

        data['result_data'] = result_data

        return render(request, 'AdminviewLadoResults.html', data)


def export_decompound_result_to_csv(request, exp_id):


    try:
        exp = LaDoExperiment.objects.get(id=exp_id)

        if exp.experiment_type == 'de compound':
            result_data = DECompoundExperimentUserAnswer.objects.filter(
                participation__experiment_id=exp_id, user_answer1__isnull=False).order_by('answering_user', 'question__block')
            # print(result_data)
            response = HttpResponse(content_type='text/csv')
            csv_out_file = 'DECompoundExperiment' + "_UserAnswers.csv"
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(csv_out_file)

            writer = csv.writer(response)



            headers = ['participant_id', 'participant_language', 'group', 'block', 'ru_defination',
                             'de_compound', 'SU', 'NS', 'user_answer1', 'answer1_time (ms)', 'user_answer2',
                             'answer2_time (ms)', 'time_taken (ms)', 'answer_order', 'started_on', 'completed_on',
                       'User Age', 'User Gender',
                       'User Living Location', 'User Living Duration (years)']

            additional_headers1 = ['User Has Language RU', 'RU spoken where user lives', 'RU native', 'RU Used at Home',
                                  'RU Learning Duration (years)', 'RU Exposer Through Living (years)', 'RU Reading',
                                  'RU Writing', 'RU Listening', 'RU Speaking']

            additional_headers2 = ['User Has Language DE', 'DE spoken where user lives', 'DE native', 'DE Used at Home',
                                   'DE Learning Duration (years)', 'DE Exposer Through Living (years)', 'DE Reading',
                                   'DE Writing', 'DE Listening', 'DE Speaking']

            total_headers = headers + additional_headers1 + additional_headers2
            writer.writerow(total_headers)

            user_count = 0
            lang_list = ''
            curr_part_id = 0

            data = []
            seen_langs = set([])
            seen_countries = set([])

            language_skills = defaultdict(lambda: defaultdict(lambda: None))  # user -> language -> (reading, writing, listening, speaking, native, used_at_home, exposure_duration_through_living, exposure_duration_through_learning, spoken_at_user_location)
            countries = defaultdict(lambda: defaultdict(lambda: [None, None]))  # user -> country -> (living duration, education duration)
            user_answers = defaultdict(lambda: defaultdict(lambda: (None, None, None, None, None, None, None,
                                                                    None)))  # user -> question ID -> given answer, abs correct yes/no, norm correct yes/no, total time, initial hesitation, typing time, submission hesitation
            # user_answers[EP.user.user.username][UA.answered_question.id] = given, abs_correct, norm_correct, incorrect, no_answer_given, time, initial_hesitation_time, typing_time, submission_hesitation_time, date/time of answer

            total_lang_weight = defaultdict(lambda: 0)
            total_country_weight = defaultdict(lambda: 0)

            # Added by AYAN
            num_languages_user = defaultdict(lambda: 0)
            user_languages_b2_reading = defaultdict(lambda: [])
            # count = 0
            for data in result_data:
                # print(data)

                part_id = data.participation.user.user_id
                if curr_part_id is not part_id:

                    user_languages = data.participation.user.getAllLanguages()
                    lang_list = ''
                    for lang in user_languages:
                        lang_list += lang.language_code + ','

                    curr_lang = 'ru'
                    for skill in UserLanguageSkill.objects.filter(user=data.participation.user,
                                                                  language__language_code__in=['ru', 'de']).order_by('language__language_code'):
                        curr_lang = skill.language.language_code
                        native = 0
                        if skill.is_native_language:
                            # native = "NATIVE1"
                            native = 1

                        # home = "HOME0"
                        home = 0
                        if skill.used_at_home:
                            # home = "HOME1"
                            home = 1

                        # location_lang = "LOC0"
                        location_lang = 0
                        if skill.spoken_at_user_location:
                            # location_lang = "LOC1"
                            location_lang = 1

                        if not skill.reading_level is None:
                            total_lang_weight[
                                skill.language.language_name] += skill.reading_level + skill.writing_level + skill.listening_level + skill.speaking_level

                        exp_living = 0
                        if not skill.exposure_through_living is None:
                            exp_living = skill.exposure_through_living

                        exp_learning = 0
                        if not skill.exposure_through_learning is None:
                            exp_learning = skill.exposure_through_learning

                        if curr_lang == 'ru':
                            ru_lang_info = [1, location_lang, native, home, exp_learning, exp_living,
                                            skill.reading_level, skill.writing_level, skill.listening_level, skill.speaking_level]
                        else:
                            de_lang_info = [1, location_lang, native, home, exp_learning, exp_living,
                                            skill.reading_level, skill.writing_level, skill.listening_level,
                                            skill.speaking_level]

                        # lang_info = [skill.language.language_code, ]
                        # language_skills[data.participation.user.user.username][skill.language.language_name] = (
                        # skill.reading_level, skill.writing_level, skill.listening_level, skill.speaking_level, native,
                        # home, exp_living, exp_learning, location_lang)

                        # additional_headers.append("User Has Language " + lang)
                        # additional_headers.append(lang + " Spoken Where User Lives")
                        # additional_headers.append(lang + " Native")
                        # additional_headers.append(lang + " Used At Home")
                        # additional_headers.append(lang + " Learning Duration (years)")
                        # additional_headers.append(lang + " Exposure Through Living (years)")
                        # additional_headers.append(lang + " Reading")
                        # additional_headers.append(lang + " Writing")
                        # additional_headers.append(lang + " Listening")
                        # additional_headers.append(lang + " Speaking")

                    curr_part_id = part_id

                block = data.question.block
                group = data.question.group
                ru_def = data.question.defination_ru
                de_com = data.question.compound_word_de
                su = int(data.question.supportive_defination_ru)
                ns = int(data.question.neutral_defination_ru)

                ans1 = data.user_answer1
                ans1_time = round(float(data.answer1_time), 2)
                ans2 = data.user_answer2
                ans2_time = round(float(data.answer2_time), 2)
                total_time = round(float(data.total_time_taken), 2)
                ans_order = data.answer_order
                started_on = data.participation.started_on
                completed_on = data.participation.completed_on

                age = data.participation.user.age
                gender = data.participation.user.gender
                country_name = data.participation.user.location.country_name
                living_duration = data.participation.user.location_living_duration


                writer.writerow(
                    [part_id, lang_list, group, block, ru_def, de_com, su, ns, ans1, ans1_time,
                     ans2, ans2_time, total_time, ans_order, started_on, completed_on,
                     age, gender, country_name, living_duration] + ru_lang_info + de_lang_info)

                #
                # prolific_id = data.participation.lado_prolific_user.prolific_id
                # part_lang = data.participation.lado_prolific_user.languages.language_code
                # other_lang = data.participation.lado_prolific_user.other_languages
                # part_age = data.participation.lado_prolific_user.age
                # part_gender = data.participation.lado_prolific_user.gender.name
                #
                # line1 = data.question.line1.lower()
                # line2 = data.question.line2.lower()
                # line2_trans = data.user_answer.lower()
                # time_taken = data.time_taken


            return response

    except Exception as e:
        return HttpResponse(e)


def export_lado_result_to_csv(request, exp_id):

    try:

        exp = LaDoExperiment.objects.get(id=exp_id)

        if exp.experiment_type == 'lado':
            result_data = LaDoUserAnswer.objects.filter(
                participation__experiment_id=exp_id, participation__completed_on__isnull=False).order_by('answering_user')

            response = HttpResponse(content_type='text/csv')
            csv_out_file = exp.experiment_name + "_LadoUserAnswers.csv"
            response['Content-Disposition'] = 'attachment; filename="LadoUserAnswers.csv"'

            writer = csv.writer(response)
            writer.writerow(['Answer Id', 'User', 'File Name', 'Correct Response', 'User Response', 'IsCorrect',
                             'User Confidence', 'Audio Count', 'Respone Time (Second)', 'User Native Languages', 'Experiment Completed On'])
            # writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])

            user_count = 0
            curr_user_name = ''
            for data in result_data:
                # print(data)

                c_id = data.id

                if data.answering_user is not None:
                    user_name = data.answering_user.user.username
                else:
                    user_name = data.participation.lado_prolific_user.id

                if curr_user_name != user_name:

                    curr_user_name = user_name
                    user_count += 1

                sess_name = 'user_' + str(user_count)

                file_name = data.question.file_name
                print(c_id, file_name)
                correct_answer = data.question.correct_answer.lower()
                user_answer = data.user_answer.lower()

                if correct_answer == user_answer:
                    is_correct = 1
                else:
                    is_correct = 0

                conf = data.answer_confidence

                audio_count = max(data.audio_listen_count, 1)
                time_taken = float(data.time_taken) / 1000
                lang_list = []

                if data.answering_user is not None:
                    for lang in data.answering_user.languages.all():
                        lang_list.append(lang)
                else:
                    lang_list.append(data.participation.lado_prolific_user.languages.language_name)

                comp_on = data.participation.completed_on

                if user_answer == '':
                    continue

                writer.writerow([c_id, sess_name, file_name, correct_answer, user_answer,
                                 is_correct, conf, audio_count, time_taken, lang_list, comp_on])

            return response


        elif exp.experiment_type == 'sentence translation':
            result_data = TranslationGameUserAnswer.objects.filter(
                participation__experiment_id=exp_id, participation__completed_on__isnull=False).order_by('answering_user')

            response = HttpResponse(content_type='text/csv')
            csv_out_file = exp.experiment_name + "_UserAnswers.csv"
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(csv_out_file)

            writer = csv.writer(response)
            # writer.writerow(['Answer Id', 'User', 'File Name', 'Correct Response', 'User Response', 'IsCorrect',
            #                  'User Confidence', 'Audio Count', 'Respone Time (Second)', 'User Native Languages', 'Experiment Completed On'])
            # writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])
            writer.writerow((['experiment_name', 'experiment_language', 'participant_id', 'prolific_id', 'participant_language',
                              'participant_other_lang', 'age', 'gender', 'line1', 'line2', 'line2_translation', 'time_taken', 'started_on', 'completed_on']))

            user_count = 0
            curr_user_name = ''
            for data in result_data:
                # print(data)

                exp_name = data.participation.experiment.experiment_name
                exp_lang = data.participation.experiment.experiment_language
                part_id = data.participation.lado_prolific_user.id
                prolific_id = data.participation.lado_prolific_user.prolific_id
                part_lang = data.participation.lado_prolific_user.languages.language_code
                other_lang = data.participation.lado_prolific_user.other_languages
                part_age = data.participation.lado_prolific_user.age
                part_gender = data.participation.lado_prolific_user.gender.name

                line1 = data.question.line1
                line2 = data.question.line2
                line2_trans = data.user_answer
                time_taken = data.time_taken
                started_on = data.participation.started_on
                completed_on = data.participation.completed_on

                writer.writerow([exp_name, exp_lang, part_id, prolific_id, part_lang, other_lang, part_age, part_gender, line1, line2, line2_trans, time_taken, started_on, completed_on])


            return response

        else:
            result_data = PrimalExperimentUserAnswer.objects.filter(
                participation__experiment_id=exp_id, participation__completed_on__isnull=False).order_by('participation__id', 'question__id', 'question_play_order')

            response = HttpResponse(content_type='text/csv')
            csv_out_file = exp.experiment_name + "_UserAnswers.csv"
            response['Content-Disposition'] = 'attachment; filename="PrimingTask1UserAnswers.csv"'

            writer = csv.writer(response)
            writer.writerow(['answer id', 'user',
                             'token1_name', 'token1_gloss', 'token1_language', 'token1_filename',
                             'token2_name', 'token2_gloss', 'token2_language', 'token2_filename',
                             'native_language', 'priming_type', 'phonetic_distance',
                             'correct_response', 'user_response', 'is_correct',
                             'Audio Count', 'respone_time (ms)', 'question_play_order',
                             'experiment_completed_on'])
            # writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])

            user_count = 0
            curr_user_name = ''
            for data in result_data:
                # print(data)

                c_id = data.id

                # if data.answering_user is not None:
                #     user_name = data.answering_user.user.username
                # else:
                #     user_name = data.participation.lado_prolific_user.id
                #
                # if curr_user_name != user_name:
                #     curr_user_name = user_name
                #     user_count += 1

                sess_name = 'user_' + str(data.participation.id)

                token1_name = data.question.token1_name
                token1_gloss = data.question.token1_gloss
                token1_language = data.question.token1_language
                token1_filename = data.question.token1_filename

                token2_name = data.question.token2_name
                token2_gloss = data.question.token2_gloss
                token2_language = data.question.token2_language
                token2_filename = data.question.token2_filename

                native_language = data.question.native_language
                priming_type = data.question.priming_type
                phonetic_distance = data.question.phonetic_distance

                correct_response = data.question.get_correct_response_display()
                user_answer = data.user_answer

                if correct_response == user_answer:
                    is_correct = 1
                else:
                    is_correct = 0

                audio_count = max(data.audio_listen_count, 1)
                if data.time_taken is not None:
                    t_time = float(data.time_taken)
                    time_taken = round(t_time, 3)

                else:
                    time_taken = ''
                # lang_list = []
                #
                # if data.answering_user is not None:
                #     for lang in data.answering_user.languages.all():
                #         lang_list.append(lang)
                # else:
                #     lang_list.append(data.participation.lado_prolific_user.languages.language_name)
                question_play_order = data.question_play_order
                comp_on = data.participation.completed_on

                if user_answer == '':
                    continue

                writer.writerow([c_id, sess_name,
                                 token1_name, token1_gloss, token1_language, token1_filename,
                                 token2_name, token2_gloss, token2_language, token2_filename,
                                 native_language, priming_type, phonetic_distance,
                                 correct_response, user_answer,
                                 is_correct, audio_count, time_taken, question_play_order, comp_on])

            return response


    except Exception as e:
        return HttpResponse(e)


class WebGazingExperimentQuestionUpload(View):

    def get(self, request):

        return render(request, 'WebGazeQuestionUpload.html')

    def post(self, request):
        media_root = settings.MEDIA_ROOT

        # section for inserting the data from csv
        # file_path = 'E:\\MSc\\Hiwi\\LSV HiWi\\lsv-c4-django-webexperiment\\Incomslav\\static\\media\\demo_webgazer\\' + "VWP_parallel_stimuli_PL_CZ_RU_updated.xlsx"
        # # file_path = 'E:\MSc\Hiwi\LSV HiWi\lsv-c4-django-webexperiment\Incomslav\static\media\demo_webgazer'
        # xls_file = pd.read_excel(file_path)
        # print(xls_file.head())
        #
        # xls_file['eng'] = xls_file['eng'].fillna('')
        # xls_file['visual_target_object'] = xls_file['visual_target_object'].fillna('')
        # xls_file['visual_fillers'] = xls_file['visual_fillers'].fillna('')


        # for idx, row in xls_file.iterrows():
            # print(row[0])
            # if pd.isnull(row[0]) == False:
            #     obj = WebGazingExperimentQuestions(con=row[1], stim=row[2], att_check=row[3], decl=row[4], interr=row[5],
            #                                        english_translation=row[6], czech_translation=row[7], polish_translation=row[8],
            #                                        russian_translation=row[9], bulgarian_translation=row[10], bcs_ijek_translation=row[11],
            #                                        visual_target=row[12], visual_fillers=row[13])
            #     print(obj.visual_target, obj.visual_fillers)
            #     obj.save()

        # audio_folder_path = "E:\\MSc\\Hiwi\\LSV HiWi\\lsv-c4-django-webexperiment\\Incomslav\\static\\media\\demo_webgazer\\TTS_VWP_BG"
        # files = []
        # # r=root, d=directories, f = files
        #
        # # text_file = "E:\\MSc\\Hiwi\\LSV HiWi\\lsv-c4-django-webexperiment\\Incomslav\\static\\media\\demo_webgazer\\test.txt"
        # # new_name = "E:\\MSc\\Hiwi\\LSV HiWi\\lsv-c4-django-webexperiment\\Incomslav\\static\\media\\demo_webgazer\\test_new.txt"
        # # os.rename(text_file, new_name)
        # root = 'demo_webgazer/TTS_VWP_BG/'
        # for r, d, f in os.walk(audio_folder_path):
        #     for file in f:
        #
        #         q_id = file.split('_')[0].strip()
        #         new_name = "audio_" + q_id + ".wav"
        #         file_path = root + new_name
        #
        #
        #         try:
        #
        #             old_file_name = os.path.join(audio_folder_path, file)
        #             new_file_name = os.path.join(audio_folder_path, new_name)
        #             print(new_file_name, old_file_name)
        #             # os.rename(old_file_name, new_file_name)
        #             question_obj = WebGazingExperimentQuestions.objects.get(question_id=q_id)
        #             files.append(file_path)
        #             print(q_id, file_path, question_obj.polish_translation)
        #             question_obj.bulgarian_audio = file_path
        #             # question_obj.save()
        #
        #         except Exception as e:
        #             HttpResponse(e)
        #
        #
        # for f in files:
        #     print(f)

        file_path = 'E:\\MSc\\Hiwi\\LSV HiWi\\lsv-c4-django-webexperiment\\Incomslav\\static\\media\\demo_webgazer\\' + "Eye tracking Russian sentences timestamps.csv"
        root = 'demo_webgazer/TTS_VWP_RU/'

        xls_file = pd.read_csv(file_path)

        q_list = []
        for idx, row in xls_file.iterrows():
            sentence = str(row[0]).split('_')
            q_id = sentence[0].strip()
            audio_file_name = sentence[-1].strip()
            q_list.append(int(q_id))

            question_obj = WebGazingExperimentQuestions.objects.get(question_id=q_id)
            question_obj.russian_audio = root + row[0]
            question_obj.russian_audio_gaze_start = row[1]
            question_obj.russian_audio_gaze_end = row[2]
            # question_obj.save()

            print(q_id, question_obj.bulgarian_audio, question_obj.bulgarian_audio_gaze_start, question_obj.bulgarian_audio_gaze_end)

        # print(sorted(q_list), len(q_list))


        return render(request, 'WebGazeQuestionUpload.html')


class SentenceTranslationQuestionUpload(View):

    def get(self, request):

        return render(request, 'WebGazeQuestionUpload.html')

    def post(self, request):
        media_root = settings.MEDIA_ROOT
