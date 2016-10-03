from django import forms
from .models import *
from django.forms import TextInput, Select, Textarea, FileInput, EmailInput, ModelChoiceField, HiddenInput


class SignupForm(forms.ModelForm):
    class Meta:
        model = Signup
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget = TextInput(attrs={
            'id': 'first_name',
            'class': 'form-control input-lg',
            'placeholder': 'First name'})
        self.fields['first_name'].label = ''

        self.fields['last_name'].widget = TextInput(attrs={
            'id': 'last_name',
            'class': 'form-control input-lg',
            'placeholder': 'Last name'})
        self.fields['last_name'].label = ''

        self.fields['email'].widget = TextInput(attrs={
            'id': 'e-mail',
            'class': 'form-control input-lg',
            'placeholder': 'Your e-mail address'})
        self.fields['email'].label = ''

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # email_base, provider = email.split("@")
        # domain, extension = provider.split('.')
        # if not domain == 'USC':
        #   raise forms.ValidationError("Please make sure you use your USC email.")
        # if not extension == "edu":
        #   raise forms.ValidationError("Please use a valid .EDU email address")
        return email