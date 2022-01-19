from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.http import HttpResponse, JsonResponse
from django_datatables_view.base_datatable_view import BaseDatatableView
import logging

from django.core.files.storage import FileSystemStorage
from django.conf import settings

from Common.constants import *
from Common.Enums import *

from FreeTranslationExperiment.importer import *
from FreeTranslationExperiment.models import *
from FreeTranslationExperiment.forms import *

from ExperimentBasics.models import *

import json
import datetime

from Users.enums import *
from django.shortcuts import get_object_or_404

class FreeTranslationExperimentsGridView(BaseDatatableView):
    """
    Grid view for uploaded files record
    """
    model = FreeTranslationExperiment

    # define the columns that will be returned
    columns = ['free_translation_experiment_id', 'experiment_name', 'native_language.language_code', 'foreign_language.language_code', 'is_active', 'priority', 'number_of_questions', 'num_answers', 'created_on', 'delete', 'stimuli_file']
    order_columns = ['free_translation_experiment_id', 'experiment_name', 'native_language.language_code', 'foreign_language.language_code', 'is_active', 'priority', 'number_of_questions', 'num_answers', 'created_on', 'delete', 'stimuli_file']
    #columns = ['free_translation_experiment_id', 'experiment_name', 'native_language.language_code', 'foreign_language.language_code', 'is_active', 'priority', 'number_of_questions', 'num_answers', 'created_on', 'delete']
    #order_columns = ['free_translation_experiment_id', 'experiment_name', 'native_language.language_code', 'foreign_language.language_code', 'is_active', 'priority', 'number_of_questions', 'num_answers', 'created_on', 'delete']

    max_display_length = 20

    def get_initial_queryset(self):
        # get initial data
        return FreeTranslationExperiment.objects.all()

    def render_column(self, item, column):
        if column == 'delete':
            return "<a onclick='deleteExperiment({});' >delete</a>".format(item.free_translation_experiment_id)
        # make activation status into a checkbox
        if column == 'is_active':
            if item.is_active:
                return '<input id="is_active_input_'+str(item.id)+'" type="checkbox" onclick="changeActivationStatus({}, true)" '.format(item.free_translation_experiment_id)+"checked >"
            else:
                return '<input id="is_active_input_'+str(item.id)+';" type="checkbox" onclick="changeActivationStatus({}, false)" '.format(item.free_translation_experiment_id)+" >"
        elif column == 'number_of_questions':
            num_questions = item.experiment_questions.count()
            return str(num_questions)
        elif column == 'medal':
            if not item.user_medal is None and item.user_medal:
                O = '<img src="%s" width="%d" height="%d" /><p>%s</p>' % (item.user_medal.url, item.user_medal.width, item.user_medal.height, item.user_medal.name)
            else:
                O = '<span style="color: red;">None</span>'
            return O
        elif column == 'num_answers':
            return ExperimentParticipation.objects.filter(experiment=item).count()
        
        elif column == 'priority':
            return '<input id="priority_input_'+str(item.id)+'" style="width:50px" type="number" step="1" min="0" max="100" value="'+str(item.priority)+'" > <a onclick="changePriority('+str(item.id)+')">save</a>'
        
        elif column == 'stimuli_file':
            if item.stimuli_file != None:
                return '<a onclick="redirectTo(\'admin/download-file/' + str(item.folder_name) + '/' + str(item.stimuli_file) + '/\');">' + str(item.stimuli_file) + '</a>'
                # return str(item.stimuli_file)
            else:
                return ''
        else:
            return super(FreeTranslationExperimentsGridView, self).render_column(item, column)



