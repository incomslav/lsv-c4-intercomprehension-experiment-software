__author__ = 'Muhammad Ahmad'

from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, HttpResponseRedirect
from django_datatables_view.base_datatable_view import BaseDatatableView
from ExperimentBasics.forms import *
from ExperimentBasics.models import *
from Users.models import *
from Users.enums import *
from django.contrib import messages
from django.db.models import Q


class NewsManagementView(View):
    """
        News Management view
    """

    def get(self, request, news_id=0):
        request.user.id = int(request.COOKIES.get(CookieFields.UserID, '0'))
        try:
            newsForm = NewsManagementForm()
            if news_id != 0:
                if News.objects.filter(id=news_id).exists():
                    news = News.objects.filter(id=news_id).get()

                    newsDict = {}
                    newsDict['news_id'] = news.id
                    if not news.news_description_en is None:
                        newsDict['txtNewsDescriptionEn'] = news.news_description_en
                    newsDict['txtNewsDescriptionDe'] = news.news_description_de
                    newsDict['txtNewsDescriptionRu'] = news.news_description_ru
                    newsDict['txtNewsDescriptionBg'] = news.news_description_bg
                    newsDict['txtNewsDescriptionUk'] = news.news_description_uk
                    newsDict['txtNewsDescriptionCs'] = news.news_description_cs
                    newsDict['txtNewsDescriptionPl'] = news.news_description_pl
                    newsDict['txtNewsDescriptionHr'] = news.news_description_hr
                    newsDict['txtNewsDescriptionSr'] = news.news_description_sr
                    newsDict['txtNewsDescriptionSk'] = news.news_description_sk
                    newsDict['txtNewsDescriptionMk'] = news.news_description_mk
                    newsDict['txtNewsDescriptionSl'] = news.news_description_sl
                    newsDict['txtNewsDescriptionBs'] = news.news_description_bs
                    newsDict['priority'] = news.priority

                    newsForm = NewsManagementForm(initial=newsDict)

            return render(request, 'adminpanel/NewsManagement.html',
                          {'form': newsForm})

        except Exception as e:
            return HttpResponse(str(e))

    def post(self, request, news_id=0):
        empty_form = NewsManagementForm()
        params = dict()
        if request.is_ajax():
            try:
                requestType = request.POST['type']
                # activate a news
                if requestType == '1':
                    news_id = int(request.POST['news_id'])
                    N = News.objects.get(pk=news_id)
                    N.is_active = True
                    N.save()
                    return HttpResponse(True)
                # deactivate a news
                if requestType == '2':
                    news_id = int(request.POST['news_id'])
                    N = News.objects.get(pk=news_id)
                    N.is_active = False
                    N.save()
                    return HttpResponse(True)

                # change a news's priority
                if requestType == '3':
                    news_id = int(request.POST['news_id'])
                    new_priority = int(request.POST['new_priority'])
                    N = News.objects.get(pk=news_id)
                    N.priority = new_priority
                    N.save()
                    return HttpResponse(True)

                # delete a news
                elif requestType == '10':
                    news_id = int(request.POST['news_id'])
                    N = News.objects.get(pk=news_id)
                    N.delete()
                    return HttpResponse(True)

                # delete all news
                elif requestType == '11':
                    N = News.objects.all()
                    for n in N:
                        n.delete()
                    return HttpResponse(True)

                return HttpResponse('Ajax request of unknown type.')
            except Exception as e:
                return HttpResponse(str(e))

        else:
            try:
                form = NewsManagementForm(request.POST)
                if form.is_valid():
                    form = form.cleaned_data

                    news_description_en = form['txtNewsDescriptionEn']
                    news_description_de = form['txtNewsDescriptionDe']
                    news_description_ru = form['txtNewsDescriptionRu']
                    news_description_bg = form['txtNewsDescriptionBg']
                    news_description_uk = form['txtNewsDescriptionUk']
                    news_description_cs = form['txtNewsDescriptionCs']
                    news_description_pl = form['txtNewsDescriptionPl']
                    news_description_hr = form['txtNewsDescriptionHr']
                    news_description_sr = form['txtNewsDescriptionSr']
                    news_description_sk = form['txtNewsDescriptionSk']
                    news_description_mk = form['txtNewsDescriptionMk']
                    news_description_sl = form['txtNewsDescriptionSl']
                    news_description_bs = form['txtNewsDescriptionBs']

                    priority = form['priority']

                    news_id = int(form['news_id'])

                    if news_description_en != '':
                        news = News()
                        if news_id != 0:
                            news = News.objects.get(pk=news_id)
                        news.news_description = news_description_en
                        news.news_description_en = news_description_en
                        news.news_description_de = news_description_de
                        news.news_description_ru = news_description_ru
                        news.news_description_bg = news_description_bg
                        news.news_description_uk = news_description_uk
                        news.news_description_cs = news_description_cs
                        news.news_description_pl = news_description_pl
                        news.news_description_hr = news_description_hr
                        news.news_description_sr = news_description_sr
                        news.news_description_sk = news_description_sk
                        news.news_description_mk = news_description_mk
                        news.news_description_sl = news_description_sl
                        news.news_description_bs = news_description_bs
                        news.priority = int(priority)
                        if news_id == 0:
                            news.is_active = True
                        news.created_by = UserInfo.objects.get(user=request.user)
                        news.save()
                    if news_id != 0:
                        return HttpResponseRedirect('/admin/NewsSectionManagement/')
                    return render(request, 'adminpanel/NewsManagement.html', {'form': empty_form})
                else:
                    messages.error(request, 'Please Enter News Description in English.')
                    return render(request, 'adminpanel/NewsManagement.html', params)

            except Exception as e:
                return HttpResponse(str(e))


