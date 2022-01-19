
# __Author__ Hasan
# This script is for adding data in Users.Script table

import csv
import string
from Users.models import Language, Script, LanguageScriptRelation
def run():
	language_list = Language.objects.values_list('language_name', flat=True)
	print(len(language_list))

	with open('DatabaseFixedValues/Lang_Scripts.csv', newline='') as csvfile:
		# file_reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
		file_reader = csv.DictReader(csvfile)
		j = 0
		for row in file_reader:
			if j < 1:
				total_created = 0
				for i, (key, value) in enumerate(row.items()):
					if key != 'Language':
						# print(key, i, list(row.keys())[i])

						code = None
						if key == 'Latin script':
							code = 'LATN'
						elif key == 'Cyrillic script':
							code == 'CYRL'
						else:
							code = None

						obj, created = Script.objects.get_or_create(
							script_name = str(key),
							script_code = code,
							defaults = {'isActive':True, 'isDelete':False})

						if created:

							total_created += 1
			j += 1

		print("Total added row: ",total_created)

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