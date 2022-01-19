__author__ = 'A. K. Fischer'

from django import forms
from django.core.exceptions import ValidationError
from ExperimentBasics.models import *


def validateExperimentFileExtension(value):
    """ Validate that uploaded experiment file is in Excel format. """
    if not (value.name.endswith(".xlsx")):
        raise ValidationError(u'Only Excel files (.xlsx) allowed!')


def validatePNGImage(value):
    if not (value.name.endswith(".png")):
        raise ValidationError(u'Only png files (.png) allowed!')


class UploadExperimentFileForm(forms.Form):
    """
    Upload experiment file form for Admin Panel.
    """
    txtFileDescription = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    file = forms.FileField(required=False, validators=[validateExperimentFileExtension])
    medal = forms.ImageField(required=False, validators=[validatePNGImage])


class UploadMedalForm(forms.Form):
    """
    Upload medal for an already-existing experiment.
    """
    experiment_id = forms.ModelChoiceField(queryset=Experiment.objects.all(), empty_label="select experiment")
    medal = forms.ImageField(required=True, validators=[validatePNGImage])


class NewsManagementForm(forms.Form):
    """
    Add news form for Admin Panel.
    """
    txtNewsDescriptionEn = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=True)
    txtNewsDescriptionDe = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtNewsDescriptionRu = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtNewsDescriptionBg = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtNewsDescriptionUk = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtNewsDescriptionCs = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtNewsDescriptionPl = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtNewsDescriptionHr = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtNewsDescriptionSr = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtNewsDescriptionSk = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)

    txtNewsDescriptionMk = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtNewsDescriptionSl = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)

    txtNewsDescriptionBs = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)

    priority = forms.ChoiceField(choices=[(i, i) for i in range(11)])

    news_id = forms.CharField(widget=forms.HiddenInput(attrs={'value':0}))


class MultilingualGenderManagementForm(forms.Form):
    """
    Multilingual gender management form for Admin Panel.
    """
    txtGenderEn = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtGenderDe = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtGenderRu = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtGenderBg = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtGenderUk = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtGenderCs = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtGenderPl = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtGenderHr = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtGenderSr = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtGenderSk = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtGenderMk = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtGenderSl = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtGenderBs = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    gender_id = forms.CharField(widget=forms.HiddenInput(attrs={'value':0}))
    
    
class MultilingualEducationDegreeManagementForm(forms.Form):
    """
    Multilingual education degree management form for Admin Panel.
    """
    txtEducationDegreeEn = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtEducationDegreeDe = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtEducationDegreeRu = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtEducationDegreeBg = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtEducationDegreeUk = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtEducationDegreeCs = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtEducationDegreePl = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtEducationDegreeHr = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtEducationDegreeSr = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtEducationDegreeSk = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtEducationDegreeMk = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtEducationDegreeSl = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtEducationDegreeBs = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    degree_id = forms.CharField(widget=forms.HiddenInput(attrs={'value':0}))
    
    
class MultilingualLanguageManagementForm(forms.Form):
    """
    Multilingual language management form for Admin Panel.
    """
    txtLanguageCode = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtLanguageEn = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtLanguageDe = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtLanguageRu = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtLanguageBg = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtLanguageUk = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtLanguageCs = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtLanguagePl = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtLanguageHr = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtLanguageSr = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtLanguageSk = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtLanguageMk = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtLanguageSl = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    txtLanguageBs = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    language_id = forms.CharField(widget=forms.HiddenInput(attrs={'value':0}))

    
class ExperimentInfoManagementForm(forms.Form):
    """
    Add experiment info form for Admin Panel.
    """
    txtExperimentInfoEn = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=True)
    txtExperimentInfoDe = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtExperimentInfoRu = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtExperimentInfoBg = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtExperimentInfoUk = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtExperimentInfoCs = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtExperimentInfoPl = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtExperimentInfoHr = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtExperimentInfoSr = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtExperimentInfoSk = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)

    txtExperimentInfoMk = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtExperimentInfoSl = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtExperimentInfoBs = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)

    experiment_info_id = forms.CharField(widget=forms.HiddenInput(attrs={'value':0}))


class InformedConsentManagementForm(forms.Form):
    """
    Add informed consent form for Admin Panel.
    """
    txtInformedConsentDescriptionEn = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=True)
    txtInformedConsentDescriptionDe = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtInformedConsentDescriptionRu = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtInformedConsentDescriptionBg = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtInformedConsentDescriptionUk = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtInformedConsentDescriptionCs = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtInformedConsentDescriptionPl = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtInformedConsentDescriptionHr = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtInformedConsentDescriptionSr = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtInformedConsentDescriptionSk = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)

    txtInformedConsentDescriptionMk = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)
    txtInformedConsentDescriptionSl = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)

    txtInformedConsentDescriptionBs = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,'cols':50, 'class': 'form-control'}),
                                           required=False)

    priority = forms.ChoiceField(choices=[(i, i) for i in range(11)])

    informed_consent_id = forms.CharField(widget=forms.HiddenInput(attrs={'value':0}))