class MultilingualGenderManagementView(View):
    """
        Multilingual Gender Management view
    """

    def get(self, request, gender_id=0):
        request.user.id = int(request.COOKIES.get(CookieFields.UserID, '0'))
        try:
            genderForm = MultilingualGenderManagementForm()
            if gender_id != 0:
                if Gender.objects.filter(id=gender_id).exists():
                    gender = Gender.objects.filter(id=gender_id).get()

                    genderDict = {}
                    genderDict['gender_id'] = gender.id
                    if not gender.name_en is None:
                        genderDict['txtGenderEn'] = gender.name_en
                    genderDict['txtGenderDe'] = gender.name_de
                    genderDict['txtGenderRu'] = gender.name_ru
                    genderDict['txtGenderBg'] = gender.name_bg
                    genderDict['txtGenderUk'] = gender.name_uk
                    genderDict['txtGenderCs'] = gender.name_cs
                    genderDict['txtGenderPl'] = gender.name_pl
                    genderDict['txtGenderHr'] = gender.name_hr
                    genderDict['txtGenderSr'] = gender.name_sr
                    genderDict['txtGenderSk'] = gender.name_sk
                    genderDict['txtGenderMk'] = gender.name_mk
                    genderDict['txtGenderSl'] = gender.name_sl
                    genderDict['txtGenderBs'] = gender.name_bs

                    genderForm = MultilingualGenderManagementForm(initial=genderDict)

            return render(request, 'adminpanel/GenderManagement.html',
                          {'form': genderForm})

        except Exception as e:
            return HttpResponse(str(e))

    def post(self, request, gender_id=0):
        empty_form = MultilingualGenderManagementForm()
        params = dict()
        try:
            form = MultilingualGenderManagementForm(request.POST)
            if form.is_valid():
                form = form.cleaned_data

                name_en = form['txtGenderEn']
                name_de = form['txtGenderDe']
                name_ru = form['txtGenderRu']
                name_bg = form['txtGenderBg']
                name_uk = form['txtGenderUk']
                name_cs = form['txtGenderCs']
                name_pl = form['txtGenderPl']
                name_hr = form['txtGenderHr']
                name_sr = form['txtGenderSr']
                name_sk = form['txtGenderSk']
                name_mk = form['txtGenderMk']
                name_sl = form['txtGenderSl']
                name_bs = form['txtGenderBs']

                gender_id = int(form['gender_id'])

                if name_en != '':

                    if gender_id != 0:
                        gender = Gender.objects.get(pk=gender_id)
                        gender.name = name_en
                        gender.name_en = name_en
                        gender.name_de = name_de
                        gender.name_ru = name_ru
                        gender.name_bg = name_bg
                        gender.name_uk = name_uk
                        gender.name_cs = name_cs
                        gender.name_pl = name_pl
                        gender.name_hr = name_hr
                        gender.name_sr = name_sr
                        gender.name_sk = name_sk
                        gender.name_mk = name_mk
                        gender.name_sl = name_sl
                        gender.name_bs = name_bs
                        gender.save()
                if gender_id != 0:
                    return HttpResponseRedirect('/admin/MultilingualGenderManagement/')
                return render(request, 'adminpanel/GenderManagement.html', {'form': empty_form})
            else:
                messages.error(request, 'Please Enter Gender in English.')
                return render(request, 'adminpanel/GenderManagement.html', params)

        except Exception as e:
            return HttpResponse(str(e))


