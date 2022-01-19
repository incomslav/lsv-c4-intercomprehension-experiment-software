__author__ = 'Muhammad Ahmad'

import unicodedata


def removeDiacritics(inputString):
    """
    remove all diacritics
    :param input_str:
    :return:
    """
    normalized_form = unicodedata.normalize('NFKD', inputString)
    return u"".join([c for c in normalized_form if not unicodedata.combining(c)])