from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.http import HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
# from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
import locale
from django.core.files.storage import default_storage

from Common import constants
from ExperimentBasics.models import *
from ExperimentBasics.forms import *
from ExperimentBasics.definitions import *

from Users.models import *
from Users.enums import *
from FreeTranslationExperiment.models import *

from random import choice

from FreeTranslationExperiment.forms import UploadFreeTranslationQuestionAudioForm, UpdateFreeTranslationQuestionAudioForm
from django.conf import settings


import logging
logger = logging.getLogger("ayan")


class UserExperimentOverviewView(View):
    def get(self, request):
        try:
            if UserInfo.objects.filter(user=request.user).exists():
                userInfo = UserInfo.objects.get(user=request.user)

                cleared = userInfo.clearedForExperiments()
                try_again_button_text = 'Try Again!'

                # fetch completed experiment with correct percentage answers
                # AYAN
                exp_with_percentage, list_plot, num_experiments = UserExperimentOverviewView.getExperimentWithMedals(userInfo)
                retry_stat_dict = {}

                free_trans_exp_list = FreeTranslationExperiment.objects.values_list('experiment_ptr_id', flat=True)
                # print(free_trans_exp_list)
                for e in exp_with_percentage:
                    print('experiment no: ' + str(e[9]))
                    retry_list = RetryExperimentParticipation.objects.filter(experiment_id=e[9], user=userInfo, is_active=True).order_by('retry_count')
                    
                    retry_dict = {}
                    for list in retry_list:
                        is_audio = False
                        try:
                            stat_obj = RetryExperimentStatistics.objects.get(retry_participation=list)
                            corr = stat_obj.total_correct
                            if stat_obj.retry_is_audio_experiment:
                                is_audio = True

                        except:
                            corr = 0

                        acc = str(round((corr / e[2]) * 100,2))
                        print(acc)
                        atmp = list.retry_count + 1

                        if is_audio:
                            acc += '% (Audio)'

                        temp_dict = {'Correct' : corr, 'Accuracy' : acc}

                        retry_dict.update({list.retry_count + 1 : temp_dict})

                    retry_stat_dict.update({e[9] : retry_dict})

                    for key, value in retry_stat_dict[e[9]].items():
                        print(key, value)


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
                            (ex.id, experimentName, toFromLanguageTable, fromLanguage, toLanguage, ex.is_audio_experiment, ex.text_experiment, ex.audio_experiment))
                    except Exception as e:
                        pass
                # AYAN
                return render(request, "ExperimentOverview.html", {'completed_experiments': exp_with_percentage,
                                                                   'available_experiments': available_experiments,
                                                                   "cleared_for_experiments": cleared,
                                                                   'list_plot': list_plot,
                                                                   'num_exp': num_experiments,
                                                                   'retry_stat_dict': retry_stat_dict,
                                                                   'try_again_button_text': try_again_button_text,
                                                                   'free_trans_exp_list': free_trans_exp_list})

            # redirect to user profile page if user profile didn't exist or user isn't cleared for experiments
            return HttpResponseRedirect("/UserInfoForm")
        except Exception as e:
            # return HttpResponse(status=500)
            return HttpResponse('Error in Experiment Overview. Please report this error to the admins: ' + str(e))


    def post(self, request):

        if 'audio_btn' in request.POST:
            try:

                # Assign experiment status for completed experiment retry
                request.session['EXPERIMENT_STATUS'] = 'complete'
                request.session[RETRY_EXPERIMENT_STATUS] = request.POST['status']
                print(request.session['EXPERIMENT_STATUS'])
            
                exp_id = int(str(request.POST["hdnId"]).strip())
                # experiment = Experiment.objects.get(id=exp_id, is_active__exact=True)
                experiment = Experiment.objects.filter(id=exp_id, is_active__exact=True)

                request.session[RETRY_ASSIGNED_EXPERIMENT] = exp_id

                # For Audio
                request.session[RETRY_AUDIO_EXPERIMENT] = 'audio'
                extra_message = 'Be sure the speaker is turned on. Please use Google Chrome Browser!!'

                print(request.session[RETRY_AUDIO_EXPERIMENT])

                if RETRY_CURRENT_PARTICIPATION in request.session:
                    del request.session[RETRY_CURRENT_PARTICIPATION]

                return render(request, 'RetryExperimentWelcome.html', {'strings': experiment.getWelcomeTemplateStrings(),
                                                                  'ExperimentWelcomeScreenConstants': ExperimentWelcomeScreenConstants,
                                                                  'extra_message': extra_message})

            except Exception as ex:
                print("Exception")
                return HttpResponseRedirect('/RetrySelectExperiment')

        if 'status' in request.POST:
            try:

                if RETRY_AUDIO_EXPERIMENT in request.session:
                        del request.session[RETRY_AUDIO_EXPERIMENT]

                # Assign experiment status for completed experiment retry
                request.session['EXPERIMENT_STATUS'] = 'complete'
                request.session[RETRY_EXPERIMENT_STATUS] = request.POST['status']
                print(request.session['EXPERIMENT_STATUS'])
            
                exp_id = int(str(request.POST["hdnId"]).strip())
                experiment = Experiment.objects.get(id=exp_id, is_active__exact=True)
                # experiment = Experiment.objects.filter(id=exp_id).select_subclasses()[0]
                request.session[RETRY_ASSIGNED_EXPERIMENT] = exp_id
                print(request.session[RETRY_ASSIGNED_EXPERIMENT])

                if RETRY_CURRENT_PARTICIPATION in request.session:
                    del request.session[RETRY_CURRENT_PARTICIPATION]

                return render(request, 'RetryExperimentWelcome.html', {'strings': experiment.getWelcomeTemplateStrings(),
                                                                  'ExperimentWelcomeScreenConstants': ExperimentWelcomeScreenConstants})

            except Exception as ex:
                print("Exception")
                return HttpResponseRedirect('/RetrySelectExperiment')

        else:
            try:
                
                # if 'status' in request.POST:
                #     print(request.POST['status'])
                #     # Assign experiment status for completed experiment retry
                #     request.session['EXPERIMENT_STATUS'] = 'complete'
                #     print(request.session['EXPERIMENT_STATUS'])

                if RETRY_AUDIO_EXPERIMENT in request.session:
                    del request.session[RETRY_AUDIO_EXPERIMENT]



                exp_id = int(str(request.POST["hdnId"]).strip())
                # experiment = Experiment.objects.filter(id=exp_id).select_subclasses()[0]
                experiment = Experiment.objects.get(id=exp_id, is_active__exact=True)
                request.session[ASSIGNED_EXPERIMENT] = exp_id
                

                exp_type = request.POST["exp_type"]
                request.session[SELECTED_EXPERIMENT_TYPE] = exp_type
                print("test", request.session[SELECTED_EXPERIMENT_TYPE])

                if CURRENT_PARTICIPATION in request.session:
                    del request.session[CURRENT_PARTICIPATION]

                return render(request, 'ExperimentWelcome.html', {'strings': experiment.getWelcomeTemplateStrings(),
                                                                  'ExperimentWelcomeScreenConstants': ExperimentWelcomeScreenConstants})
            except Exception as ex:
                print(ex)
                return HttpResponseRedirect('/SelectExperiment')
                # return HttpResponse("ERROR:"+str(ex))


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
                (experimentName, toFromLanguageTable, num_total, num_correct, correct_perc, fromLanguage, toLanguage, medal, competedOn, ex.id, ex.is_audio_experiment, ex.is_active, ex.text_experiment, ex.audio_experiment))
        # AYAN
        return experiments, list_for_plot, len(list_for_plot)


    # Hasan for experiment order   
    @staticmethod
    def getExperimentWithMedalsNew(userInfo):
        experiments = []
        # AYAN
        # Maintain list of data-points to generate the plot later
        list_for_plot = []
        for ep in ExperimentParticipation.objects.filter(user=userInfo, completed_on__isnull=False).order_by("completed_on"):
            num_total, num_correct, num_incorrect, num_not_answered, total_time = ep.getResults()
            correct_perc = float(num_correct) / float(num_total)
            competedOn = ep.completed_on
            competedOn = competedOn.strftime('%c')
            # Hasan
            experimentTitle = ep.experiment.experiment_name
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
                (experimentName, toFromLanguageTable, num_total, num_correct, correct_perc, fromLanguage, toLanguage, medal, competedOn, experimentTitle))
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


