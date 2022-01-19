from django.shortcuts import render

# Create your views here.

from urllib import request

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.generic import View
from django.core.urlresolvers import reverse
from .models import *
from django.core.exceptions import ObjectDoesNotExist
import csv
import os
from django.contrib.staticfiles.storage import staticfiles_storage
import datetime
from pathlib import Path
from django.conf import settings
import csv


def PrimalTask(request):

    return render(request, 'PrimalTask.html')


class PrimalTaskQuestion(View):

    def get(self, request):

        return render(request, 'PrimalTask.html')


    def post(self, request):

        return render(request, 'PrimalTask.html')