class MultilingualEducationDegreesManagementView(View):
    """
        Multilingual Education Degrees Management view
    """

    def get(self, request, degree_id=0):
        request.user.id = int(request.COOKIES.get(CookieFields.UserID, '0'))
        try:
            degreeForm = MultilingualEducationDegreeManagementForm()
            if degree_id != 0:
                if EducationDegree.objects.filter(id=degree_id).exists():
                    degrees = EducationDegree.objects.filter(id=degree_id).get()

                    degreeDict = {}
                    degreeDict['degree_id'] = degrees.id
                    if not degrees.name_en is None:
                        degreeDict['txtEducationDegreeEn'] = degrees.name_en
                    degreeDict['txtEducationDegreeDe'] = degrees.name_de
                    degreeDict['txtEducationDegreeRu'] = degrees.name_ru
                    degreeDict['txtEducationDegreeBg'] = degrees.name_bg
                    degreeDict['txtEducationDegreeUk'] = degrees.name_uk
                    degreeDict['txtEducationDegreeCs'] = degrees.name_cs
                    degreeDict['txtEducationDegreePl'] = degrees.name_pl
                    degreeDict['txtEducationDegreeHr'] = degrees.name_hr
                    degreeDict['txtEducationDegreeSr'] = degrees.name_sr
                    degreeDict['txtEducationDegreeSk'] = degrees.name_sk
                    degreeDict['txtEducationDegreeMk'] = degrees.name_mk
                    degreeDict['txtEducationDegreeSl'] = degrees.name_sl
                    degreeDict['txtEducationDegreeBs'] = degrees.name_bs

                    degreeForm = MultilingualEducationDegreeManagementForm(initial=degreeDict)

            return render(request, 'adminpanel/EducationDegreeManagement.html',
                          {'form': degreeForm})

        except Exception as e:
            return HttpResponse(str(e))

    def post(self, request, degree_id=0):
        empty_form = MultilingualEducationDegreeManagementForm()
        params = dict()

        try:
            form = MultilingualEducationDegreeManagementForm(request.POST)
            if form.is_valid():
                form = form.cleaned_data

                name_en = form['txtEducationDegreeEn']
                name_de = form['txtEducationDegreeDe']
                name_ru = form['txtEducationDegreeRu']
                name_bg = form['txtEducationDegreeBg']
                name_uk = form['txtEducationDegreeUk']
                name_cs = form['txtEducationDegreeCs']
                name_pl = form['txtEducationDegreePl']
                name_hr = form['txtEducationDegreeHr']
                name_sr = form['txtEducationDegreeSr']
                name_sk = form['txtEducationDegreeSk']
                name_mk = form['txtEducationDegreeMk']
                name_sl = form['txtEducationDegreeSl']
                name_bs = form['txtEducationDegreeBs']

                degree_id = int(form['degree_id'])

                if name_en != '':
                    degree = EducationDegree()
                    if degree_id != 0:
                        degree = EducationDegree.objects.get(pk=degree_id)
                    degree.name = name_en
                    degree.name_en = name_en
                    degree.name_de = name_de
                    degree.name_ru = name_ru
                    degree.name_bg = name_bg
                    degree.name_uk = name_uk
                    degree.name_cs = name_cs
                    degree.name_pl = name_pl
                    degree.name_hr = name_hr
                    degree.name_sr = name_sr
                    degree.name_sk = name_sk
                    degree.name_mk = name_mk
                    degree.name_sl = name_sl
                    degree.name_bs = name_bs
                    degree.save()
                if degree_id != 0:
                    return HttpResponseRedirect('/admin/MultilingualEducationDegreeManagement/')
                return render(request, 'adminpanel/EducationDegreeManagement.html', {'form': empty_form})
            else:
                messages.error(request, 'Please Enter Education Degree in English.')
                return render(request, 'adminpanel/EducationDegreeManagement.html', params)

        except Exception as e:
            return HttpResponse(str(e))


