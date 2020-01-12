from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    context = {

    }
    template = 'main/home.html'
    return render(request, template, context)

def user_logout(request):
    logout(request)
    return redirect('/main/home')

def user_login(request):
    if request.method=='GET':
        context = {}
    else:
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        try:
            user = User.objects.get(email=email)
            auth = authenticate(email=user.email, password=password)
            if auth==None:
                context={
                    'message': 'Wrong password',
                }
            else:
                print('logged in')
                login(request, auth)
                return redirect('/main/home')
        except (User.DoesNotExist):
            context={
                'message': 'Email not registered',
            }
            
    template = 'main/login.html'
    return render(request, template, context)

def register(request):
    if request.method == 'GET':
        registerForm = RegisterForm()
    else:
        registerForm = RegisterForm(request.POST)
        if registerForm.is_valid():
            user = registerForm.save()
            user.save()
            return redirect('/main/home')
        else:
            pass
    context = {
        'form': registerForm
    }
    template = 'main/register.html'
    return render(request, template, context)

@login_required
def createQuiz(request):
    if request.method=='GET':
        quizForm = createQuizForm()
    else:
        quizForm = createQuizForm(request.POST)
        if quizForm.is_valid():
            print('form is valid')
            quiz = quizForm.save(commit=False)
            quiz.tutor_id = request.user
            quiz.save()
            return redirect('/main/addQuestion/?id='+str(quiz.id))
        else:
            print('form is invalid')
    context = {
        'form': quizForm
    }
    template = 'main/createQuiz.html'
    return render(request, template, context)

@login_required
def addQuestion(request):
    if request.method=='GET':
        if 'id' not in request.GET:
            return redirect('/main/home')
        context = {
            'id': request.GET['id']
        }
        template = 'main/addQuestion.html'
        return render(request, template, context)

def takeQuiz(request):
    pass