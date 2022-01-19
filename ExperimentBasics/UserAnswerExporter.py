from collections import defaultdict
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.utils.encoding import smart_str
from Common.common_utils import removeDiacritics
from django.conf import *
import csv
import json
import re
from GapFillingExperiment.models import *
from MixedLanguagesGapFillingExperiment.models import *
from ExperimentBasics.models import *
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper
from django.utils.encoding import force_text
from FreeTranslationWithContextExperiment.models import *


def getHesitationAndTypingTimeFromResponseChanges(json_data):
    """
    get hesitation and typing time from response changes(i.e list of time stamps)
    """
    if json_data != None:
        changes = json.loads(json_data)
    else:
        changes = []

    if len(changes) >= 2:
        hesitation_time = float(changes[1][1]) - float(changes[0][1])
    else:
        # hesitation_time = float("inf")
        hesitation_time = 0

    if len(changes) >= 3:
        time_spent_typing = float(changes[-1][1]) - float(changes[1][1])
    
    else:
        # time_spent_typing = float("inf")
        time_spent_typing = 0

    if len(changes) >= 3:
        final_hesitation_time = float(changes[-1][1]) - float(changes[-2][1])
    
    else:
        final_hesitation_time = 0
    
    return hesitation_time, time_spent_typing, final_hesitation_time


def getHesitationAndTypingTimeFromResponseChangesForGapFilling(json_data,totalGaps):
    """
    get hesitation and typing time from response changes(i.e list of time stamps)
    """
    list_of_times =[]

    try:
        if json_data != None:
            changes = json.loads(json_data)
        else:
            changes = []
        previous_gap_final_time=0.0

        for g in range(totalGaps):

            ls = list(filter(lambda x: '_gap'+str(g) in x[0],changes))

            if len(ls)!=0:
                if len(ls) >= 2:
                    # if it is first input related to time i.e. initial timestamp
                    if g==0:
                        hesitation_time = float(ls[0][1]) - float(changes[0][1])
                    else:
                        hesitation_time = float(ls[0][1]) - float(previous_gap_final_time)
                else:
                    hesitation_time = 0

                if len(ls) >= 3:
                    time_spent_typing = float(ls[-1][1]) - float(ls[0][1])
                else:
                    time_spent_typing = 0

                if g!=totalGaps-1:
                    next_gap_time = list(filter(lambda x: '_gap'+str(g+1) in x[0],changes))
                    if len(ls) >= 3 and len(next_gap_time)>0:
                        final_hesitation_time = float(next_gap_time[0][1])-float(ls[-1][1])
                    else:
                        final_hesitation_time = 0
                else:
                    final_hesitation_time=0

                previous_gap_final_time = ls[-1][1]
            else:
                hesitation_time, time_spent_typing, final_hesitation_time=0.0,0.0,0.0

            list_of_times.append([hesitation_time, time_spent_typing, final_hesitation_time])
    except Exception as ex:
        print(str(ex))
    return list_of_times


def getReadingTimeFromWordsClick(json_data):
    """
    get reading time from words click time
    """
    if json_data != None:
        clicks = json.loads(json_data)
    else:
        clicks = []

    dict_of_times ={}

    for c in clicks:
        i = c[0].split('_')[1]
        # dict_of_times[int(i)]= c[0].split('_')[0]+'_'+str(c[1])
        dict_of_times[int(i)]= c[1]

    return dict_of_times


