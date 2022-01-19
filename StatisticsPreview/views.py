from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.http import HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
from .models import *

from distutils.util import strtobool

# Create your views here.

def upload_menu(request):

	return render(request, 'upload_menu.html')

class UploadMenuView(View):
	def get(self, request):
		context = {}

		menu_list = ResultMenu.objects.all()
		context['menu_list'] = menu_list

		return render(request, 'upload_menu.html', context)

	def post(self, request):

		menu_name = request.POST['menu_name']
		is_root = strtobool(request.POST['is_root'])
		# is_root = True
		parent_id = request.POST['parent_id']

		if parent_id != 'null':
			parent = get_object_or_404(ResultMenu, pk=request.POST['parent_id'])
		else:
			parent = None

		print(parent)
		# obj = ResultMenu(menu_name=menu_name, parent_id=parent)
		# obj.save()
		obj, created = ResultMenu.objects.get_or_create(
			menu_name=menu_name,
			parent_id=parent,
			defaults={'is_root':is_root},
			)


		return redirect('SlavMatrix:uploadMenu')


class ResultTableView(View):
	def get(self, request):
		context = {}

		menu_list = ResultMenu.objects.all()

		# for menu in menu_list:
		# 	if menu.is_root:


		context['menu_list'] = menu_list

		return render(request, 'result_table.html', context)


class UploadColumnView(View):
	def get(self, request):
		data = {}

		column_list = ColumnName.objects.all()
		data['column_list'] = column_list

		return render(request, 'upload_column.html', data)

	def post(self, request):

		full_name = request.POST['column_name']
		abbvr_name = request.POST['abbvr_name']
		obj, created = ColumnName.objects.get_or_create(
			full_name=full_name,
			abbvr_name=abbvr_name,
			defaults={'is_active':True},
			)

		return redirect('SlavMatrix:uploadColumn')


def ResultUpload(request):

	return render(request, 'blank.html')

def IntelligibilityIndividualPanslavic(request):

	return render(request, 'Intell_panslavic.html')

def IntelligibilityIndividualTop(request):

	return render(request, 'intell_top100.html')

def IntelligibilityPredictiveWords(request):

	return render(request, 'intell_predictive.html')

def CorrLeven(request):
	return render(request, 'corr_levenshtein.html')

def CorrWasp(request):
	return render(request, 'corr_wasp.html')

def PredictorsCE(request):
	
	return render(request, 'predictors_ce.html')

def PredictorsWASP(request):

	return render(request, 'predictors_wasp.html')

def PredictorDistanceLevenshteinPanslavic(request):

	return render(request, 'predictors_dist_levensh_panslav.html')


def PredictorDistanceLevenshteinTop(request):

	return render(request, 'predictors_dist_levensh_top100.html')


def PredictorDistanceLexical(request):

	return render(request, 'predictors_dist_lexical.html')

	