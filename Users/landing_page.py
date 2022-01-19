from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.utils import translation
from django.views.generic import View
from django.contrib import auth, messages
from django.utils.safestring import mark_safe

from Common import constants
from Common.Enums import *

from Users.enums import *
from ExperimentBasics.models import News, ExperimentInfo
import re
from datetime import date


def getNews():
    try:
        lsNews = News.objects.filter(is_active=1).order_by('-priority')[:5]
        res = []
        res.append("<ul>")
        heading = ''
        for news in lsNews:
            news = str(news)
            if news != '':
                news=news.split(']')
                if len(news) == 2:
                    res.append('<li>')
                    heading = news[0][1:]
                    detail = news[1]
                    res.append('<p>')
                    # res.append(str(date.now()))
                    # res.append(':')
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
                    # heading = news.split('</h>')[0][1:]
                    detail = news[0]
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


def getExperimentInfo():
    try:
        lsExperimentInfo = ExperimentInfo.objects.order_by('id')
        res = []
        res.append("<ul style='list-style: none;padding-left: 0px;'>")
        for experimentInfo in lsExperimentInfo:
            experimentInfo = str(experimentInfo)
            if experimentInfo != '':
                res.append('<li>')
                res.append('<p>')
                res.append(experimentInfo)
                res.append('</p>')
                res.append('</li>')
            else:
                res.append('<li>')
                res.append('</li>')

        res.append("</ul>")
        return ''.join(res)
    except Exception as ex:
        return ''


class Index(View):
    def get(self, request):
        params = dict()
        # params["landingPageConstants"] = constants.LandingPageConstants

        # loginPageConstants = constants.LoginPageConstants
        # loginPageConstants.LANDING_PAGE_START_EXPERIMENT_HERE_TEXT = mark_safe(str(loginPageConstants.LANDING_PAGE_START_EXPERIMENT_HERE_TEXT).format('<a href="/userRegistration">','</a>'))
        # params["loginPageConstants"] = loginPageConstants
        params["loginPageConstants"] = constants.LoginPageConstants
        params["news"] = getNews()
        params["experimentInfo"] = getExperimentInfo()
        response = render(request, 'LandingPage.html', params)
        return response

    def post(self, request):
        try:
            if not request.is_ajax():
                params = dict()
                params["loginPageConstants"] = constants.LoginPageConstants
                username = request.POST.get('username')
                password = request.POST.get('password')

                if not request.user.is_authenticated():

                    try:
                        nextUrl = request.GET['next']
                    except:
                        nextUrl = ''

                    if username == '' or password == '':
                        messages.error(request, constants.LoginPageConstants.EMPTY_EMAIL_PASSWORD_ERROR_MESSAGE)
                        return render(request, 'LandingPage.html', params)

                    user = auth.authenticate(
                        username=username,
                        password=password
                    )

                    if user is not None:
                        if user.is_active:
                            auth.login(request, user)
                            # response = HttpResponseRedirect("/UserInfoForm")
                            response = HttpResponseRedirect("/Experiments")
                            if nextUrl != '':
                                response = HttpResponseRedirect(nextUrl)
                            response.set_cookie(CookieFields.UserID, user.id)
                            return response
                        else:
                            messages.error(request, mark_safe(
                                str(constants.LoginPageConstants.ACCOUNT_NOT_AVAILABLE_ERROR_MESSAGE).format(
                                    "<a href='/userRegistration'>", "</a>")))
                    else:
                        messages.error(request, mark_safe(str(constants.LoginPageConstants.LOGIN_ERROR_MESSAGE).format(
                            ("<a href='/userRegistration'>"), "</a>")))

                        return render(request, 'LandingPage.html', params)
                else:
                    # response = HttpResponseRedirect('/UserInfoForm/')
                    response = HttpResponseRedirect("/Experiments")
                    response.set_cookie(CookieFields.UserID, request.user.id)
                    return response

        except Exception as e:
            return HttpResponse(str(e))  # status=500)
        return HttpResponseRedirect('')
