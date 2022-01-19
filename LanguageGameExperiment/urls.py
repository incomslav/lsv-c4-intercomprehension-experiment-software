from django.conf.urls import url
from . import views
from LanguageGameExperiment.views import *
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

loginUrl = '/'

urlpatterns = [
	
	url(r'^LanguageGameExp/$', login_required(LanguageGameExperimentView.as_view(), login_url=loginUrl), name='LanguageGameExp'),
	url(r'^ExperimentTextView/$', login_required(ExperimentTextView.as_view(), login_url=loginUrl) , name='ExperimentTextView'),

	url(r'LaDoShowResult/(?P<stat_id>[0-9]+)/$', login_required(views.LaDoShowResult, login_url=loginUrl), name='LaDoShowResult'),
	url(r'LaDoResultDownloadCSV/(?P<exp_id>[0-9]+)/$', login_required(views.export_lado_result_to_csv, login_url=loginUrl), name='LaDoResultDownloadCSV'),

	url(r'^PrimalTaskExperiment/$', login_required(PrimalTaskExperimentView.as_view(), login_url=loginUrl), name='PrimalTaskExperiment'),
	url(r'^PrimalTaskExperimentText/$', login_required(PrimalTaskExperimentTextView.as_view(), login_url=loginUrl), name='PrimalTaskExperimentText'),
	url(r'^ProlificPrimalTaskExperiment/$', ProlificPrimalTaskExperimentView.as_view(), name='ProlificPrimalTaskExperiment'),
	url(r'^ProlificPrimalTaskExperimentText/$', ProlificPrimalTaskExperimentTextView.as_view(), name='ProlificPrimalTaskExperimentText'),

	url(r'^ExperimentTextViewLado1/$', ExperimentTextViewLado1.as_view(), name='Lado1ExperimentTextView'),
	url(r'^Lado1LanguageGameExpPage/$', LanguageGameExperimentViewProlific.as_view(), name='Lado1LanguageGameExpPage'),
	url(r'LaDo1ShowResultPage/(?P<stat_id>[0-9]+)/$', views.LaDoShowResultProlific, name='LaDo1ShowResultPage'),

	url(r'demo_webgazer/$', DemoWebgazerView.as_view(), name='demo_webgazer'),
	url(r'WebGazingQuestionUpload/$', WebGazingExperimentQuestionUpload.as_view(), name='WebGazingQuestionUpload'),
	url(r'WebGazingIntro/$', WebGazingIntro.as_view(), name='WebGazingIntro'),

	url(r'SentenceTranslationExperimentPage/$', SentenceTranslationExperimentPage.as_view(), name='SentenceTranslationExperimentPage'),
	url(r'(?P<exp_id>[0-9]+)/SentenceTranslationWelcomePage/$', SentenceTranslationWelcomePage.as_view(), name='SentenceTranslationWelcomePage'),
	url(r'SentenceTranslationShowResults/$', SentenceTranslationShowResults.as_view(), name='SentenceTranslationShowResults'),

	url(r'CloseTestExperimentPage/$', login_required(CloseTestExperimentPage.as_view(), login_url=loginUrl), name='CloseTestExperimentPage'),
	url(r'(?P<exp_id>[0-9]+)/CloseTestWelcomePage/$', login_required(CloseTestWelcomePage.as_view(), login_url=loginUrl), name='CloseTestWelcomePage'),
	# url(r'CloseTestExperimentUpload/$', CloseTestExperimentPage.as_view(), name='CloseTestExperimentUpload'),
	# url(r'CloseTestShowResults/$', SentenceTranslationShowResults.as_view(), name='CloseTestShowResults'),
	url(r'CloseTestDownloadCSV/(?P<lang_id>[0-9]+)/$', login_required(views.export_close_test_results_csv, login_url=loginUrl), name='CloseTestDownloadCSV'),



	url(r'(?P<exp_id>[0-9]+)/DECompoundWelcomePage/$', DECompoundWelcomePage.as_view(),
		name='DECompoundWelcomePage'),
	url(r'DECompoundExperimentPage/$', DECompoundExperimentPage.as_view(), name='DECompoundExperimentPage'),

	url(r'DECompoundResultDownloadCSV/(?P<exp_id>[0-9]+)/$', login_required(views.export_decompound_result_to_csv, login_url=loginUrl), name='DECompoundResultDownloadCSV'),


]