class RetrySelectExperimentView(View):

    def get(self, request):

        try:

            if RETRY_ASSIGNED_EXPERIMENT in request.session:
                experiments = Experiment.objects.filter(id=request.session[RETRY_ASSIGNED_EXPERIMENT]).select_subclasses()
                print(request.session[RETRY_EXPERIMENT_STATUS])
                if len(experiments) > 0:
                    selected = experiments[0]

                else:
                    del request.session[RETRY_ASSIGNED_EXPERIMENT]
                    return HttpResponseRedirect("/Experiments")

                # return HttpResponse("Already had an experiment assigned: "+str(request.session[ASSIGNED_EXPERIMENT]))
                return render(request, 'RetryExperimentWelcome.html', {'strings': selected.getWelcomeTemplateStrings(),
                                                                  'ExperimentWelcomeScreenConstants': ExperimentWelcomeScreenConstants,
                                                                  'enableJavaScriptMessage': EnableJavaScriptMessageConstants})
            else:
                return HttpResponseRedirect("/Experiments")


        except Exception as e:
            # return HttpResponse(status=500)
            return HttpResponse('Error in Select Experiment view. Please report this error to the admins: ' + str(e))


    def post(self, request):

        try:

            userInfo = UserInfo.objects.get(user=request.user)

            # if RETRY_EXPERIMENT_STATUS in request.session:

            experiments = Experiment.objects.filter(id=request.session[RETRY_ASSIGNED_EXPERIMENT]).select_subclasses()
            print(request.session[RETRY_ASSIGNED_EXPERIMENT])
            if len(experiments) > 0:
                experiment = experiments[0]
            else:
                del request.session[RETRY_ASSIGNED_EXPERIMENT]
                del request.session[RETRY_EXPERIMENT_STATUS]
                return HttpResponseRedirect("/Experiments")

            newParticipation = experiment.retryGetActiveParticipationForUser(userInfo)
            if newParticipation == 'MAXED':
                del request.session[RETRY_ASSIGNED_EXPERIMENT]
                del request.session[RETRY_EXPERIMENT_STATUS]
                return HttpResponseRedirect("/Experiments")

            print(newParticipation.retry_count)

            if RETRY_CURRENT_PARTICIPATION not in request.session:
                request.session[RETRY_CURRENT_PARTICIPATION] = newParticipation.id
            print(request.session[RETRY_CURRENT_PARTICIPATION])

            return HttpResponseRedirect("/RetryFreeTranslationQuestions")
      
        except:
            return HttpResponse('Error Faced. Please report:'+str(e))        




