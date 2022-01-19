from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
import locale

from Common import constants
from ExperimentBasics.models import *
from ExperimentBasics.forms import *
from ExperimentBasics.definitions import *

from Users.models import *
from Users.enums import *

from random import choice


class UserExperimentOverviewView(View):
    def get(self, request):
        try:
            if UserInfo.objects.filter(user=request.user).exists():
                userInfo = UserInfo.objects.get(user=request.user)

                cleared = userInfo.clearedForExperiments()

                # fetch completed experiment with correct percentage answers
                # AYAN
                exp_with_percentage, list_plot, num_experiments = UserExperimentOverviewView.getExperimentWithMedals(userInfo)

                available_experiments = []
                X = Experiment.getExperimentsAvailableToUser(userInfo)
                for ex in X:
                    try:
                        experimentName, toFromLanguageTable = ex.getExperimentNameForExperimentMedalsPage()
                        fromLanguage = _("XL")
                        if ex.foreign_language != 'XL':
                            fromLanguage = str(ex.foreign_language.language_code)
                        toLanguage = str(ex.native_language.language_code)
                        available_experiments.append(
                            (ex.id, experimentName, toFromLanguageTable, fromLanguage, toLanguage))
                    except Exception as e:
                        pass
                # AYAN
                return render(request, "ExperimentOverview.html", {'completed_experiments': exp_with_percentage,
                                                                   'available_experiments': available_experiments,
                                                                   "cleared_for_experiments": cleared,
                                                                   'list_plot': list_plot,
                                                                   'num_exp': num_experiments})

            # redirect to user profile page if user profile didn't exist or user isn't cleared for experiments
            return HttpResponseRedirect("/UserInfoForm")
        except Exception as e:
            # return HttpResponse(status=500)
            return HttpResponse('Error in Experiment Overview. Please report this error to the admins: ' + str(e))


    def post(self, request):
        try:
            exp_id = int(str(request.POST["hdnId"]).strip())
            experiment = Experiment.objects.get(id=exp_id, is_active__exact=True)
            request.session[ASSIGNED_EXPERIMENT] = exp_id
            if CURRENT_PARTICIPATION in request.session:
                del request.session[CURRENT_PARTICIPATION]
            return render(request, 'ExperimentWelcome.html', {'strings': experiment.getWelcomeTemplateStrings(),
                                                              'ExperimentWelcomeScreenConstants': ExperimentWelcomeScreenConstants})
        except Exception as ex:
            return HttpResponseRedirect('/SelectExperiment')

    @staticmethod
    def getExperimentWithMedals(userInfo):
        experiments = []
        # AYAN
        # Maintain list of data-points to generate the plot later
        list_for_plot = []
        for ep in ExperimentParticipation.objects.filter(user=userInfo, completed_on__isnull=False).distinct(
                "experiment"):
            num_total, num_correct, num_incorrect, num_not_answered, total_time = ep.getResults()
            correct_perc = float(num_correct) / float(num_total)
            competedOn = ep.completed_on
            competedOn = competedOn.strftime('%a, %x')
            ex = Experiment.objects.filter(pk=ep.experiment.id).select_subclasses()[0]
            # ex = ep.experiment
            fromLanguage = _("XL")
            if ex.foreign_language != "XL":
                fromLanguage = str(ex.foreign_language.language_code)
            toLanguage = str(ex.native_language.language_code)
            medal = "bronze"
            if correct_perc >= 0.80:
                medal = "gold"
            elif correct_perc >= 0.60:
                medal = "silver"

            experimentName, toFromLanguageTable = ex.getExperimentNameForExperimentMedalsPage()
            
            # AYAN
            correct_perc = round(correct_perc*100,2)
            exp_type = "-".join(experimentName.split()[0:2]) if len(experimentName) > 2 else "-".join(experimentName.split())
            list_for_plot.append([fromLanguage.upper()+'-'+toLanguage.upper()+'-'+exp_type, correct_perc])

            experiments.append(
                (experimentName, toFromLanguageTable, num_total, num_correct, correct_perc, fromLanguage, toLanguage, medal, competedOn))
        # AYAN
        return experiments, list_for_plot, len(list_for_plot)


