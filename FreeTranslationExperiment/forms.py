__author__ = 'A. K. Fischer'

from django import forms
from django.core.exceptions import ValidationError
from FreeTranslationExperiment.models import FreeTranslationQuestion

def validateExperimentFileExtension(value):
    """ Validate that uploaded experiment file is in Excel format. """
    if not (value.name.endswith(".xls") or value.name.endswith(".xlsx")):
        raise ValidationError(u'Only Excel files (.xls, .xlsx) allowed!')


def validatePNGImage(value):
    if not (value.name.endswith(".png")):
        raise ValidationError(u'Only png files (.png) allowed!')


class UploadFreeTranslationExperimentFileForm(forms.Form):
    """
    Upload experiment file form for Admin Panel.
    """
    experiment_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    priority = forms.ChoiceField(choices=[(i,i) for i in range(101)])
    file = forms.FileField(required=False, validators=[validateExperimentFileExtension])
    medal = forms.ImageField(required=False, validators=[validatePNGImage])


class UploadFreeTranslationQuestionAudioForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UploadFreeTranslationQuestionAudioForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['foreign_word'].widget.attrs['readonly'] = True

    def clean_foreign_word(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.foreign_word
        else:
            return self.cleaned_data['foreign_word']



    class Meta:
        model = FreeTranslationQuestion
        fields = [
            'foreign_word',
            'audio_file',]


class UpdateFreeTranslationQuestionAudioForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UpdateFreeTranslationQuestionAudioForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['foreign_word'].widget.attrs['readonly'] = True

    def clean_foreign_word(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.foreign_word
        else:
            return self.cleaned_data['foreign_word']


    class Meta:
        model = FreeTranslationQuestion
        fields = [
            'foreign_word',
            'has_audio',
            'audio_file',]