class SelectExperimentView(View):
    """ View that selects an experiment for a user if the user is not involved in an experiment already. """

    def get(self, request):
        print('Coming here..')
        logger.error("Get Select Experiment")

        # if 'EXPERIMENT_STATUS' in request.session:
        #     print('ok')
        #     return render(request, 'RetryExperimentWelcome.html')

        try:

            # if RETRY_ASSIGNED_EXPERIMENT in request.session:
            #     experiments = Experiment.objects.filter(id=request.session[RETRY_ASSIGNED_EXPERIMENT]).select_subclasses()
            #     print(request.session[RETRY_EXPERIMENT_STATUS])
            #     if len(experiments) > 0:
            #         selected = experiments[0]

            #     else:
            #         del request.session[RETRY_ASSIGNED_EXPERIMENT]
            #         return HttpResponseRedirect("/Experiments")

            #     # return HttpResponse("Already had an experiment assigned: "+str(request.session[ASSIGNED_EXPERIMENT]))
            #     return render(request, 'ExperimentWelcome.html', {'strings': selected.getWelcomeTemplateStrings(),
            #                                                       'ExperimentWelcomeScreenConstants': ExperimentWelcomeScreenConstants,
            #                                                       'enableJavaScriptMessage': EnableJavaScriptMessageConstants})


            # print(request.session[ASSIGNED_EXPERIMENT])
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
                logger.error("AYAN:Select Experiment Got user infor")
            else:
                userInfo = UserInfo()
                logger.error("AYAN:Select Experiment Empty user info")

            user_native_languages = [x.language_code for x in userInfo.getNativeLanguages()]
            user_all_languages = list(userInfo.getAllLanguages())

            preselected = []
            # for all active experiments, check if user fulfills prerequisites
            experiments = Experiment.objects.filter(is_active__exact=True).select_subclasses()
            user_rank = ExperimentParticipation.getUserRank(userInfo)
            last_priority = None
            if len(experiments) > 0:
                logger.error("AYAN: LEN EXP MORE THAN ZERO")
                logger.error("AYAN:USER LANGS"+str(user_native_languages)+str(user_all_languages))
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
                logger.error("AYAN: NO PRESELECTED")
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
        print("Coming here")


        userInfo = UserInfo.objects.get(user=request.user)


        # if RETRY_EXPERIMENT_STATUS in request.session:

        #     experiments = Experiment.objects.filter(id=request.session[RETRY_ASSIGNED_EXPERIMENT]).select_subclasses()
        #     print(request.session[RETRY_ASSIGNED_EXPERIMENT])
        #     if len(experiments) > 0:
        #         experiment = experiments[0]
        #     else:
        #         del request.session[RETRY_ASSIGNED_EXPERIMENT]
        #         return HttpResponseRedirect("/SelectExperiment")

        #     newParticipation = experiment.retryGetActiveParticipationForUser(userInfo)
        #     if newParticipation == 'MAXED':
        #         del request.session[RETRY_ASSIGNED_EXPERIMENT]
        #         return HttpResponseRedirect("/SelectExperiment")

        #     print(newParticipation.retry_count)

        #     if RETRY_CURRENT_PARTICIPATION not in request.session:
        #         request.session[RETRY_CURRENT_PARTICIPATION] = newParticipation.id
        #     print(request.session[RETRY_CURRENT_PARTICIPATION])

        #     return HttpResponseRedirect("/RetryFreeTranslationQuestions")
        #     # return HttpResponseRedirect("/Experiments")

        # else:
        experiments = Experiment.objects.filter(id=request.session[ASSIGNED_EXPERIMENT]).select_subclasses()
        if len(experiments) > 0:
            experiment = experiments[0]
        else:
            del request.session[ASSIGNED_EXPERIMENT]
            return HttpResponseRedirect("/SelectExperiment")

        if CURRENT_PARTICIPATION not in request.session:
            expType = request.session[SELECTED_EXPERIMENT_TYPE]
            participation = experiment.getActiveParticipationForUser(userInfo, expType)
            if participation.experiment_type != request.session[SELECTED_EXPERIMENT_TYPE]:
                request.session[SELECTED_EXPERIMENT_TYPE] = participation.experiment_type

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
        #print(script_code)
        logger.error("GetAvailableExp:"+str(script_code))

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
                #print(experiment.foreign_script, script_code)
                logger.error("GetAvailableExp: Exp ForeignScript is not None... ForeignScript, UsrScriptCode = "+str(experiment.foreign_script)+" "+str(script_code))
                if experiment.foreign_script not in script_code:
                    logger.error("GetAvailableExp: experiment_foregin_script not in user script_code. Continued")
                    print('continued')
                    continue

                foreign_lang_script = LanguageScriptRelation.objects.filter(language=foreign_lang)
                continue_flag = False
                for cs in foreign_lang_script:
                    logger.error("GetAvailableExp: Exp foreign script is not None... for cs in foreign_lang_script: "+str(cs.script.script_code)+" "+str(script_code))
                    if cs.script.script_code in script_code:
                        logger.error("GetAvailableExp: exp foreign script is not none... Set continue_flag")
                        continue_flag = True
                        continue

                if continue_flag is True:
                    continue
                    
            else:
                foreign_lang_script = LanguageScriptRelation.objects.filter(language=foreign_lang)
                continue_flag = True
                logger.error("GetAvailableExp: Exp foreign lang script is None")
                for sc in foreign_lang_script:
                    logger.error("GetAvailableExp: foreign lang script "+str(sc.script.script_code)+" "+str(script_code))
                    if sc.script.script_code in script_code:
                        logger.error("GetAvailableExp: exp foreign lang script is none... setting continue flag")
                        continue_flag = False
                        logger.error("GetAvailableExp: Exp foreign lang script is none... continue_flag " + str(continue_flag))

                if continue_flag is True:
                    logger.error("GetAvailableExp: Exp foreign lang script is none... continue_flag is True so...")
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
    columns = ['experiment_name', 'is_active', 'text_experiment', 'audio_experiment', 'priority', 'user_prerequisites', 'freetranslationexperiment__foreign_language__language_name','number_of_questions',
               'number of answers', 'created_on', 'details', 'users', 'stimuli_file', 'folder_name', 'is_audio_experiment']
    order_columns = ['experiment_name', 'is_active', 'text_experiment', 'audio_experiment' , 'priority', 'user_prerequisites', 'freetranslationexperiment__foreign_language__language_name', '', '', 'created_on', '', '', 'stimuli_file', '', '']


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

        elif column == 'text_experiment':
            if item.text_experiment:
                return '<input type="checkbox" onclick="changeTextStatus({}, true)" '.format(
                    item.id) + " checked >"
            else:
                return '<input type="checkbox" onclick="changeTextStatus({}, false)" '.format(item.id) + " >"

        elif column == 'audio_experiment':

            if item.is_audio_experiment:

                if item.audio_experiment:
                    return '<input type="checkbox" onclick="changeAudioStatus({}, true)" '.format(
                        item.id) + " checked >"
                else:
                    return '<input type="checkbox" onclick="changeAudioStatus({}, false)" '.format(item.id) + " >"
            else:
                return(str(item.audio_experiment))

            

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

        elif column == "freetranslationexperiment__foreign_language__language_name":
            experiments = Experiment.objects.filter(id=item.id).select_subclasses()
            return str(experiments[0].foreign_language)

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

                # activate Audio experiment
                if requestType == '4':
                    experiment_id = int(request.POST['experiment_id'])
                    E = Experiment.objects.get(pk=experiment_id)
                    E.audio_experiment = True
                    E.save()
                    return HttpResponse(True)
                # deactivate Audio experiment
                if requestType == '5':
                    experiment_id = int(request.POST['experiment_id'])
                    E = Experiment.objects.get(pk=experiment_id)
                    E.audio_experiment = False
                    E.save()
                    return HttpResponse(True)

                # activate Text experiment
                if requestType == '6':
                    experiment_id = int(request.POST['experiment_id'])
                    E = Experiment.objects.get(pk=experiment_id)
                    E.text_experiment = True
                    E.save()
                    return HttpResponse(True)
                # deactivate Text experiment
                if requestType == '7':
                    experiment_id = int(request.POST['experiment_id'])
                    E = Experiment.objects.get(pk=experiment_id)
                    E.text_experiment = False
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


