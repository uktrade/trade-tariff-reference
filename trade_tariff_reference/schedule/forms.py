from datetime import date

from django import forms

from .models import Agreement


class AgreementModelForm(forms.ModelForm):
    extended_information = forms.BooleanField(
        required=False,
    )
    agreement_date_day = forms.CharField(
        required=True, max_length=2,
        widget=forms.NumberInput(
            attrs={
                'class': 'govuk-input govuk-date-input__input govuk-input--width-2',
                'pattern': '[0-9]*',
            }
        ),
    )
    agreement_date_month = forms.CharField(
        required=True, max_length=2,
        widget=forms.NumberInput(
            attrs={
                'class': 'govuk-input govuk-date-input__input govuk-input--width-2',
                'pattern': '[0-9]*',
            }
        ),
    )
    agreement_date_year = forms.CharField(
        required=True, max_length=4,
        widget=forms.NumberInput(
            attrs={
                'class': 'govuk-input govuk-date-input__input govuk-input--width-4',
                'pattern': '[0-9]*',
            }
        ),
    )
    agreement_date = forms.CharField(required=False, max_length=20, widget=forms.HiddenInput(attrs={'required': False}))

    class Meta:
        model = Agreement
        fields = [
            'slug',
            'country_codes',
            'agreement_name',
            'version',
            'geographical_area',
            'extended_information',
            'agreement_date_day',
            'agreement_date_month',
            'agreement_date_year',
            'agreement_date',
        ]
        labels = {
            'slug': 'Unique ID',
            'country_codes': 'Country code',
            'agreement_name': 'Agreement title',
            'version': 'Agreement version',
            'geographical_area': 'Geographical area name',

        }
        widgets = {
            'slug': forms.TextInput(attrs={'class': 'govuk-input', 'required': False}),
            'agreement_name': forms.TextInput(attrs={'class': 'govuk-input'}),
            'version': forms.TextInput(attrs={'class': 'govuk-input'}),
            'geographical_area': forms.TextInput(attrs={'class': 'govuk-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.agreement_date:
            self.initial['agreement_date_year'] = self.instance.agreement_date.year
            self.initial['agreement_date_month'] = self.instance.agreement_date.month
            self.initial['agreement_date_day'] = self.instance.agreement_date.day

    def clean(self):
        cleaned_data = super().clean()
        year = cleaned_data.pop('agreement_date_year', None)
        month = cleaned_data.pop('agreement_date_month', None)
        day = cleaned_data.pop('agreement_date_day', None)
        if year and month and day:
            try:
                agreement_date = date(int(year), int(month), int(day))
            except ValueError:
                self.add_error('agreement_date', 'Invalid date')
            else:
                cleaned_data['agreement_date'] = agreement_date
        return cleaned_data

    def clean_country_codes(self):
        country_codes = self.data.getlist('country_codes')
        for country_code in country_codes:
            if len(country_code) > 6:
                raise forms.ValidationError(f'Invalid country code [{country_code}] value too long max 6.')
        return country_codes


class ManageExtendedInformationForm(forms.Form):
    pass