class UploadFreeTranslationExperimentFile(View):
    """
        Uploader view for Free Translation experiment.
    """
    def get(self, request):
        request.user.id = int(request.COOKIES.get(CookieFields.UserID, '0'))
        try:
            return render(request, 'adminpanel/UploadFreeTranslationExperimentFile.html',
                          {'form': UploadFreeTranslationExperimentFileForm()})

        except Exception as e:
            return HttpResponse(str(e))#status=500)
    
    def post(self, request):
        empty_form = UploadFreeTranslationExperimentFileForm()

        if request.is_ajax():
            try:
                requestType = request.POST['type']
                # activate an experiment
                if requestType == '1':
                    experiment_id = int(request.POST['experiment_id'])
                    E = FreeTranslationExperiment.objects.get(pk=experiment_id)
                    E.is_active = True
                    E.save()
                    return HttpResponse(True)
                # deactivate an experiment
                if requestType == '2':
                    experiment_id = int(request.POST['experiment_id'])
                    E = FreeTranslationExperiment.objects.get(pk=experiment_id)
                    E.is_active = False
                    E.save()
                    return HttpResponse(True)
                
                # change an experiment's priority
                if requestType == '3':
                    experiment_id = int(request.POST['experiment_id'])
                    new_priority = int(request.POST['new_priority'])
                    E = Experiment.objects.get(pk=experiment_id)
                    E.priority = new_priority
                    E.save()
                    return HttpResponse(True)
                
                # delete an experiment
                elif requestType == '10':
                    experiment_id = int(request.POST['experiment_id'])
                    E = FreeTranslationExperiment.objects.get(pk=experiment_id)
                    E.delete()
                    return HttpResponse(True)

                # delete all experiments
                elif requestType == '11':
                    E = FreeTranslationExperiment.objects.all()
                    for e in E:
                        e.delete()
                    return HttpResponse(True)


                return HttpResponse('Ajax request of unknown type.')
            except Exception as e:
                return HttpResponse(str(e))#status=500)

        else:
            try:
                form = UploadFreeTranslationExperimentFileForm(request.POST, request.FILES)
                if form.is_valid():
                    form = form.cleaned_data
                    medal_filename = None
                    if "medal" in request.FILES:
                        medal_file = request.FILES['medal']
                        medalFileName = medal_file.name
                        fs = FileSystemStorage(location=settings.EXPERIMENT_MEDAL_FOLDER, base_url = settings.EXPERIMENT_MEDAL_URL)
                        medal_filename = fs.save(medalFileName, medal_file)

                    uploaded_file = request.FILES['file']
                    fileName = uploaded_file.name
                    content_type = uploaded_file.content_type
                    fs = FileSystemStorage(location=settings.FREE_TRANSLATION_UPLOAD_FOLDER)
                    filename = fs.save(fileName, uploaded_file)
                    experiment_name = form['experiment_name']
                    priority = form['priority']
                    imported_experiments = processFreeTranslationUploadedFile(FREE_TRANSLATION_UPLOAD_FOLDER, filename, experiment_name, priority, medal_filename=medal_filename)
                    return render(request, 'adminpanel/UploadFreeTranslationExperimentFile.html', {'imported_experiments': imported_experiments, 'form': empty_form})
                

            except Exception as e:
                return HttpResponse(str(e))#status=500)

