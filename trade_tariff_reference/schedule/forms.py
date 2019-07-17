from django import forms


class CreateAgreementForm(forms.Form):
    unique_id = forms.CharField(
        required=False,
        label='Unique ID',
        widget=forms.TextInput(
            attrs={'class': 'govuk-input', 'required': False}
        )
    )
    geographical_area_name = forms.CharField(
        required=False,
        label='Geographical area name',
        widget=forms.TextInput(
            attrs={'class': 'govuk-input'}
        )
    )
    country_code = forms.CharField(
        required=False,
        label='Country code',
        widget=forms.TextInput(
            attrs={'class': 'govuk-input'}
        )
    )
    agreement_title = forms.CharField(
        required=False,
        label='Agreement title',
        widget=forms.TextInput(
            attrs={'class': 'govuk-input'}
        )
    )
    agreement_version = forms.CharField(
        required=False,
        label='Agreement version',
        widget=forms.TextInput(
            attrs={'class': 'govuk-input'}
        )
    )
    extended_information = forms.BooleanField(
        required=False,
    )


class ManageExtendedInformationForm(forms.Form):
    pass
