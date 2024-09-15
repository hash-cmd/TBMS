from django.shortcuts import get_object_or_404
from dataclasses import field
from django import forms
from django_select2.forms import ModelSelect2Widget
from branch.models import CustomerInformation
from treasury.models import TreasuryBills, Branchs, Currency
from dal import autocomplete


class AccountNumberWidget(autocomplete.ModelSelect2):
    model = CustomerInformation
    search_fields = ['account_number__icontains']
    
    def label_from_instance(self, obj):
        return obj.account_number

class NewTreasuryBillForm(forms.ModelForm):
    class Meta:
        model = TreasuryBills
        fields = [
            'branch_purchased_at', 'account_domicile_branch', 'transaction_code',
            'account_number', 'currency', 'customer_amount', 'tenor', 'maturity_instruction',
            'file',
        ]                    
        widgets = {
            'account_number': AccountNumberWidget(url='customer-autocomplete'),
            'file': forms.FileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'account_number' in self.data:
            try:
                account_number = self.data.get('account_number')
                # Find the CustomerInformation instance with this account number
                instance = CustomerInformation.objects.get(account_number=account_number)
                self.fields['account_number'].initial = instance.account_number
            except CustomerInformation.DoesNotExist:
                pass


       
        
        
class NewCustomerForm(forms.ModelForm):
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
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/jpeg'}),
            'csd_file': forms.FileInput(attrs={'class': 'form-control', 'accept': 'application/pdf'}),  # Update here
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
            'image': 'Image',
            'csd_file': 'CSD File',
        } 
        title = forms.ChoiceField(required=True)
        surname_or_company_name = forms.CharField(required=True)
        other_names = forms.CharField(required=False)
        date_of_birth_or_incorporation_of_business = forms.DateField(required=True)
        nationality = forms.CharField(required=False)
        occupation = forms.CharField(required=False)
        address = forms.CharField(required=True)
        residential_address = forms.CharField(required=False)
        residential_status = forms.ChoiceField(required=True)
        phone_number = forms.CharField(required=True)
        fax_number = forms.CharField(required=False)
        email = forms.EmailField(required=True)
        id_type = forms.ChoiceField(required=True)
        id_number = forms.CharField(required=True)
        place_of_issue = forms.CharField(required=True)
        expiry_date = forms.DateField(required=True)
        account_number = forms.CharField(required=True)
        account_branch = forms.CharField(required=True)
        csd_number = forms.CharField(required=False)
        image = forms.ImageField(required=False)
        csd_file = forms.FileField(required=True)
        
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check file extension
            if not image.name.lower().endswith('.jpg') and not image.name.lower().endswith('.jpeg'):
                raise ValidationError('Only JPEG images are allowed.')
        return image
        
    def clean_csd_file(self):
        file = self.cleaned_data.get('csd_file')
        if file and file.content_type != 'application/pdf':
            raise ValidationError('Only PDF files are allowed.')
        return file