def makeUserAnswersCSVFileForExperiment(exp_id, is_audio=False):
    try:
        E = Experiment.objects.filter(pk=exp_id).select_subclasses()[0]
        if not is_audio:
            Fname = EXPERIMENT_EXPORT_FILE_FOLDER+E.experiment_name.replace(" ", "_")+"_UserAnswers.csv"
        else:
            Fname = EXPERIMENT_EXPORT_FILE_FOLDER+E.experiment_name.replace(" ", "_")+"_AudioUserAnswers.csv"

        #with open(Fname, "w", encoding="utf-8") as f:
            #CW = csv.writer(f)

        headers = []
        if not is_audio:
            headers.append("Question ID")
            headers.append("Question Native Language")
            headers.append("Question Stimulus Language")
            headers.append("Question Stimulus")
        else:
            headers.append("Audio Question ID")
            headers.append("Audio Question Native Language")
            headers.append("Audio Question Stimulus Language")
            headers.append("Audio Question Stimulus")
        
        headers.append("Given Answer")
        headers.append("Given Answer Absolutely Correct")
        headers.append("Given Answer Correct Up To Normalization")
        headers.append("Given Answer Incorrect")
        headers.append("No Answer Given")
        headers.append("Total Time Spent (ms)")
        headers.append("Initial Hesitation Time (ms)")
        headers.append("Typing Time (ms)")
        headers.append("Final Hesitation Time (ms)")
        headers.append("Date/Time Of Answer")
        headers.append("Participation Start Date")
        headers.append("Participation Finish Date")
        headers.append("Participation Rank")
        headers.append("User Account Name")
        # Removing due to privacy issues
        #headers.append("User Mail")
        headers.append("User Age")
        headers.append("User Gender")
        headers.append("User Living Location")
        headers.append("User Living Duration (years)")
        headers.append("User Knows Stimulus Language")

        #Added by AYAN
        headers.append("Number of Languages User Knows")
        headers.append("Languages With >= B2 Reading Level")
        headers.append("Number of Languages With >= B2 Reading Level")


        data = []
        seen_langs = set([])
        seen_countries = set([])

        language_skills = defaultdict(lambda: defaultdict(lambda: None )) # user -> language -> (reading, writing, listening, speaking, native, used_at_home, exposure_duration_through_living, exposure_duration_through_learning, spoken_at_user_location)
        countries = defaultdict(lambda: defaultdict(lambda: [None,None])) # user -> country -> (living duration, education duration)
        user_answers = defaultdict(lambda: defaultdict(lambda: (None, None, None, None, None, None, None, None))) # user -> question ID -> given answer, abs correct yes/no, norm correct yes/no, total time, initial hesitation, typing time, submission hesitation
        #user_answers[EP.user.user.username][UA.answered_question.id] = given, abs_correct, norm_correct, incorrect, no_answer_given, time, initial_hesitation_time, typing_time, submission_hesitation_time, date/time of answer

        total_lang_weight = defaultdict(lambda: 0)
        total_country_weight = defaultdict(lambda: 0)

        #Added by AYAN
        num_languages_user = defaultdict(lambda:0)
        user_languages_b2_reading = defaultdict(lambda:[])

        if is_audio:
            list_EPs = ExperimentParticipation.objects.filter(experiment = exp_id, experiment_type="audio")
        else:
            list_EPs = ExperimentParticipation.objects.filter(experiment=exp_id, experiment_type="text")

        for EP in list_EPs: 
            if EP.completed_on is None:
                continue

            D = []
            D.append(EP.started_on)
            D.append(EP.completed_on)
            D.append(EP.getAnswerRank())
            D.append(EP.user.user.username)
            # Removing due to privacy issues.
            #D.append(EP.user.user.email)
            D.append(EP.user.age)
            D.append(EP.user.gender.code)
            D.append(EP.user.location.country_name)
            D.append(EP.user.location_living_duration)

            for skill in UserLanguageSkill.objects.filter(user=EP.user):
                seen_langs.add(skill.language.language_name)
                #print(skill.language,skill.reading_level,skill.writing_level,skill.listening_level,skill.speaking_level)
                #native = "NATIVE0"
                native = 0
                if skill.is_native_language:
                    #native = "NATIVE1"
                    native = 1

                #home = "HOME0"
                home = 0
                if skill.used_at_home:
                    #home = "HOME1"
                    home = 1

                #location_lang = "LOC0"
                location_lang = 0
                if skill.spoken_at_user_location:
                    #location_lang = "LOC1"
                    location_lang = 1

                if not skill.reading_level is None:
                    total_lang_weight[skill.language.language_name] += skill.reading_level+skill.writing_level+skill.listening_level+skill.speaking_level

                exp_living = 0
                if not skill.exposure_through_living is None:
                    exp_living = skill.exposure_through_living

                exp_learning = 0
                if not skill.exposure_through_learning is None:
                    exp_learning = skill.exposure_through_learning

                language_skills[EP.user.user.username][skill.language.language_name] = (skill.reading_level, skill.writing_level, skill.listening_level, skill.speaking_level, native, home, exp_living, exp_learning, location_lang)

                # Added by AYAN
                if not skill.reading_level is None:
                    if skill.reading_level >= 65:
                        user_languages_b2_reading[EP.user.user.username].append(skill.language.language_name)
            try:
                num_languages_user[EP.user.user.username] = len(language_skills[EP.user.user.username])
            except Exception as e:
                print(e)

            for stay in LivingCountryStay.objects.filter(user=EP.user):
                seen_countries.add(stay.country.country_name)
                countries[EP.user.user.username][stay.country.country_name][0] = stay.duration
                total_country_weight[stay.country.country_name] += stay.duration

            for stay in EducationCountryStay.objects.filter(user=EP.user):
                seen_countries.add(stay.country.country_name)
                countries[EP.user.user.username][stay.country.country_name][1] = stay.duration
                total_country_weight[stay.country.country_name] += stay.duration

            for UA in UserAnswer.objects.filter(experiment_participation=EP).select_subclasses():
                abs_correct = UA.isExactlyCorrectAnswer()
                if abs_correct:
                    abs_correct = 1
                else:
                    abs_correct = 0
                norm_correct = UA.isCorrectAnswer()
                if norm_correct:
                    norm_correct = 1
                else:
                    norm_correct = 0

                if isinstance(UA, FreeTranslationWithContextUserAnswer):
                    no_answer = UA.gap_answer == ""
                    native_word = UA.gap_answer.lower()
                else:
                    no_answer = UA.native_word == ""
                    native_word = UA.native_word

                if no_answer:
                    no_answer = 1
                else:
                    no_answer = 0

                incorrect = (not no_answer) and (not norm_correct)
                if incorrect:
                    incorrect = 1
                else:
                    incorrect = 0

                Q = Question.objects.filter(id=UA.answered_question.id).select_subclasses()[0]
                if isinstance(Q, FreeTranslationWithContextQuestion):
                    foreign_word = Q.sentence
                else:
                    foreign_word = Q.foreign_word
                # print(type(Q))
                aborted_prematurely = UA.answer_given is None
                answer_date = UA.answer_date
                time = UA.time_spent
                initial_hesitation_time, typing_time,submission_hesitation_time = getHesitationAndTypingTimeFromResponseChanges(UA.result_changes)
                answer_date = UA.answer_date
                #user_answers[EP.user.user.username][UA.answered_question.id] = given, abs_correct, norm_correct, time, initial_hesitation_time, typing_time, submission_hesitation_time, answer_date
                X = [UA.answered_question.id, str(E.native_language), str(E.foreign_language), foreign_word, native_word, abs_correct, norm_correct, incorrect, no_answer, time, initial_hesitation_time, typing_time, submission_hesitation_time, answer_date] + D

                data.append(X)

        # add additional headers
        additional_headers = []
        lang_order = []
        for lang,w in sorted(total_lang_weight.items(), reverse=True):
            lang_order.append(lang)
            additional_headers.append("User Has Language "+lang)
            additional_headers.append(lang+" Spoken Where User Lives")
            additional_headers.append(lang+" Native")
            additional_headers.append(lang+" Used At Home")
            additional_headers.append(lang+" Learning Duration (years)")
            additional_headers.append(lang+" Exposure Through Living (years)")
            additional_headers.append(lang+" Reading")
            additional_headers.append(lang+" Writing")
            additional_headers.append(lang+" Listening")
            additional_headers.append(lang+" Speaking")

        country_order = []
        for country,w in sorted(total_country_weight.items(), reverse=True):
            country_order.append(country)
            additional_headers.append("Lived In "+country+" (years)")
            additional_headers.append("Went To School In "+country+" (years)")

        headers = headers + additional_headers

        #CW.writerow(headers)
        yield headers
        
        for d in data:
            U = d[17]

            X = language_skills[U][E.foreign_language.language_name]
            if X is None:
                #d.append("STIMLANG0")
                d.append(0)

            else:
                #d.append("STIMLANG1")
                d.append(1)

            #Added by AYAN
            d.append(num_languages_user[U])
            d.append(','.join(user_languages_b2_reading[U]))
            d.append(len(user_languages_b2_reading[U]))

            for lang in lang_order:
                X = language_skills[U][lang]

                if X is None:
                    #d.append("HASLANG0")
                    d.append(0)

                else:
                    #d.append("HASLANG1")
                    d.append(1)
                #print(U,lang,X)
                if not X is None:
                    #"""
                    R, W, L, S, N, H, LIV, LEARN, LOC = X
        #language_skills = defaultdict(lambda: defaultdict(lambda: None )) # user -> language -> (reading, writing, listening, speaking, native, used_at_home, exposure_duration_through_living, exposure_duration_through_learning, spoken_at_user_location)
                    #d.append("LOC"+str(LOC))
                    d.append(LOC)
                    #d.append("NAT"+str(N))
                    d.append(N)
                    #d.append("HOME"+str(H))
                    d.append(H)
                    #d.append("LEARN"+str(LEARN))
                    d.append(LEARN)
                    #d.append("LIV"+str(LIV))
                    d.append(LIV)
                    if not R is None:
                        d.append(R)
                        #d.append("READ"+str(R))
                    else:
                        d.append(0)
                        #d.append("READ0")

                    if not W is None:
                        d.append(W)
                        #d.append("WRITE"+str(W))
                    else:
                        d.append(0)
                        #d.append("WRITE0")

                    if not L is None:
                        d.append(L)
                        #d.append("LISTEN"+str(L))
                    else:
                        d.append(0)
                        #d.append("LISTEN0")

                    if not S is None:
                        d.append(S)
                        #d.append("SPEAK"+str(S))
                    else:
                        d.append(0)
                        #d.append("SPEAK0")
                    #"""
                else:
                    d = d + [0]*9

        #countries = defaultdict(lambda: defaultdict(lambda: [None,None])) # user -> country -> (living duration, education duration)
            for country in country_order:
                LD, ED = countries[U][country]
                if LD is None:
                    d.append(0)

                else:
                    d.append(LD)

                if ED is None:
                    d.append(0)

                else:
                    d.append(ED)

            #CW.writerow(d)
            yield d

        #return Fname
    except Exception as ex:
        print(str(ex))
        #return ''


# def makeUserAnswersCSVFileForExperiment(exp_id):
#     try:
#         E = Experiment.objects.filter(pk=exp_id).select_subclasses()[0]
#         Fname = EXPERIMENT_EXPORT_FILE_FOLDER+E.experiment_name.replace(" ", "_")+"_UserAnswers.csv"

#         with open(Fname, "w", encoding="utf-8") as f:
#             CW = csv.writer(f)

#             headers = []
#             headers.append("Question ID")
#             headers.append("Question Native Language")
#             headers.append("Question Stimulus Language")
#             headers.append("Question Stimulus")
#             headers.append("Given Answer")
#             headers.append("Given Answer Absolutely Correct")
#             headers.append("Given Answer Correct Up To Normalization")
#             headers.append("Given Answer Incorrect")
#             headers.append("No Answer Given")
#             headers.append("Total Time Spent (ms)")
#             headers.append("Initial Hesitation Time (ms)")
#             headers.append("Typing Time (ms)")
#             headers.append("Final Hesitation Time (ms)")
#             headers.append("Date/Time Of Answer")
#             headers.append("Participation Start Date")
#             headers.append("Participation Finish Date")
#             headers.append("Participation Rank")
#             headers.append("User Account Name")
#             headers.append("User Mail")
#             headers.append("User Age")
#             headers.append("User Gender")
#             headers.append("User Living Location")
#             headers.append("User Living Duration (years)")
#             headers.append("User Knows Stimulus Language")


#             data = []
#             seen_langs = set([])
#             seen_countries = set([])

#             language_skills = defaultdict(lambda: defaultdict(lambda: None )) # user -> language -> (reading, writing, listening, speaking, native, used_at_home, exposure_duration_through_living, exposure_duration_through_learning, spoken_at_user_location)
#             countries = defaultdict(lambda: defaultdict(lambda: [None,None])) # user -> country -> (living duration, education duration)
#             user_answers = defaultdict(lambda: defaultdict(lambda: (None, None, None, None, None, None, None, None))) # user -> question ID -> given answer, abs correct yes/no, norm correct yes/no, total time, initial hesitation, typing time, submission hesitation
#             #user_answers[EP.user.user.username][UA.answered_question.id] = given, abs_correct, norm_correct, incorrect, no_answer_given, time, initial_hesitation_time, typing_time, submission_hesitation_time, date/time of answer

#             total_lang_weight = defaultdict(lambda: 0)
#             total_country_weight = defaultdict(lambda: 0)

#             for EP in ExperimentParticipation.objects.filter(experiment = exp_id):
#                 if EP.completed_on is None:
#                     continue

#                 D = []
#                 D.append(EP.started_on)
#                 D.append(EP.completed_on)
#                 D.append(EP.getAnswerRank())
#                 D.append(EP.user.user.username)
#                 D.append(EP.user.user.email)
#                 D.append(EP.user.age)
#                 D.append(EP.user.gender.code)
#                 D.append(EP.user.location.country_name)
#                 D.append(EP.user.location_living_duration)