class TestView(View):
    def get(self, request):
        common = []
        data = []
        for e in Experiment.objects.all():
            ranks = e.getNumbersOfCollectedAnswers()
            common.append((e, sum(ranks.values())))
            for r, cnt in ranks.items():
                data.append((e, r, cnt))

        return render(request, "adminpanel/ListAnswers.html", {'common_data': common, 'data': data})


class SelectExperimentView(View):
    """ View that selects an experiment for a user if the user is not involved in an experiment already. """

    def get(self, request):
        try:
            if ASSIGNED_EXPERIMENT in request.session:
                experiments = Experiment.objects.filter(id=request.session[ASSIGNED_EXPERIMENT]).select_subclasses()
                if len(experiments) > 0:
                    selected = experiments[0]
                else:
                    del request.session[ASSIGNED_EXPERIMENT]
                    return HttpResponseRedirect("/SelectExperiment")

                # return HttpResponse("Already had an experiment assigned: "+str(request.session[ASSIGNED_EXPERIMENT]))
                return render(request, 'ExperimentWelcome.html', {'strings': selected.getWelcomeTemplateStrings(),
                                                                  'ExperimentWelcomeScreenConstants': ExperimentWelcomeScreenConstants,
                                                                  'enableJavaScriptMessage': EnableJavaScriptMessageConstants})

            if UserInfo.objects.filter(user=request.user).exists():
                userInfo = UserInfo.objects.get(user=request.user)
            else:
                userInfo = UserInfo()

            user_native_languages = [x.language_code for x in userInfo.getNativeLanguages()]
            user_all_languages = list(userInfo.getAllLanguages())

            preselected = []
            # for all active experiments, check if user fulfills prerequisites
            experiments = Experiment.objects.filter(is_active__exact=True).select_subclasses()
            user_rank = ExperimentParticipation.getUserRank(userInfo)
            last_priority = None
            if len(experiments) > 0:
                preselected = self.getAvailableExperiments(experiments, userInfo, user_native_languages,
                                                                           user_all_languages, isEnglish=False)

            if preselected:
                # select from the available experiments at random
                selected = self.selectExperimentRandomly(preselected, user_rank)
                # testing for gap filling experiment
                # request.session[ASSIGNED_EXPERIMENT] = 143
                request.session[ASSIGNED_EXPERIMENT] = selected.id
                return render(request, 'ExperimentWelcome.html', {'strings': selected.getWelcomeTemplateStrings(),
                                                                  'ExperimentWelcomeScreenConstants': ExperimentWelcomeScreenConstants})
            else:
                # here will be the logic for english language speaker
                lang = Language.objects.get(language_code='en')
                ep = ExperimentPrerequisite.objects.filter(
                    nativelanguageprerequisite__required_language=lang).select_subclasses()[0]
                experiments = Experiment.objects.filter(is_active__exact=True,
                                                        user_prerequisites=ep).select_subclasses()
                if len(experiments) > 0:
                    preselected = self.getAvailableExperiments(experiments, userInfo,
                                                                               user_native_languages,
                                                                               user_all_languages, isEnglish=True)
                if preselected:
                    # select from the available experiments at random
                    selected = self.selectExperimentRandomly(preselected, user_rank)
                    request.session[ASSIGNED_EXPERIMENT] = selected.id
                    return render(request, 'ExperimentWelcome.html', {'strings': selected.getWelcomeTemplateStrings(),
                                                                      'ExperimentWelcomeScreenConstants': ExperimentWelcomeScreenConstants})
                # --------------end of english speaker logic----------
                params = dict()
                params["NoExperimentExistConstants"] = constants.NoExperimentExistConstants
                return render(request, 'StayTuned.html', params)

        except Exception as e:
            # return HttpResponse(status=500)
            return HttpResponse('Error in Select Experiment view. Please report this error to the admins: ' + str(e))

    def post(self, request):
        userInfo = UserInfo.objects.get(user=request.user)
        experiments = Experiment.objects.filter(id=request.session[ASSIGNED_EXPERIMENT]).select_subclasses()
        if len(experiments) > 0:
            experiment = experiments[0]
        else:
            del request.session[ASSIGNED_EXPERIMENT]
            return HttpResponseRedirect("/SelectExperiment")
        if CURRENT_PARTICIPATION not in request.session:
            participation = experiment.getActiveParticipationForUser(userInfo)
            request.session[CURRENT_PARTICIPATION] = participation.id
        return HttpResponseRedirect(experiment.getRedirectURL())

    def getAvailableExperiments(self,experiments, userInfo, userNativeLanguages, userAllLanguages, isEnglish):
        """
        get all available experiments
        """
        preselected = []
        last_priority = None

        user_languages= [x.language_code for x in userAllLanguages]

        # if user does not know any cyrillic language then don't show any experiment in cyrillic languages

        # Commented by Hasan on 2018-06-10
        # is_cyrillic = False
        # ls_cyrillic_languages = ['bg','sr','ru','uk','be','mk']
        # for ul in user_languages:
        #     if ul in ls_cyrillic_languages:
        #         is_cyrillic = True
        #         break
        # end comment


        # Added by Hasan on 10_06_2018
        user_scripts = LanguageScriptRelation.objects.filter(language__in=userAllLanguages).distinct('script__script_name')
        for s in user_scripts:
            print(s.script.script_name, s.language.language_name)

        script_code = [x.script.script_code for x in user_scripts]
        print(script_code)

        for experiment in experiments:
            exp = None

            # cyrillic languages related logic
            foreign_lang = experiment.foreign_language
            native_language = experiment.native_language
            # exclude experiments related to cyrillic language
            # Commented by Hasan on 2018_06_10
            # if not is_cyrillic:
            #     if foreign_lang.language_code in ls_cyrillic_languages or native_language.language_code in ls_cyrillic_languages:
            #         # return the control to the beginning of the experiment for loop
            #         continue

            # We need to do for native language also
            if experiment.foreign_script is not None:
                if experiment.foreign_script not in script_code:
                    continue
            else:
                foreign_lang_script = LanguageScriptRelation.objects.filter(language=foreign_lang)
                continue_flag = True
                for sc in foreign_lang_script:
                    
                    if sc.script.script_code in script_code:
                        continue_flag = False

                if continue_flag is True:
                    continue

            if not isEnglish:
                if experiment.userFulfillsPrerequisites(userInfo):
                    # mark this experiment as available for this user if the user hasn't completed this experiment before
                    exp, last_priority = self.getNotCompletedExperiment(experiment, userInfo,
                                                                                       userNativeLanguages,
                                                                                       userAllLanguages, last_priority)
            else:
                exp, last_priority = self.getNotCompletedExperiment(experiment, userInfo,
                                                                                   userNativeLanguages,
                                                                                   userAllLanguages, last_priority)
            if exp is not None:
                preselected.append(exp)
            # last_priority = lastPriority
        return preselected

    def getNotCompletedExperiment(self,experiment, userInfo, userNativeLanguages, userAllLanguages, lastPriority):
        """
        get all experiments which haven't been completed by user
        """

        if not experiment.userHasCompletedExperiment(userInfo):
            keep = False

            # here add logic for cz users
            # if they know pl exclude pl for cz, if they know bg exclude bg for cz etc.
            if 'cs' in userNativeLanguages:
                foreign_lang = experiment.foreign_language
                if foreign_lang not in userAllLanguages:
                    if lastPriority is None:
                        keep = True
                        lastPriority = experiment.priority
                    else:
                        if experiment.priority >= lastPriority:
                            keep = True
                            lastPriority = experiment.priority

            # logic for german natives, if german native knows ru show him/her bg-de experiment and so on
            elif 'de' in userNativeLanguages:
                allowed_languages = self.getAllowedExperimentLanguages(userAllLanguages)
                foreign_lang = experiment.foreign_language
                if foreign_lang.language_code in allowed_languages:
                    if lastPriority is None:
                        keep = True
                        lastPriority = experiment.priority
                    else:
                        if experiment.priority >= lastPriority:
                            keep = True
                            lastPriority = experiment.priority
            else:
                if lastPriority is None:
                    keep = True
                    lastPriority = experiment.priority
                else:
                    if experiment.priority >= lastPriority:
                        keep = True
                        lastPriority = experiment.priority
            if keep:
                # lsPreselectedExperiments.append(experiment)
                return experiment, lastPriority

        return None, lastPriority

    def selectExperimentRandomly(self,preselectedExperiments, userRank):
        """
        Select experiment randomly from pre-selected experiments
        """

        exps_with_nums = []
        for experiment in preselectedExperiments:
            ranks = experiment.getNumbersOfCollectedAnswers()
            num_answers_at_rank = ranks.get(userRank, 0)
            exps_with_nums.append((experiment, num_answers_at_rank))
        available_experiments = []
        last_num = None
        for exp, num in sorted(exps_with_nums, key=lambda x: x[-1]):
            if last_num is None:
                available_experiments.append(exp)
            else:
                if last_num == num:
                    available_experiments.append(exp)

            # this line shouldn't be here it should be the part of both (if last_num) statements
            last_num = num
        # select from the available experiments at random
        selected = choice(available_experiments)
        return selected

    def getAllowedExperimentLanguages(self,userAllLanguages):
        """
        get allowed experiments languages
        """

        user_languages= [x.language_code for x in userAllLanguages]
        allowed_languages =[]
        # if user knows ru allow bg and uk
        if 'ru' in user_languages:

            if 'ru' in allowed_languages:
                allowed_languages.remove('ru')

            allowed_languages.append('bg')
            allowed_languages.append('uk')
        # if user knows bg allow ru and uk
        elif 'bg' in user_languages:
            if 'bg' in allowed_languages:
                allowed_languages.remove('bg')
            allowed_languages.append('ru')
            allowed_languages.append('uk')
        # if user knows cs allow pl
        elif 'cs' in user_languages:
            if 'cs' in allowed_languages:
                allowed_languages.remove('cs')
            allowed_languages.append('pl')
        # if user knows pl allow cs
        elif 'pl' in user_languages:
            if 'pl' in allowed_languages:
                allowed_languages.remove('pl')
            allowed_languages.append('cs')

        return allowed_languages


