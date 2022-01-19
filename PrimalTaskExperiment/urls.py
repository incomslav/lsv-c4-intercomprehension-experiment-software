from django.conf.urls import url
from . import views
from LanguageGameExperiment.views import *
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

loginUrl = '/'

urlpatterns = [

    url(r'^PrimalTask/$', login_required(views.PrimalTask, login_url=loginUrl),
        name='PrimalTask'),
]