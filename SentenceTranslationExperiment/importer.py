__author__ = 'Andrea Fischer'

from openpyxl import load_workbook
from collections import defaultdict
import json

import os

from Users.models import Language
from SentenceTranslationExperiment.models import *

from django.conf import settings

DEFAULT_NUMBER_REQUIRED_ANSWERS = 20

NATIVE_LANGUAGE = 0
FOREIGN_LANGUAGE = 1
GROUP=2
ALTERNATIVE_ANSWERS = 3


def changeSentenceTranslationExperimentFileActivationStatus(userId, fileId, activationStatus):
    try:
        SentenceTranslation_file = SentenceTranslationUploadedExperimentQuestionFile.objects.get(pk=fileId)
        if activationStatus != SentenceTranslation_file.is_active:
            SentenceTranslation_file.is_active = activationStatus
            # set all associated questions to the given activation status
            for question in SentenceTranslation_file.associated_questions.all():
                question.is_active = activationStatus
                question.save()
            SentenceTranslation_file.save()
            return True
        return False
    except Exception as e:
        return HttpResponse(status=500)


def processSentenceTranslationHeaders(headers):
    lang_native = headers[NATIVE_LANGUAGE].split()[-1]
    lang_foreign = headers[FOREIGN_LANGUAGE].split()[-1]
    counts = defaultdict(lambda:0)
    processed_headers = []
    for i,header in enumerate(headers):
        counts[header] += 1
    for i,header in enumerate(headers):
        if counts[header] > 1:
            processed_headers.append((header, False))
        else:
            processed_headers.append((header, True))

    return lang_native, lang_foreign, processed_headers


#Added by Hasan on 2018-06-10
def processSentenceTranslationHeadersNew(headers):
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


def parseSentenceTranslationFileRow(row, headers):
    meta = {}
    lang_native_entry = row[NATIVE_LANGUAGE]
    lang_foreign_entry = row[FOREIGN_LANGUAGE]
    entry_group = row[GROUP]
    for entry,(header, single_entry) in zip(row[4:], headers[4:]):
        if single_entry:
            meta[header] = entry
        else:
            if not entry is None:
                if not header in meta:
                    meta[header] = []
  
                meta[header].append(entry)
  
    return lang_native_entry, lang_foreign_entry, entry_group, meta


def processSentenceTranslationUploadedFile(location, filename, experiment_name, priority):
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
                    headers = list(map(lambda x:x.value,c))
            else:
                data.append(list(map(lambda x:x.value,c)))
            i += 1
    

        if not headers is None:
                # Lnative, Lforeign, headers = processSentenceTranslationHeaders(headers)

                Lnative, Lforeign, Snative, Sforeign, headers = processSentenceTranslationHeadersNew(headers)
                # get native language from database
                LNobject = Language.objects.get(language_code=Lnative.lower())
                # get foreign language from database
                LFobject = Language.objects.get(language_code=Lforeign.lower())
                
                groups = {}


                for d in data:
                    native_entry, foreign_entry, group, meta = parseSentenceTranslationFileRow(d,headers)
                    if not group in groups:
                        groups[group] = []
                    groups[group].append((native_entry, foreign_entry, meta))
                
                for group, L in groups.items():
                    # make the experiment
                    name = experiment_name+"_%s-%s_group-%s" % (Lnative,Lforeign, group)
                    experiment_object = SentenceTranslationExperiment()
                    experiment_object.save()
                    experiment_object.native_language = LNobject
                    experiment_object.foreign_language = LFobject
                    experiment_object.experiment_name = name
                    experiment_object.priority = priority

                    #Added by Hasan on 2018-06-10
                    experiment_object.native_script = Snative
                    experiment_object.foreign_script = Sforeign

                    experiment_object.stimuli_file = filename
                    experiment_object.save()
                    # add language requirements
                    # user must be native speaker of native language
                    native_req, created = NativeLanguagePrerequisite.objects.get_or_create(required_language=LNobject, positive=True)
                    if created:
                        native_req.save()
                    experiment_object.user_prerequisites.add(native_req)
                    """ Nixed this prerequisite as per decision on December 19, 2016
                    # user cannot be native speaker of foreign language
                    non_native_req, created = NativeLanguagePrerequisite.objects.get_or_create(required_language=LFobject, positive=False)
                    if created:
                        non_native_req.save()
                    experiment_object.user_prerequisites.add(non_native_req)
                    """
                    for native_entry, foreign_entry, meta in L:
                        # make a question plus possible correct answers and link them to this experiment_object
                        # make SentenceTranslationQuestion
                        FQ = SentenceTranslationQuestion(stimulus_sentence=foreign_entry)
                        FQ.save()
                        # add question to experiment
                        experiment_object.experiment_questions.add(FQ)
                    
                    exp = {}
                    exp["experiment_name"] = name
                    exp["native_language"] = Lnative
                    exp["foreign_language"] = Lforeign
                    exp["number_of_questions"] = len(L)
                    imported_experiments.append(exp)
    
    return imported_experiments
