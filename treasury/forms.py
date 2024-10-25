from django import forms
from treasury.models import Branchs, Currency


class NewBranchForm(forms.ModelForm):
    class Meta:
        model = Branchs
        fields = ['branch_code', 'branch_name']
        labels = {
            'branch_code': 'Branch Code',
            'branch_name': 'Branch Name',
        }
        widgets = {
            'branch_code': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Branch Code',
            }),
            'branch_name': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Branch Name',
            })
        }


class NewCurrencyForm(forms.ModelForm):
    class Meta:
        model = Currency
        fields = ['currency_sign', 'currency_name']
        labels = {
            'currency_sign': 'Currency Sign',
            'currency_name': 'Currency Name',
        }
        widgets = {
            'currency_sign': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Currency Sign',
            }),
            'currency_name': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Currency Name',
            })
        }