class MultilingualLanguageManagementView(View):
    """
        Multilingual Language Management view
    """

    def get(self, request, language_id=0):
        request.user.id = int(request.COOKIES.get(CookieFields.UserID, '0'))
        try:
            languageForm = MultilingualLanguageManagementForm()
            if language_id != 0:
                if Language.objects.filter(language_id=language_id).exists():
                    language = Language.objects.filter(language_id=language_id).get()

                    languageDict = {}
                    languageDict['language_id'] = language.language_id
                    if not language.language_name_en is None:
                        languageDict['txtLanguageCode'] = language.language_code
                        languageDict['txtLanguageEn'] = language.language_name_en
                    languageDict['txtLanguageDe'] = language.language_name_de
                    languageDict['txtLanguageRu'] = language.language_name_ru
                    languageDict['txtLanguageBg'] = language.language_name_bg
                    languageDict['txtLanguageUk'] = language.language_name_uk
                    languageDict['txtLanguageCs'] = language.language_name_cs
                    languageDict['txtLanguagePl'] = language.language_name_pl
                    languageDict['txtLanguageHr'] = language.language_name_hr
                    languageDict['txtLanguageSr'] = language.language_name_sr
                    languageDict['txtLanguageSk'] = language.language_name_sk
                    languageDict['txtLanguageMk'] = language.language_name_mk
                    languageDict['txtLanguageSl'] = language.language_name_sl
                    languageDict['txtLanguageBs'] = language.language_name_bs

                    languageForm = MultilingualLanguageManagementForm(initial=languageDict)

            return render(request, 'adminpanel/LanguageManagement.html',
                          {'form': languageForm})

        except Exception as e:
            return HttpResponse(str(e))

    def post(self, request, language_id=0):
        empty_form = MultilingualLanguageManagementForm()

        try:
            form = MultilingualLanguageManagementForm(request.POST)
            if form.is_valid():
                form = form.cleaned_data

                language_code = str(form['txtLanguageCode']).strip()
                language_en = str(form['txtLanguageEn']).strip()
                language_de = form['txtLanguageDe']
                language_ru = form['txtLanguageRu']
                language_bg = form['txtLanguageBg']
                language_uk = form['txtLanguageUk']
                language_cs = form['txtLanguageCs']
                language_pl = form['txtLanguagePl']
                language_hr = form['txtLanguageHr']
                language_sr = form['txtLanguageSr']
                language_sk = form['txtLanguageSk']
                language_mk = form['txtLanguageMk']
                language_sl = form['txtLanguageSl']
                language_bs = form['txtLanguageBs']

                language_id = int(form['language_id'])

                if language_en != '' and language_code != '':
                    if len(Language.objects.filter(
                                    Q(language_code__iexact=language_code) | Q(
                                    language_name_en__iexact=language_en)).exclude(
                            language_id=language_id)) > 0:
                        messages.error(request, 'Language code or Language name already exists.')
                        return render(request, 'adminpanel/LanguageManagement.html',
                                      {'form': MultilingualLanguageManagementForm(initial=form)})
                    else:
                        language = Language()
                        if language_id != 0:
                            language = Language.objects.get(pk=language_id)
                        language.language_code = language_code
                        language.language_name = language_en
                        language.language_name_en = language_en
                        language.language_name_de = language_de
                        language.language_name_ru = language_ru
                        language.language_name_bg = language_bg
                        language.language_name_uk = language_uk
                        language.language_name_cs = language_cs
                        language.language_name_pl = language_pl
                        language.language_name_hr = language_hr
                        language.language_name_sr = language_sr
                        language.language_name_sk = language_sk
                        language.language_name_mk = language_mk
                        language.language_name_sl = language_sl
                        language.language_name_bs = language_bs
                        language.save()

                else:
                    messages.error(request, 'Please Enter Language Name in English.')
                    return render(request, 'adminpanel/LanguageManagement.html',
                                  {'form': MultilingualLanguageManagementForm(initial=form)})

                if language_id != 0:
                    return HttpResponseRedirect('/admin/MultilingualLanguageManagement/')

                messages.info(request, 'Saved Successfully.')
                return render(request, 'adminpanel/LanguageManagement.html',
                              {'form': empty_form})
            else:
                return render(request, 'adminpanel/LanguageManagement.html',
                              {'form': empty_form})

        except Exception as e:
            return HttpResponse(str(e))