#                 for skill in UserLanguageSkill.objects.filter(user=EP.user):
#                     seen_langs.add(skill.language.language_name)
#                     #print(skill.language,skill.reading_level,skill.writing_level,skill.listening_level,skill.speaking_level)
#                     #native = "NATIVE0"
#                     native = 0
#                     if skill.is_native_language:
#                         #native = "NATIVE1"
#                         native = 1

#                     #home = "HOME0"
#                     home = 0
#                     if skill.used_at_home:
#                         #home = "HOME1"
#                         home = 1

#                     #location_lang = "LOC0"
#                     location_lang = 0
#                     if skill.spoken_at_user_location:
#                         #location_lang = "LOC1"
#                         location_lang = 1

#                     if not skill.reading_level is None:
#                         total_lang_weight[skill.language.language_name] += skill.reading_level+skill.writing_level+skill.listening_level+skill.speaking_level

#                     exp_living = 0
#                     if not skill.exposure_through_living is None:
#                         exp_living = skill.exposure_through_living

#                     exp_learning = 0
#                     if not skill.exposure_through_learning is None:
#                         exp_learning = skill.exposure_through_learning

#                     language_skills[EP.user.user.username][skill.language.language_name] = (skill.reading_level, skill.writing_level, skill.listening_level, skill.speaking_level, native, home, exp_living, exp_learning, location_lang)

#                 for stay in LivingCountryStay.objects.filter(user=EP.user):
#                     seen_countries.add(stay.country.country_name)
#                     countries[EP.user.user.username][stay.country.country_name][0] = stay.duration
#                     total_country_weight[stay.country.country_name] += stay.duration

#                 for stay in EducationCountryStay.objects.filter(user=EP.user):
#                     seen_countries.add(stay.country.country_name)
#                     countries[EP.user.user.username][stay.country.country_name][1] = stay.duration
#                     total_country_weight[stay.country.country_name] += stay.duration

#                 for UA in UserAnswer.objects.filter(experiment_participation=EP).select_subclasses():
#                     abs_correct = UA.isExactlyCorrectAnswer()
#                     if abs_correct:
#                         abs_correct = 1
#                     else:
#                         abs_correct = 0
#                     norm_correct = UA.isCorrectAnswer()
#                     if norm_correct:
#                         norm_correct = 1
#                     else:
#                         norm_correct = 0

#                     no_answer = UA.native_word == ""
#                     if no_answer:
#                         no_answer = 1
#                     else:
#                         no_answer = 0

#                     incorrect = (not no_answer) and (not norm_correct)
#                     if incorrect:
#                         incorrect = 1
#                     else:
#                         incorrect = 0

#                     Q = Question.objects.filter(id=UA.answered_question.id).select_subclasses()[0]

#                     aborted_prematurely = UA.answer_given is None
#                     answer_date = UA.answer_date
#                     time = UA.time_spent
#                     initial_hesitation_time, typing_time,submission_hesitation_time = getHesitationAndTypingTimeFromResponseChanges(UA.result_changes)
#                     answer_date = UA.answer_date
#                     #user_answers[EP.user.user.username][UA.answered_question.id] = given, abs_correct, norm_correct, time, initial_hesitation_time, typing_time, submission_hesitation_time, answer_date
#                     X = [UA.answered_question.id, str(E.native_language), str(E.foreign_language), Q.foreign_word, UA.native_word, abs_correct, norm_correct, incorrect, no_answer, time, initial_hesitation_time, typing_time, submission_hesitation_time, answer_date] + D

#                     data.append(X)

#             # add additional headers
#             additional_headers = []
#             lang_order = []
#             for lang,w in sorted(total_lang_weight.items(), reverse=True):
#                 lang_order.append(lang)
#                 additional_headers.append("User Has Language "+lang)
#                 additional_headers.append(lang+" Spoken Where User Lives")
#                 additional_headers.append(lang+" Native")
#                 additional_headers.append(lang+" Used At Home")
#                 additional_headers.append(lang+" Learning Duration (years)")
#                 additional_headers.append(lang+" Exposure Through Living (years)")
#                 additional_headers.append(lang+" Reading")
#                 additional_headers.append(lang+" Writing")
#                 additional_headers.append(lang+" Listening")
#                 additional_headers.append(lang+" Speaking")

#             country_order = []
#             for country,w in sorted(total_country_weight.items(), reverse=True):
#                 country_order.append(country)
#                 additional_headers.append("Lived In "+country+" (years)")
#                 additional_headers.append("Went To School In "+country+" (years)")

#             headers = headers + additional_headers

#             CW.writerow(headers)
#             for d in data:
#                 U = d[17]

#                 X = language_skills[U][E.foreign_language.language_name]
#                 if X is None:
#                     #d.append("STIMLANG0")
#                     d.append(0)

#                 else:
#                     #d.append("STIMLANG1")
#                     d.append(1)

#                 for lang in lang_order:
#                     X = language_skills[U][lang]

#                     if X is None:
#                         #d.append("HASLANG0")
#                         d.append(0)

#                     else:
#                         #d.append("HASLANG1")
#                         d.append(1)
#                     #print(U,lang,X)
#                     if not X is None:
#                         #"""
#                         R, W, L, S, N, H, LIV, LEARN, LOC = X
#             #language_skills = defaultdict(lambda: defaultdict(lambda: None )) # user -> language -> (reading, writing, listening, speaking, native, used_at_home, exposure_duration_through_living, exposure_duration_through_learning, spoken_at_user_location)
#                         #d.append("LOC"+str(LOC))
#                         d.append(LOC)
#                         #d.append("NAT"+str(N))
#                         d.append(N)
#                         #d.append("HOME"+str(H))
#                         d.append(H)
#                         #d.append("LEARN"+str(LEARN))
#                         d.append(LEARN)
#                         #d.append("LIV"+str(LIV))
#                         d.append(LIV)
#                         if not R is None:
#                             d.append(R)
#                             #d.append("READ"+str(R))
#                         else:
#                             d.append(0)
#                             #d.append("READ0")

#                         if not W is None:
#                             d.append(W)
#                             #d.append("WRITE"+str(W))
#                         else:
#                             d.append(0)
#                             #d.append("WRITE0")

#                         if not L is None:
#                             d.append(L)
#                             #d.append("LISTEN"+str(L))
#                         else:
#                             d.append(0)
#                             #d.append("LISTEN0")

#                         if not S is None:
#                             d.append(S)
#                             #d.append("SPEAK"+str(S))
#                         else:
#                             d.append(0)
#                             #d.append("SPEAK0")
#                         #"""
#                     else:
#                         d = d + [0]*9

#             #countries = defaultdict(lambda: defaultdict(lambda: [None,None])) # user -> country -> (living duration, education duration)
#                 for country in country_order:
#                     LD, ED = countries[U][country]
#                     if LD is None:
#                         d.append(0)

#                     else:
#                         d.append(LD)

#                     if ED is None:
#                         d.append(0)

#                     else:
#                         d.append(ED)

#                 CW.writerow(d)

#         return Fname
#     except Exception as ex:
#         print(str(ex))
#         return ''


