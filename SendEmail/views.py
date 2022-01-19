from django.shortcuts import render
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.views.generic import View
from django.core.validators import validate_email
from Users.models import *
from ExperimentBasics.models import *
from django.contrib import messages
from Common.constants import LoginPageConstants
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string


def sendEmail(userId):
    """
    send email
    """
    try:
        experiments = len(getExperimentsAvailableToUser(userId))
        subject = _("SUBSCRIPTION_EMAIL_SUBJECT")
        user = User.objects.filter(id=userId).get()
        emailTo = user.email
        body = generateMailBody(user.username, experiments)
        send_mail(subject, '', '',
                  [emailTo], html_message=body, fail_silently=False)
        # send_mail(subject,'','incomslav@intercomprehension.coli.uni-saarland.de',[emailTo],html_message=body)
    except Exception as ex:
        print(str(ex))


def updateUserNewsletterSubscription(user, isSubscribed):
    """
    update user newsletter subscription
    """
    userInfo = UserInfo.objects.filter(user=user).get()
    userInfo.confirmed_signup_for_newsletter = isSubscribed
    userInfo.save()


def getExperimentsAvailableToUser(userId):
    """
    get all experiments user hasn't started
    """
    try:
        userInfo = UserInfo.objects.filter(id=userId).get()
        experiments_available = []
        # for all active experiments, check if user fulfills prerequisites
        experiments = Experiment.objects.filter(is_active__exact=True).select_subclasses()
        last_priority = None
        if len(experiments) > 0:
            for experiment in experiments:
                if experiment.userFulfillsPrerequisites(userInfo):
                    # mark this experiment as available for this user if the user hasn't completed this experiment before
                    if not experiment.userHasCompletedExperiment(userInfo):
                        keep = False
                        if last_priority is None:
                            keep = True
                        else:
                            if experiment.priority >= last_priority:
                                keep = True
                        last_priority = experiment.priority
                        if keep:
                            experiments_available.append(experiment)

        return experiments_available

    except Exception as ex:
        return None


def generateMailBody(userName, experiments):
    """generate email body by rendering email.html template"""
    email_placeholders = {"userName": _('EMAIL_SALUTATION_TEXT').format(userName)}
    medal_message = _('EMAIL_BODY')  # 'There are {} medals waiting for you'
    email_placeholders["medalMessage"] = medal_message.format(experiments)
    # return email_body
    return render_to_string("emailtemplates/email.html", email_placeholders)


class NewsLetterView(View):
    def get(self, request):
        params = dict()
        params["loginPageConstants"] = LoginPageConstants
        params["userEmail"] = request.user.email
        return render(request, 'emailtemplates/NewsLetter.html', params)

    def post(self, request):
        params = dict()
        params["loginPageConstants"] = LoginPageConstants
        params["userEmail"] = request.user.email

        try:
            newsletter = request.POST.get('checkbox', '')

            if newsletter == 'on':
                updateUserNewsletterSubscription(request.user, True)
                sendEmail(request.user.id)
            else:
                messages.error(request, _('NEWS_LETTER_PAGE_CHECKBOX_UNCHECK_ERROR_MESSAGE'))
                return render(request, 'emailtemplates/NewsLetter.html', params)

            return render(request, 'emailtemplates/success.html')
        except Exception as ex:
            return render(request, 'emailtemplates/NewsLetter.html', params)
