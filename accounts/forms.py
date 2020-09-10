from django import forms
from .models import Player
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name',
                  'username',
                  'password1', 'password2')
        widgets = {'first_name': forms.TextInput(attrs={'placeholder': 'Enter Your Name'}),
                   'username': forms.TextInput(attrs={'placeholder': 'Pick a Username'}),
                   'password1': forms.PasswordInput(attrs={'placeholder': 'Password'}),
                   'password2': forms.PasswordInput(attrs={'placeholder': 'Retype Password'}),
                   }
        labels = {'first_name': 'Name',
                  'password1': 'Password',
                  'password2': 'Confirm Password'}


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ('team', )
        labels = {'team': "Predict IPL Winner (Rs.250 Bet)",
                  }


class UserLoginForm(AuthenticationForm):
    class Meta:
        fields = ('username', 'password')


class UserPwdChangeForm(PasswordChangeForm):
    class Meta:
        fields = ('old_password',
                  'new_password1',
                  'new_password2',
                  )