# class for multiple retry
class RetryFreeTranslationQuestionView(View):
    """ View for showing Free Translation questions to the user. """
    def get(self, request):
        userInfo = UserInfo.objects.get(user=request.user)
        try:
            params = dict()
            params["freeTranslationPageConstants"] = FreeTranslationPageConstants
            params["commonConstants"] = CommonConstants
            
            if RETRY_ASSIGNED_EXPERIMENT in request.session:
                if RETRY_CURRENT_PARTICIPATION in request.session:
                    experiments = Experiment.objects.filter(id=request.session[RETRY_ASSIGNED_EXPERIMENT]).select_subclasses()
                    if len(experiments) > 0:
                        experiment = experiments[0]
                    else:
                        del request.session[RETRY_ASSIGNED_EXPERIMENT]
                        return HttpResponseRedirect("/SelectExperiment")
                    params["UserLanguage"] = experiment.native_language.language_name
                    

                    if RETRY_AUDIO_EXPERIMENT in request.session:
                        return render(request, 'RetryFreeTranslationAudio.html', params)
                    else:
                        return render(request, 'RetryFreeTranslation.html', params)
            
            return HttpResponseRedirect("/SelectExperiment")
        except Exception as e:
            return HttpResponseRedirect("/SelectExperiment")

    def post(self, request):
        if request.is_ajax():
            requestType = request.POST['type']
            
            try:
                participation = RetryExperimentParticipation.objects.get(id=request.session[RETRY_CURRENT_PARTICIPATION])

            except ObjectDoesNotExist as e:
                del request.session[RETRY_CURRENT_PARTICIPATION]
                lang_code = request.COOKIES.get(CookieFields.WebsiteLanguageCode, 'en')
                return HttpResponseRedirect("/"+lang_code+"/SelectExperiment")
            
            # fetch next question for current Participation in this Free Translation task
            if requestType == '1':

                isCorrectAnswer = False
                # save user's answer if a question had been issued
                lastAnswerId = request.POST['qId']
                # print(lastAnswerId)
                if lastAnswerId != '':
                    # get the answer object
                    answer_object = RetryFreeTranslationUserAnswer.objects.get(retryuseranswer_ptr_id=lastAnswerId)
                    # store the given final translation
                    answer_object.re_answer_date = datetime.datetime.now()
                    userAnswer = request.POST['translation']
                    answer_object.native_word = userAnswer
                    answer_object.re_answer_given = True
                    # store elapsed time in milliseconds
                    try:
                        timestampExperimentStarted = float(request.POST['timestampExperimentStarted'])
                        timestampCompletion = float(request.POST['timestampCompletion'])
                        timeSpent = timestampCompletion - timestampExperimentStarted

                        # print(timestampExperimentStarted, timestampCompletion, timeSpent)
                        # print("time question started: ", timestampExperimentStarted)
                        # print("time button pressed: ", timestampCompletion)
                        # print("Total time taken: ", timeSpent)

                    except Exception as e:
                        timeSpent = 99999
                    answer_object.re_time_spent = timeSpent
                    inputChanges = request.POST['inputChanges']
                    changes = inputChanges
                    answer_object.result_changes = changes
                    # print("Keypressed timestamp: ",changes)
                    # save the answer object to commit to database
                    answer_object.save()
                    
                    # finally, get whether the answer was correct
                    isCorrectAnswer = answer_object.isCorrectAnswer()
                
                # checked until here
                # get question for free translation experiment
                nextID = participation.getNextUserAnswerID()
                # print(nextID)
                if nextID is None:
                    participation.completed_on = datetime.datetime.now()
                    participation.save()
                    if RETRY_ASSIGNED_EXPERIMENT in request.session:
                        del request.session[RETRY_ASSIGNED_EXPERIMENT]
                    if RETRY_CURRENT_PARTICIPATION in request.session:
                        del request.session[RETRY_CURRENT_PARTICIPATION]
                    if RETRY_EXPERIMENT_STATUS in request.session:
                        del request.session[RETRY_EXPERIMENT_STATUS]

                    request.session[RETRY_LAST_COMPLETED_EXPERIMENT] = participation.experiment.id
                    request.session[RETRY_LAST_COMPLETED_PARTICIPATION] = participation.id
                    return HttpResponse("0_END")
                else:
                    # print("checked here")
                    nextAnswer = RetryFreeTranslationUserAnswer.objects.get(retryuseranswer_ptr_id=nextID)
                    nextQuestion = FreeTranslationQuestion.objects.get(question_ptr_id=nextAnswer.re_answered_question.id)

                    # get total number of questions, number of answered questions so far, and resulting percentage
                    total = participation.getTotalNumberOfQuestions()
                    answered = participation.getNumberOfAnsweredQuestions()
                    try:
                        percentage = answered/total*100
                    except:
                        percentage = 0
                    

                    has_audio = 'no'
                    nextUrl = ''
                    # For Audio Experiment
                    if RETRY_AUDIO_EXPERIMENT in request.session:
                        if nextQuestion.has_audio == True and nextQuestion.audio_file != None:
                            nextUrl = str(nextQuestion.audio_file.url)
                            has_audio = 'yes'
                            msg = str(nextQuestion.id) + '_' + str(nextQuestion.foreign_word) + '_' + str(nextQuestion.audio_file.url)
                            print(msg)
                            # logger.info(msg)



                    # return result
                    res = [str(nextAnswer.id), nextQuestion.foreign_word, str(percentage), str(total), str(answered), str(isCorrectAnswer), has_audio, nextUrl]
                    return HttpResponse('_'.join(res))

            # get experiment completion percentage for free translation experiment
            elif requestType == '2':
                total = participation.getTotalNumberOfQuestions()
                answered = participation.getNumberOfAnsweredQuestions()
                try:
                    percentage = answered/total
                except:
                    percentage = 0
                res = [str(percentage), str(total), str(answered)]
                return HttpResponse('_'.join(res))
    
        return HttpResponse(status=500)



