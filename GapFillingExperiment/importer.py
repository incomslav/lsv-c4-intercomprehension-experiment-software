from openpyxl import load_workbook
from collections import defaultdict
from GapFillingExperiment.models import *
import re

import os
from django.conf import settings

DEFAULT_NUMBER_REQUIRED_ANSWERS = 20
SENTENCE = 0
GROUP = 1
NATIVE_LANGUAGE = 2
FOREIGN_LANGUAGE = 3


def processGapFillingHeaders(headers):
    """
    process header
    """

    lang_native = headers[NATIVE_LANGUAGE].split()[-1]
    lang_foreign = headers[FOREIGN_LANGUAGE].split()[-1]
    counts = defaultdict(lambda: 0)
    processed_headers = []
    for i, header in enumerate(headers):
        counts[header] += 1
    for i, header in enumerate(headers):
        if counts[header] > 1:
            processed_headers.append((header, False))
        else:
            processed_headers.append((header, True))

    return lang_native, lang_foreign, processed_headers

#Added by Hasan on 2018-06-10
def processGapFillingHeadersNew(headers):
    print(headers)

    native_header = headers[NATIVE_LANGUAGE].split()[-1]
    foreign_header = headers[FOREIGN_LANGUAGE].split()[-1]

    native_split = native_header.split('_')
    foregin_split = foreign_header.split('_')

    lang_native = native_split[0]
    lang_foreign = foregin_split[0]

    script_native = None
    script_foreign = None

    if len(native_split) > 1:
        script_native = native_split[-1].upper()

    if len(foregin_split) > 1:
        script_foreign = foregin_split[-1].upper()

    counts = defaultdict(lambda:0)
    processed_headers = []
    for i,header in enumerate(headers):
        counts[header] += 1
    for i,header in enumerate(headers):
        if counts[header] > 1:
            processed_headers.append((header, False))
        else:
            processed_headers.append((header, True))

    return lang_native, lang_foreign, script_native, script_foreign, processed_headers 


def parseSentence(sentence):
    """
    parse sentence and return correct answer for each gap
    """
    sentence = sentence.replace("{", "[").replace("}", "]")
    sentence_without_gaps = sentence
    gaps = re.findall(r"[^[]*\[([^]]*)\]", sentence)
    total_gaps = len(gaps)
    gap_answer = ''
    for i in range(total_gaps):
        # gap_ans = re.findall(r"[^[]*\(([^]]*)\)", g)[0]
        # get all possible correct ans
        gap_ans = gaps[i].split('|')[1].split(',')
        for g in gap_ans:
            gap_answer += str('Gap'+str(i)+'_'+g + ',').strip()
        sentence_without_gaps = sentence_without_gaps.replace('[' + gaps[i] + ']', "").strip()

    sentence_without_gaps = sentence_without_gaps.split()
    # removing symbols
    symbols_to_remove = ['.', ',', ';', ':', '-','_']
    for symbol in symbols_to_remove:
        if symbol in sentence_without_gaps:
            sentence_without_gaps.remove(symbol)

    return gap_answer.strip(',').strip(),total_gaps,  sentence_without_gaps


def parseGapFillingFileRow(row):
    """
    parse row
    """
    sentence = str(row[SENTENCE]).strip()
    gap_answers,total_gaps, sentence_without_gaps = parseSentence(sentence)
    entry_group = row[GROUP]
    return sentence, gap_answers, entry_group,total_gaps, len(sentence_without_gaps)


def processGapFillingUploadedFile(location, filename, experiment_name, priority, medal_filename=None):
    # open the file
    filepath = os.path.join(location, filename)
    f = load_workbook(filepath)

    imported_experiments = []

    # make corresponding experiment
    for ws in f.worksheets:
        data = []
        i = 0
        headers = None
        for c in ws.rows:
            if i == 0:
                if not c[0].value is None:
                    headers = list(map(lambda x: x.value, c))
            else:
                data.append(list(map(lambda x: x.value, c)))
            i += 1

        if not headers is None:

            # Lnative, Lforeign, headers = processGapFillingHeaders(headers)

            Lnative, Lforeign, Snative, Sforeign, headers = processGapFillingHeadersNew(headers)

            # get native language from database
            LNobject = Language.objects.get(language_code=Lnative.lower())
            # get foreign language from database
            LFobject = Language.objects.get(language_code=Lforeign.lower())

            groups = {}

            # folder_name = os.path.basename(settings.GAP_FILLING_UPLOAD_FOLDER)
            folder_name = 'GapFilling'

            for d in data:
                sentence, gap_answers, group,total_gaps, sentence_words_without_gaps = parseGapFillingFileRow(d)
                if not group in groups:
                    groups[group] = []
                groups[group].append((sentence, gap_answers,total_gaps, sentence_words_without_gaps))

            for group, L in groups.items():
                # make the experiment
                name = experiment_name + "_%s-%s_group-%s" % (Lnative, Lforeign, group)
                experiment_object = GapFillingExperiment()
                experiment_object.user_medal = medal_filename
                experiment_object.save()
                experiment_object.native_language = LNobject
                experiment_object.foreign_language = LFobject
                experiment_object.experiment_name = name
                experiment_object.priority = priority

                #Added by Hasan on 2018-06-10
                experiment_object.native_script = Snative
                experiment_object.foreign_script = Sforeign

                #Added by Hasan on 2018-05-28
                experiment_object.stimuli_file = filename
                experiment_object.folder_name = folder_name
                experiment_object.save()
                # add language requirements
                # user must be native speaker of native language
                native_req, created = NativeLanguagePrerequisite.objects.get_or_create(required_language=LNobject,
                                                                                       positive=True)
                if created:
                    native_req.save()
                experiment_object.user_prerequisites.add(native_req)

                for sentence, gaps_answers,total_gaps, words_without_gaps in L:
                    # make a question plus comma separated answers for gaps and link it to this experiment_object
                    # make GapFillingQuestion
                    # total_gaps = len(gaps_answers.split(','))
                    total_words = total_gaps + words_without_gaps
                    GQ = GapFillingQuestion(sentence=sentence)
                    # set total time in seconds (3 seconds for each word + 10 seconds for each gap)
                    GQ.question_answer_time = (total_words * 3) + (total_gaps * 10)
                    GQ.save()
                    # make correct answer comma separated answer for each gap
                    GA = GapFillingCorrectAnswer()
                    GA.gaps_answers = gaps_answers
                    GA.save()
                    GQ.correct_answers.add(GA)
                    GQ.save()
                    # add question to experiment
                    experiment_object.experiment_questions.add(GQ)

                exp = {}
                exp["experiment_name"] = name
                exp["native_language"] = Lnative
                exp["foreign_language"] = Lforeign
                exp["number_of_questions"] = len(L)
                imported_experiments.append(exp)

    return imported_experiments
