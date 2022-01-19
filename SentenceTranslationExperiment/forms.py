__author__ = 'A. K. Fischer'

from django import forms
from django.core.exceptions import ValidationError

def validateExperimentFileExtension(value):
    """ Validate that uploaded experiment file is in Excel format. """
    if not (value.name.endswith(".xls") or value.name.endswith(".xlsx")):
        raise ValidationError(u'Only Excel files (.xls, .xlsx) allowed!')


class UploadSentenceTranslationExperimentFileForm(forms.Form):
    """
    Upload experiment file form for Admin Panel.
    """
    experiment_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    priority = forms.ChoiceField(choices=[(i,i) for i in range(101)])
    file = forms.FileField(required=False, validators=[validateExperimentFileExtension])
