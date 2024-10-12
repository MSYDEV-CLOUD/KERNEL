from django import forms
from .models import IFTACalculatorService

class IFTACalculatorForm(forms.ModelForm):
    class Meta:
        model = IFTACalculatorService
        fields = ['company_name', 'phone_number', 'email', 'document']
        widgets = {
            'phone_number': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }
