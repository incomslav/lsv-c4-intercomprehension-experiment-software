from django.core.mail import send_mail
from django.shortcuts import render, redirect, render_to_response
from django.views.generic import View
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import hashers, login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.utils.translation import ugettext_lazy as _
from django.core import serializers
from django.core.validators import EmailValidator, validate_email
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template import loader
from Incomslav.settings import DEFAULT_FROM_EMAIL
import json
from datetime import datetime

from Common.Enums import *
from Common.constants import *

from Users.forms import *
from Users.enums import *
from Users.models import *
from ExperimentBasics.models import InformedConsent

def createUserAccount(email, password, name):
    try:
        if not User.objects.filter(username=email).exists():
            user = User()
            user.username = name
            user.email = email
            user.password = hashers.make_password(password)
            user.save()
            authUser = authenticate(
                username=user.username,
                password=password
            )
            return user.id, authUser
        else:
            return 0, 'AlreadyExists'

    except Exception as e:
        return str(e), None


def generateHtmlForAreaLanguage(divId, languageName, languageId):
    res = []
    res.append("<div class='row' id='")
    res.append(divId)
    res.append("'>")
    res.append("<div class='col-md-4 col-xs-10'>")
    res.append("<label style='background-color:#F5F5F5; font-size:13px;' class='form-control'>")
    res.append(languageName)
    res.append("</label>")
    res.append("</div>")
    res.append("<div class='col-md-1 col-xs-2' style='padding:0px;'>")
    res.append(
        "<a class='pointer' title='{0}' onclick ='deleteAreaLanguage(".format(CommonConstants.DELETE_BUTTON_TEXT))
    res.append(divId)
    res.append(",")
    res.append(str(languageId))
    res.append(",")
    res.append(str(LanguageType.LivingAreaLanguage))
    res.append(");' >")
    res.append("<img src='/static/images/delete.jpg' style='height:35px;'>")
    res.append("</a>")
    res.append("</div>")
    res.append("</div>")

    return ''.join(res)


def generateHtmlForAnotherAreaLanguage(divId, languageName, livingYear, languageId):
    res = []
    res.append("<div class='row another_area' id='")
    res.append(divId)
    res.append("'>")
    res.append("<div class='col-md-4 col-xs-8'>")
    res.append("<label style='background-color:#F5F5F5; font-size:13px;' class='form-control'>")
    res.append(languageName)
    res.append("</label>")
    res.append("</div>")
    res.append("<div class='col-md-1 col-xs-2'>")
    res.append("<label style='background-color:#F5F5F5; font-size:13px;' class='form-control'>")
    res.append(livingYear)
    res.append("</label>")
    res.append("</div>")
    res.append("<div class='col-md-1 col-xs-2' style='padding:0px;'>")
    res.append("<a title='{0}' onclick ='deleteAnotherAreaLanguage(".format(CommonConstants.DELETE_BUTTON_TEXT))
    res.append(divId)
    res.append(",")
    res.append(str(languageId))
    res.append(",")
    res.append(str(LanguageType.AnotherAreaLanguage))
    res.append(");' >")
    res.append("<img src='/static/images/delete.jpg' style='height:35px;'>")
    res.append("</a>")
    res.append("</div></div>")
    return ''.join(res)


def generateHtmlForNativeLanguage(divId, languageName, languageId):
    res = []
    res.append("<div class='row multilingual ' id='")
    res.append(divId)
    res.append("'>")
    res.append("<div class='col-md-4 col-xs-10'>")
    res.append("<label style='background-color:#F5F5F5; font-size:13px;' class='form-control'>")
    res.append(languageName)
    res.append("</label>")
    res.append("</div>")
    res.append("<div class='col-md-1 col-xs-2' style='padding:0px;'>")
    res.append("<a title='{0}' onclick ='deleteNativeLanguage(".format(CommonConstants.DELETE_BUTTON_TEXT))
    res.append(divId)
    res.append(",")
    res.append(str(languageId))
    res.append(",")
    res.append(str(LanguageType.NativeLanguage))
    res.append(");' >")
    res.append("<img src='/static/images/delete.jpg' style='height:35px;'>")
    res.append("</a>")
    res.append("</div></div>")
    return ''.join(res)


def generateHtmlForEducationCountry(divId, countryName, educationYear, countryId):
    res = []
    res.append("<div class='row' id='")
    res.append(divId)
    res.append("'>")
    res.append("<div class='col-md-4 col-xs-8'>")
    res.append("<label style='background-color:#F5F5F5; font-size:13px;' class='form-control'>")
    res.append(countryName)
    res.append("</label>")
    res.append("</div>")
    res.append("<div class='col-md-1 col-xs-2'>")
    res.append("<label style='background-color:#F5F5F5; font-size:13px;' class='form-control'>")
    res.append(educationYear)
    res.append("</label>")
    res.append("</div>")
    res.append("<div class='col-md-1 col-xs-2' style='padding:0px;'>")
    res.append(
        "<a title='{0}' onclick ='deleteEducationCountry(".format(CommonConstants.DELETE_BUTTON_TEXT))
    res.append(divId)
    res.append(",")
    res.append(str(countryId))
    res.append(");' >")
    res.append("<img src='/static/images/delete.jpg' style='height:35px;'>")
    res.append("</a>")
    res.append("</div></div>")
    return ''.join(res)