def NewmakeUserAnswersCSVFileForExperiment(exp_id):
    try:
        E = Experiment.objects.filter(pk=exp_id).select_subclasses()[0]
        Fname = EXPERIMENT_EXPORT_FILE_FOLDER+E.experiment_name.replace(" ", "_")+"_UserAnswers.csv"

        rows = []
        # with open(Fname, "w", encoding="utf-8") as f:
        #     CW = csv.writer(f)

        headers = []
        headers.append("Question ID")
        headers.append("Question Native Language")
        headers.append("Question Stimulus Language")
        headers.append("Question Stimulus")
        headers.append("Given Answer")
        headers.append("Given Answer Absolutely Correct")
        headers.append("Given Answer Correct Up To Normalization")
        headers.append("Given Answer Incorrect")
        headers.append("No Answer Given")
        headers.append("Total Time Spent (ms)")
        headers.append("Initial Hesitation Time (ms)")
        headers.append("Typing Time (ms)")
        headers.append("Final Hesitation Time (ms)")
        headers.append("Date/Time Of Answer")
        headers.append("Participation Start Date")
        headers.append("Participation Finish Date")
        headers.append("Participation Rank")
        headers.append("User Account Name")
        # Removed due to privacy issues
        #headers.append("User Mail")
        headers.append("User Age")
        headers.append("User Gender")
        headers.append("User Living Location")
        headers.append("User Living Duration (years)")
        headers.append("User Knows Stimulus Language")


        data = []
        seen_langs = set([])
        seen_countries = set([])

        language_skills = defaultdict(lambda: defaultdict(lambda: None )) # user -> language -> (reading, writing, listening, speaking, native, used_at_home, exposure_duration_through_living, exposure_duration_through_learning, spoken_at_user_location)
        countries = defaultdict(lambda: defaultdict(lambda: [None,None])) # user -> country -> (living duration, education duration)
        user_answers = defaultdict(lambda: defaultdict(lambda: (None, None, None, None, None, None, None, None))) # user -> question ID -> given answer, abs correct yes/no, norm correct yes/no, total time, initial hesitation, typing time, submission hesitation
        #user_answers[EP.user.user.username][UA.answered_question.id] = given, abs_correct, norm_correct, incorrect, no_answer_given, time, initial_hesitation_time, typing_time, submission_hesitation_time, date/time of answer

        total_lang_weight = defaultdict(lambda: 0)
        total_country_weight = defaultdict(lambda: 0)

        for EP in ExperimentParticipation.objects.filter(experiment = exp_id):
            if EP.completed_on is None:
                continue

            D = []
            D.append(EP.started_on)
            D.append(EP.completed_on)
            D.append(EP.getAnswerRank())
            D.append(EP.user.user.username)
            # Removed due to privacy issues
            #D.append(EP.user.user.email)
            D.append(EP.user.age)
            D.append(EP.user.gender.code)
            D.append(EP.user.location.country_name)
            D.append(EP.user.location_living_duration)

            for skill in UserLanguageSkill.objects.filter(user=EP.user):
                seen_langs.add(skill.language.language_name)
                #print(skill.language,skill.reading_level,skill.writing_level,skill.listening_level,skill.speaking_level)
                #native = "NATIVE0"
                native = 0
                if skill.is_native_language:
                    #native = "NATIVE1"
                    native = 1

                #home = "HOME0"
                home = 0
                if skill.used_at_home:
                    #home = "HOME1"
                    home = 1

                #location_lang = "LOC0"
                location_lang = 0
                if skill.spoken_at_user_location:
                    #location_lang = "LOC1"
                    location_lang = 1

                if not skill.reading_level is None:
                    total_lang_weight[skill.language.language_name] += skill.reading_level+skill.writing_level+skill.listening_level+skill.speaking_level

                exp_living = 0
                if not skill.exposure_through_living is None:
                    exp_living = skill.exposure_through_living

                exp_learning = 0
                if not skill.exposure_through_learning is None:
                    exp_learning = skill.exposure_through_learning

                language_skills[EP.user.user.username][skill.language.language_name] = (skill.reading_level, skill.writing_level, skill.listening_level, skill.speaking_level, native, home, exp_living, exp_learning, location_lang)

            for stay in LivingCountryStay.objects.filter(user=EP.user):
                seen_countries.add(stay.country.country_name)
                countries[EP.user.user.username][stay.country.country_name][0] = stay.duration
                total_country_weight[stay.country.country_name] += stay.duration

            for stay in EducationCountryStay.objects.filter(user=EP.user):
                seen_countries.add(stay.country.country_name)
                countries[EP.user.user.username][stay.country.country_name][1] = stay.duration
                total_country_weight[stay.country.country_name] += stay.duration

            for UA in UserAnswer.objects.filter(experiment_participation=EP).select_subclasses():
                abs_correct = UA.isExactlyCorrectAnswer()
                if abs_correct:
                    abs_correct = 1
                else:
                    abs_correct = 0
                norm_correct = UA.isCorrectAnswer()
                if norm_correct:
                    norm_correct = 1
                else:
                    norm_correct = 0

                no_answer = UA.native_word == ""
                if no_answer:
                    no_answer = 1
                else:
                    no_answer = 0

                incorrect = (not no_answer) and (not norm_correct)
                if incorrect:
                    incorrect = 1
                else:
                    incorrect = 0

                Q = Question.objects.filter(id=UA.answered_question.id).select_subclasses()[0]

                aborted_prematurely = UA.answer_given is None
                answer_date = UA.answer_date
                time = UA.time_spent
                initial_hesitation_time, typing_time,submission_hesitation_time = getHesitationAndTypingTimeFromResponseChanges(UA.result_changes)
                answer_date = UA.answer_date
                #user_answers[EP.user.user.username][UA.answered_question.id] = given, abs_correct, norm_correct, time, initial_hesitation_time, typing_time, submission_hesitation_time, answer_date
                X = [UA.answered_question.id, str(E.native_language), str(E.foreign_language), Q.foreign_word, UA.native_word, abs_correct, norm_correct, incorrect, no_answer, time, initial_hesitation_time, typing_time, submission_hesitation_time, answer_date] + D

                data.append(X)

        # add additional headers
        additional_headers = []
        lang_order = []
        for lang,w in sorted(total_lang_weight.items(), reverse=True):
            lang_order.append(lang)
            additional_headers.append("User Has Language "+lang)
            additional_headers.append(lang+" Spoken Where User Lives")
            additional_headers.append(lang+" Native")
            additional_headers.append(lang+" Used At Home")
            additional_headers.append(lang+" Learning Duration (years)")
            additional_headers.append(lang+" Exposure Through Living (years)")
            additional_headers.append(lang+" Reading")
            additional_headers.append(lang+" Writing")
            additional_headers.append(lang+" Listening")
            additional_headers.append(lang+" Speaking")

        country_order = []
        for country,w in sorted(total_country_weight.items(), reverse=True):
            country_order.append(country)
            additional_headers.append("Lived In "+country+" (years)")
            additional_headers.append("Went To School In "+country+" (years)")

        headers = headers + additional_headers

        CW.writerow(headers)
        for d in data:
            U = d[17]

            X = language_skills[U][E.foreign_language.language_name]
            if X is None:
                #d.append("STIMLANG0")
                d.append(0)

            else:
                #d.append("STIMLANG1")
                d.append(1)

            for lang in lang_order:
                X = language_skills[U][lang]

                if X is None:
                    #d.append("HASLANG0")
                    d.append(0)

                else:
                    #d.append("HASLANG1")
                    d.append(1)
                #print(U,lang,X)
                if not X is None:
                    #"""
                    R, W, L, S, N, H, LIV, LEARN, LOC = X
        #language_skills = defaultdict(lambda: defaultdict(lambda: None )) # user -> language -> (reading, writing, listening, speaking, native, used_at_home, exposure_duration_through_living, exposure_duration_through_learning, spoken_at_user_location)
                    #d.append("LOC"+str(LOC))
                    d.append(LOC)
                    #d.append("NAT"+str(N))
                    d.append(N)
                    #d.append("HOME"+str(H))
                    d.append(H)
                    #d.append("LEARN"+str(LEARN))
                    d.append(LEARN)
                    #d.append("LIV"+str(LIV))
                    d.append(LIV)
                    if not R is None:
                        d.append(R)
                        #d.append("READ"+str(R))
                    else:
                        d.append(0)
                        #d.append("READ0")

                    if not W is None:
                        d.append(W)
                        #d.append("WRITE"+str(W))
                    else:
                        d.append(0)
                        #d.append("WRITE0")

                    if not L is None:
                        d.append(L)
                        #d.append("LISTEN"+str(L))
                    else:
                        d.append(0)
                        #d.append("LISTEN0")

                    if not S is None:
                        d.append(S)
                        #d.append("SPEAK"+str(S))
                    else:
                        d.append(0)
                        #d.append("SPEAK0")
                    #"""
                else:
                    d = d + [0]*9

        #countries = defaultdict(lambda: defaultdict(lambda: [None,None])) # user -> country -> (living duration, education duration)
            for country in country_order:
                LD, ED = countries[U][country]
                if LD is None:
                    d.append(0)

                else:
                    d.append(LD)

                if ED is None:
                    d.append(0)

                else:
                    d.append(ED)

            rows.append(d)

            #CW.writerow(d)

        return Fname, headers, rows
    except Exception as ex:
        print(str(ex))
        return '', '', ''


# class QuestionAnswersCSVExportView(View):
#     def get(self, request, exp_id):
#         try:
#             experiments = Experiment.objects.filter(id=exp_id).select_subclasses()
#             if len(experiments) > 0:
#                 experiment = experiments[0]
#             experimentName = experiment.getExperimentNameForUser()
#             if "Gap Filling" in experimentName:
#                 makeUserAnswersCSVFileForGapFillingExperiment(exp_id)
#             else:
#                 makeUserAnswersCSVFileForExperiment(exp_id)

