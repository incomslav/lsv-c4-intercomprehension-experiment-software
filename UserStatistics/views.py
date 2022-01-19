from django.shortcuts import render
from ExperimentBasics.models import *
from Users.models import *
from ExperimentBasics.views import *
import csv
from django.http import HttpResponse

from FreeTranslationExperiment.models import *
from GapFillingExperiment.models import *
from PhraseTranslationExperiment.models import *

# Create your views here.

def ExperimentStatistics(request):

	data = {}

	experiment_list = Experiment.objects.all()
	# print(user_prerequisit_list[1].user_prerequisites.select_subclasses())
	preq_list = []
	for li in experiment_list:
		for preq in li.user_prerequisites.select_subclasses():

			# print(preq.required_language.language_name)
			preq_list.append(preq.required_language.language_name)

	
	sorted_list = sorted(set(preq_list))
	data['language_list'] = sorted_list

	if request.method == "POST":

		table_data = []

		try:

			native_lang = request.POST['native_lang_name']
			foreign_lang = request.POST['foreign_lang_name']
			experiment_type = request.POST['experiment_type']

			native_lang_obj = Language.objects.get(language_name=native_lang)
			foreign_lang_obj = Language.objects.get(language_name=foreign_lang)

			data['native_lang'] = native_lang
			data['foreign_lang'] = foreign_lang
			

			if experiment_type == 'free_translation':
				required_exp_list = FreeTranslationExperiment.objects.filter(native_language = native_lang_obj, foreign_language = foreign_lang_obj)
				data['exp_type'] = "Free Translation"
			elif experiment_type == 'gap_filling':
				required_exp_list = GapFillingExperiment.objects.filter(native_language = native_lang_obj, foreign_language = foreign_lang_obj)
				data['exp_type'] = "Gap Filling"
			elif experiment_type == 'phrase_trans':
				required_exp_list = PhraseTranslationExperiment.objects.filter(native_language = native_lang_obj, foreign_language = foreign_lang_obj)
				data['exp_type'] = "Phrase Translation"
			else:
				required_exp_list = FreeTranslationExperiment.objects.filter(native_language = native_lang_obj, foreign_language = foreign_lang_obj)



			native_user_list = UserLanguageSkill.objects.filter(language=native_lang_obj, is_native_language=True).distinct()
			total_native_user = native_user_list.count()
			# print(total_native_user)

			native_user_list_values = native_user_list.values('user')
			# print(native_user_list_values)

			overall_questions = 0
			overall_answers = 0
			overall_time = 0
			overall_partpt = 0

			for exp in required_exp_list:
				print(exp.experiment_name)
				total_correct_perc = 0
				total_exp_time = 0
				total_exp_particpant = 0

				# for average calculation in frontend
				total_question_sum = 0
				total_correct_sum = 0

				mean_intellect_score = '-'
				avg_time = '-'


				ep_user_list = ExperimentParticipation.objects.filter(user__in = native_user_list_values, experiment__id = exp.id)
				print(ep_user_list.count())

				for ep in ep_user_list:
					num_total, num_correct, num_incorrect, num_not_answered, total_time = ep.getResults()

					correct_perc = float(num_correct) / float(num_total)
					total_correct_perc += float(correct_perc)
					total_exp_time += total_time
					total_exp_particpant += 1

					total_question_sum += num_total
					total_correct_sum += num_correct


					# print(ep.user.user.username, ep.experiment.experiment_name)
					# print(num_total, num_correct, num_incorrect, num_not_answered, total_time)


				overall_questions += total_question_sum
				overall_answers += total_correct_sum
				overall_time += total_exp_time
				overall_partpt += total_exp_particpant

				if total_exp_particpant > 0:
					mean_intellect_score = total_correct_perc / total_exp_particpant
					mean_intellect_score = round(mean_intellect_score*100,2)

					avg_time = int(total_exp_time / total_exp_particpant)
					avg_time = round(avg_time / (1000 * 60), 2)

					print(mean_intellect_score, avg_time)

				row_list = [exp.experiment_name, total_native_user, total_exp_particpant, mean_intellect_score, avg_time, total_question_sum, total_correct_sum]

				table_data.append(row_list)

			data['table_data'] = table_data

			data['total_mean_avg'] = round((overall_answers / overall_questions) * 100, 2)
			data['total_time_avg'] = round(overall_time / (overall_partpt * 1000 * 60), 2)
			data['total_partpt'] = overall_partpt


		except Exception as e:
			return HttpResponse(str(e))







	return render(request, 'adminpanel/ExperimentStatistics.html', data) 