def generateHtmlForHomeLanguage(divId, languageName, languageId):
    res = []
    res.append("<div class='row' id='")
    res.append(divId)
    res.append("'>")
    res.append("<div class='col-md-4 col-xs-10'>")
    res.append("<label style='background-color:#F5F5F5; font-size:13px;' class='form-control'>")
    res.append(languageName)
    res.append("</label>")
    res.append("</div>")
    res.append("<div class='col-md-1 col-xs-2' style='padding:0px;'>")
    res.append("<a title='{0}' onclick ='deleteHomeLanguage(".format(CommonConstants.DELETE_BUTTON_TEXT))
    res.append(divId)
    res.append(",")
    res.append(str(languageId))
    res.append(",")
    res.append(str(LanguageType.HomeLanguage))
    res.append(");' >")
    res.append("<img src='/static/images/delete.jpg' style='height:35px;'>")
    res.append("</a>")
    res.append("</div></div>")
    return ''.join(res)


def generateHtmlForLearnedLanguage(divId, languageName, learningTime, languageId):
    res = []
    res.append("<div class='row' id='")
    res.append(divId)
    res.append("'>")
    res.append("<div class='col-md-4 col-xs-8'>")
    res.append("<label style='background-color:#F5F5F5; font-size:13px;' class='form-control'>")
    res.append(languageName)
    res.append("</label>")
    res.append("</div>")
    res.append("<div class='col-md-1 col-xs-2'>")
    res.append("<label style='background-color:#F5F5F5; font-size:13px;' class='form-control'>")
    res.append(learningTime)
    res.append("</label>")
    res.append("</div>")
    res.append("<div class='col-md-1 col-xs-2' style='padding:0px;'>")
    res.append(
        "<a title='{0}' onclick ='deleteLearnedLanguage(".format(CommonConstants.DELETE_BUTTON_TEXT))
    res.append(divId)
    res.append(",")
    res.append(str(languageId))
    res.append(",")
    res.append(str(LanguageType.LearnedLanguage))
    res.append(");' >")
    res.append("<img src='/static/images/delete.jpg' style='height:35px;'>")
    res.append("</a>")
    res.append("</div></div>")
    return ''.join(res)


def setUserGender(userInfo, gender):
    userInfo.gender = gender
    userInfo.save()


def setUserCountry(userInfo, area_country):
    userInfo.location = area_country
    userInfo.save()


def setUserLanguageSkills(userInfo, languageId, readingLevel, writingLevel, listeningLevel, speakingLevel):
    lang = Language.objects.get(language_id=languageId)
    language_skill, created = UserLanguageSkill.objects.get_or_create(user=userInfo, language=lang)
    language_skill.reading_level = max(0, readingLevel)
    language_skill.writing_level = max(0, writingLevel)
    language_skill.listening_level = max(0, listeningLevel)
    language_skill.speaking_level = max(0, speakingLevel)
    # language_skill.speaking_level = None
    language_skill.save()
    return "language" + lang.language_name + " skills set to: reading=" + str(
        language_skill.reading_level) + ", writing=" + str(language_skill.writing_level) + ", listening=" + str(
        language_skill.listening_level) + ", speaking=" + str(language_skill.speaking_level)
    return not created


def setUserHighestEducationDegree(userInfo, educationDegree):
    userInfo.highest_education_degree = educationDegree
    userInfo.save()


def addUserLocationLanguage(userInfo, area_language):
    language_skill, created = UserLanguageSkill.objects.get_or_create(user=userInfo, language=area_language)
    was_not_location_language = not language_skill.spoken_at_user_location
    language_skill.spoken_at_user_location = True
    language_skill.save()
    return created or was_not_location_language


def addUserLocationLanguageByID(userInfo, area_language):
    area_language = Language.objects.get(language_id=area_language)
    return addUserLocationLanguage(userInfo, area_language)


def deleteUserLocationLanguage(userInfo, area_language):
    language_skill, created = UserLanguageSkill.objects.get_or_create(user=userInfo, language=area_language)
    language_skill.spoken_at_user_location = False
    language_skill.save_or_delete()
    return not created


def deleteUserLocationLanguageByID(userInfo, area_language):
    lang = Language.objects.get(language_id=area_language)
    return deleteUserLocationLanguage(userInfo, lang)


def deleteUserNativeLanguage(userInfo, language):
    language_skill, created = UserLanguageSkill.objects.get_or_create(user=userInfo, language=language,
                                                                      is_native_language=True)
    if not created:
        language_skill.is_native_language = False
        language_skill.save_or_delete()
    return not created


def deleteUserNativeLanguageByID(userInfo, language):
    lang = Language.objects.get(language_id=language)
    return deleteUserNativeLanguage(userInfo, lang)


def setUserLanguageToNative(userInfo, native_language):
    language_skill, created = UserLanguageSkill.objects.get_or_create(user=userInfo, language=native_language)
    was_native = language_skill.is_native_language
    language_skill.is_native_language = True
    language_skill.save()
    return created or not was_native


def setUserLanguageToNativeByID(userInfo, native_language):
    lang = Language.objects.get(language_id=native_language)
    return setUserLanguageToNative(userInfo, lang)


def deleteUserHomeLanguage(userInfo, language):
    language_skill, created = UserLanguageSkill.objects.get_or_create(user=userInfo, language=language,
                                                                      used_at_home=True)
    if not created:
        language_skill.used_at_home = False
        language_skill.save_or_delete()
    return not created


