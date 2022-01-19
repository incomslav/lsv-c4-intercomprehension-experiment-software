from django import forms
from django.utils.translation import activate

from Common import constants

from Users.enums import *
from Users.models import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import PasswordChangeForm


class UserInfoForm(forms.Form):
    """
    User info form
    """
    # languageCode= 'en'
    def __init__(self, *args, **kwargs):
        # self.webLanguageId = kwargs.pop(CookieFields.WebsiteLanguageId)
        self.languageCode = kwargs.pop('languageCode','en')
        # excluding the australian and britain english and order by web language
        qs_language = Language.objects.exclude(language_code__in=['en-au','en-gb','pt-br','es-ar','es-mx','es-ni','es-ve']).order_by('language_name_'+self.languageCode)
        qs_country = Country.objects.order_by('country_name_'+self.languageCode)
        super(UserInfoForm, self).__init__(*args, **kwargs)

        self.fields['area_country'].queryset = qs_country
        self.fields['education_country'].queryset = qs_country

        self.fields['area_language'].queryset = qs_language
        self.fields['living_area_language'].queryset = qs_language
        self.fields['native_language'].queryset = qs_language
        self.fields['home_language'].queryset = qs_language
        self.fields['learned_language'].queryset = qs_language


    age = forms.CharField(widget=forms.TextInput(attrs={'class': 'onlyInt number-input form-control'}), required=True)

    gender = forms.ModelChoiceField(queryset=Gender.objects.all(), to_field_name="name",
                                    widget=forms.Select(attrs={'class': 'form-control'}), required=True)

    area_country = forms.ModelChoiceField(queryset=Country.objects.order_by('country_name'),
                                          widget=forms.Select(attrs={'class': 'form-control'}), required=True)

    area_language = forms.ModelChoiceField(queryset=Language.objects.order_by('language_name'),
                                           widget=forms.Select(attrs={'class': 'form-control'}), required=False)

    living_period = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control onlyInt lessThanEqualAge number-input'}), required=True)

    is_lived_in_other_area = forms.BooleanField(widget=forms.RadioSelect(
        choices=((False, constants.CommonConstants.NO_TEXT), (True, constants.CommonConstants.YES_TEXT))),
                                                initial=False, required=False)

    #living_area_language = forms.TypedChoiceField(choices=LanguageList, widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    living_area_language = forms.ModelChoiceField(queryset=Language.objects.order_by('language_name'),
                                                  widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    living_area_period = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control onlyInt lessThanAge number-input'}), required=False)

    is_multilingual = forms.BooleanField(widget=forms.RadioSelect(
        choices=[(False, constants.CommonConstants.NO_TEXT), (True, constants.CommonConstants.YES_TEXT)]),
                                         initial=False, required=False)

    native_language = forms.ModelChoiceField(queryset=Language.objects.all(),
                                             widget=forms.Select(attrs={'class': 'form-control'}), required=False)

    education_country = forms.ModelChoiceField(queryset=Country.objects.order_by('country_name'),
                                               widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    education_time = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control onlyInt lessThanAge number-input'}), required=False)

    home_language = forms.ModelChoiceField(queryset=Language.objects.order_by('language_name'),
                                           widget=forms.Select(attrs={'class': 'form-control'}), required=False)

    learned_language = forms.ModelChoiceField(queryset=Language.objects.order_by('language_name'),
                                              widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    learned_language_time = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control onlyInt lessThanAge number-input'}), required=False)

    # EducationDegree
    highest_education_degree = forms.ModelChoiceField(queryset=EducationDegree.objects.all(),
                                                      widget=forms.Select(attrs={'class': 'form-control'}),
                                                      required=False)
    have_linguistics_degree = forms.BooleanField(widget=forms.RadioSelect(
        choices=[(False, constants.CommonConstants.NO_TEXT), (True, constants.CommonConstants.YES_TEXT)]),
                                                 initial=False, required=False)

    prolific_id = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)


class PasswordChangeCustomForm(PasswordChangeForm):

    old_password = forms.CharField(required=True,
                                   widget=forms.PasswordInput(attrs={
                                        'placeholder': _('OLD_PASSWORD_TEXT')}))
    new_password1 = forms.CharField(required=True,widget=forms.PasswordInput(attrs={
                                        'placeholder': _('NEW_PASSWORD_TEXT')}))
    new_password2 = forms.CharField(required=True,
                                    widget=forms.PasswordInput(attrs={
                                        'placeholder': _("NEW_PASSWORD_CONFIRMATION_TEXT")}))

class PasswordResetConfirmationForm(forms.Form):

    new_password1 = forms.CharField(required=True,widget=forms.PasswordInput(attrs={
                                        'placeholder': _('NEW_PASSWORD_TEXT')}))
    new_password2 = forms.CharField(required=True,
                                    widget=forms.PasswordInput(attrs={
                                        'placeholder': _("NEW_PASSWORD_CONFIRMATION_TEXT")}))
