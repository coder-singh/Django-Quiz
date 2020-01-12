from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm

class createQuizForm(forms.ModelForm):
    class Meta():
        model = Quiz
        fields = ('name', 'time', 'max_marks', 'pass_marks', 'no_questions')

class RegisterForm(UserCreationForm):
    role_choices = (
        (1, 'Admin'),
        (2, 'Tutor'),
        (3, 'Student'),
    )
    role = forms.ChoiceField(choices=role_choices)
    class Meta():
        model = User
        fields = ('email','password1','password2', 'first_name', 'last_name', 'role')