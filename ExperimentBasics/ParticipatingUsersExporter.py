
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.utils.encoding import smart_str

from .exporter import *

import csv

from django.conf import *

from openpyxl import Workbook
from openpyxl.styles import Font
# from openpyxl.worksheet.write_only import WriteOnlyCell

def makeParticipatingUsersCSVFileForExperiment(exp_id):
    try:
        E = Experiment.objects.filter(pk=exp_id).select_subclasses()[0]
        Fname = EXPERIMENT_EXPORT_FILE_FOLDER+E.experiment_name.replace(" ", "_")+"_ParticipatingUsers.csv"

        nlang = E.native_language
        flang = E.foreign_language

        with open(Fname, "w", encoding="utf-8") as f:
            CW = csv.writer(f)

            headers = []
            headers.append("Participation Start Date")
            headers.append("Participation Finish Date")
            headers.append("Participation Rank")
            headers.append("User Account Name")
            # Removing the User Mail exporting due to privacy issues.
            #headers.append("User Mail")
            headers.append("User Age")
            headers.append("User Gender")
            headers.append("User Living Location")
            headers.append("User Living Duration (years)")
            # add 2 new columns for user highest education degree and does user has linguistic degree
            headers.append("User Highest Education Degree")
            headers.append("User Has Linguistic Degree")

            headers.append("User Knows Stimulus Language")

            data = []
            seen_langs = set([])
            seen_countries = set([])

            language_skills = defaultdict(lambda: defaultdict(lambda: None )) # user -> language -> (reading, writing, listening, speaking, native, used_at_home, exposure_duration_through_living, exposure_duration_through_learning, spoken_at_user_location)
            countries = defaultdict(lambda: defaultdict(lambda: [None,None])) # user -> country -> (living duration, education duration)
            user_answers = defaultdict(lambda: defaultdict(lambda: (None, None, None, None, None, None, None, None))) # user -> question ID -> given answer, abs correct yes/no, norm correct yes/no, total time, initial hesitation, typing time, submission hesitation

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
                # Removing due to privacy issues
                #D.append(EP.user.user.email)
                D.append(EP.user.age)
                D.append(EP.user.gender.code)
                D.append(EP.user.location.country_name)
                D.append(EP.user.location_living_duration)

                # 2 new columns for user highest education degree and does user has linguistic degree
                D.append(EP.user.highest_education_degree)
                linguistic_degree =0
                if EP.user.degree_in_linguistics:
                    linguistic_degree = 1
                D.append(linguistic_degree)

                for skill in UserLanguageSkill.objects.filter(user=EP.user):
                    seen_langs.add(skill.language.language_name)

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

                    #print(skill.language,skill.reading_level,skill.writing_level,skill.listening_level,skill.speaking_level)
                    language_skills[EP.user.user.username][skill.language.language_name] = (skill.reading_level, skill.writing_level, skill.listening_level, skill.speaking_level, native, home, skill.exposure_through_living, skill.exposure_through_learning, location_lang)

                for stay in LivingCountryStay.objects.filter(user=EP.user):
                    seen_countries.add(stay.country.country_name)
                    countries[EP.user.user.username][stay.country.country_name][0] = stay.duration
                    total_country_weight[stay.country.country_name] += stay.duration

                for stay in EducationCountryStay.objects.filter(user=EP.user):
                    seen_countries.add(stay.country.country_name)
                    countries[EP.user.user.username][stay.country.country_name][1] = stay.duration
                    total_country_weight[stay.country.country_name] += stay.duration

                data.append(D)

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
                U = d[3]

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
                        #d.append("NAT"+str(N))
                        d.append(N)
                        #d.append("HOME"+str(H))
                        d.append(H)
                        #d.append("LEARN"+str(LEARN))
                        d.append(LEARN)
                        #d.append("LIV"+str(LIV))
                        d.append(LIV)
                        #d.append("LOC"+str(LOC))
                        d.append(LOC)
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

                    else:
                        d = d + [0]*9

                for country in country_order:
                    LD, ED = countries[U][country]
                    if LD is None:
                        #d.append("LIVDUR0")
                        d.append(0)

                    else:
                        d.append(LD)
                        #d.append("LIVDUR"+str(LD))

                    if ED is None:
                        d.append(0)
                        #d.append("EDUDUR0")

                    else:
                        d.append(ED)
                        #d.append("EDUDUR"+str(ED))

                CW.writerow(d)

        return Fname
    except Exception as ex:
        print(str(ex))
        return ''



class ParticipatingUsersCSVExportView(View):
    def get(self, request, exp_id):
        try:
            makeParticipatingUsersCSVFileForExperiment(exp_id)
        except Exception as ex:
            return HttpResponse(str(ex))
        try:
            E = Experiment.objects.filter(pk=exp_id).select_subclasses()[0]
            Fpath = EXPERIMENT_EXPORT_FILE_FOLDER+E.experiment_name.replace(" ", "_")+"_ParticipatingUsers.csv"
            Fname = E.experiment_name.replace(" ", "_")+"_ParticipatingUsers.csv"

            with open(Fpath, "r", encoding="utf-8") as f:
                response = HttpResponse(f, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename={}'.format(Fname)
                return response
        
        except Exception as e:
            return HttpResponse(str(e))
        




class ParticipatingUsersXLSXExportView(View):
    def get(self, request, exp_id):
        try:
            E = Experiment.objects.filter(pk=exp_id).select_subclasses()[0]
            Fpath = EXPERIMENT_EXPORT_FILE_FOLDER+E.experiment_name.replace(" ", "_")+"_ParticipatingUsers.xlsx"
            Fname = E.experiment_name.replace(" ", "_")+"_ParticipatingUsers.xlsx"
            
            response = HttpResponse(content_type='application/force-download') # mimetype is replaced by content_type for django 1.7
            response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(Fname)
            response['X-Sendfile'] = smart_str(Fpath)
            return response
        
        except Exception as e:
            return HttpResponse(str(e))
        
