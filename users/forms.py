from django import forms
from .models import UserProfile
import re

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'profile_picture']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Cognome',
            'email': 'Email',
            'profile_picture': 'Foto del Profilo',
        }

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if re.search(r'\d', first_name):
            raise forms.ValidationError("Il nome non può contenere numeri.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if re.search(r'\d', last_name):
            raise forms.ValidationError("Il cognome non può contenere numeri.")
        return last_name