def showstatistics(request):
	data = {}

	user_prerequisit_list = Experiment.objects.all()
	# print(user_prerequisit_list[1].user_prerequisites.select_subclasses())
	preq_list = []
	for li in user_prerequisit_list:
		for preq in li.user_prerequisites.select_subclasses():

			# print(preq.required_language.language_name)
			preq_list.append(preq.required_language.language_name)

	
	sorted_list = sorted(set(preq_list))
	data['language_list'] = sorted_list

	overall_user = UserInfo.objects.all().count()
	data['overall_user'] = overall_user

	if request.method == "POST":
		lang_name = request.POST['lang_name']

		user_ex_performed = []
		try:
			language_obj = Language.objects.get(language_name=lang_name)
			native_user_list = UserLanguageSkill.objects.filter(language=language_obj, is_native_language=True).distinct()

			for na in native_user_list:
				print(na.user.user.username)
			user_list = UserInfo.objects.filter(languages=language_obj)

			total_native = native_user_list.count()
			data['total_native'] = total_native
			participant_count = 0
			for li in native_user_list:
			
				experiment, a, b = UserExperimentOverviewView.getExperimentWithMedalsNew(li.user)
				language_list = UserLanguageSkill.objects.filter(user=li.user).values_list('language__language_name')
				native_lang_list = language_list.filter(is_native_language=True)
				exp_serial = 1
				# print(language_list)
				# print(experiment)
				if len(experiment) > 0:
					participant_count += 1
					for e in experiment:
						# b = e[0] e[2:]

						exp_type = e[0] + '_' + e[5] + "_" + e[6]
						print(exp_type)
						correct_by_total = str(e[3]) + ' / ' + str(e[2])
						accuracy = str(e[4]) + '%'
						exp_name = e[9]
						completed_on = e[8]
						curr_list = [li.user, language_list, native_lang_list, exp_serial, completed_on, exp_type, exp_name, correct_by_total, accuracy]
						print(e[-1])
						# print(curr_list)
						# curr_list = sorted(curr_list, key=lambda x:x[-1])
						print("CURR LIST:",curr_list)
						user_ex_performed.append(curr_list)
						exp_serial += 1

			data['participant_count'] = participant_count
			data['user_ex_performed'] = user_ex_performed
		except:
			pass

		link = "../UserStatisticsDownload/" + lang_name + "/"
		data['link'] = link
		data['user_native_language'] = lang_name

	return render(request, 'adminpanel/UserStatistics.html', data)




def makeUserDetailsCSVExporter(request, language):

	user_ex_performed = []
	try:
		language_obj = Language.objects.get(language_name=language)
		native_user_list = UserLanguageSkill.objects.filter(language=language_obj, is_native_language=True).distinct()
		for na in native_user_list:
			print(na.user.user.username)
		user_list = UserInfo.objects.filter(languages=language_obj)

		for li in native_user_list:
		
			experiment, a, b = UserExperimentOverviewView.getExperimentWithMedalsNew(li.user)
			language_list = UserLanguageSkill.objects.filter(user=li.user).values_list('language__language_name')
			native_lang_list = language_list.filter(is_native_language=True)
			# print(language_list)
			# print(experiment)
			if len(experiment) > 0:
				exp_serial = 1
				for e in experiment:
					# b = e[0] e[2:]
					curr_list = [li.user.user.username, li.user.user.email, language_list, native_lang_list, exp_serial, e[0], e[9], e[8], e[5], e[6], e[2], e[3], e[4]]
					# total 12 elements
					# print(e[-1])
					# print(curr_list)
					# curr_list = sorted(curr_list, key=lambda x:x[-1])
					# print("CURR LIST:",curr_list)
					user_ex_performed.append(curr_list)
					exp_serial += 1

		# data['user_ex_performed'] = user_ex_performed

		# Define the Fname
		
		Fname = "User_Details_"+str(language)+".csv"
		

		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}'.format(Fname)
		# response['Content-Disposition'] = 'attachment; filename="User_Details_{}.csv"'.format(str(language))
		
		headers = []
		headers.append("User Name")
		headers.append("User Email")
		headers.append("User Languages")
		headers.append("Native Languages")
		headers.append("Experiment Serial No.")
		headers.append("Experiment Type")
		headers.append("Experiment Name")
		headers.append("Completion Date Time")
		headers.append("From Language")
		headers.append("To Language")
		headers.append("Total Questions")
		headers.append("Accurate Answers")
		headers.append("Correct Percentage")
		# total 12 headers



		writer = csv.writer(response)
		writer.writerow(headers)
		for list in user_ex_performed:

			writer.writerow(list)

		return response

	except Exception as e:
		return HttpResponse(str(e))

	