# Added by Hasan
# Retry Experiment
class RetryShowExperimentResultsView(View):
    def get(self, request):
        if not RETRY_LAST_COMPLETED_EXPERIMENT in request.session or not RETRY_LAST_COMPLETED_PARTICIPATION in request.session:
            return HttpResponseRedirect("/SelectExperiment")

        params = dict()
        params["pageConstants"] = constants.FreeTranslationCompletionPageConstants
        params["commonConstants"] = constants.CommonConstants
        params["gap_filling"] = False
        experimentResults = {}

        try:
            # get the completed experiment's name for the view
            experiments = Experiment.objects.filter(id=request.session[RETRY_LAST_COMPLETED_EXPERIMENT]).select_subclasses()
            if len(experiments) > 0:
                experiment = experiments[0]
            experiment_name = experiment.getExperimentNameForUser()
            # get the completion statistics from the participation
            participation = RetryExperimentParticipation.objects.get(id=request.session[RETRY_LAST_COMPLETED_PARTICIPATION])

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

            medal, completedOn, fromLanguage, toLanguage = RetryShowExperimentResultsView.retryGetExperimentMedal(
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

            # creating RetryExperimentStatistics object to store data

            stat_obj = RetryExperimentStatistics()

            if RETRY_AUDIO_EXPERIMENT in request.session:
                stat_obj.retry_is_audio_experiment = True
                del request.session[RETRY_AUDIO_EXPERIMENT]
            
            stat_obj.retry_participation = participation
            stat_obj.total_question = total
            stat_obj.total_correct = correct
            stat_obj.total_time_in_min = round(total_time_min, 2)
            stat_obj.avg_time_in_sec = round(avg_time_secs, 2)
            stat_obj.save()

            return render(request, 'RetryExperimentCompletion.html', params)
        except Exception as e:
            # return HttpResponse(status=500)
            return HttpResponse("Error: " + str(e))

    def post(self, request):
        return HttpResponse("POST")

    @staticmethod
    def retryGetExperimentMedal(experimentId, correct_perc, completed_on):
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



def post_update_question_audio(request, exp_id, ques_id):
    data = {}


    instance = get_object_or_404(FreeTranslationQuestion, free_translation_question_id = ques_id)
    form = UploadFreeTranslationQuestionAudioForm(request.POST or None, request.FILES or None, instance=instance)
    # print("Created")
    if request.method == "POST":
        if form.is_valid():
            print("Created on")
            instance = form.save(commit = False)
        
            instance.has_audio = True

            instance.save()
            redirect_path = '/admin/FreeTranslationQuestionAnswerList/' + str(exp_id) + '/'
            print(redirect_path)
            return HttpResponseRedirect(redirect_path)

    data['form'] = form
    return render(request, 'adminpanel/AddAudio.html', data)


def post_edit_question_audio(request, exp_id, ques_id):
    data = {}

    instance = get_object_or_404(FreeTranslationQuestion, free_translation_question_id = ques_id)
    form = UpdateFreeTranslationQuestionAudioForm(request.POST or None, request.FILES or None, instance=instance)

    if request.method == "POST":
        if form.is_valid():
            instance = form.save(commit = False)

            if instance.has_audio == False:
                instance.audio_file = None
                experiment = get_object_or_404(Experiment, id=exp_id)
                experiment.is_audio_experiment = False
                experiment.save()

            instance.save()
            redirect_path = '/admin/FreeTranslationQuestionAnswerList/' + str(exp_id) + '/'
            
            return HttpResponseRedirect(redirect_path)

    data['form'] = form
    return render(request, 'adminpanel/AddAudio.html', data)




# def post_update_question_audio(request, exp_id):

#     data = {}
   
#     experiment = get_object_or_404(Experiment, id=exp_id)

#     questions = experiment.experiment_questions.all().distinct('id')
#     # print(questions.select_subclasses()[0].foreign_word)
#     id_list = []
#     foreign_word_list = []
#     has_audio_list = []
#     audio_path_list = []

#     for i in range(len(questions)):
#         name = questions.select_subclasses()[i]
#         print(name, name.foreign_word, name.free_translation_question_id, i)

#         id_list.append(name.free_translation_question_id)
#         foreign_word_list.append(name.foreign_word)
#         has_audio_list.append(name.has_audio)
#         audio_path_list.append(name.audio_path)

#         next_audio = False
#         if name.has_audio != True and next_audio == False:

#             instance = name
#             # to_upload_foreign_word = name.foreign_word
#             # data['to_upload_question_id'] = to_upload_question_id
#             # data['to_upload_foreign_word']= to_upload_foreign_word

#             next_audio = True

#     questions_list = zip(id_list, foreign_word_list, has_audio_list, audio_path_list)
        

#     form = UploadFreeTranslationQuestionAudioForm(request.POST or None, request.FILES or None, instance=instance)
#     print("Created")
#     if form.is_valid():
#         print("Created")
#         instance = form.save(commit = False)
#         instance.save()

#     data['questions_list'] = questions_list
#     data['form'] = form
#     data['exp_id'] = exp_id

#     return render(request, 'adminpanel/AddAudio.html', data)




class ExperimentQuestionAudioView(View):

    def get(self, request):

        data = {}

        # experiment_list = Experiment.objects.filter(experiment_name__icontains='free')
        experiment_list = FreeTranslationExperiment.objects.all()
        data['experiment_list'] = experiment_list

        return render(request, 'adminpanel/QuestionsAudio.html', data)


    def post(self, request):


        if request.is_ajax():
            # exp_id = request.POST.get('exp_id')
            # print(formdata)
            data = "working"
            return JsonResponse(data, safe = False)


        experiment_id = request.POST['experiment_id']

        return post_update_question_audio(request, experiment_id)

        # data = {}

        # experiment_list = Experiment.objects.all()
        # data['experiment_list'] = experiment_list




        # try:


        #     if 'question_id' in request.POST:

        #         FTQuestion = FreeTranslationQuestion.objects.get(free_translation_question_id = request.POST['question_id'])
        #         print("working 1")
        #         FTQuestion.audio_file = request.FILES['audio_file']
        #         print("worming 2")
        #         FTQuestion.has_audio = True
        #         FTQuestion.save()
        #         print("Working 3")
        #         data['message'] = "Audion Saved for id: " + str(FreeTranslationQuestion.free_translation_question_id)

        #     experiment = Experiment.objects.get(id=experiment_id)
        #     print(experiment_id)
        #     questions = experiment.experiment_questions.all().distinct('id')
        #     # print(questions.select_subclasses()[0].foreign_word)
        #     id_list = []
        #     foreign_word_list = []
        #     has_audio_list = []
        #     audio_path_list = []

        #     next_audio = False

        #     for i in range(len(questions)):
        #         name = questions.select_subclasses()[i]
        #         print(name, name.foreign_word, name.free_translation_question_id, i, name.audio_file)

        #         id_list.append(name.free_translation_question_id)
        #         foreign_word_list.append(name.foreign_word)
        #         has_audio_list.append(name.has_audio)
        #         audio_path_list.append(name.audio_file.name)

        #         if name.has_audio != True and next_audio == False:

        #             to_upload_question_id = name.free_translation_question_id
        #             to_upload_foreign_word = name.foreign_word
        #             data['to_upload_question_id'] = to_upload_question_id
        #             data['to_upload_foreign_word']= to_upload_foreign_word

        #             next_audio = True


        #     questions_list = zip(id_list, foreign_word_list, has_audio_list, audio_path_list)

        #     print(sorted(id_list))
        #     data['questions_list'] = questions_list
        # except:
        #     pass

        # return render(request, 'adminpanel/QuestionsAudio.html', data)



class FreeTranslationQuestionAnswerListView(View):

    def get(self, request, exp_id):

        data = {}

        if exp_id == '0':
            experiment_id = request.GET['experiment_id']
        else:
            experiment_id = exp_id
            
        
        try:
            experiment = Experiment.objects.get(id=experiment_id)
            
            questions = experiment.experiment_questions.all().distinct('id')
            data['total_question'] = questions.count()
            # print(questions.select_subclasses()[0].foreign_word)
            id_list = []
            foreign_word_list = []
            has_audio_list = []
            audio_path_list = []

            next_audio = False
            has_not_audio_count = 0

            for i in range(len(questions)):
                name = questions.select_subclasses()[i]
                print(name, name.foreign_word, name.free_translation_question_id, i, name.audio_file)

                id_list.append(name.free_translation_question_id)
                foreign_word_list.append(name.foreign_word)
                has_audio_list.append(name.has_audio)
                audio_path_list.append(name.audio_file)
                # print(name.audio_file.url)

                if name.has_audio != True:
                    has_not_audio_count += 1

                if name.has_audio != True and next_audio == False:

                    form = UploadFreeTranslationQuestionAudioForm(instance=name)
                    data['form'] = form
                    data['form_ques_id'] = name.free_translation_question_id

                    next_audio = True


            if next_audio == False:
                experiment.is_audio_experiment = True
                experiment.save()
                data['message'] = 'Audio for All questions for this experiment has been uploaded'

            questions_list = zip(id_list, foreign_word_list, has_audio_list, audio_path_list)

            print(sorted(id_list))
            data['experiment'] = experiment

            data['questions_list'] = questions_list
            data['total_question_count'] = len(questions)
            data['has_not_audio_count'] = has_not_audio_count
        except:
            pass


        return render(request, 'adminpanel/FreeTranslationQuestionAnswerList.html', data)


    def post(self, request, exp_id):

        data = {}


        instance = get_object_or_404(FreeTranslationQuestion, free_translation_question_id = exp_id)
        form = UploadFreeTranslationQuestionAudioForm(request.POST or None, request.FILES or None, instance=instance)
        print("Created")
        if request.method == "POST":
            if form.is_valid():
                print("Created on")
                instance = form.save(commit = False)
                if instance.has_audio == False:
                    instance.audio_file = None

                instance.save()
                return HttpResponseRedirect('/admin/QuestionsAudio')

        data['form'] = form
        return render(request, 'adminpanel/AddAudio.html', data)

