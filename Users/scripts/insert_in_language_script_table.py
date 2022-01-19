
import csv
import string
from Users.models import Language, Script, LanguageScriptRelation
def run():
	language_list = Language.objects.values_list('language_name', flat=True)
	print(len(language_list))
	counter = 0
	with open('DatabaseFixedValues/Lang_Scripts.csv', newline='') as csvfile:
		# file_reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
		file_reader = csv.DictReader(csvfile)
		for row in file_reader:
			if row['Language'] in language_list:
				for i, (key, value) in enumerate(row.items()):
					if value == '1':
						# print(row['Language'], key, value, list(row.keys())[i])
						try:
							script_object = Script.objects.get(script_name=str(key))
							language_object = Language.objects.get(language_name=row['Language'])
							# print(script_object.script_name, language_object.language_name)

							obj, created = LanguageScriptRelation.objects.get_or_create(
								language=language_object,
								script=script_object,
								defaults = {'isActive':True, 'isDelete':False})

							if created:
								counter += 1

						except:
							pass
				

	print("Total added rows: ", counter)


	# # This Block is for viewing the languages
	# i = 0
	# with open('DatabaseFixedValues/Lang_Scripts.csv', newline='') as csvfile:
	# 	# file_reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
	# 	file_reader = csv.DictReader(csvfile)
	# 	for row in file_reader:
	# 		if row['Language']  in language_list:
	# 			sc_list = ''
	# 			for key, value in row.items():
	# 				if value == '1':
	# 					sc_list = sc_list + '"' + str(key) + '"' + ' '
						
	# 			print(row['Language'], sc_list, len(row))
	# 			i += 1

	# print(i)

	# # end block