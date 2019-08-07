from datetime import date

from django import forms

from trade_tariff_reference.tariff.models import GeographicalAreas

from .models import Agreement, ExtendedQuota


class AgreementModelForm(forms.ModelForm):

    extended_information = forms.BooleanField(
        required=False,
    )
    agreement_date_day = forms.CharField(
        required=True,
        max_length=2,
        widget=forms.NumberInput(
            attrs={
                'class': 'govuk-input govuk-date-input__input govuk-input--width-2',
                'pattern': '[0-9]*',
            }
        ),
    )
    agreement_date_month = forms.CharField(
        required=True,
        max_length=2,
        widget=forms.NumberInput(
            attrs={
                'class': 'govuk-input govuk-date-input__input govuk-input--width-2',
                'pattern': '[0-9]*',
            }
        ),
    )
    agreement_date_year = forms.CharField(
        required=True,
        max_length=4,
        widget=forms.NumberInput(
            attrs={
                'class': 'govuk-input govuk-date-input__input govuk-input--width-4',
                'pattern': '[0-9]*',
            }
        ),
    )
    agreement_date = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.HiddenInput(
            attrs={'required': False}
        ),
    )

    class Meta:
        model = Agreement
        fields = [
            'slug',
            'country_codes',
            'agreement_name',
            'version',
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

        }
        widgets = {
            'slug': forms.TextInput(attrs={'class': 'govuk-input', 'required': False}),
            'agreement_name': forms.TextInput(attrs={'class': 'govuk-input'}),
            'version': forms.TextInput(attrs={'class': 'govuk-input'}),
            'country_codes': forms.TextInput(attrs={'class': 'govuk-input'}),
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
        geographical_areas = list(
            GeographicalAreas.objects.filter(
                validity_start_date__lte=date.today()
            ).exclude(
                validity_end_date__lte=date.today()
            ).values_list(
                'geographical_area_id', flat=True
            )
        )
        invalid_country_codes_list = []
        country_codes = self.data.getlist('country_codes')
        for country_code in country_codes:
            if country_code not in geographical_areas:
                invalid_country_codes_list.append(country_code)
        if invalid_country_codes_list:
            invalid_country_codes = ', '.join(invalid_country_codes_list)
            raise forms.ValidationError(f'Invalid country code [{invalid_country_codes}]')
        return country_codes

    def is_valid(self):
        is_valid = super().is_valid()
        for field_name, error in self.errors.items():
            field_class = self.fields[field_name].widget.attrs.get('class')
            if field_class:
                self.fields[field_name].widget.attrs['class'] = f'{field_class} {field_class}--error'
        return is_valid


class ManageExtendedInformationForm(forms.Form):
    origin_quotas = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'govuk-textarea', 'rows': 8, 'required': False}
        ),
    )
    licensed_quotas = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'govuk-textarea', 'rows': 8, 'required': False}
        ),
    )
    scope_quotas = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'govuk-textarea', 'rows': 8, 'required': False}
        )
    )
    staging_quotas = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'govuk-textarea', 'rows': 8, 'required': False}
        ),
    )

    def __init__(self, *args, **kwargs):
        self.agreement = kwargs.pop('agreement')
        super().__init__(*args, **kwargs)
        self.initial['origin_quotas'] = self.get_initial_origin_quotas()
        self.initial['licensed_quotas'] = self.get_initial_licensed_quotas()
        self.initial['scope_quotas'] = self.get_initial_scope_quotas()
        self.initial['staging_quotas'] = self.get_initial_staging_quotas()

    def get_initial_origin_quotas(self):
        quotas = [quota.origin_quota_string for quota in self.agreement.origin_quotas]
        return '\r\n'.join(quotas)

    def get_initial_licensed_quotas(self):
        quotas = [quota.licensed_quota_string for quota in self.agreement.licensed_quotas]
        return '\r\n'.join(quotas)

    def get_initial_scope_quotas(self):
        quotas = [quota.scope_quota_string for quota in self.agreement.scope_quotas]
        return '\r\n'.join(quotas)

    def get_initial_staging_quotas(self):
        quotas = [quota.staging_quota_string for quota in self.agreement.staging_quotas]
        return '\r\n'.join(quotas)


class ExtendedQuotaForm(forms.ModelForm):

    class Meta:
        model = ExtendedQuota
        fields = [
            'agreement',
            'quota_order_number_id',
            'is_origin_quota',
            'opening_balance',
            'measurement_unit_code',
            'quota_type',
            'scope',
            'addendum',
        ]