class ExperimentInfoManagementView(View):
    """
        Experiment Info Management view
    """

    def get(self, request, experiment_info_id=0):
        request.user.id = int(request.COOKIES.get(CookieFields.UserID, '0'))
        try:
            experimentInfoForm = ExperimentInfoManagementForm()
            if experiment_info_id != 0:
                if ExperimentInfo.objects.filter(id=experiment_info_id).exists():
                    experiment_info = ExperimentInfo.objects.filter(id=experiment_info_id).get()

                    experiment_infoDict = {}
                    experiment_infoDict['experiment_info_id'] = experiment_info.id
                    if not experiment_info.experiment_info_en is None:
                        experiment_infoDict['txtExperimentInfoEn'] = experiment_info.experiment_info_en
                    experiment_infoDict['txtExperimentInfoDe'] = experiment_info.experiment_info_de
                    experiment_infoDict['txtExperimentInfoRu'] = experiment_info.experiment_info_ru
                    experiment_infoDict['txtExperimentInfoBg'] = experiment_info.experiment_info_bg
                    experiment_infoDict['txtExperimentInfoUk'] = experiment_info.experiment_info_uk
                    experiment_infoDict['txtExperimentInfoCs'] = experiment_info.experiment_info_cs
                    experiment_infoDict['txtExperimentInfoPl'] = experiment_info.experiment_info_pl
                    experiment_infoDict['txtExperimentInfoHr'] = experiment_info.experiment_info_hr
                    experiment_infoDict['txtExperimentInfoSr'] = experiment_info.experiment_info_sr
                    experiment_infoDict['txtExperimentInfoSk'] = experiment_info.experiment_info_sk
                    experiment_infoDict['txtExperimentInfoMk'] = experiment_info.experiment_info_mk
                    experiment_infoDict['txtExperimentInfoSl'] = experiment_info.experiment_info_sl
                    experiment_infoDict['txtExperimentInfoBs'] = experiment_info.experiment_info_bs

                    experimentInfoForm = ExperimentInfoManagementForm(initial=experiment_infoDict)

            return render(request, 'adminpanel/ExperimentInfoManagement.html',
                          {'form': experimentInfoForm})

        except Exception as e:
            return HttpResponse(str(e))

    def post(self, request, experiment_info_id=0):
        empty_form = ExperimentInfoManagementForm()
        params = dict()
        if request.is_ajax():
            try:
                requestType = request.POST['type']

                # delete an experiment_info
                if requestType == '1':
                    experiment_info_id = int(request.POST['experiment_info_id'])
                    N = ExperimentInfo.objects.get(pk=experiment_info_id)
                    N.delete()
                    return HttpResponse(True)

                # delete all experiment_info
                elif requestType == '2':
                    N = ExperimentInfo.objects.all()
                    for n in N:
                        n.delete()
                    return HttpResponse(True)

                return HttpResponse('Ajax request of unknown type.')
            except Exception as e:
                return HttpResponse(str(e))

        else:
            try:
                form = ExperimentInfoManagementForm(request.POST)
                if form.is_valid():
                    form = form.cleaned_data

                    experiment_info_en = form['txtExperimentInfoEn']
                    experiment_info_de = form['txtExperimentInfoDe']
                    experiment_info_ru = form['txtExperimentInfoRu']
                    experiment_info_bg = form['txtExperimentInfoBg']
                    experiment_info_uk = form['txtExperimentInfoUk']
                    experiment_info_cs = form['txtExperimentInfoCs']
                    experiment_info_pl = form['txtExperimentInfoPl']
                    experiment_info_hr = form['txtExperimentInfoHr']
                    experiment_info_sr = form['txtExperimentInfoSr']
                    experiment_info_sk = form['txtExperimentInfoSk']
                    experiment_info_mk = form['txtExperimentInfoMk']
                    experiment_info_sl = form['txtExperimentInfoSl']
                    experiment_info_bs = form['txtExperimentInfoBs']

                    experiment_info_id = int(form['experiment_info_id'])

                    if experiment_info_en != '':
                        experiment_info = ExperimentInfo()
                        if experiment_info_id != 0:
                            experiment_info = ExperimentInfo.objects.get(pk=experiment_info_id)
                        experiment_info.experiment_info = experiment_info_en
                        experiment_info.experiment_info_en = experiment_info_en
                        experiment_info.experiment_info_de = experiment_info_de
                        experiment_info.experiment_info_ru = experiment_info_ru
                        experiment_info.experiment_info_bg = experiment_info_bg
                        experiment_info.experiment_info_uk = experiment_info_uk
                        experiment_info.experiment_info_cs = experiment_info_cs
                        experiment_info.experiment_info_pl = experiment_info_pl
                        experiment_info.experiment_info_hr = experiment_info_hr
                        experiment_info.experiment_info_sr = experiment_info_sr
                        experiment_info.experiment_info_sk = experiment_info_sk
                        experiment_info.experiment_info_mk = experiment_info_mk
                        experiment_info.experiment_info_sl = experiment_info_sl
                        experiment_info.experiment_info_bs = experiment_info_bs

                        experiment_info.created_by = UserInfo.objects.get(user=request.user)
                        experiment_info.save()
                    if experiment_info_id != 0:
                        return HttpResponseRedirect('/admin/ExperimentInfoSectionManagement/')
                    return render(request, 'adminpanel/ExperimentInfoManagement.html', {'form': empty_form})
                else:
                    messages.error(request, 'Please Enter Experiment Info in English.')
                    return render(request, 'adminpanel/ExperimentInfoManagement.html', params)

            except Exception as e:
                return HttpResponse(str(e))


