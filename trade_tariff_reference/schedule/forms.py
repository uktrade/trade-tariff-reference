import json
import logging
from datetime import date

from deepdiff import DeepDiff

from django import forms
from django.utils import timezone

from trade_tariff_reference.tariff.models import GeographicalAreas

from .models import Agreement, ExtendedQuota
from .utils import get_initial_quotas


logger = logging.getLogger(__name__)


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
            'country_name',
            'extended_information',
            'agreement_date_day',
            'agreement_date_month',
            'agreement_date_year',
            'agreement_date',
        ]
        labels = {
            'slug': 'Unique ID',
            'country_codes': 'Country code',
            'country_name': 'Area name',
            'agreement_name': 'Agreement title',
            'version': 'Agreement version',

        }
        widgets = {
            'slug': forms.TextInput(attrs={'class': 'govuk-input', 'required': False}),
            'agreement_name': forms.TextInput(attrs={'class': 'govuk-input'}),
            'version': forms.TextInput(attrs={'class': 'govuk-input'}),
            'country_codes': forms.TextInput(attrs={'class': 'govuk-input'}),
            'country_name': forms.TextInput(attrs={'class': 'govuk-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request') if 'request' in kwargs else None
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.agreement_date:
            self.initial['agreement_date_year'] = self.instance.agreement_date.year
            self.initial['agreement_date_month'] = self.instance.agreement_date.month
            self.initial['agreement_date_day'] = self.instance.agreement_date.day
        self.initial_change_data = self.change_dict(self.instance)

    def change_dict(self, change_instance):
        if change_instance:
            return change_instance.serialize
        return {}

    def log_change(self, change_data):
        result = DeepDiff(
            self.initial_change_data,
            change_data,
        )
        result = json.loads(result.to_json())
        if result:
            self._log_message(result)

    def _log_message(self, extra):
        extra['request'] = self.request
        logger.info('Agreement updated', extra=extra)

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        change_data = self.change_dict(instance)
        try:
            self.log_change(change_data)
        except TypeError:
            self._log_message({})
        return instance

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
                validity_start_date__lte=timezone.now()
            ).exclude(
                validity_end_date__lte=timezone.now()
            ).values_list(
                'geographical_area_id', flat=True
            )
        )
        invalid_country_codes_list = []
        country_codes = self.data.getlist('country_codes')
        found = False
        for country_code in country_codes:
            if country_code not in geographical_areas:
                found = True
                invalid_country_codes_list.append(f'Invalid country code {country_code}')
            else:
                invalid_country_codes_list.append(None)
        if found:
            self.add_error('country_codes', invalid_country_codes_list)
        return country_codes

    def is_valid(self):
        is_valid = super().is_valid()
        for field_name, error in self.errors.items():
            field = self.fields.get(field_name)
            if not field:
                return is_valid
            field_class = field.widget.attrs.get('class')
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
        self.initial.update(get_initial_quotas(self.agreement))


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
