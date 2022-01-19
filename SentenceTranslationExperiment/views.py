from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django_datatables_view.base_datatable_view import BaseDatatableView

from django.core.files.storage import FileSystemStorage

from Common.constants import *
from Common.Enums import *

from SentenceTranslationExperiment.constants import *
from SentenceTranslationExperiment.importer import *
from SentenceTranslationExperiment.models import *
from SentenceTranslationExperiment.forms import *

from ExperimentBasics.models import *

import json
import datetime

from Users.enums import *

class SentenceTranslationExperimentsGridView(BaseDatatableView):
    """
    Grid view for uploaded files record
    """
    model = SentenceTranslationExperiment

    # define the columns that will be returned
    columns = ['sentence_translation_experiment_id', 'experiment_name', 'native_language.language_code', 'foreign_language.language_code', 'is_active', 'priority', 'number_of_questions', 'num_answers', 'created_on', 'delete']
    order_columns = ['sentence_translation_experiment_id', 'experiment_name', 'native_language.language_code', 'foreign_language.language_code', 'is_active', '', 'priority', 'number_of_questions', 'created_on', '']

    max_display_length = 20

    def get_initial_queryset(self):
        # get initial data
        return SentenceTranslationExperiment.objects.all()

    def render_column(self, item, column):
        if column == 'delete':
            return "<a onclick='deleteExperiment({});' >delete</a>".format(item.sentence_translation_experiment_id)
        # make activation status into a checkbox
        if column == 'is_active':
            if item.is_active:
                return '<input id="is_active_input_'+str(item.id)+'" type="checkbox" onclick="changeActivationStatus({}, true)" '.format(item.sentence_translation_experiment_id)+"checked >"
            else:
                return '<input id="is_active_input_'+str(item.id)+';" type="checkbox" onclick="changeActivationStatus({}, false)" '.format(item.sentence_translation_experiment_id)+" >"
        elif column == 'number_of_questions':
            num_questions = item.experiment_questions.count()
            return str(num_questions)
        elif column == 'num_answers':
            ranks = SentenceTranslationExperiment.objects.get(pk=item.sentence_translation_experiment_id).getNumbersOfCollectedAnswers()
            out = []
            for rank, number in sorted(ranks.items(), key=lambda x:x[0]):
                out.append(str(number)+"@"+str(rank+1))
            if out:
                return str(sum(ranks.values()))+" ("+" + ".join(out)+")"
            else:
                return str(sum(ranks.values()))
        elif column == 'priority':
            return '<input id="priority_input_'+str(item.id)+'" style="width:50px" type="number" step="1" min="0" max="100" value="'+str(item.priority)+'" > <a onclick="changePriority('+str(item.id)+')">save</a>'
        else:
            return super(SentenceTranslationExperimentsGridView, self).render_column(item, column)



class UploadSentenceTranslationExperimentFile(View):
    """
        Uploader view for Sentence Translation experiment.
    """
    def get(self, request):
        request.user.id = int(request.COOKIES.get(CookieFields.UserID, '0'))
        try:
            return render(request, 'adminpanel/UploadSentenceTranslationExperimentFile.html',
                          {'form': UploadSentenceTranslationExperimentFileForm()})

        except Exception as e:
            return HttpResponse(str(e))#status=500)
    
    def post(self, request):
        empty_form = UploadSentenceTranslationExperimentFileForm()

        if request.is_ajax():
            try:
                requestType = request.POST['type']
                # activate an experiment
                if requestType == '1':
                    experiment_id = int(request.POST['experiment_id'])
                    E = SentenceTranslationExperiment.objects.get(pk=experiment_id)
                    E.is_active = True
                    E.save()
                    return HttpResponse(True)
                # deactivate an experiment
                if requestType == '2':
                    experiment_id = int(request.POST['experiment_id'])
                    E = SentenceTranslationExperiment.objects.get(pk=experiment_id)
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
                
                elif requestType == '10':
                    experiment_id = int(request.POST['experiment_id'])
                    E = SentenceTranslationExperiment.objects.get(pk=experiment_id)
                    E.delete()
                    return HttpResponse(True)

                elif requestType == '11':
                    E = SentenceTranslationExperiment.objects.all()
                    for e in E:
                        e.delete()
                    return HttpResponse(True)

                return HttpResponse('Ajax request of unknown type.')
            except Exception as e:
                return HttpResponse(str(e))#status=500)

        else:
            try:
                form = UploadSentenceTranslationExperimentFileForm(request.POST, request.FILES)
                if form.is_valid():
                    form = form.cleaned_data
                    uploaded_file = request.FILES['file']
                    fileName = uploaded_file.name
                    content_type = uploaded_file.content_type
                    SENTENCE_TRANSLATION_UPLOAD_FOLDER = '/srv/C4-django/c4-django-webexperiments/uploadedfiles/SentenceTranslation/'
                    fs = FileSystemStorage(location=SENTENCE_TRANSLATION_UPLOAD_FOLDER)
                    filename = fs.save(fileName, uploaded_file)
                    experiment_name = form['experiment_name']
                    priority = form['priority']
                    imported_experiments = processSentenceTranslationUploadedFile(SENTENCE_TRANSLATION_UPLOAD_FOLDER, filename, experiment_name, priority)
                    return render(request, 'adminpanel/UploadSentenceTranslationExperimentFile.html', {'imported_experiments': imported_experiments, 'form': empty_form})
                
            except Exception as e:
                return HttpResponse(str(e))#status=500)




