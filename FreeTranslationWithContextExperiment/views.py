from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from Common.constants import *
from Common.Enums import *

from FreeTranslationWithContextExperiment.importer import *
from FreeTranslationWithContextExperiment.models import *
from FreeTranslationWithContextExperiment.forms import *

from ExperimentBasics.models import *

import json
import datetime
import random

from Users.enums import *


class FreeTranslationWithContextExperimentsGridView(BaseDatatableView):
    """
    Grid view for uploaded files record
    """
    model = FreeTranslationWithContextExperiment

    # define the columns that will be returned
    columns = ['free_translation_with_context_experiment_id', 'experiment_name', 'native_language.language_code',
               'foreign_language.language_code', 'is_active', 'priority', 'number_of_questions', 'num_answers',
               'created_on', 'delete']
    order_columns = ['free_translation_with_context_experiment_id', 'experiment_name', 'native_language.language_code',
                     'foreign_language.language_code', 'is_active', 'priority', 'number_of_questions', 'num_answers',
                     'created_on', 'delete']

    max_display_length = 20

    def get_initial_queryset(self):
        # get initial data
        return FreeTranslationWithContextExperiment.objects.all()

    def render_column(self, item, column):
        if column == 'delete':
            return "<a onclick='deleteExperiment({});' >delete</a>".format(item.free_translation_with_context_experiment_id)
        # make activation status into a checkbox
        if column == 'is_active':
            if item.is_active:
                return '<input id="is_active_input_' + str(
                    item.id) + '" type="checkbox" onclick="changeActivationStatus({}, true)" '.format(
                    item.free_translation_with_context_experiment_id) + "checked >"
            else:
                return '<input id="is_active_input_' + str(
                    item.id) + ';" type="checkbox" onclick="changeActivationStatus({}, false)" '.format(
                    item.free_translation_with_context_experiment_id) + " >"
        elif column == 'number_of_questions':
            num_questions = item.experiment_questions.count()
            return str(num_questions)
        elif column == 'medal':
            if not item.user_medal is None and item.user_medal:
                O = '<img src="%s" width="%d" height="%d" /><p>%s</p>' % (
                item.user_medal.url, item.user_medal.width, item.user_medal.height, item.user_medal.name)
            else:
                O = '<span style="color: red;">None</span>'
            return O
        elif column == 'num_answers':
            return ExperimentParticipation.objects.filter(experiment=item).count()

        elif column == 'priority':
            return '<input id="priority_input_' + str(
                item.id) + '" style="width:50px" type="number" step="1" min="0" max="100" value="' + str(
                item.priority) + '" > <a onclick="changePriority(' + str(item.id) + ')">save</a>'
        else:
            return super(FreeTranslationWithContextExperimentsGridView, self).render_column(item, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(experiment_name__istartswith=search.strip())
            return qs
        else:
            return qs


class UploadFreeTranslationWithContextExperimentFile(View):
    """
        Uploader view for Free Translation With Context experiment.
    """

    def get(self, request):
        request.user.id = int(request.COOKIES.get(CookieFields.UserID, '0'))
        try:
            return render(request, 'adminpanel/UploadFreeTranslationWithContextExperimentFile.html',
                          {'form': UploadFreeTranslationWithContextExperimentFileForm()})

        except Exception as e:
            return HttpResponse(str(e))

    def post(self, request):
        empty_form = UploadFreeTranslationWithContextExperimentFileForm()

        if request.is_ajax():
            try:
                requestType = request.POST['type']
                # activate an experiment
                if requestType == '1':
                    experiment_id = int(request.POST['experiment_id'])
                    E = FreeTranslationWithContextExperiment.objects.get(pk=experiment_id)
                    E.is_active = True
                    E.save()
                    return HttpResponse(True)
                # deactivate an experiment
                if requestType == '2':
                    experiment_id = int(request.POST['experiment_id'])
                    E = FreeTranslationWithContextExperiment.objects.get(pk=experiment_id)
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
                    E = FreeTranslationWithContextExperiment.objects.get(pk=experiment_id)
                    E.delete()
                    return HttpResponse(True)

                # delete all experiments
                elif requestType == '11':
                    E = FreeTranslationWithContextExperiment.objects.all()
                    for e in E:
                        e.delete()
                    return HttpResponse(True)

                return HttpResponse('Ajax request of unknown type.')
            except Exception as e:
                return HttpResponse(str(e))

        else:
            try:
                form = UploadFreeTranslationWithContextExperimentFileForm(request.POST, request.FILES)
                if form.is_valid():
                    form = form.cleaned_data
                    medal_filename = None
                    if "medal" in request.FILES:
                        medal_file = request.FILES['medal']
                        medalFileName = medal_file.name
                        fs = FileSystemStorage(location=settings.EXPERIMENT_MEDAL_FOLDER,
                                               base_url=settings.EXPERIMENT_MEDAL_URL)
                        medal_filename = fs.save(medalFileName, medal_file)

                    uploaded_file = request.FILES['file']
                    fileName = uploaded_file.name
                    content_type = uploaded_file.content_type
                    fs = FileSystemStorage(location=settings.FREE_TRANSLATION_WITH_CONTEXT_UPLOAD_FOLDER)
                    filename = fs.save(fileName, uploaded_file)
                    experiment_name = form['experiment_name']
                    priority = form['priority']
                    imported_experiments = processFreeTranslationWithContextUploadedFile(FREE_TRANSLATION_WITH_CONTEXT_UPLOAD_FOLDER, filename,
                                                                         experiment_name, priority,
                                                                         medal_filename=medal_filename)
                    return render(request, 'adminpanel/UploadFreeTranslationWithContextExperimentFile.html',
                                  {'imported_experiments': imported_experiments, 'form': empty_form})


            except Exception as e:
                return HttpResponse(str(e))


def parseQuestionWithoutGapIndication(sentence):
    """
    parse sentence and return sentence without gap indication
    """
    sentence = sentence.replace("{", "[").replace("}", "]")
    gaps = re.findall(r"[^[]*\[([^]]*)\]", sentence)
    for g in range(len(gaps)):
        first_option = gaps[g].split('|')[0]
        sentence=sentence.replace(gaps[g],first_option).replace('[','').replace(']','')

    lsWords=sentence.split()
    for i in range(len(lsWords)):
        lsWords[i] = "<span id='spnWord{}' onclick='showNextWord({});' class='spnWords'>".format(i,i)+lsWords[i]+"</span>"

    return ' '.join(lsWords)


def parseQuestion(sentence, translate_language='Translate Here...'):
    """
    parse sentence and return correct answer for each gap
    """
    sentence = sentence.replace("{", "[").replace("}", "]")
    gaps = re.findall(r"[^[]*\[([^]]*)\]", sentence)

    first_option = gaps[0].split('|')[0]
    # textbox = '<input type="text" id="txtTranslation" onchange="handleGapInput();" placeholder="{}">'.format(first_option.strip())
    textbox = '<input type="text" class="task-form-control" id="txtTranslation" onchange="handleGapInput();" placeholder="{}" style="text-align:center;">'.format(translate_language)
    mark_field = '<mark style="background-color: #337ab7; color:white;"> {} </mark>'.format(first_option.strip())
    updated_field = mark_field + '-' + textbox
    sentence=sentence.replace(gaps[0],updated_field).replace('[','').replace(']','')
    return sentence


class FreeTranslationWithContextQuestionsView(View):
    """ View for showing Free Translation With Context experiment questions to the user. """

    def get(self, request):
        # userInfo = UserInfo.objects.get(user=request.user)
        try:
            params = dict()

            if ASSIGNED_EXPERIMENT in request.session:
                if CURRENT_PARTICIPATION in request.session:
                    experiments = Experiment.objects.filter(id=request.session[ASSIGNED_EXPERIMENT]).select_subclasses()
                    if len(experiments) > 0:
                        experiment = experiments[0]
                    else:
                        del request.session[ASSIGNED_EXPERIMENT]
                        return HttpResponseRedirect("/SelectExperiment")
                    params["UserLanguage"] = experiment.native_language.language_name

                    return render(request, 'FreeTranslationWithContext.html', params)

            return HttpResponseRedirect("/SelectExperiment")
        except Exception as e:
            return HttpResponseRedirect("/SelectExperiment")

    def post(self, request):
        if request.is_ajax():
            requestType = request.POST['type']

            try:
                participation = ExperimentParticipation.objects.get(id=request.session[CURRENT_PARTICIPATION])
                # exp_obj = participation.experiment.select_subclasses()
                exp_obj = Experiment.objects.filter(id=participation.experiment.id).select_subclasses()
                if len(exp_obj) > 0:
                    translate_language = exp_obj[0].native_language.language_name
                else:
                    translate_language = 'Translate Here...'

            except ObjectDoesNotExist as e:
                del request.session[CURRENT_PARTICIPATION]
                lang_code = request.COOKIES.get(CookieFields.WebsiteLanguageCode, 'en')
                return HttpResponseRedirect("/" + lang_code + "/SelectExperiment")

            # fetch next sentence for current Participation in this Free Translation With Context task
            if requestType == '1':
                isCorrectAnswer = False
                # save user's answer if a question had been issued
                lastAnswerId = request.POST['qId']
                if lastAnswerId != '':
                    # get the answer object
                    answer_object = FreeTranslationWithContextUserAnswer.objects.get(useranswer_ptr_id=lastAnswerId)
                    # store the given final gap answers
                    answer_object.answer_date = datetime.datetime.now()
                    userAnswer = request.POST['gapsAnswers']
                    answer_object.gap_answer = userAnswer.lower()
                    answer_object.answer_given = True
                    # store elapsed time in milliseconds
                    try:
                        timestampReadSentenceStarted = float(request.POST['timestampReadSentenceStarted'])
                        timestampExperimentStarted = float(request.POST['timestampExperimentStarted'])
                        timestampCompletion = float(request.POST['timestampCompletion'])
                        timeSpent = timestampCompletion - timestampExperimentStarted
                    except Exception as e:
                        timeSpent = 99999
                    answer_object.time_spent = timeSpent
                    inputChanges = request.POST['inputChanges']
                    changes = inputChanges
                    answer_object.result_changes = changes
                    clickedWordsTimeWithWordIndex = request.POST['clickedWordsTime']
                    answer_object.words_click_time= clickedWordsTimeWithWordIndex
                    # save the answer object to commit to database
                    answer_object.save()

                    # finally, get whether the answer was correct
                    isCorrectAnswer = answer_object.isExactlyCorrectAnswer()

                # get question for free translation with context experiment
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
                    nextAnswer = FreeTranslationWithContextUserAnswer.objects.get(useranswer_ptr_id=nextID)
                    nextQuestion =FreeTranslationWithContextQuestion.objects.get(question_ptr_id=nextAnswer.answered_question.id)

                    # get total number of questions, number of answered questions so far, and resulting percentage
                    total = participation.getTotalNumberOfQuestions()
                    answered = participation.getNumberOfAnsweredQuestions()
                    percentage = answered / total * 100
                    q=parseQuestion(nextQuestion.sentence, translate_language=translate_language)
                    q_without_gap_indication=parseQuestionWithoutGapIndication(nextQuestion.sentence)
                    # print(q_without_gap_indication)
                    answer_time= nextQuestion.question_answer_time
                    # return result
                    res = [str(nextAnswer.id), q, str(percentage), str(total), str(answered),
                           str(isCorrectAnswer),str(answer_time),q_without_gap_indication]
                    return HttpResponse('_'.join(res))

            # get experiment completion percentage for free translation with context experiment
            elif requestType == '2':
                total = participation.getTotalNumberOfQuestions()
                answered = participation.getNumberOfAnsweredQuestions()
                if total == 0:
                    percentage = 0
                else:
                    percentage = answered / total
                res = [str(percentage), str(total), str(answered)]
                return HttpResponse('_'.join(res))

        return HttpResponse(status=500)