#         except Exception as ex:
#             return HttpResponse(str(ex)+'ExperimentID {}'.format(exp_id))
#         try:
#             #Fname = makeUserAnswersCSVFileForExperiment(exp_id)
#             E = Experiment.objects.filter(pk=exp_id).select_subclasses()[0]
#             #Fpath = EXPERIMENT_EXPORT_FILE_FOLDER+E.experiment_name.replace(" ", "_")+"_UserAnswers.csv"
#             Fpath = EXPERIMENT_EXPORT_FILE_FOLDER+E.experiment_name.replace(" ", "_")+"_UserAnswers.csv"
#             #Fname = E.experiment_name.replace(" ", "_")+"_UserAnswers.csv"
#             Fname = E.experiment_name.replace(" ", "_")+"_UserAnswers.csv"

#             # with open(Fpath, "r", encoding="utf-8") as f:
#             #     response = StreamingHttpResponse(FileWrapper(f), content_type='text/csv')
#             #     response['Content-Disposition'] = 'attachment; filename={}'.format(Fname)
#             #     return response
            
#             response = StreamingHttpResponse(FileWrapper(open(Fpath, "r", encoding="utf-8")), content_type='text/csv')
#             response['Content-Disposition'] = 'attachment; filename={}'.format(Fname)
#             return response
        
#         except Exception as e:
#             return HttpResponse(str(e))