def deleteUserHomeLanguageByID(userInfo, languageID):
    lang = Language.objects.get(language_id=languageID)
    return deleteUserHomeLanguage(userInfo, lang)


def setUserLanguageUsedAtHome(userInfo, home_language):
    language_skill, created = UserLanguageSkill.objects.get_or_create(user=userInfo, language=home_language)
    was_used_at_home = language_skill.used_at_home
    language_skill.used_at_home = True
    language_skill.save()
    return created or not was_used_at_home


def setUserLanguageUsedAtHomeByID(userInfo, home_languageID):
    lang = Language.objects.get(language_id=home_languageID)
    return setUserLanguageUsedAtHome(userInfo, lang)


def deleteAllUserLanguageExposuresThroughLiving(userInfo):
    for language_skill in UserLanguageSkill.objects.filter(user=userInfo).all():
        language_skill.exposure_through_living = None
        language_skill.save_or_delete()


def deleteUserLanguageExposureThroughLivingByID(userInfo, language):
    lang = Language.objects.get(language_id=language)
    language_skill, created = UserLanguageSkill.objects.get_or_create(user=userInfo, language=lang)
    if not created:
        language_skill.exposure_through_living = None
        language_skill.save_or_delete()
    return not created


def addUserLanguageExposureThroughLiving(userInfo, language, duration):
    if duration <= 0.0:
        return False
    language_skill, created = UserLanguageSkill.objects.get_or_create(user=userInfo, language=language)
    not_lived_before = language_skill.exposure_through_living is None
    language_skill.exposure_through_living = duration
    language_skill.save()
    return created or not_lived_before


def addUserLanguageExposureThroughLivingByID(userInfo, language, duration):
    if duration <= 0.0:
        return False
    language = Language.objects.get(language_id=language)
    return addUserLanguageExposureThroughLiving(userInfo, language, duration)


def deleteUserLanguageExposureThroughLearningByID(userInfo, language):
    lang = Language.objects.get(language_id=language)
    language_skill, created = UserLanguageSkill.objects.get_or_create(user=userInfo, language=lang)
    if not created:
        language_skill.exposure_through_learning = None
        language_skill.save_or_delete()
    return not created


def deleteUserLocationLanguageByID(userInfo, language):
    lang = Language.objects.get(language_id=language)
    language_skill, created = UserLanguageSkill.objects.get_or_create(user=userInfo, language=lang)
    was_spoken_at_user_location = language_skill.spoken_at_user_location
    language_skill.spoken_at_user_location = False
    language_skill.save_or_delete()
    return not was_spoken_at_user_location


def addUserLanguageExposureThroughLearning(userInfo, language, duration):
    if duration <= 0.0:
        return False
    language_skill, created = UserLanguageSkill.objects.get_or_create(user=userInfo, language=language)
    previously_not_learned = language_skill.exposure_through_learning is None
    language_skill.exposure_through_learning = duration
    language_skill.save()
    return created or previously_not_learned


def addUserLanguageExposureThroughLearningByID(userInfo, language, duration):
    lang = Language.objects.get(language_id=language)
    return addUserLanguageExposureThroughLearning(userInfo, lang, duration)


def deleteUserEducationCountryStayByID(userInfo, education_country):
    country = Country.objects.get(country_id=education_country)
    stay, created = EducationCountryStay.objects.get_or_create(user=userInfo, country=country)
    if not created:
        stay.delete()


def addUserEducationCountryStay(userInfo, education_country, education_time):
    if education_time <= 0.0:
        return False
    stay, created = EducationCountryStay.objects.get_or_create(user=userInfo, country=education_country)
    stay.duration = float(education_time)
    stay.save()
    return created


def addUserEducationCountryStayByID(userInfo, education_country, education_time):
    education_country = Country.objects.get(country_id=education_country)
    return addUserEducationCountryStay(userInfo, education_country, education_time)