class InformedConsentManagementView(View):
    """
        Informed Consent Management view
    """

    def get(self, request, informed_consent_id=0):
        request.user.id = int(request.COOKIES.get(CookieFields.UserID, '0'))
        try:
            consentForm = InformedConsentManagementForm()
            if informed_consent_id != 0:
                if InformedConsent.objects.filter(id=informed_consent_id).exists():
                    consent = InformedConsent.objects.filter(id=informed_consent_id).get()

                    consentDict = {}
                    consentDict['informed_consent_id'] = consent.id
                    if not consent.consent_description_en is None:
                        consentDict['txtInformedConsentDescriptionEn'] = consent.consent_description_en
                    consentDict['txtInformedConsentDescriptionDe'] = consent.consent_description_de
                    consentDict['txtInformedConsentDescriptionRu'] = consent.consent_description_ru
                    consentDict['txtInformedConsentDescriptionBg'] = consent.consent_description_bg
                    consentDict['txtInformedConsentDescriptionUk'] = consent.consent_description_uk
                    consentDict['txtInformedConsentDescriptionCs'] = consent.consent_description_cs
                    consentDict['txtInformedConsentDescriptionPl'] = consent.consent_description_pl
                    consentDict['txtInformedConsentDescriptionHr'] = consent.consent_description_hr
                    consentDict['txtInformedConsentDescriptionSr'] = consent.consent_description_sr
                    consentDict['txtInformedConsentDescriptionSk'] = consent.consent_description_sk
                    consentDict['txtInformedConsentDescriptionMk'] = consent.consent_description_mk
                    consentDict['txtInformedConsentDescriptionSl'] = consent.consent_description_sl
                    consentDict['txtInformedConsentDescriptionBs'] = consent.consent_description_bs
                    consentDict['priority'] = consent.priority

                    consentForm = InformedConsentManagementForm(initial=consentDict)

            return render(request, 'adminpanel/InformedConsentManagement.html',
                          {'form': consentForm})

        except Exception as e:
            return HttpResponse(str(e))

    def post(self, request, informed_consent_id=0):
        empty_form = InformedConsentManagementForm()
        params = dict()
        if request.is_ajax():
            try:
                requestType = request.POST['type']
                # activate a consent
                if requestType == '1':
                    informed_consent_id = int(request.POST['informed_consent_id'])
                    N = InformedConsent.objects.get(pk=informed_consent_id)
                    N.is_active = True
                    N.save()
                    return HttpResponse(True)
                # deactivate a consent
                if requestType == '2':
                    informed_consent_id = int(request.POST['informed_consent_id'])
                    N = InformedConsent.objects.get(pk=informed_consent_id)
                    N.is_active = False
                    N.save()
                    return HttpResponse(True)

                # change a consent's priority
                if requestType == '3':
                    informed_consent_id = int(request.POST['informed_consent_id'])
                    consent_priority = int(request.POST['consent_priority'])
                    N = InformedConsent.objects.get(pk=informed_consent_id)
                    N.priority = consent_priority
                    N.save()
                    return HttpResponse(True)

                # delete a consent
                elif requestType == '10':
                    informed_consent_id = int(request.POST['informed_consent_id'])
                    N = InformedConsent.objects.get(pk=informed_consent_id)
                    N.delete()
                    return HttpResponse(True)

                # delete all consents
                elif requestType == '11':
                    N = InformedConsent.objects.all()
                    for n in N:
                        n.delete()
                    return HttpResponse(True)

                return HttpResponse('Ajax request of unknown type.')
            except Exception as e:
                return HttpResponse(str(e))

        else:
            try:
                form = InformedConsentManagementForm(request.POST)
                if form.is_valid():
                    form = form.cleaned_data

                    consent_description_en = form['txtInformedConsentDescriptionEn']
                    consent_description_de = form['txtInformedConsentDescriptionDe']
                    consent_description_ru = form['txtInformedConsentDescriptionRu']
                    consent_description_bg = form['txtInformedConsentDescriptionBg']
                    consent_description_uk = form['txtInformedConsentDescriptionUk']
                    consent_description_cs = form['txtInformedConsentDescriptionCs']
                    consent_description_pl = form['txtInformedConsentDescriptionPl']
                    consent_description_hr = form['txtInformedConsentDescriptionHr']
                    consent_description_sr = form['txtInformedConsentDescriptionSr']
                    consent_description_sk = form['txtInformedConsentDescriptionSk']
                    consent_description_mk = form['txtInformedConsentDescriptionMk']
                    consent_description_sl = form['txtInformedConsentDescriptionSl']
                    consent_description_bs = form['txtInformedConsentDescriptionBs']

                    priority = form['priority']

                    informed_consent_id = int(form['informed_consent_id'])

                    if consent_description_en != '':
                        consent = InformedConsent()
                        if informed_consent_id != 0:
                            consent = InformedConsent.objects.get(pk=informed_consent_id)
                        consent.consent_description = consent_description_en
                        consent.consent_description_en = consent_description_en
                        consent.consent_description_de = consent_description_de
                        consent.consent_description_ru = consent_description_ru
                        consent.consent_description_bg = consent_description_bg
                        consent.consent_description_uk = consent_description_uk
                        consent.consent_description_cs = consent_description_cs
                        consent.consent_description_pl = consent_description_pl
                        consent.consent_description_hr = consent_description_hr
                        consent.consent_description_sr = consent_description_sr
                        consent.consent_description_sk = consent_description_sk
                        consent.consent_description_mk = consent_description_mk
                        consent.consent_description_sl = consent_description_sl
                        consent.consent_description_bs = consent_description_bs
                        consent.priority = int(priority)
                        if informed_consent_id == 0:
                            consent.is_active = True
                        consent.created_by = UserInfo.objects.get(user=request.user)
                        consent.save()
                    if informed_consent_id != 0:
                        return HttpResponseRedirect('/admin/InformedConsentManagement/')
                    return render(request, 'adminpanel/InformedConsentManagement.html', {'form': empty_form})
                else:
                    messages.error(request, 'Please Enter Informed Consent Description in English.')
                    return render(request, 'adminpanel/InformedConsentManagement.html', params)

            except Exception as e:
                return HttpResponse(str(e))