class InspectExperimentsGridView(BaseDatatableView):
    """
    Grid view for inspecting available Experiments.
    """
    model = Experiment

    # define the columns that will be returned
    columns = ['experiment_name', 'is_active', 'priority', 'user_prerequisites', 'number_of_questions',
               'number of answers', 'created_on', 'details', 'users', 'stimuli_file', 'folder_name']
    order_columns = ['experiment_name', 'is_active', 'priority', 'user_prerequisites', '', '', 'created_on', '', '', 'stimuli_file']

    max_display_length = 20

    def get_initial_queryset(self):
        # get initial data
        # return Experiment.objects.all()
        return Experiment.objects.exclude(experiment_name__exact='').exclude(experiment_name__isnull=True)

    def render_column(self, item, column):

        # native_lang = self.request.GET.get(u'native_lang[value]', None)
        # print(native_lang)
        # make activation status into a checkbox
        if column == 'is_active':
            if item.is_active:
                return '<input type="checkbox" onclick="changeActivationStatus({}, true)" '.format(
                    item.id) + " checked >"
            else:
                return '<input type="checkbox" onclick="changeActivationStatus({}, false)" '.format(item.id) + " >"
        elif column == 'number_of_questions':
            num_questions = item.experiment_questions.count()
            return str(num_questions)
        elif column == 'number of answers':
            ranks = Experiment.objects.get(pk=item.id).getNumbersOfCollectedAnswers()
            out = []
            for rank, number in sorted(ranks.items(), key=lambda x: x[0]):
                out.append(str(number) + "@" + str(rank + 1))
            if out:
                return str(sum(ranks.values())) + " (" + " + ".join(out) + ")"
            else:
                return str(sum(ranks.values()))
        elif column == 'user_prerequisites':
            outstr = []
            for preq in item.user_prerequisites.select_subclasses():
                outstr.append(str(preq))
            return ", ".join(outstr)
        elif column == "details":
            experiments = Experiment.objects.filter(id=item.id).select_subclasses()
            if len(experiments) > 0:
                experiment = experiments[0]
            experimentName = experiment.getExperimentNameForUser()
            if "Gap Filling" in experimentName:
                return 'download answers (<a onclick="redirectTo(\'admin/ExportUserAnswersCSV/' + str(
                    item.id) + '/\');">csv</a> |<a onclick="redirectTo(\'admin/ExportQuestionReadingTimeCSV/' + str(
                    item.id) + '/\');">reading time csv</a> | <a onclick="redirectTo(\'admin/ExportUserAnswersXLSX/' + str(
                    item.id) + '/\');">xlsx</a>)'

            return 'download answers (<a onclick="redirectTo(\'admin/ExportUserAnswersCSV/' + str(
                item.id) + '/\');">csv</a> | <a onclick="redirectTo(\'admin/ExportUserAnswersXLSX/' + str(
                item.id) + '/\');">xlsx</a>)'
        elif column == "users":
            return 'download users (<a onclick="redirectTo(\'admin/ExportParticipatingUsersCSV/' + str(
                item.id) + '/\');">csv</a> | <a onclick="redirectTo(\'admin/ExportParticipatingUsersXLSX/' + str(
                item.id) + '/\');">xlsx</a>)'
            # return '<a onclick="redirectTo(\'admin/ExportParticipatingUsers/' + str(item.id) + '/\');">download users</a>'
        elif column == 'priority':
            return '<input id="priority_input_' + str(
                item.id) + '" style="width:50px" type="number" step="1" min="0" max="100" value="' + str(
                item.priority) + '" > <a onclick="changePriority(' + str(item.id) + ')">save</a>'
        elif column == 'created_on':
            # return item.created_on.strftime("%Y-%m-%d %H:%M")
            return item.created_on.strftime("%d-%m-%Y at %H:%M")
        elif column == 'stimuli_file':
            if item.stimuli_file != None and item.folder_name != None:
                return '<a onclick="redirectTo(\'admin/download-file/' + str(item.folder_name) + '/' + str(item.stimuli_file) + '/\');">' + str(item.stimuli_file) + '</a>'
                
            else:
                return ''
        else:
            return super(InspectExperimentsGridView, self).render_column(item, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        # native_lang = self.request.GET.get(u'native_lang[value]', None)
        # print(native_lang)
        if search:
            qs = qs.filter(experiment_name__icontains=search.strip())
            return qs
        # if native_lang:
        # qs = qs.filter(experiment_name__icontains=native_lang.strip())
        # return qs

        return qs


class ExperimentDetailView(View):
    def get(self, request, exp):
        try:
            exp = Experiment.objects.get(pk=exp)
            questions = []
            for Q in exp.experiment_questions.select_subclasses():
                num_correct, num_incorrect = Q.getNumbersOfAnswers()
                T = num_correct + num_incorrect
                PC = 100.0 * num_correct / T
                PI = 100.0 * num_incorrect / T
                questions.append((Q.id, str(Q), T, num_correct, num_incorrect, PC, PI))
            return render(request, 'adminpanel/ExperimentDetails.html',
                          {"exp": exp, "questions": questions, "answers": exp.getNumbersOfCollectedAnswers()})
        except Exception as e:
            return HttpResponse(status=500)

    def post(self, request):
        return False


class InspectExperimentsView(View):
    """
        View to allow inspection of all available experiments.
    """

    def get(self, request):
        """ GET handler. """
        try:
            return render(request, 'adminpanel/InspectExperiments.html')

        except Exception as e:
            return HttpResponse(status=500)
            # return HttpResponse('Error in Inspect Experiments view. Please report this error to the admins: '+str(e))

    def post(self, request):
        """ POST handler. """
        if request.is_ajax():
            try:
                requestType = request.POST['type']
                # activate an experiment
                if requestType == '1':
                    experiment_id = int(request.POST['experiment_id'])
                    E = Experiment.objects.get(pk=experiment_id)
                    E.is_active = True
                    E.save()
                    return HttpResponse(True)
                # deactivate an experiment
                if requestType == '2':
                    experiment_id = int(request.POST['experiment_id'])
                    E = Experiment.objects.get(pk=experiment_id)
                    E.is_active = False
                    E.save()
                    return HttpResponse(True)

                # change experiment priority
                if requestType == '3':
                    experiment_id = int(request.POST['experiment_id'])
                    new_priority = int(request.POST['new_priority'])
                    E = Experiment.objects.get(pk=experiment_id)
                    E.priority = new_priority
                    E.save()
                    return HttpResponse(True)

                return HttpResponse("Unknown request type.")
            except Exception as e:
                return HttpResponse(status=500)
        else:
            return HttpResponse(status=500)


class ShowExperimentResultsView(View):
    def get(self, request):
        if not LAST_COMPLETED_EXPERIMENT in request.session or not LAST_COMPLETED_PARTICIPATION in request.session:
            return HttpResponseRedirect("/SelectExperiment")

        params = dict()
        params["pageConstants"] = constants.FreeTranslationCompletionPageConstants
        params["commonConstants"] = constants.CommonConstants
        params["gap_filling"] = False
        experimentResults = {}

        try:
            # get the completed experiment's name for the view
            experiments = Experiment.objects.filter(id=request.session[LAST_COMPLETED_EXPERIMENT]).select_subclasses()
            if len(experiments) > 0:
                experiment = experiments[0]
            experiment_name = experiment.getExperimentNameForUser()
            # get the completion statistics from the participation
            participation = ExperimentParticipation.objects.get(id=request.session[LAST_COMPLETED_PARTICIPATION])

            if 'Phrase Translation' in experiment_name:
                params["pageConstants"] = constants.PhraseTranslationCompletionPageConstants
            if 'Gap Filling' in experiment_name:
                params["pageConstants"] = constants.GapFillingCompletionPageConstants
                params["gap_filling"] = True

                total, correct, incorrect, not_answered, total_time_ms, total_gaps, correct_gaps, incorrect_gaps = participation.getResultsForGapFilling()
                experimentResults["total_gaps"] = total_gaps
                experimentResults["correct_gaps"] = correct_gaps
                experimentResults["incorrect_gaps"] = incorrect_gaps
            else:
                total, correct, incorrect, not_answered, total_time_ms = participation.getResults()

            total_time_min = total_time_ms / 60000
            avg_time_secs = total_time_ms / total / 1000

            userInfo = UserInfo.objects.get(user=request.user)

            prolific_user = False
            if userInfo.prolific_id != '' and userInfo.prolific_id != None:
                prolific_user = True

            num_available = len(Experiment.getExperimentsAvailableToUser(userInfo))

            medal, completedOn, fromLanguage, toLanguage = ShowExperimentResultsView.getExperimentMedal(
                participation.experiment.id, float(float(correct) / float(total)), participation.completed_on)

            experimentResults['total_questions'] = total
            experimentResults['total_correct'] = correct
            experimentResults['total_time_in_minutes'] = round(total_time_min, 2)
            experimentResults['avg_time'] = round(avg_time_secs, 2)
            params['experimentResults'] = experimentResults
            params['moreExperimentsAvailable'] = num_available > 0
            params['medal'] = medal
            params['date'] = completedOn
            params['fromLanguage'] = fromLanguage
            params['toLanguage'] = toLanguage
            params['prolific_user'] = prolific_user

            return render(request, 'ExperimentCompletion.html', params)
        except Exception as e:
            # return HttpResponse(status=500)
            return HttpResponse("Error: " + str(e))

    def post(self, request):
        return HttpResponse("POST")

    @staticmethod
    def getExperimentMedal(experimentId, correct_perc, completed_on):
        competedOn = completed_on
        competedOn = competedOn.strftime('%a, %x')
        ex = Experiment.objects.filter(pk=experimentId).select_subclasses()[0]
        # ex = ep.experiment
        fromLanguage = _("XL")
        if ex.foreign_language != "XL":
            fromLanguage = str(ex.foreign_language.language_code)
        toLanguage = str(ex.native_language.language_code)
        medal = "bronze"
        if correct_perc >= 0.80:
            medal = "gold"
        elif correct_perc >= 0.60:
            medal = "silver"

        return medal, competedOn, fromLanguage, toLanguage



class UploadExperimentMedalView(View):
    def get(self, request):
        form = UploadMedalForm()
        return render(request, 'adminpanel/UploadMedal.html', {"form": form})

    def post(self, request):
        # return HttpResponse("POST"+str(request))
        try:
            form = UploadMedalForm(request.POST, request.FILES)
            if form.is_valid():
                form = form.cleaned_data
                exp = form["experiment_id"]
                medal_file = request.FILES['medal']
                medalFileName = medal_file.name
                fs = FileSystemStorage(location=settings.EXPERIMENT_MEDAL_FOLDER,
                                       base_url=settings.EXPERIMENT_MEDAL_URL)
                medal_filename = fs.save(medalFileName, medal_file)
                had_medal = not exp.user_medal is None
                exp.user_medal = medal_filename
                exp.save()

                if had_medal:
                    msg = "Medal replaced for experiment"

                else:
                    msg = "Medal added for experiment"

                msg += " " + exp.experiment_name

                form = UploadMedalForm()
                return render(request, 'adminpanel/UploadMedal.html', {"form": form, "msg": msg})

            return HttpResponse("form invalid")

        except Exception as e:
            return HttpResponse(str(e))  # status=500)