class UserInfoFormView(View):
    """ View for user to enter his/her background information. """

    def get(self, request):
        userForm = UserInfoForm(languageCode=request.LANGUAGE_CODE)
        try:
            if request.user.is_authenticated():
                if UserInfo.objects.filter(user=request.user).exists():
                    userInfo = UserInfo.objects.filter(user=request.user).get()

                    userInfoDict = {}
                    if not userInfo.age is None:
                        userInfoDict['age'] = userInfo.age
                    if not userInfo.gender is None:
                        userInfoDict['gender'] = userInfo.gender
                    if not userInfo.location is None:
                        userInfoDict['area_country'] = userInfo.location
                    if not userInfo.location_living_duration is None:
                        userInfoDict['living_period'] = int(userInfo.location_living_duration)
                    if not userInfo.prolific_id is None:
                        userInfoDict['prolific_id'] = userInfo.prolific_id

                    userInfoDict['is_lived_in_other_area'] = userInfo.hasLivedInAnotherArea()
                    userInfoDict['is_multilingual'] = userInfo.grew_up_multilingually
                    userInfoDict['highest_education_degree'] = userInfo.highest_education_degree
                    userInfoDict['have_linguistics_degree'] = userInfo.degree_in_linguistics

                    userForm = UserInfoForm(languageCode=request.LANGUAGE_CODE, initial=userInfoDict)
                else:
                    userForm = UserInfoForm(languageCode=request.LANGUAGE_CODE)
                return render(request, 'UserInfo.html',
                              {'form': userForm, 'userInfoPageConstants': UserInfoPageConstants,
                               'commonConstants': CommonConstants})
            else:
                messages.error(request, MultilingualMessagesConstants.PLEASE_LOGIN_MESSAGE)
                params = dict()
                params["landingPageConstants"] = LandingPageConstants
                params["loginPageConstants"] = LoginPageConstants
                return render(request, 'LandingPage.html', params)
        except Exception as e:
            return HttpResponse("Exception in UserInfoForm view, please report to the admins: " + str(e))

    def post(self, request):
        if not request.user.is_authenticated():
            messages.error(request, MultilingualMessagesConstants.PLEASE_LOGIN_MESSAGE)
            params = dict()
            params["landingPageConstants"] = LandingPageConstants
            params["loginPageConstants"] = LoginPageConstants
            return render(request, 'LandingPage.html', params)

        try:
            userInfoForm = UserInfoForm(request.POST, languageCode=request.LANGUAGE_CODE)

            if userInfoForm.is_valid():
                form = userInfoForm.cleaned_data

                if request.user.is_authenticated():
                    if UserInfo.objects.filter(user=request.user).exists():
                        userInfo = UserInfo.objects.get(user=request.user)
                    else:
                        userInfo = UserInfo()
                        userInfo.user = request.user
                else:
                    messages.error(request, MultilingualMessagesConstants.PLEASE_LOGIN_MESSAGE)
                    params = dict()
                    params["landingPageConstants"] = LandingPageConstants
                    params["loginPageConstants"] = LoginPageConstants
                    return render(request, 'LandingPage.html', params)

                # handle user's age
                age = form['age']
                if age != '':
                    userInfo.age = int(age)

                # handle user's gender
                gender = form['gender']
                if gender != '':
                    setUserGender(userInfo, gender)

                # handle user's country
                area_country = form['area_country']
                if area_country != None:
                    setUserCountry(userInfo, area_country)

                # handle language spoken in user's country
                area_language = form['area_language']
                if area_language != None:
                    addUserLocationLanguage(userInfo, area_language)

                # handle duration of living in current country
                living_period = str(form['living_period']).strip()
                if living_period != '':
                    userInfo.location_living_duration = float(living_period)

                # handle user's potential multilinguality
                is_multilingual = form['is_multilingual']
                if is_multilingual != '':
                    userInfo.grew_up_multilingually = bool(is_multilingual)

                # handle user's native language
                native_language = form['native_language']
                if native_language != None:
                    setUserLanguageToNative(userInfo, native_language)

                # handle the language the user uses at home
                home_language = form['home_language']
                if home_language != None:
                    setUserLanguageUsedAtHome(userInfo, home_language)

                # handle user's exposure to other language through living in that area
                is_lived_in_other_area = bool(form['is_lived_in_other_area'])
                if not is_lived_in_other_area:
                    deleteAllUserLanguageExposuresThroughLiving(userInfo)
                else:
                    another_area_language = form['living_area_language']
                    another_living_area_period = str(form['living_area_period']).strip()
                    # return HttpResponse(another_area_language+" "+another_living_area_period)
                    if another_area_language != None:
                        addUserLanguageExposureThroughLiving(userInfo, another_area_language,
                                                             float(another_living_area_period))

                # handle user's exposure to other languages through learning them
                learned_language = form['learned_language']
                learned_language_time = str(form['learned_language_time']).strip()
                if learned_language != None and learned_language_time != '':
                    addUserLanguageExposureThroughLearning(userInfo, learned_language, float(learned_language_time))

                # handle user's specified education country
                education_country = form['education_country']
                education_time = str(form['education_time']).strip()

                if education_country != None and education_time != '':
                    addUserEducationCountryStay(userInfo, education_country, float(education_time))

                # handle user's specified education degree
                education_degree = form['highest_education_degree']
                if education_degree != None:
                    setUserHighestEducationDegree(userInfo, education_degree)

                # handle user's potential degree in linguistics
                have_linguistics_degree = form['have_linguistics_degree']
                if have_linguistics_degree != '':
                    userInfo.degree_in_linguistics = bool(have_linguistics_degree)

                # prolific id
                prolific_id = form['prolific_id']
                userInfo.prolific_id = str(prolific_id).strip()

                userInfo.save()
                if userInfo.enteredAllInfo():
                    response = HttpResponseRedirect('/LanguageProficiencyForm/')
                    return response

                else:
                    info_errors = userInfo.getEnteredInformationErrors()
                    return render(request, 'UserInfo.html', {'form': userInfoForm, 'missingEntries': info_errors,
                                                             'userInfoPageConstants': UserInfoPageConstants,
                                                             'commonConstants': CommonConstants})

            else:
                messages.error(request, MultilingualMessagesConstants.PLEASE_FILL_ALL_USER_INFO_FIELDS_ERROR_MESSAGE)
                return render(request, 'UserInfo.html',
                              {'form': userInfoForm, 'userInfoPageConstants': UserInfoPageConstants,
                               'commonConstants': CommonConstants})
        except Exception as e:
            return HttpResponse("Exception in UserInfoForm view, please report to the admins: " + str(e))