class QuestionAnswersCSVExportView(View):
    def get(self, request, exp_id):
        try:
            experiments = Experiment.objects.filter(id=exp_id).select_subclasses()
            if len(experiments) > 0:
                experiment = experiments[0]
            experimentName = experiment.getExperimentNameForUser()
            if "Gap Filling" in experimentName:
                makeUserAnswersCSVFileForGapFillingExperiment(exp_id)
            else:
                E = Experiment.objects.filter(pk=exp_id).select_subclasses()[0]
                Fname = E.experiment_name.replace(" ", "_")+"_UserAnswers.csv"
                rows = makeUserAnswersCSVFileForExperiment(exp_id)
                pseudo_buffer = Echo()
                writer = csv.writer(pseudo_buffer)
                response = StreamingHttpResponse((writer.writerow(row) for row in rows),content_type="text/csv")
                response['Content-Disposition'] = 'attachment; filename={}'.format(Fname)
                return response

        except Exception as ex:
            return HttpResponse(str(ex)+'ExperimentID {}'.format(exp_id))
        try:
            #Fname = makeUserAnswersCSVFileForExperiment(exp_id)
            E = Experiment.objects.filter(pk=exp_id).select_subclasses()[0]
            #Fpath = EXPERIMENT_EXPORT_FILE_FOLDER+E.experiment_name.replace(" ", "_")+"_UserAnswers.csv"
            Fpath = EXPERIMENT_EXPORT_FILE_FOLDER+E.experiment_name.replace(" ", "_")+"_UserAnswers.csv"
            #Fname = E.experiment_name.replace(" ", "_")+"_UserAnswers.csv"
            Fname = E.experiment_name.replace(" ", "_")+"_UserAnswers.csv"

            # with open(Fpath, "r", encoding="utf-8") as f:
            #     response = StreamingHttpResponse(FileWrapper(f), content_type='text/csv')
            #     response['Content-Disposition'] = 'attachment; filename={}'.format(Fname)
            #     return response
            
            response = StreamingHttpResponse(FileWrapper(open(Fpath, "r", encoding="utf-8")), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename={}'.format(Fname)
            return response
        
        except Exception as e:
            return HttpResponse(str(e))


class AudioQuestionAnswersCSVExportView(View):
    def get(self, request, exp_id):
        try:
            experiments = Experiment.objects.filter(id=exp_id).select_subclasses()
            if len(experiments) > 0:
                experiment = experiments[0]
            experimentName = experiment.getExperimentNameForUser()
            if "Gap Filling" in experimentName:
                makeUserAnswersCSVFileForGapFillingExperiment(exp_id)
            else:
                print("Here in AudioQuestionAnswersCSVExportView")
                E = Experiment.objects.filter(pk=exp_id).select_subclasses()[0]
                Fname = E.experiment_name.replace(" ", "_")+"_AudioUserAnswers.csv"
                rows = makeUserAnswersCSVFileForExperiment(exp_id, is_audio=True)
                pseudo_buffer = Echo()
                writer = csv.writer(pseudo_buffer)
                response = StreamingHttpResponse((writer.writerow(row) for row in rows),content_type="text/csv")
                response['Content-Disposition'] = 'attachment; filename={}'.format(Fname)
                return response

        except Exception as ex:
            return HttpResponse(str(ex)+'ExperimentID {}'.format(exp_id))
        try:
            #Fname = makeUserAnswersCSVFileForExperiment(exp_id)
            E = Experiment.objects.filter(pk=exp_id).select_subclasses()[0]
            #Fpath = EXPERIMENT_EXPORT_FILE_FOLDER+E.experiment_name.replace(" ", "_")+"_UserAnswers.csv"
            Fpath = EXPERIMENT_EXPORT_FILE_FOLDER+E.experiment_name.replace(" ", "_")+"_AudioUserAnswers.csv"
            #Fname = E.experiment_name.replace(" ", "_")+"_UserAnswers.csv"
            Fname = E.experiment_name.replace(" ", "_")+"_AudioUserAnswers.csv"

            # with open(Fpath, "r", encoding="utf-8") as f:
            #     response = StreamingHttpResponse(FileWrapper(f), content_type='text/csv')
            #     response['Content-Disposition'] = 'attachment; filename={}'.format(Fname)
            #     return response
            
            response = StreamingHttpResponse(FileWrapper(open(Fpath, "r", encoding="utf-8")), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename={}'.format(Fname)
            return response
        
        except Exception as e:
            return HttpResponse(str(e))


# Added for NeW CSV Export on 21-08-2018

class Echo(object):

    def write(self, value):
        return value

class NewQuestionAnswersCSVExportView(View):

    def get(self, request, exp_id):
        try:
            file_name, headers, rows = NewmakeUserAnswersCSVFileForExperiment(exp_id)

            pseudo_buffer = Echo()

            writer = csv.writer(pseudo_buffer)

            def row_generator():

                yield map(convert_value_to_unicode, headers)

                for row in rows:
                    yield map(convert_value_to_unicode, row)


            response = StreamingHttpResponse((writer.writerow(row) for row in row_generator()), content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
            return response
        except Exception as e:
            return HttpResponse(str(e))


class QuestionReadingTimeCSVExportView(View):
    def get(self, request, exp_id):
        try:
            # for testing gap filling experiment reading time file
            makeQuestionReadingTimeCSVFileForGapFillingExperiment(exp_id)

        except Exception as ex:
            return HttpResponse(str(ex)+'ExperimentID {}'.format(exp_id))
        try:
            E = Experiment.objects.filter(pk=exp_id).select_subclasses()[0]
            Fpath = EXPERIMENT_EXPORT_FILE_FOLDER+E.experiment_name.replace(" ", "_")+"_ReadingTime.csv"
            Fname = E.experiment_name.replace(" ", "_")+"_ReadingTime.csv"

            with open(Fpath, "r", encoding="utf-8") as f:
                response = HttpResponse(f, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename={}'.format(Fname)
                return response

        except Exception as e:
            return HttpResponse(str(e))


def convert_value_to_unicode(v):

    if v is None:
        return u''
    elif hasattr(v, 'isoformat'):
        return v.isoformat()
    else:
        return force_text(v)



def parseGapFillingQuestion(sentence):
    """
    parse sentence and return sentence and list of gap words
    """
    sentence = sentence.replace("{", "[").replace("}", "]").replace('_','')
    sentence_with_all_words = sentence
    gaps = re.findall(r"[^[]*\[([^]]*)\]", sentence)
    ls_gap_words = []
    for g in range(len(gaps)):
        placeholder = gaps[g].split('|')[0]
        sentence_with_all_words = sentence_with_all_words.replace('['+gaps[g]+']',placeholder)
        ls_gap_words.append(placeholder)
    # return ls_gap_words, sentence_with_all_words.replace('[','').replace(']','')
    return ls_gap_words, sentence_with_all_words


def makeUserAnswersCSVFileForGapFillingExperiment(exp_id):
    try:
        E = Experiment.objects.filter(pk=exp_id).select_subclasses()[0]
        Fname = EXPERIMENT_EXPORT_FILE_FOLDER+E.experiment_name.replace(" ", "_")+"_UserAnswers.csv"

        with open(Fname, "w", encoding="utf-8") as f:
            CW = csv.writer(f)

            headers = []
            headers.append("Question ID")
            headers.append("Question Native Language")
            headers.append("Question Stimulus Language")
            headers.append("Question Stimulus")
            headers.append("Given Answer")
            headers.append("Given Answer Absolutely Correct")
            headers.append("Given Answer Correct Up To Normalization")
            headers.append("Given Answer Incorrect")
            headers.append("No Answer Given")
            headers.append("Total Time Spent (ms)")
            headers.append("Initial Hesitation Time (ms)")
            headers.append("Typing Time (ms)")
            headers.append("Final Hesitation Time (ms)")
            headers.append("Date/Time Of Answer")
            headers.append("Participation Start Date")
            headers.append("Participation Finish Date")
            headers.append("Participation Rank")
            headers.append("User Account Name")
            # Removed due to privacy issues
            #headers.append("User Mail")
            headers.append("User Age")
            headers.append("User Gender")
            headers.append("User Living Location")
            headers.append("User Living Duration (years)")
            headers.append("User Knows Stimulus Language")

            #Added by AYAN
            headers.append("Number of Languages User Knows")
            headers.append("Languages With >= B2 Reading Level")
            headers.append("Number of Languages With >= B2 Reading Level")

            data = []
            seen_langs = set([])
            seen_countries = set([])

            language_skills = defaultdict(lambda: defaultdict(lambda: None )) # user -> language -> (reading, writing, listening, speaking, native, used_at_home, exposure_duration_through_living, exposure_duration_through_learning, spoken_at_user_location)
            countries = defaultdict(lambda: defaultdict(lambda: [None,None])) # user -> country -> (living duration, education duration)
            user_answers = defaultdict(lambda: defaultdict(lambda: (None, None, None, None, None, None, None, None))) # user -> question ID -> given answer, abs correct yes/no, norm correct yes/no, total time, initial hesitation, typing time, submission hesitation
            #user_answers[EP.user.user.username][UA.answered_question.id] = given, abs_correct, norm_correct, incorrect, no_answer_given, time, initial_hesitation_time, typing_time, submission_hesitation_time, date/time of answer

            total_lang_weight = defaultdict(lambda: 0)
            total_country_weight = defaultdict(lambda: 0)

            #Added by AYAN
            num_languages_user = defaultdict(lambda:0)
            user_languages_b2_reading = defaultdict(lambda:[])

            for EP in ExperimentParticipation.objects.filter(experiment = exp_id):
                if EP.completed_on is None:
                    continue
                D = []
                D.append(EP.started_on)
                D.append(EP.completed_on)
                D.append(EP.getAnswerRank())
                D.append(EP.user.user.username)
                # Removed due to privacy issues
                #D.append(EP.user.user.email)
                D.append(EP.user.age)
                D.append(EP.user.gender.code)
                D.append(EP.user.location.country_name)
                D.append(EP.user.location_living_duration)

                for skill in UserLanguageSkill.objects.filter(user=EP.user):
                    seen_langs.add(skill.language.language_name)
                    #print(skill.language,skill.reading_level,skill.writing_level,skill.listening_level,skill.speaking_level)
                    #native = "NATIVE0"
                    native = 0
                    if skill.is_native_language:
                        #native = "NATIVE1"
                        native = 1

                    #home = "HOME0"
                    home = 0
                    if skill.used_at_home:
                        #home = "HOME1"
                        home = 1

                    #location_lang = "LOC0"
                    location_lang = 0
                    if skill.spoken_at_user_location:
                        #location_lang = "LOC1"
                        location_lang = 1

                    if not skill.reading_level is None:
                        total_lang_weight[skill.language.language_name] += skill.reading_level+skill.writing_level+skill.listening_level+skill.speaking_level

                    exp_living = 0
                    if not skill.exposure_through_living is None:
                        exp_living = skill.exposure_through_living

                    exp_learning = 0
                    if not skill.exposure_through_learning is None:
                        exp_learning = skill.exposure_through_learning

                    language_skills[EP.user.user.username][skill.language.language_name] = (skill.reading_level, skill.writing_level, skill.listening_level, skill.speaking_level, native, home, exp_living, exp_learning, location_lang)

                    # Added by AYAN
                    if not skill.reading_level is None:
                        if skill.reading_level >= 65:
                            user_languages_b2_reading[EP.user.user.username].append(skill.language.language_name)
                try:
                    num_languages_user[EP.user.user.username] = len(language_skills[EP.user.user.username])
                except Exception as e:
                    print(e)

                for stay in LivingCountryStay.objects.filter(user=EP.user):
                    seen_countries.add(stay.country.country_name)
                    countries[EP.user.user.username][stay.country.country_name][0] = stay.duration
                    total_country_weight[stay.country.country_name] += stay.duration

                for stay in EducationCountryStay.objects.filter(user=EP.user):
                    seen_countries.add(stay.country.country_name)
                    countries[EP.user.user.username][stay.country.country_name][1] = stay.duration
                    total_country_weight[stay.country.country_name] += stay.duration

                for UA in UserAnswer.objects.filter(experiment_participation=EP).select_subclasses():
                    answers = UA.gaps_answers.split(',')
                    if E.foreign_language == 'XL':
                        AQ = MixedLanguagesGapFillingQuestion.objects.get(id=UA.answered_question.id)
                    else:
                        AQ = GapFillingQuestion.objects.get(id=UA.answered_question.id)
                    sentence = AQ.sentence
                    ls_all_gaps, normal_sentence = parseGapFillingQuestion(sentence)
                    # print(normal_sentence)
                    ls_gaps_time = getHesitationAndTypingTimeFromResponseChangesForGapFilling(UA.result_changes,len(ls_all_gaps))
                    correct_answers = AQ.correct_answers.all()[0].gaps_answers.strip().split(',')
                    ca_dict = {}
                    ca_normalize_dict = {}

                    # making all possible correct answers dictionary
                    for ca in correct_answers:
                        k, val = ca.split('_')
                        if k not in ca_dict:
                            ca_dict[k] = [str(val).strip()]
                            # filling normalized version
                            ca_normalize_dict[k] = [str(removeDiacritics(val.lower())).strip()]
                        else:
                            ca_dict[k].append(str(val).strip())
                            # filling normalized version
                            ca_normalize_dict[k].append(str(removeDiacritics(val.lower())).strip())

                    # checking user answer for each gap
                    for i in range(len(answers)):
                        try:
                            gap_word = ls_all_gaps[i]
                            ans = answers[i].strip()
                            normalized_ans = removeDiacritics(answers[i].lower())
                        except Exception as ex:
                            continue

                        k = 'Gap' + str(i)

                        ls = ca_dict[k]
                        if ans in ls:
                            abs_correct = 1
                            # no_answer=0
                        else:
                            abs_correct = 0

                        ls_norm=ca_normalize_dict[k]
                        if normalized_ans in ls_norm:
                            norm_correct = 1
                            # no_answer= 0
                        else:
                            norm_correct = 0

                        if ans =="":
                            no_answer=1
                        else:
                            no_answer =0

                        if no_answer==0 and norm_correct==0:
                            incorrect = 1
                        else:
                            incorrect=0

                        # Q = Question.objects.filter(id=UA.answered_question.id).select_subclasses()[0]

                        # aborted_prematurely = UA.answer_given is None
                        # answer_date = UA.answer_date
                        time = UA.time_spent
                        initial_hesitation_time, typing_time,submission_hesitation_time = ls_gaps_time[i]
                        answer_date = UA.answer_date

                        # X = [UA.answered_question.id, str(E.native_language), str(E.foreign_language), Q.foreign_word, UA.native_word, abs_correct, norm_correct, incorrect, no_answer, time, initial_hesitation_time, typing_time, submission_hesitation_time, answer_date] + D
                        X = [UA.answered_question.id, str(E.native_language), str(E.foreign_language), gap_word, ans, abs_correct, norm_correct, incorrect, no_answer, time, initial_hesitation_time, typing_time, submission_hesitation_time, answer_date] + D
                        data.append(X)

            # add additional headers
            additional_headers = []
            lang_order = []
            for lang,w in sorted(total_lang_weight.items(), reverse=True):
                lang_order.append(lang)
                additional_headers.append("User Has Language "+lang)
                additional_headers.append(lang+" Spoken Where User Lives")
                additional_headers.append(lang+" Native")
                additional_headers.append(lang+" Used At Home")
                additional_headers.append(lang+" Learning Duration (years)")
                additional_headers.append(lang+" Exposure Through Living (years)")
                additional_headers.append(lang+" Reading")
                additional_headers.append(lang+" Writing")
                additional_headers.append(lang+" Listening")
                additional_headers.append(lang+" Speaking")

            country_order = []
            for country,w in sorted(total_country_weight.items(), reverse=True):
                country_order.append(country)
                additional_headers.append("Lived In "+country+" (years)")
                additional_headers.append("Went To School In "+country+" (years)")

            headers = headers + additional_headers

            CW.writerow(headers)
            for d in data:
                U = d[17]

                if E.foreign_language != 'XL':
                    X = language_skills[U][E.foreign_language.language_name]
                else:
                    X = language_skills[U][E.foreign_language]

                if X is None:
                    #d.append("STIMLANG0")
                    d.append(0)

                else:
                    #d.append("STIMLANG1")
                    d.append(1)

                #Added by AYAN
                d.append(num_languages_user[U])
                d.append(','.join(user_languages_b2_reading[U]))
                d.append(len(user_languages_b2_reading[U]))

                for lang in lang_order:
                    X = language_skills[U][lang]

                    if X is None:
                        #d.append("HASLANG0")
                        d.append(0)

                    else:
                        #d.append("HASLANG1")
                        d.append(1)
                    #print(U,lang,X)
                    if not X is None:
                        #"""
                        R, W, L, S, N, H, LIV, LEARN, LOC = X
            #language_skills = defaultdict(lambda: defaultdict(lambda: None )) # user -> language -> (reading, writing, listening, speaking, native, used_at_home, exposure_duration_through_living, exposure_duration_through_learning, spoken_at_user_location)
                        #d.append("LOC"+str(LOC))
                        d.append(LOC)
                        #d.append("NAT"+str(N))
                        d.append(N)
                        #d.append("HOME"+str(H))
                        d.append(H)
                        #d.append("LEARN"+str(LEARN))
                        d.append(LEARN)
                        #d.append("LIV"+str(LIV))
                        d.append(LIV)
                        if not R is None:
                            d.append(R)
                            #d.append("READ"+str(R))
                        else:
                            d.append(0)
                            #d.append("READ0")

                        if not W is None:
                            d.append(W)
                            #d.append("WRITE"+str(W))
                        else:
                            d.append(0)
                            #d.append("WRITE0")

                        if not L is None:
                            d.append(L)
                            #d.append("LISTEN"+str(L))
                        else:
                            d.append(0)
                            #d.append("LISTEN0")

                        if not S is None:
                            d.append(S)
                            #d.append("SPEAK"+str(S))
                        else:
                            d.append(0)
                            #d.append("SPEAK0")
                        #"""
                    else:
                        d = d + [0]*9

            #countries = defaultdict(lambda: defaultdict(lambda: [None,None])) # user -> country -> (living duration, education duration)
                for country in country_order:
                    LD, ED = countries[U][country]
                    if LD is None:
                        d.append(0)

                    else:
                        d.append(LD)

                    if ED is None:
                        d.append(0)

                    else:
                        d.append(ED)

                CW.writerow(d)

        return Fname
    except Exception as ex:
        print(str(ex))
        return ''


def makeQuestionReadingTimeCSVFileForGapFillingExperiment(exp_id):
    """
    making question reading time file for gap filling experiment (time for every word click)
    """
    try:
        E = Experiment.objects.filter(pk=exp_id).select_subclasses()[0]
        Fname = EXPERIMENT_EXPORT_FILE_FOLDER+E.experiment_name.replace(" ", "_")+"_ReadingTime.csv"

        with open(Fname, "w", encoding="utf-8") as f:
            CW = csv.writer(f)

            headers = []
            headers.append("Question ID")
            headers.append("Question Native Language")
            headers.append("Question Stimulus Language")
            headers.append("Question Stimulus")
            headers.append("Reading Time Spent (ms)")
            headers.append("Date/Time Of Answer")
            headers.append("Participation Start Date")
            headers.append("Participation Finish Date")
            headers.append("Participation Rank")
            headers.append("User Account Name")
            # Removed due to privacy issues
            #headers.append("User Mail")
            headers.append("User Age")
            headers.append("User Gender")
            headers.append("User Living Location")
            headers.append("User Living Duration (years)")
            headers.append("User Knows Stimulus Language")

            data = []
            seen_langs = set([])
            seen_countries = set([])

            language_skills = defaultdict(lambda: defaultdict(lambda: None )) # user -> language -> (reading, writing, listening, speaking, native, used_at_home, exposure_duration_through_living, exposure_duration_through_learning, spoken_at_user_location)
            countries = defaultdict(lambda: defaultdict(lambda: [None,None])) # user -> country -> (living duration, education duration)

            total_lang_weight = defaultdict(lambda: 0)
            total_country_weight = defaultdict(lambda: 0)

            for EP in ExperimentParticipation.objects.filter(experiment = exp_id):
                if EP.completed_on is None:
                    continue

                D = []
                D.append(EP.started_on)
                D.append(EP.completed_on)
                D.append(EP.getAnswerRank())
                D.append(EP.user.user.username)
                # Removed due to privacy issues.
                #D.append(EP.user.user.email)
                D.append(EP.user.age)
                D.append(EP.user.gender.code)
                D.append(EP.user.location.country_name)
                D.append(EP.user.location_living_duration)

                for skill in UserLanguageSkill.objects.filter(user=EP.user):
                    seen_langs.add(skill.language.language_name)
                    native = 0
                    if skill.is_native_language:
                        native = 1

                    home = 0
                    if skill.used_at_home:
                        home = 1

                    location_lang = 0
                    if skill.spoken_at_user_location:
                        location_lang = 1

                    if not skill.reading_level is None:
                        total_lang_weight[skill.language.language_name] += skill.reading_level+skill.writing_level+skill.listening_level+skill.speaking_level

                    exp_living = 0
                    if not skill.exposure_through_living is None:
                        exp_living = skill.exposure_through_living

                    exp_learning = 0
                    if not skill.exposure_through_learning is None:
                        exp_learning = skill.exposure_through_learning

                    language_skills[EP.user.user.username][skill.language.language_name] = (skill.reading_level, skill.writing_level, skill.listening_level, skill.speaking_level, native, home, exp_living, exp_learning, location_lang)

                for stay in LivingCountryStay.objects.filter(user=EP.user):
                    seen_countries.add(stay.country.country_name)
                    countries[EP.user.user.username][stay.country.country_name][0] = stay.duration
                    total_country_weight[stay.country.country_name] += stay.duration

                for stay in EducationCountryStay.objects.filter(user=EP.user):
                    seen_countries.add(stay.country.country_name)
                    countries[EP.user.user.username][stay.country.country_name][1] = stay.duration
                    total_country_weight[stay.country.country_name] += stay.duration

                for UA in UserAnswer.objects.filter(experiment_participation=EP).select_subclasses():

                    # -------------start---------------

                    # word click time
                    words_click_time = UA.words_click_time

                    if E.foreign_language == 'XL':
                        AQ = MixedLanguagesGapFillingQuestion.objects.get(id=UA.answered_question.id)
                    else:
                        AQ = GapFillingQuestion.objects.get(id=UA.answered_question.id)
                    sentence = AQ.sentence
                    ls_all_gaps, n_sentence = parseGapFillingQuestion(sentence)
                    click_time_dict = getReadingTimeFromWordsClick(words_click_time)
                    # print(click_time_dict)
                    # print(words_click_time)
                    normal_sentence = n_sentence.split()

                    for i in range(1,len(normal_sentence)+1):
                        answer_date = UA.answer_date
                        reading_time=click_time_dict[i]-click_time_dict[i-1]
                        stimulus = normal_sentence[i-1]
                        X = [UA.answered_question.id, str(E.native_language), str(E.foreign_language), stimulus,reading_time, answer_date] + D
                        data.append(X)

            # add additional headers
            additional_headers = []
            lang_order = []
            for lang,w in sorted(total_lang_weight.items(), reverse=True):
                lang_order.append(lang)
                additional_headers.append("User Has Language "+lang)
                additional_headers.append(lang+" Spoken Where User Lives")
                additional_headers.append(lang+" Native")
                additional_headers.append(lang+" Used At Home")
                additional_headers.append(lang+" Learning Duration (years)")
                additional_headers.append(lang+" Exposure Through Living (years)")
                additional_headers.append(lang+" Reading")
                additional_headers.append(lang+" Writing")
                additional_headers.append(lang+" Listening")
                additional_headers.append(lang+" Speaking")

            country_order = []
            for country,w in sorted(total_country_weight.items(), reverse=True):
                country_order.append(country)
                additional_headers.append("Lived In "+country+" (years)")
                additional_headers.append("Went To School In "+country+" (years)")

            headers = headers + additional_headers

            CW.writerow(headers)
            for d in data:
                # U = d[17]
                # print(len(d))
                U = d[14]
                if E.foreign_language !='XL':
                    X = language_skills[U][E.foreign_language.language_name]
                else:
                    X = language_skills[U][E.foreign_language]
                if X is None:
                    d.append(0)
                else:
                    d.append(1)

                for lang in lang_order:
                    X = language_skills[U][lang]

                    if X is None:
                        d.append(0)
                    else:
                        d.append(1)

                    if not X is None:
                        R, W, L, S, N, H, LIV, LEARN, LOC = X
                        d.append(LOC)
                        d.append(N)
                        d.append(H)
                        d.append(LEARN)
                        d.append(LIV)

                        if not R is None:
                            d.append(R)
                        else:
                            d.append(0)

                        if not W is None:
                            d.append(W)
                        else:
                            d.append(0)

                        if not L is None:
                            d.append(L)
                        else:
                            d.append(0)

                        if not S is None:
                            d.append(S)
                        else:
                            d.append(0)

                    else:
                        d = d + [0]*9

                for country in country_order:
                    LD, ED = countries[U][country]
                    if LD is None:
                        d.append(0)
                    else:
                        d.append(LD)

                    if ED is None:
                        d.append(0)
                    else:
                        d.append(ED)

                CW.writerow(d)

        return Fname
    except Exception as ex:
        print(str(ex))
        return ''


def NewmakeQuestionReadingTimeCSVFileForGapFillingExperiment(exp_id):
    """
    making question reading time file for gap filling experiment (time for every word click)
    """
    try:
        E = Experiment.objects.filter(pk=exp_id).select_subclasses()[0]
        Fname = EXPERIMENT_EXPORT_FILE_FOLDER+E.experiment_name.replace(" ", "_")+"_ReadingTime.csv"
        rows = []

        # with open(Fname, "w", encoding="utf-8") as f:
        #     CW = csv.writer(f)

        headers = []
        headers.append("Question ID")
        headers.append("Question Native Language")
        headers.append("Question Stimulus Language")
        headers.append("Question Stimulus")
        headers.append("Reading Time Spent (ms)")
        headers.append("Date/Time Of Answer")
        headers.append("Participation Start Date")
        headers.append("Participation Finish Date")
        headers.append("Participation Rank")
        headers.append("User Account Name")
        # Removed due to privacy issues
        #headers.append("User Mail")
        headers.append("User Age")
        headers.append("User Gender")
        headers.append("User Living Location")
        headers.append("User Living Duration (years)")
        headers.append("User Knows Stimulus Language")

        data = []
        seen_langs = set([])
        seen_countries = set([])

        language_skills = defaultdict(lambda: defaultdict(lambda: None )) # user -> language -> (reading, writing, listening, speaking, native, used_at_home, exposure_duration_through_living, exposure_duration_through_learning, spoken_at_user_location)
        countries = defaultdict(lambda: defaultdict(lambda: [None,None])) # user -> country -> (living duration, education duration)

        total_lang_weight = defaultdict(lambda: 0)
        total_country_weight = defaultdict(lambda: 0)

        for EP in ExperimentParticipation.objects.filter(experiment = exp_id):
            if EP.completed_on is None:
                continue

            D = []
            D.append(EP.started_on)
            D.append(EP.completed_on)
            D.append(EP.getAnswerRank())
            D.append(EP.user.user.username)
            # Removed due to privacy issues
            #D.append(EP.user.user.email)
            D.append(EP.user.age)
            D.append(EP.user.gender.code)
            D.append(EP.user.location.country_name)
            D.append(EP.user.location_living_duration)

            for skill in UserLanguageSkill.objects.filter(user=EP.user):
                seen_langs.add(skill.language.language_name)
                native = 0
                if skill.is_native_language:
                    native = 1

                home = 0
                if skill.used_at_home:
                    home = 1

                location_lang = 0
                if skill.spoken_at_user_location:
                    location_lang = 1

                if not skill.reading_level is None:
                    total_lang_weight[skill.language.language_name] += skill.reading_level+skill.writing_level+skill.listening_level+skill.speaking_level

                exp_living = 0
                if not skill.exposure_through_living is None:
                    exp_living = skill.exposure_through_living

                exp_learning = 0
                if not skill.exposure_through_learning is None:
                    exp_learning = skill.exposure_through_learning

                language_skills[EP.user.user.username][skill.language.language_name] = (skill.reading_level, skill.writing_level, skill.listening_level, skill.speaking_level, native, home, exp_living, exp_learning, location_lang)

            for stay in LivingCountryStay.objects.filter(user=EP.user):
                seen_countries.add(stay.country.country_name)
                countries[EP.user.user.username][stay.country.country_name][0] = stay.duration
                total_country_weight[stay.country.country_name] += stay.duration

            for stay in EducationCountryStay.objects.filter(user=EP.user):
                seen_countries.add(stay.country.country_name)
                countries[EP.user.user.username][stay.country.country_name][1] = stay.duration
                total_country_weight[stay.country.country_name] += stay.duration

            for UA in UserAnswer.objects.filter(experiment_participation=EP).select_subclasses():

                # -------------start---------------

                # word click time
                words_click_time = UA.words_click_time

                if E.foreign_language == 'XL':
                    AQ = MixedLanguagesGapFillingQuestion.objects.get(id=UA.answered_question.id)
                else:
                    AQ = GapFillingQuestion.objects.get(id=UA.answered_question.id)
                sentence = AQ.sentence
                ls_all_gaps, n_sentence = parseGapFillingQuestion(sentence)
                click_time_dict = getReadingTimeFromWordsClick(words_click_time)
                # print(click_time_dict)
                # print(words_click_time)
                normal_sentence = n_sentence.split()

                for i in range(1,len(normal_sentence)+1):
                    answer_date = UA.answer_date
                    reading_time=click_time_dict[i]-click_time_dict[i-1]
                    stimulus = normal_sentence[i-1]
                    X = [UA.answered_question.id, str(E.native_language), str(E.foreign_language), stimulus,reading_time, answer_date] + D
                    data.append(X)

        # add additional headers
        additional_headers = []
        lang_order = []
        for lang,w in sorted(total_lang_weight.items(), reverse=True):
            lang_order.append(lang)
            additional_headers.append("User Has Language "+lang)
            additional_headers.append(lang+" Spoken Where User Lives")
            additional_headers.append(lang+" Native")
            additional_headers.append(lang+" Used At Home")
            additional_headers.append(lang+" Learning Duration (years)")
            additional_headers.append(lang+" Exposure Through Living (years)")
            additional_headers.append(lang+" Reading")
            additional_headers.append(lang+" Writing")
            additional_headers.append(lang+" Listening")
            additional_headers.append(lang+" Speaking")

        country_order = []
        for country,w in sorted(total_country_weight.items(), reverse=True):
            country_order.append(country)
            additional_headers.append("Lived In "+country+" (years)")
            additional_headers.append("Went To School In "+country+" (years)")

        headers = headers + additional_headers

        # CW.writerow(headers)
        for d in data:
            # U = d[17]
            # print(len(d))
            U = d[14]
            if E.foreign_language !='XL':
                X = language_skills[U][E.foreign_language.language_name]
            else:
                X = language_skills[U][E.foreign_language]
            if X is None:
                d.append(0)
            else:
                d.append(1)

            for lang in lang_order:
                X = language_skills[U][lang]

                if X is None:
                    d.append(0)
                else:
                    d.append(1)

                if not X is None:
                    R, W, L, S, N, H, LIV, LEARN, LOC = X
                    d.append(LOC)
                    d.append(N)
                    d.append(H)
                    d.append(LEARN)
                    d.append(LIV)

                    if not R is None:
                        d.append(R)
                    else:
                        d.append(0)

                    if not W is None:
                        d.append(W)
                    else:
                        d.append(0)

                    if not L is None:
                        d.append(L)
                    else:
                        d.append(0)

                    if not S is None:
                        d.append(S)
                    else:
                        d.append(0)

                else:
                    d = d + [0]*9

            for country in country_order:
                LD, ED = countries[U][country]
                if LD is None:
                    d.append(0)
                else:
                    d.append(LD)

                if ED is None:
                    d.append(0)
                else:
                    d.append(ED)

            rows.append(d)
                # CW.writerow(d)


        return Fname, headers, rows
    except Exception as ex:
        print(str(ex))
        return ''


class QuestionAnswersXLSXExportView(View):
    def get(self, request, exp_id):
        try:
            #Fname = makeUserAnswersCSVFileForExperiment(exp_id)
            E = Experiment.objects.filter(pk=exp_id).select_subclasses()[0]
            #Fpath = EXPERIMENT_EXPORT_FILE_FOLDER+E.experiment_name.replace(" ", "_")+"_UserAnswers.csv"
            Fpath = EXPERIMENT_EXPORT_FILE_FOLDER+E.experiment_name.replace(" ", "_")+"_UserAnswers.xlsx"
            #Fname = E.experiment_name.replace(" ", "_")+"_UserAnswers.csv"
            Fname = E.experiment_name.replace(" ", "_")+"_UserAnswers.xlsx"

            response = HttpResponse(content_type='application/force-download') # mimetype is replaced by content_type for django 1.7
            response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(Fname)
            response['X-Sendfile'] = smart_str(Fpath)
            return response

        except Exception as e:
            return HttpResponse(str(e))