class FreeTranslationQuestionView(View):
    """ View for showing Free Translation questions to the user. """
    def get(self, request):

        userInfo = UserInfo.objects.get(user=request.user)
        try:
            params = dict()
            params["freeTranslationPageConstants"] = FreeTranslationPageConstants
            params["commonConstants"] = CommonConstants
            
            if ASSIGNED_EXPERIMENT in request.session:
                if CURRENT_PARTICIPATION in request.session:
                    experiments = Experiment.objects.filter(id=request.session[ASSIGNED_EXPERIMENT]).select_subclasses()

                    if len(experiments) > 0:
                        experiment = experiments[0]

                    else:
                        del request.session[ASSIGNED_EXPERIMENT]

                        return HttpResponseRedirect("/SelectExperiment")
                        
                    params["UserLanguage"] = experiment.native_language.language_name
                    print("coming here too!!!")

                    if request.session[SELECTED_EXPERIMENT_TYPE] == 'audio':
                        print("Going to Free translation Audio!!!")
                        return render(request, 'FreeTranslationAudio.html', params)
                    else:
                        return render(request, 'FreeTranslation.html', params)

                    return render(request, 'FreeTranslation.html', params)
            
            print("coming here Exception!!!")
            return HttpResponseRedirect("/SelectExperiment")
        except Exception as e:

            return HttpResponseRedirect("/SelectExperiment")

    def post(self, request):
        if request.is_ajax():
            requestType = request.POST['type']
            
            try:
                participation = ExperimentParticipation.objects.get(id=request.session[CURRENT_PARTICIPATION])
            except ObjectDoesNotExist as e:
                del request.session[CURRENT_PARTICIPATION]
                lang_code = request.COOKIES.get(CookieFields.WebsiteLanguageCode, 'en')
                return HttpResponseRedirect("/"+lang_code+"/SelectExperiment")
            
            # fetch next question for current Participation in this Free Translation task
            if requestType == '1':
                isCorrectAnswer = False
                # save user's answer if a question had been issued
                lastAnswerId = request.POST['qId']
                if lastAnswerId != '':
                    # get the answer object
                    answer_object = FreeTranslationUserAnswer.objects.get(useranswer_ptr_id=lastAnswerId)
                    # store the given final translation
                    answer_object.answer_date = datetime.datetime.now()
                    userAnswer = request.POST['translation']
                    answer_object.native_word = userAnswer
                    answer_object.answer_given = True
                    # store elapsed time in milliseconds
                    try:
                        timestampExperimentStarted = float(request.POST['timestampExperimentStarted'])
                        timestampCompletion = float(request.POST['timestampCompletion'])
                        timeSpent = timestampCompletion - timestampExperimentStarted
                    except Exception as e:
                        timeSpent = 99999
                    answer_object.time_spent = timeSpent
                    inputChanges = request.POST['inputChanges']
                    changes = inputChanges
                    answer_object.result_changes = changes
                    # save the answer object to commit to database
                    answer_object.save()
                    
                    # finally, get whether the answer was correct
                    isCorrectAnswer = answer_object.isCorrectAnswer()
                
                # get question for free translation experiment
                nextID = participation.getNextUserAnswerID()
                if nextID is None:
                    participation.completed_on = datetime.datetime.now()
                    participation.save()
                    if ASSIGNED_EXPERIMENT in request.session:
                        del request.session[ASSIGNED_EXPERIMENT]
                    if CURRENT_PARTICIPATION in request.session:
                        del request.session[CURRENT_PARTICIPATION]
                    request.session[LAST_COMPLETED_EXPERIMENT] = participation.experiment.id
                    request.session[LAST_COMPLETED_PARTICIPATION] = participation.id
                    return HttpResponse("0_END")
                else:
                    # print("checked here")
                    nextAnswer = FreeTranslationUserAnswer.objects.get(useranswer_ptr_id=nextID)
                    nextQuestion = FreeTranslationQuestion.objects.get(question_ptr_id=nextAnswer.answered_question.id)

                    # get total number of questions, number of answered questions so far, and resulting percentage
                    total = participation.getTotalNumberOfQuestions()
                    answered = participation.getNumberOfAnsweredQuestions()
                    percentage = answered/total*100


                    has_audio = 'no'
                    nextUrl = ''
                    # For Audio Experiment
                    if request.session[SELECTED_EXPERIMENT_TYPE] == 'audio':
                        if nextQuestion.has_audio == True and nextQuestion.audio_file != None:
                            nextUrl = str(nextQuestion.audio_file.url)
                            # print(nextUrl)
                            has_audio = 'yes'
                            # msg = str(nextQuestion.id) + '_' + str(nextQuestion.foreign_word) + '_' + str(
                            #     nextQuestion.audio_file.url)
                            # print(msg)

                    
                    # return result
                    res = [str(nextAnswer.id), nextQuestion.foreign_word, str(percentage), str(total), str(answered), str(isCorrectAnswer), has_audio, nextUrl, str(nextQuestion.free_translation_question_id)]
                    return HttpResponse('_'.join(res))

            # get experiment completion percentage for free translation experiment
            elif requestType == '2':
                total = participation.getTotalNumberOfQuestions()
                answered = participation.getNumberOfAnsweredQuestions()
                percentage = answered/total
                res = [str(percentage), str(total), str(answered)]
                return HttpResponse('_'.join(res))
    
        return HttpResponse(status=500)