class UserLanguageChangeHandler(View):
    def get(self, request):
        return HttpResponse(str("Get Call"))

    def post(self, request):

        resp = HttpResponse('')
        if request.is_ajax():
            requestType = request.POST['type']

            if not request.user.is_authenticated():
                messages.error(request, MultilingualMessagesConstants.PLEASE_LOGIN_MESSAGE)
                params = dict()
                params["landingPageConstants"] = LandingPageConstants
                params["loginPageConstants"] = LoginPageConstants
                return render(request, 'LandingPage.html', params)

            else:
                if UserInfo.objects.filter(user=request.user).exists():
                    userInfo = UserInfo.objects.get(user=request.user)
                else:
                    userInfo = UserInfo()
                    userInfo.user = request.user

                resp = HttpResponse('')
                # save living area language
                if requestType == '1':
                    languageId = request.POST['languageId']
                    languageName = request.POST['language']
                    divId = 'div_area_lang_' + str(languageId).replace('-', '_')
                    success = addUserLocationLanguageByID(userInfo, languageId)
                    if success:
                        resp = HttpResponse(
                            generateHtmlForAreaLanguage(divId=divId, languageName=languageName, languageId=languageId))

                # save another area languages
                elif requestType == '2':
                    languageId = request.POST['languageId']
                    languageName = request.POST['language']
                    livingYear = str(request.POST['livingYear']).strip()
                    divId = 'div_another_area_lang' + str(languageId).replace('-', '_')
                    # return HttpResponse(languageId+" "+livingYear)
                    success = addUserLanguageExposureThroughLivingByID(userInfo, languageId, float(livingYear))
                    if success:
                        resp = HttpResponse(generateHtmlForAnotherAreaLanguage(divId=divId, languageName=languageName,
                                                                               livingYear=livingYear,
                                                                               languageId=languageId))

                # save native languages
                elif requestType == '3':
                    languageId = request.POST['languageId']
                    languageName = request.POST['language']
                    divId = 'div_native_lang_' + str(languageId).replace('-', '_')
                    success = setUserLanguageToNativeByID(userInfo, languageId)
                    if success:
                        resp = HttpResponse(generateHtmlForNativeLanguage(divId=divId, languageName=languageName,
                                                                          languageId=languageId))

                # save education country
                elif requestType == '4':
                    countryId = request.POST['countryId']
                    countryName = request.POST['countryName']
                    educationYear = str(request.POST['educationYear']).strip()
                    divId = 'div_education_country_' + str(countryId).replace('-', '_')
                    success = addUserEducationCountryStayByID(userInfo, countryId, float(educationYear))
                    if success:
                        resp = HttpResponse(generateHtmlForEducationCountry(divId=divId, countryName=countryName,
                                                                            educationYear=educationYear,
                                                                            countryId=countryId))

                # save home languages
                elif requestType == '5':
                    languageId = request.POST['languageId']
                    languageName = request.POST['language']
                    divId = 'div_home_lang_' + str(languageId).replace('-', '_')
                    success = setUserLanguageUsedAtHomeByID(userInfo, languageId)
                    if success:
                        resp = HttpResponse(
                            generateHtmlForHomeLanguage(divId=divId, languageName=languageName, languageId=languageId))

                # save learned languages
                elif requestType == '6':
                    languageId = request.POST['languageId']
                    languageName = request.POST['language']
                    learningTime = str(request.POST['learningTime']).strip()
                    divId = 'div_learned_lang' + str(languageId).replace('-', '_')
                    success = addUserLanguageExposureThroughLearningByID(userInfo, languageId, float(learningTime))
                    if success:
                        resp = HttpResponse(generateHtmlForLearnedLanguage(divId=divId, languageName=languageName,
                                                                           learningTime=learningTime,
                                                                           languageId=languageId))

                # delete language
                elif requestType == '7':
                    languageId = request.POST['languageId']
                    languageType = int(str(request.POST['languageType']).strip())
                    if languageType == LanguageType.LivingAreaLanguage:
                        deleteUserLocationLanguageByID(userInfo, languageId)
                    elif languageType == LanguageType.HomeLanguage:
                        deleteUserHomeLanguageByID(userInfo, languageId)
                    elif languageType == LanguageType.LearnedLanguage:
                        deleteUserLanguageExposureThroughLearningByID(userInfo, languageId)
                    elif languageType == LanguageType.NativeLanguage:
                        deleteUserNativeLanguageByID(userInfo, languageId)
                    elif languageType == LanguageType.AnotherAreaLanguage:
                        deleteUserLanguageExposureThroughLivingByID(userInfo, languageId)

                # load living area languages
                elif requestType == '8':
                    langs = userInfo.getLocationLanguages()
                    websiteLanguage = request.POST['websiteLanguage']
                    activate(websiteLanguage)
                    finalHtml = ''
                    for lang in langs:
                        divId = 'div_area_lang_' + str(lang.language_id).replace('-', '_')
                        LN = lang.language_name
                        finalHtml += generateHtmlForAreaLanguage(divId=divId, languageName=LN,
                                                                 languageId=str(lang.language_id))

                    resp = HttpResponse(finalHtml)

                # load another area languages
                elif requestType == '9':
                    # LanguageType.AnotherAreaLanguage
                    websiteLanguage = request.POST['websiteLanguage']
                    activate(websiteLanguage)
                    lstAnotherAreaLanguages = userInfo.getLanguageSkillsExposedToByLiving()
                    finalHtml = ''
                    for lang_skill in lstAnotherAreaLanguages:
                        LN = lang_skill.language.language_name
                        divId = 'div_another_area_lang' + str(lang_skill.language.language_id).replace('-', '_')
                        finalHtml += generateHtmlForAnotherAreaLanguage(divId=divId, languageName=LN, livingYear=str(
                            int(lang_skill.exposure_through_living)), languageId=str(lang_skill.language.language_id))

                    resp = HttpResponse(finalHtml)

                # load native languages
                elif requestType == '10':
                    websiteLanguage = request.POST['websiteLanguage']
                    activate(websiteLanguage)

                    lstNativeLanguages = userInfo.getNativeLanguages()

                    finalHtml = ''
                    for lang in lstNativeLanguages:
                        LN = lang.language_name
                        divId = 'div_native_lang_' + str(lang.language_id).replace('-', '_')
                        finalHtml += generateHtmlForNativeLanguage(divId=divId, languageName=LN,
                                                                   languageId=str(lang.language_id))

                    resp = HttpResponse(finalHtml)

                # load education countries
                elif requestType == '11':
                    websiteLanguage = request.POST['websiteLanguage']
                    activate(websiteLanguage)
                    lstEducationCountries = userInfo.getEducationCountryStays()

                    finalHtml = ''
                    if len(lstEducationCountries) > 0:
                        for country in lstEducationCountries:
                            divId = 'div_education_country_' + str(country.country.country_code).replace('-', '_')
                            finalHtml += generateHtmlForEducationCountry(divId=divId,
                                                                         countryName=country.country.country_name,
                                                                         educationYear=str(int(country.duration)),
                                                                         countryId=str(country.country.country_id))

                    resp = HttpResponse(finalHtml)

                # delete education countries
                elif requestType == '12':
                    educationCountryId = request.POST['educationCountryId']
                    deleteUserEducationCountryStayByID(userInfo, educationCountryId)

                # load home languages
                elif requestType == '13':
                    websiteLanguage = request.POST['websiteLanguage']
                    activate(websiteLanguage)
                    lstHomeLanguages = userInfo.getHomeLanguages()

                    finalHtml = ''
                    for lang in lstHomeLanguages:
                        divId = 'div_home_lang_' + str(lang.language_id).replace('-', '_')
                        finalHtml += generateHtmlForHomeLanguage(divId=divId, languageName=lang.language_name,
                                                                 languageId=str(lang.language_id))

                    resp = HttpResponse(finalHtml)

                # load learned languages
                elif requestType == '14':
                    websiteLanguage = request.POST['websiteLanguage']
                    activate(websiteLanguage)
                    lstLearnedLanguages = userInfo.getLearnedLanguageSkills()

                    finalHtml = ''
                    for lang_skill in lstLearnedLanguages:
                        divId = 'div_learned_lang' + str(lang_skill.language.language_id).replace('-', '_')
                        N = lang_skill.language.language_name
                        finalHtml += generateHtmlForLearnedLanguage(divId=divId, languageName=N, learningTime=str(
                            int(lang_skill.exposure_through_learning)), languageId=str(lang_skill.language.language_id))

                    resp = HttpResponse(finalHtml)

        else:
            # raise Http404
            resp = HttpResponse('Not Saved')

        return resp


