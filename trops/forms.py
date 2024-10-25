from django.shortcuts import get_object_or_404
from dataclasses import field
from django import forms
from django_select2.forms import ModelSelect2Widget
from branch.models import CustomerInformation
from treasury.models import TreasuryBills, Branchs, Currency, BOG_Weekly_Code


class EditCustomerForm(forms.ModelForm):
    class Meta:
        model = CustomerInformation
        fields = [
            'title',
            'surname_or_company_name',
            'other_names',
            'date_of_birth_or_incorporation_of_business',
            'nationality',
            'occupation',
            'address',
            'residential_address',
            'residential_status',
            'phone_number',
            'fax_number',
            'email',
            'id_type',
            'id_number',
            'place_of_issue',
            'expiry_date',
            'account_number',
            'account_branch',
            'csd_number',
            'image',
            'csd_file'
        ]
        widgets = {
            'title': forms.Select(attrs={'class': 'form-select'}),
            'surname_or_company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'other_names': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth_or_incorporation_of_business': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'residential_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Residential Address'}),
            'residential_status': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'fax_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fax Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'id_type': forms.Select(attrs={'class': 'form-select'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID Number'}),
            'place_of_issue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Place of Issue'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD', 'type': 'date'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Number'}),
            'account_branch': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Branch'}),
            'csd_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CSD Number'}),
        }
        labels = {
            'title': 'Title',
            'surname_or_company_name': 'Surname/Company Name',
            'other_names': 'Other Names',
            'date_of_birth_or_incorporation_of_business': 'Date of Birth/Date of Incorporation',
            'nationality': 'Nationality',
            'occupation': 'Occupation',
            'address': 'Address',
            'residential_address': 'Residential Address',
            'residential_status': 'Residential Status',
            'phone_number': 'Phone Number',
            'fax_number': 'Fax Number',
            'email': 'Email',
            'id_type': 'ID Type',
            'id_number': 'ID Number',
            'place_of_issue': 'Place of Issue',
            'expiry_date': 'Expiry Date',
            'account_number': 'Account Number',
            'account_branch': 'Account Branch',
            'csd_number': 'CSD Number',
        }


class BOGWeeklyForm(forms.ModelForm):
    class Meta:
        model = BOG_Weekly_Code
        fields = ['code' ] 
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter code'}),
        }

        labels = {
            'code': 'BOG Weekly Code',
        }