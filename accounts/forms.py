from django import forms
from allauth.account.forms import SignupForm

class CustomSignupForm(SignupForm):
    DEPARTMENT_CHOICES = (
        ('admin', 'Internal Control'),
        ('branch', 'Branch'),
        ('treasury', 'Treasury Department'),
        ('trops', 'Troops Department'),
    )
    
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES, required=True)
    branch_code = forms.CharField(max_length=50, required=False)

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.department = self.cleaned_data.get('department')
        user.branch_code = self.cleaned_data.get('branch_code')
        user.save()
        return user