class LanguageProficiencyView(View):
    def get(self, request):
        try:
            if request.user.is_authenticated():
                if UserInfo.objects.filter(user=request.user).exists():
                    userInfo = UserInfo.objects.get(user=request.user)
                else:
                    userInfo = UserInfo()
                    userInfo.user = request.user
                    # userInfo.save()

                params = dict()
                params["language_objects"] = userInfo.getAllLanguages()
                params["languageProficiencyPageConstants"] = LanguageProficiencyPageConstants
                return render(request, 'LanguageProficiency.html', params)
            else:
                messages.error(request, MultilingualMessagesConstants.PLEASE_LOGIN_MESSAGE)
                params = dict()
                params["landingPageConstants"] = LandingPageConstants
                params["loginPageConstants"] = LoginPageConstants
                return render(request, 'LandingPage.html', params)

        except Exception as e:
            return HttpResponse("Exception in Language Proficiency View, please report: " + str(e))

    def post(self, request):
        userInfo, created = UserInfo.objects.get_or_create(user=request.user)
        try:
            # response = HttpResponse('')
            if request.is_ajax():
                requestType = request.POST['type']

                # load language proficiency list
                if requestType == '1':
                    languageSkillsList = userInfo.getAllLanguageSkills()
                    if len(languageSkillsList) > 0:
                        response = languageSkillsList
                        response = serializers.serialize('json', response)
                        return HttpResponse(response)
                    else:
                        return HttpResponse('')

                # save language proficiencies
                else:
                    reqData = request.POST['listOfObjects']
                    lst = json.loads(reqData)
                    resp_str = []
                    for item in lst:
                        languageId = int(item["languageId"])
                        readingLevel = int(item["readingLevel"])
                        writingLevel = int(item["writingLevel"])
                        listeningLevel = int(item["listeningLevel"])
                        speakingLevel = int(item["speakingLevel"])

                        X = setUserLanguageSkills(userInfo, languageId, readingLevel, writingLevel, listeningLevel,
                                                  speakingLevel)
                        resp_str.append(str(X))
                    return HttpResponse(True)
        except Exception as e:
            return HttpResponse('Error: ' + str(e))


