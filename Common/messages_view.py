__author__ = 'Muhammad Ahmad'

from django.http import HttpResponse
from django.views.generic import View
from Common import constants


class MessagesView(View):
    """
    Messages View
    """

    def get(self, request):
        return HttpResponse(str("Get Call"))

    def post(self, request):
        resp = HttpResponse('')
        if request.is_ajax():
            requestType = request.POST['type']
            if requestType == '1':
                messageId = request.POST['messageId']

                if messageId == '1':
                    resp = HttpResponse(
                        constants.MultilingualMessagesConstants.ARE_YOU_SURE_YOU_WANT_TO_DELETE_WARNING_MESSAGE)
                elif messageId == '2':
                    resp = HttpResponse(
                        constants.MultilingualMessagesConstants.SELECT_PROFICIENCY_LEVEL_FOR_ALL_LANGUAGES_MESSAGE)
                elif messageId == '3':
                    resp = HttpResponse(
                        constants.MultilingualMessagesConstants.SELECT_LANGUAGE_MESSAGE)
                elif messageId == '4':
                    resp = HttpResponse(
                        constants.MultilingualMessagesConstants.ARE_YOU_SURE_YOU_WANT_TO_ACCEPT_THIS_TRANSLATION_ONCE_YOU_ACCEPT_YOU_CANT_CHANGE)
                elif messageId == '5':
                    # resp = HttpResponse(
                    #     constants.MultilingualMessagesConstants.CLICK_ALL_WORDS_BEFORE_GETTING_NEW_SENTENCE_MESSAGE)
                    resp = HttpResponse(
                        constants.MultilingualMessagesConstants.YOU_DID_NOT_ENTER_ANY_TRANSLATION_ARE_YOU_SURE_YOU_WANT_TO_SEE_NEXT_SENTENCE)
                elif messageId == '6':
                    resp = HttpResponse(
                        constants.MultilingualMessagesConstants.DO_NOT_NAVIGATE_AWAY_FROM_YOUR_BROWSER_MESSAGE)
                elif messageId == '7':
                    resp = HttpResponse(
                        constants.MultilingualMessagesConstants.CLICK_ALL_WORDS_BEFORE_GETTING_NEW_SENTENCE_MESSAGE)

        return resp