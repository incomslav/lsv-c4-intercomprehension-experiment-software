"""Copyright Askbot SpA 2014, Licensed under GPLv3 license."""
import os
from django.conf import settings
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import StreamingHttpResponse, Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from datetime import datetime

try:
    from django.utils.module_loading import import_string as import_module
except ImportError:
    from django.utils.module_loading import import_by_path as import_module

#utils functions
def check_access(request):
    """Returns true if user has access to the directory"""
    access_mode = getattr(settings, 'DIRECTORY_ACCESS_MODE', 'public')
    if access_mode == 'public':
        return True
    elif access_mode == 'use-perms':
        if request.user.is_anonymous():
            return False
        else:
            return request.user.has_perm('directory.read')
    elif access_mode == 'custom':
        check_perm = settings.DIRECTORY_ACCESS_FUNCTION
        if isinstance(check_perm, basestring):
            check_perm = import_module(check_perm)
        elif not hasattr(check_perm, '__call__'):
            raise ImproperlyConfigured('DIRECTORY_ACCESS_FUNCTION must either be a function or python path')
        return check_perm(request)
    else:
        raise ImproperlyConfigured(
            "Invalid setting DIRECTORY_ACCESS_MODE: only values "
            "'public', 'use-perms', and 'custom' are allowed"
        )


def get_file_names(directory):
    """Returns list of file names within directory"""
    contents = os.listdir(directory)
    files = list()
    for item in contents:
        if os.path.isfile(os.path.join(directory, item)):
            files.append(item)
    return files

def get_creation_time(directory):
    file_list = {}
    try:
        contents = os.listdir(directory)

        for item in contents:
            if os.path.isfile(os.path.join(directory,item)):
                file_list[item] = datetime.fromtimestamp(os.path.getctime(os.path.join(directory,item))).strftime('%B %d, %Y %H:%M:%S %Z')

    except:
        pass
    
    return file_list

def read_file_chunkwise(file_obj):
    """Reads file in 32Kb chunks"""
    while True:
        data = file_obj.read(32768)
        if not data:
            break
        yield data

#view functions below
def index(request):
    # return HttpResponseRedirect(reverse('backups:directory_list', args=()))
    return list_directory(request)

def list_directory(request):
    """default view - listing of the directory"""
    data = {}
    if check_access(request):
        # directory = settings.DIRECTORY_DIRECTORY

        # For Free Translation experiment files
        free_translation_directory = settings.FREE_TRANSLATION_UPLOAD_FOLDER
        # data['free_translation_directory_name'] = os.path.basename(free_translation_directory)
        data['free_translation_directory_name'] = 'FreeTranslation'
        data['free_translation_directory_files'] = get_creation_time(free_translation_directory)
        
        # For gap filling experiment files
        gap_filling_directory = settings.GAP_FILLING_UPLOAD_FOLDER
        # data['gap_filling_directory_name'] = os.path.basename(gap_filling_directory)
        data['gap_filling_directory_name'] = 'GapFilling'
        data['gap_filling_directory_files'] = get_creation_time(gap_filling_directory)

        # For pharse translation experiment files
        pharse_translation_directory = settings.PHRASE_TRANSLATION_UPLOAD_FOLDER
        # data['pharse_translation_directory_name'] = os.path.basename(pharse_translation_directory)
        data['pharse_translation_directory_name'] = 'PhraseTranslation'
        data['pharse_translation_directory_files'] = get_creation_time(pharse_translation_directory)

        # For Free translation with context experiment
        free_translation_with_context_directoy = settings.FREE_TRANSLATION_WITH_CONTEXT_UPLOAD_FOLDER
        data['free_translation_with_context_directory_name'] = "FreeTranslationWithContext"
        data['free_translation_with_context_directory_files'] = get_creation_time(free_translation_with_context_directoy)

        template = getattr(settings, 'DIRECTORY_TEMPLATE', 'directory/list.html')
        return render(request, 'directory/list.html', data)
        
    else:
        raise PermissionDenied()

def download_file(request, folder_name, file_name):
    """allows authorized user to download a given file"""

    if os.path.sep in file_name:
        raise PermissionDenied()

    if check_access(request):
        directory = os.path.join(settings.UPLOADED_FILE_DIRECTORY, folder_name)
        print(directory)
        #make sure that file exists within current directory
        files = get_file_names(directory)
        print(files)
        if file_name in files:
            file_path = os.path.join(directory, file_name)
            # response = StreamingHttpResponse(content_type='application/force-download')
            # response['Content-Disposition'] = 'attachment; filename=%s' % file_name
            # file_obj = open(os.path.join(directory, file_name))
            # response.streaming_content = read_file_chunkwise(file_obj)
            # return response
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response
        else:
            raise Http404