class LoginView(View):
    def get(self, request):
        params = dict()
        params["loginPageConstants"] = LoginPageConstants

        try:
            return render(request, 'accounts/Login.html', params)
        except Exception as e:
            return render(request, 'accounts/Login.html', params)

    def post(self, request):
        params = dict()
        params["loginPageConstants"] = LoginPageConstants
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')

            if not request.user.is_authenticated():

                try:
                    nextUrl = request.GET['next']
                except:
                    nextUrl = ''

                if username == '' or password == '':
                    messages.error(request, LoginPageConstants.EMPTY_EMAIL_PASSWORD_ERROR_MESSAGE)
                    return render(request, 'accounts/Login.html', params)

                user = authenticate(
                    username=username,
                    password=password
                )

                if user is not None:
                    if user.is_active:
                        login(request, user)
                        response = HttpResponseRedirect('/UserInfoForm/')
                        if nextUrl != '':
                            response = HttpResponseRedirect(nextUrl)
                        response.set_cookie(CookieFields.UserID, user.id)
                        return response
                    else:
                        messages.error(request, LoginPageConstants.ACCOUNT_NOT_AVAILABLE_ERROR_MESSAGE)
                else:
                    messages.error(request, LoginPageConstants.LOGIN_ERROR_MESSAGE)
                    return render(request, 'accounts/Login.html', params)
            else:
                response = HttpResponseRedirect('/UserInfoForm/')
                response.set_cookie(CookieFields.UserID, request.user.id)
                return response
        except Exception as e:
            return HttpResponse(status=500)


class RegistrationView(View):
    def get(self, request):
        try:
            params = dict()
            params["loginPageConstants"] = LoginPageConstants
            return render(request, 'accounts/Registration.html', params)
        except Exception as e:
            return HttpResponse(status=500)


    def post(self, request):
        params = dict()
        params["loginPageConstants"] = LoginPageConstants
        try:
            username = request.POST.get("username")
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirmPassword = request.POST.get('confirmPassword')
            isAgreeForNewsLetter = request.POST.get('chkNewsLetter')
            isAgreeForConsent = request.POST.get('chkInformationConsent')

            if isAgreeForConsent == None:
                messages.error(request, LoginPageConstants.INFORMED_CONSENT_ERROR_MESSAGE_TEXT)
                return render(request, 'accounts/Registration.html', params)

            if username != '' and email != '' and password != '' and confirmPassword != '':

                isValidEmail = EmailValidator(email)
                if not isValidEmail:
                    messages.error(request, LoginPageConstants.INVALID_EMAIL_ERROR_MESSAGE)
                    return render(request, 'accounts/Registration.html', params)
                else:
                    if User.objects.filter(email=email).exists():
                        messages.error(request, LoginPageConstants.EMAIL_ALREADY_REGISTERED_ERROR_MESSAGE)
                        return render(request, 'accounts/Registration.html', params)
                if User.objects.filter(username=username).exists():
                    messages.error(request, LoginPageConstants.USERNAME_ALREADY_REGISTERED_ERROR_MESSAGE)
                    return render(request, 'accounts/Registration.html', params)

                if password != confirmPassword:
                    messages.error(request, LoginPageConstants.PASSWORD_MISMATCH_ERROR_MESSAGE)
                    return render(request, 'accounts/Registration.html', params)

                userId, authUser = createUserAccount(email, password, username)
                if userId == 0 and authUser == 'AlreadyExists':
                    messages.error(request, LoginPageConstants.EMAIL_ALREADY_REGISTERED_ERROR_MESSAGE)
                    messages.error(request, LoginPageConstants.USERNAME_ALREADY_REGISTERED_ERROR_MESSAGE)
                    return render(request, 'accounts/Registration.html', params)

                if authUser != None:
                    login(request, authUser)
                    response = HttpResponseRedirect('/UserInfoForm/')
                    userInfo = UserInfo()
                    userInfo.user = authUser
                    userInfo.date_added = datetime.now()
                    if isAgreeForNewsLetter != None:
                        userInfo.requested_signup_for_newsletter = isAgreeForNewsLetter
                    else:
                        userInfo.requested_signup_for_newsletter = 0
                    userInfo.save()  # force_insert=True)
                    response.set_cookie(CookieFields.UserID, userId)
                    return response

                return HttpResponse("Authentication failed. " + str(authUser) + " " + str(userId))
            else:
                messages.error(request, LoginPageConstants.EMPTY_EMAIL_PASSWORD_ERROR_MESSAGE)
                return render(request, 'accounts/Registration.html', params)
        except Exception as e:
            return HttpResponse("Please report this error to the admins: " + str(e))


class LogoutView(View):
    def get(self, request):
        try:
            logout(request)
            response = HttpResponseRedirect('/')
            response.delete_cookie(CookieFields.UserID)
            # response.delete_cookie(CookieFields.WebsiteLanguageCode)
            #response.delete_cookie(CookieFields.WebsiteLanguageId)
            return response
        except Exception as e:
            return HttpResponseRedirect('/')

    def post(self, request):
        try:
            return HttpResponseRedirect('/')
        except Exception as e:
            return HttpResponseRedirect('/')


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeCustomForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Updating current session of logged-in user
            update_session_auth_hash(request, user)
            messages.success(request, _('YOUR_PASSWORD_WAS_SUCCESSFULLY_UPDATED_MESSAGE_TEXT'))
            # return redirect('ChangePassword')
        else:
            messages.error(request, _('OLD_PASSWORD_INCORRECT_OR_NEW_PASSWORDS_DO_NOT_MATCH_ERROR_TEXT'))
    else:
        form = PasswordChangeCustomForm(request.user)
    return render(request, 'accounts/ChangePassword.html', {
        'form': form
    })


