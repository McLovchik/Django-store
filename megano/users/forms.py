from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UsernameField, UserCreationForm


User = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input'
    }))
    phone = forms.CharField(widget=forms.NumberInput(attrs={
        'class': 'form-input'
    }))
    fullname = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input'
    }))
    city = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input'
    }))
    address = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input'
    }))

    class Meta:
        model = User
        fields = [
            'email',
            'password1',
            'password2',
            'fullname',
            'phone',
            'city',
            'avatar',
            'address',
        ]
        field_classes = {'email': UsernameField}


class AccountEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            'fullname',
            'phone',
            'city',
            'avatar',
            'address',
        ]