class ListAnswersView(View):
    def get(self, request):
        userInfo = UserInfo.objects.get(user=request.user)
        common = []
        common.append(("user id",userInfo.id))
        if ASSIGNED_EXPERIMENT in request.session:
            experiments = Experiment.objects.filter(id=request.session[ASSIGNED_EXPERIMENT]).select_subclasses()
            if len(experiments) > 0:
                experiment = experiments[0]
            else:
                del request.session[ASSIGNED_EXPERIMENT]
                lang_code = request.COOKIES.get(CookieFields.WebsiteLanguageCode, 'en')
                return HttpResponseRedirect("/"+lang_code+"/SelectExperiment")
            common.append(("exp id", experiment.id))
        else:
            common.append("no experiment in session")

        if CURRENT_PARTICIPATION in request.session:
            try:
                participation = ExperimentParticipation.objects.get(id=request.session[CURRENT_PARTICIPATION])
            except ObjectDoesNotExist as e:
                del request.session[CURRENT_PARTICIPATION]
                lang_code = request.COOKIES.get(CookieFields.WebsiteLanguageCode, 'en')
                return HttpResponseRedirect("/"+lang_code+"/SelectExperiment")
            common.append(("participation id", participation.id))
        else:
            common.append("no participation in session")
        data = []
        
        data.append("-------- FREE TRANSLATION ANSWERS ")
        for UA in FreeTranslationUserAnswer.objects.filter(answering_user=userInfo).all():
            AQ = UA.answered_question
            AQ = FreeTranslationQuestion.objects.get(id=AQ.id)
            d = [UA.id, UA.native_word, AQ.id, AQ.foreign_word, UA.answer_given, UA.answer_date, UA.result_changes, UA.time_spent]
            
            for CA in AQ.correct_answers.all():
                d.extend(["C", CA, CA.native_word])
            data.append(d)

        data.append("-------- PARTICIPATIONS ")
        for P in ExperimentParticipation.objects.filter(user=userInfo):
            data.append((P.id, "COMPLETED?", P.completed_on))

        return render(request, "adminpanel/ListAnswers.html", {'common_data': common, 'data': data })


class FreeTranslationQuestionAudioUploadAjaxView(View):

    def post(self, request, id):
        print("Ajax Calling....")
        instance = get_object_or_404(FreeTranslationQuestion, id=id)
        form = UploadFreeTranslationQuestionAudioFrom(self.request.POST, self.request.FIlES, instance=instance)

        if form.is_valid():
            data = {'is_valid' : True}
        else:
            data = {'is_valid' : False}
        # if form.is_valid():
        #     audio = form.save()
        #     data = {'is_valid' : True, 'name': audio.audio_file.name, 'url': audio.audio_file.url}
        # else:
        #     data = {'is_valid' : False}


        return JsonResponse(data)