class ForgotPasswordView(View):
    def get(self, request):
        params = dict()
        params["loginPageConstants"] = LoginPageConstants
        try:
            return render(request, 'accounts/ForgotPassword.html', params)
        except Exception as e:
            return render(request, 'accounts/ForgotPassword.html', params)

    def post(self, request):
        params = dict()
        params["loginPageConstants"] = LoginPageConstants
        try:
            email = request.POST.get('email')

            try:
                validate_email(email)
                isValidEmail = True
            except:
                isValidEmail = False

            if isValidEmail:
                users = User.objects.filter(email=email)
                if users.exists():
                    for user in users:
                        params = {
                            'email': user.email,
                            'domain': request.META['HTTP_HOST'],
                            'site_name': 'INCOMSLAV',
                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                            'user': user,
                            'token': default_token_generator.make_token(user),
                            'protocol': 'http',
                        }

                        email_template_name = 'emailtemplates/password_reset_email.html'

                        subject = _("RESET_PASSWORD")

                        email_body = loader.render_to_string(email_template_name, params)
                        send_mail(subject, email_body, DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                    reset_password_email_success_message= _("AN_EMIL_HAS_BEEN_SENT_TO_MESSAGE")
                    messages.success(request,reset_password_email_success_message.format(email))
                    return HttpResponseRedirect('/ForgotPassword/')
                else:
                    messages.error(request, _("THIS_EMAIL_IS_NOT_REGISTERED_WITH_OUR_SYSTEM"))
                    return HttpResponseRedirect('/ForgotPassword/')
            else:
                messages.error(request, LoginPageConstants.INVALID_EMAIL_ERROR_MESSAGE)
                return HttpResponseRedirect('/ForgotPassword/')
        except Exception as e:
            return HttpResponse(status=500)


class PasswordResetConfirmView(View):
    def get(self, request, uidb64=None, token=None):
        params = dict()
        params["loginPageConstants"] = LoginPageConstants
        params["form"] = PasswordResetConfirmationForm()
        try:
            return render(request, 'accounts/ResetForgotPassword.html', params)
        except Exception as e:
            return render(request, 'accounts/ResetForgotPassword.html', params)


    def post(self, request, uidb64=None, token=None):
        try:
            UserModel = get_user_model()
            form = PasswordResetConfirmationForm(request.POST)

            try:
                # p=request.path
                # params= p.split('/')
                # uidb64 = params[-1].split('-')[0]
                # token = params[-1].split('-')[1]+params[-1].split('-')[2]
                uid = urlsafe_base64_decode(uidb64)
                user = UserModel._default_manager.get(pk=uid)
            except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):
                if form.is_valid():
                    new_password1 = str(form.cleaned_data['new_password1']).strip()
                    new_password2 = str(form.cleaned_data['new_password2']).strip()
                    if new_password1 != "" and new_password2 != "":
                        if new_password1 == new_password2:
                            user.set_password(new_password1)
                            user.save()
                            messages.success(request, _('YOUR_PASSWORD_WAS_SUCCESSFULLY_UPDATED_MESSAGE_TEXT'))
                        else:
                            messages.error(request, _('PASSWORDS_MISMATCH_ERROR'))
                    else:
                        messages.error(request, _('INVALID_INPUT_ERROR'))
                else:
                    messages.error(request, _('INVALID_INPUT_ERROR'))
            else:
                messages.error(request, _('THE_RESET_PASSWORD_LINK_IS_NO_LONGER_VALID'))

            return HttpResponseRedirect(request.path)

        except Exception as e:
            return HttpResponseRedirect(request.path)


class InformedConsentView(View):
    """
    Informed consent view to display informed consent text
    """
    def get(self, request):
        params = dict()
        params["informedConsent"] = InformedConsentView.getInformedConsent()
        try:
            return render(request, 'InformedConsent.html', params)
        except Exception as e:
            return render(request, 'InformedConsent.html', params)

    def post(self, request):

        return HttpResponseRedirect(request.path)

    @staticmethod
    def getInformedConsent():
        try:
            lsInformedConsent = InformedConsent.objects.filter(is_active=1).order_by('-priority')
            res = []
            res.append("<ul>")
            heading = ''
            for consent in lsInformedConsent:
                consent = str(consent)
                if consent != '':
                    consent=consent.split(']')
                    if len(consent) == 2:
                        res.append('<li>')
                        heading = consent[0][1:]
                        detail = consent[1]
                        res.append('<p>')
                        res.append('<text style="color:#63b540; font-weight:bold">')
                        res.append(heading)
                        res.append('</text>')
                        res.append('</p>')
                        res.append('<p>')
                        res.append(detail)
                        res.append('</p>')
                        res.append('</li>')
                    else:
                        res.append('<li>')
                        detail = consent[0]
                        res.append('<p>')
                        res.append('<text style="color:#63b540; font-weight:bold">')
                        res.append(heading)
                        res.append('</text>')
                        res.append('</p>')
                        res.append('<p>')
                        res.append(detail)
                        res.append('</p>')
                        res.append('</li>')

            res.append("</ul>")
            return ''.join(res)
        except Exception as ex:
            return ''


    