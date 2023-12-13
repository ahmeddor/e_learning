# user_authentification/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserTypes, User


class SignupForm(UserCreationForm):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=UserTypes.choices)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "role"]


class SignInForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ["username", "password"]