class SentenceTranslationQuestionView(View):
    """ View for showing Sentence Translation questions to the user. """
    def get(self, request):
        userInfo = UserInfo.objects.get(user=request.user)
        try:
            params = dict()
            params["sentenceTranslationPageConstants"] = SentenceTranslationPageConstants
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
                    
                    return render(request, 'SentenceTranslation.html', params)
            
            return HttpResponse(str(request))#HttpResponseRedirect("/SelectExperiment")
        except Exception as e:
            return HttpResponse(str(e))#HttpResponseRedirect("/SelectExperiment")

    def post(self, request):
        if request.is_ajax():
            requestType = request.POST['type']
            
            try:
                participation = ExperimentParticipation.objects.get(id=request.session[CURRENT_PARTICIPATION])
            except ObjectDoesNotExist as e:
                del request.session[CURRENT_PARTICIPATION]
                lang_code = request.COOKIES.get(CookieFields.WebsiteLanguageCode, 'en')
                return HttpResponseRedirect("/"+lang_code+"/SelectExperiment")
            
            # fetch next question for current Participation in this Sentence Translation task
            if requestType == '1':
                # save user's answer if a question had been issued
                lastAnswerId = request.POST['qId']
                if lastAnswerId != '':
                    # get the answer object
                    answer_object = SentenceTranslationUserAnswer.objects.get(useranswer_ptr_id=lastAnswerId)
                    # store the given final translation
                    answer_object.answer_date = datetime.datetime.now()
                    userAnswer = request.POST['translation']
                    answer_object.translated_sentence = userAnswer
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
                
                # get question for sentence translation experiment
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
                    nextAnswer = SentenceTranslationUserAnswer.objects.get(useranswer_ptr_id=nextID)
                    nextQuestion = SentenceTranslationQuestion.objects.get(question_ptr_id=nextAnswer.answered_question.id)

                    # get total number of questions, number of answered questions so far, and resulting percentage
                    total = participation.getTotalNumberOfQuestions()
                    answered = participation.getNumberOfAnsweredQuestions()
                    percentage = answered/total*100
                    
                    # return result
                    res = [str(nextAnswer.id), nextQuestion.stimulus_sentence, str(percentage), str(total), str(answered)]
                    return HttpResponse('_'.join(res))

            # get experiment completion percentage for sentence translation experiment
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
        
        data.append("-------- SENTENCE TRANSLATION ANSWERS ")
        for UA in SentenceTranslationUserAnswer.objects.filter(answering_user=userInfo).all():
            AQ = UA.answered_question
            AQ = SentenceTranslationQuestion.objects.get(id=AQ.id)
            d = [UA.id, UA.translated_sentence, AQ.id, AQ.stimulus_sentence, UA.answer_given, UA.answer_date, UA.result_changes, UA.time_spent]
            
            for CA in AQ.correct_answers.all():
                d.extend(["C", CA, CA.translated_sentence])
            data.append(d)

        data.append("-------- PARTICIPATIONS ")
        for P in ExperimentParticipation.objects.filter(user=userInfo):
            data.append((P.id, "COMPLETED?", P.completed_on))

        return render(request, "adminpanel/ListAnswers.html", {'common_data': common, 'data': data })
