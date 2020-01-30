from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm

class createQuizForm(forms.ModelForm):
    quiz_choices = (
        ('normal', 'Normal'),
        ('adaptive', 'Adaptive'),
    )
    quiz_type = forms.ChoiceField(choices=quiz_choices)
    class Meta():
        model = Quiz
        fields = ('name', 'time', 'max_marks', 'pass_marks', 'no_questions', 'quiz_type')

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