class NewsManagementGridView(BaseDatatableView):
    """
    Grid view for all news
    """
    model = News

    # define the columns that will be returned
    columns = ['id', 'news_description_en', 'is_active', 'priority', 'created_on', 'update', 'delete']
    order_columns = ['id', 'news_description_en', 'is_active', 'priority', 'created_on', 'update', 'delete']

    max_display_length = 20

    def get_initial_queryset(self):
        # get initial data
        return News.objects.all()

    def render_column(self, item, column):
        if column == 'delete':
            return "<a onclick='deleteNews({});' >delete</a>".format(item.id)
        if column == 'update':
            return "<a onclick='redirectTo(\"admin/NewsSectionManagement/" + str(item.id) + "/\");' >update</a>"
        # make activation status into a checkbox
        if column == 'is_active':
            if item.is_active:
                return '<input id="is_active_input_' + str(
                    item.id) + '" type="checkbox" onclick="changeActivationStatus({}, true)" '.format(
                    item.id) + "checked >"
            else:
                return '<input id="is_active_input_' + str(
                    item.id) + ';" type="checkbox" onclick="changeActivationStatus({}, false)" '.format(item.id) + " >"

        elif column == 'priority':
            return '<input id="priority_input_' + str(
                item.id) + '" style="width:50px" type="number" step="1" min="0" max="10" value="' + str(
                item.priority) + '" > <a onclick="changePriority(' + str(item.id) + ')">save</a>'
        else:
            return super(NewsManagementGridView, self).render_column(item, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(news_description_en__istartswith=search.strip())
            return qs
        else:
            return qs


class MultilingualGenderManagementGridView(BaseDatatableView):
    """
    Grid view for all gender
    """
    model = Gender

    # define the columns that will be returned
    columns = ['name_en', 'code', 'update']
    order_columns = ['name_en', 'code', 'update']

    max_display_length = 5

    def get_initial_queryset(self):
        # get initial data
        return Gender.objects.all()

    def render_column(self, item, column):
        if column == 'update':
            return "<a onclick='redirectTo(\"admin/MultilingualGenderManagement/" + str(item.id) + "/\");' >update</a>"
        else:
            return super(MultilingualGenderManagementGridView, self).render_column(item, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(name_en__istartswith=search.strip())
            return qs
        else:
            return qs


class MultilingualEducationDegreeManagementGridView(BaseDatatableView):
    """
    Grid view for all education degree
    """
    model = EducationDegree

    # define the columns that will be returned
    columns = ['name_en', 'update']
    order_columns = ['name_en', 'update']

    max_display_length = 10

    def get_initial_queryset(self):
        # get initial data
        return EducationDegree.objects.all()

    def render_column(self, item, column):
        if column == 'update':
            return "<a onclick='redirectTo(\"admin/MultilingualEducationDegreeManagement/" + str(
                item.id) + "/\");' >update</a>"
        else:
            return super(MultilingualEducationDegreeManagementGridView, self).render_column(item, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(name_en__istartswith=search.strip())
            return qs
        else:
            return qs


class MultilingualLanguageManagementGridView(BaseDatatableView):
    """
    Grid view for all languages
    """
    model = Language

    # define the columns that will be returned
    columns = ['language_name_en', 'language_code', 'update']
    order_columns = ['language_name_en', 'language_code', 'update']

    max_display_length = 10

    def get_initial_queryset(self):
        # get initial data
        return Language.objects.all()

    def render_column(self, item, column):
        if column == 'update':
            return "<a onclick='redirectTo(\"admin/MultilingualLanguageManagement/" + str(
                item.language_id) + "/\");' >update</a>"
        else:
            return super(MultilingualLanguageManagementGridView, self).render_column(item, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(language_name__istartswith=search.strip())
            return qs
        else:
            return qs


class MultilingualExperimentInfoManagementGridView(BaseDatatableView):
    """
    Grid view for all news
    """
    model = ExperimentInfo

    # define the columns that will be returned
    columns = ['id', 'experiment_info_en', 'created_on', 'update', 'delete']
    order_columns = ['id', 'experiment_info_en', 'created_on', 'update', 'delete']

    max_display_length = 20

    def get_initial_queryset(self):
        # get initial data
        return ExperimentInfo.objects.all()

    def render_column(self, item, column):
        if column == 'experiment_info_en':
            st = "<table>" \
                 "<tr><td>English:</td><td>{}</td></tr>" \
                 "<tr><td>German:</td><td>{}</td></tr>" \
                 "<tr><td>Russian:</td><td>{}</td></tr>" \
                 "<tr><td>Bulgarian:</td><td>{}</td></tr>" \
                 "<tr><td>Ukrainian:</td><td>{}</td></tr>" \
                 "<tr><td>Czech:</td><td>{}</td></tr>" \
                 "<tr><td>Polish:</td><td>{}</td></tr>" \
                 "<tr><td>Croatian:</td><td>{}</td></tr>" \
                 "<tr><td>Bosnian:</td><td>{}</td></tr>" \
                 "<tr><td>Serbian:</td><td>{}</td></tr>" \
                 "<tr><td>Slovak:</td><td>{}</td></tr>" \
                 "<tr><td>Macedonian:</td><td>{}</td></tr>" \
                 "<tr><td>Slovenian:</td><td>{}</td></tr>" \
                 "</table>"
            return st.format(item.experiment_info_en, item.experiment_info_de, item.experiment_info_ru,
                             item.experiment_info_bg, item.experiment_info_uk, item.experiment_info_cs,
                             item.experiment_info_pl, item.experiment_info_hr, item.experiment_info_bs,item.experiment_info_sr,
                             item.experiment_info_sk, item.experiment_info_mk, item.experiment_info_sl)
        elif column == 'delete':
            return "<a onclick='deleteExperimentInfo({});' >delete</a>".format(item.id)
        elif column == 'update':
            return "<a onclick='redirectTo(\"admin/ExperimentInfoSectionManagement/" + str(
                item.id) + "/\");' >update</a>"
        elif column=='created_on':
            return item.created_on.strftime("%d-%m-%Y")
        else:
            return super(MultilingualExperimentInfoManagementGridView, self).render_column(item, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(experiment_info_en__istartswith=search.strip())
            return qs
        else:
            return qs


class InformedConsentManagementGridView(BaseDatatableView):
    """
    Grid view for all news
    """
    model = InformedConsent()

    # define the columns that will be returned
    columns = ['id', 'consent_description_en', 'is_active', 'priority', 'created_on', 'update', 'delete']
    order_columns = ['id', 'consent_description_en', 'is_active', 'priority', 'created_on', 'update', 'delete']

    max_display_length = 20

    def get_initial_queryset(self):
        # get initial data
        return InformedConsent.objects.all()

    def render_column(self, item, column):
        if column == 'delete':
            return "<a onclick='deleteInformedConsent({});' >delete</a>".format(item.id)
        if column == 'update':
            return "<a onclick='redirectTo(\"admin/InformedConsentManagement/" + str(item.id) + "/\");' >update</a>"
        # make activation status into a checkbox
        if column == 'is_active':
            if item.is_active:
                return '<input id="is_active_input_' + str(
                    item.id) + '" type="checkbox" onclick="changeActivationStatus({}, true)" '.format(
                    item.id) + "checked >"
            else:
                return '<input id="is_active_input_' + str(
                    item.id) + ';" type="checkbox" onclick="changeActivationStatus({}, false)" '.format(item.id) + " >"

        elif column == 'priority':
            return '<input id="priority_input_' + str(
                item.id) + '" style="width:50px" type="number" step="1" min="0" max="10" value="' + str(
                item.priority) + '" > <a onclick="changePriority(' + str(item.id) + ')">save</a>'
        else:
            return super(InformedConsentManagementGridView, self).render_column(item, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(consent_description_en__istartswith=search.strip())
            return qs
        else:
            return qs