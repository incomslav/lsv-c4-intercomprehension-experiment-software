from django.conf.urls import url
from . import views

urlpatterns = [
	# url(r'^uploadMenu/$', views.upload_menu, name='uploadMenu'),
	url(r'^uploadMenu/$', views.UploadMenuView.as_view(), name='uploadMenu'),
	url(r'^Results/$', views.ResultTableView.as_view(), name='Results'),
	url(r'^uploadColumn/$', views.UploadColumnView.as_view(), name='uploadColumn'),
	url(r'^IntelligibilityIndividualPanslavic/', views.IntelligibilityIndividualPanslavic, name='IntelligibilityIndividualPanslavic'),
	url(r'^IntelligibilityIndividualTop/', views.IntelligibilityIndividualTop, name='IntelligibilityIndividualTop'),
	url(r'^IntelligibilityPredictiveWords/', views.IntelligibilityPredictiveWords, name='IntelligibilityPredictiveWords'),
	url(r'^CorrLeven/', views.CorrLeven, name='CorrLeven'),
	url(r'^CorrWasp/', views.CorrWasp, name='CorrWasp'),
	url(r'^PredictorsCE/', views.PredictorsCE, name='PredictorsCE'),
	url(r'^PredictorsWASP/', views.PredictorsWASP, name='PredictorsWASP'),
	url(r'^ResultUpload/', views.ResultUpload, name='ResultUpload'),
	url(r'^PredictorDistanceLevenshteinPanslavic/', views.PredictorDistanceLevenshteinPanslavic, name='PredictorDistanceLevenshteinPanslavic'),
	url(r'^PredictorDistanceLevenshteinTop/', views.PredictorDistanceLevenshteinTop, name='PredictorDistanceLevenshteinTop'),
	url(r'^PredictorDistanceLexical/', views.PredictorDistanceLexical, name='PredictorDistanceLexical'),
	
	]