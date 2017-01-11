from django import forms
from .models import *
from django.contrib.auth.models import User
from django.forms import TextInput, Select, Textarea, FileInput, EmailInput, PasswordInput, ModelChoiceField, HiddenInput


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

        self.fields['email'].widget = EmailInput(attrs={
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

class InviteForm(forms.Form):
    email = forms.EmailField(label='Email')

class EditUserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [ 'public_name', 'public_email', 'website', 'location', 'picture', 'about' ]

    def __init__(self, *args, **kwargs):
        super(EditUserProfileForm, self).__init__(*args, **kwargs)

        self.fields['public_name'].widget = TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your real name, if you choose...',
            })
        self.fields['public_name'].label = 'Public Name'

        self.fields['about'].widget = Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Share a little bit about yourself',
            })
        self.fields['about'].label = 'About You'

        self.fields['location'].widget = TextInput(attrs={
            'class': 'form-control ',
            'placeholder': 'Where do you live?',
            })
        self.fields['location'].label = 'Location'

        # self.fields['picture'].widget = FileInput(attrs={
        #     'class': 'form-control',
        #     'placeholder': 'Upload an avatar image',
        #     })
        # self.fields['picture'].label = 'Profile Picture'

        self.fields['website'].widget = TextInput(attrs={
            'class': 'form-control',
            'placeholder': "If you have one",
            })
        self.fields['website'].label = 'Website'

        self.fields['public_email'].widget = EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your public email address',
            })
        self.fields['public_email'].label = 'Public Email'

class EditUserAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [ 'username', 'email', ]

        def __init__(self, *args, **kwargs):
            super(EditUserAccountForm, self).__init__(*args, **kwargs)

            self.fields['username'].widget = TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your username on OmniBuilds',
                })
            self.fields['username'].label = 'Username'

            self.fields['email'].widget = EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your account email address',
                })
            self.fields['email'].label = 'Account Email'

            # self.fields['password'].widget = PasswordInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': 'Your password to login to OmniBuilds',
            #     })
            # self.fields['email'].label = 'Account Password'

