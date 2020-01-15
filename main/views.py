from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from .models import *

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
            quiz.tutor = request.user
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
    else:
        question = Question()
        quiz_id = request.POST.get('quiz_id')
        question.quiz=Quiz.objects.get(pk=quiz_id)
        question.q_text = request.POST.get('q_text')
        question.q_type = request.POST.get('q_type')
         
        if 'q_image' in request.FILES:
            q_image = request.FILES['q_image']
            question.q_image=q_image
            
        if 'q_video' in request.POST:
            q_video = request.POST.get('q_video')
            question.q_video=q_video
            
        if 'q_audio' in request.FILES:
            q_audio = request.FILES['q_audio']
            question.q_audio=q_audio

        q_type = int(request.POST.get('q_type'))

        # SETTING OPTION DATA

        if q_type==2 or q_type==3 or q_type==4:
            question.a_text = request.POST.get('a_text'+str(q_type))

            if 'a_image'+str(q_type) in request.FILES:
                a_image = request.FILES['a_image'+str(q_type)]
                question.a_image=a_image

            if 'a_video'+str(q_type) in request.POST:
                a_video = request.POST.get('a_video'+str(q_type))
                question.a_video=a_video
                
            if 'a_audio'+str(q_type) in request.FILES:
                a_audio = request.FILES['a_audio'+str(q_type)]
                question.a_audio=a_audio
                
            question.b_text = request.POST.get('b_text'+str(q_type))
            
            if 'b_image'+str(q_type) in request.FILES:
                b_image = request.FILES['b_image'+str(q_type)]
                question.b_image=b_image

            if 'b_video'+str(q_type) in request.POST:
                b_video = request.POST.get('b_video'+str(q_type))
                question.b_video=b_video
                
            if 'b_audio'+str(q_type) in request.FILES:
                b_audio = request.FILES['b_audio'+str(q_type)]
                question.b_audio=b_audio
                
            question.c_text = request.POST.get('c_text'+str(q_type))
            
            if 'c_image'+str(q_type) in request.FILES:
                c_image = request.FILES['c_image'+str(q_type)]
                question.c_image=c_image

            if 'c_video'+str(q_type) in request.POST:
                c_video = request.POST.get('c_video'+str(q_type))
                question.c_video=c_video
                
            if 'c_audio'+str(q_type) in request.FILES:
                c_audio = request.FILES['c_audio'+str(q_type)]
                question.c_audio=c_audio
                
            question.d_text = request.POST.get('d_text'+str(q_type))
            
            if 'd_image'+str(q_type) in request.FILES:
                d_image = request.FILES['d_image'+str(q_type)]
                question.d_image=d_image

            if 'd_video'+str(q_type) in request.POST:
                d_video = request.POST.get('d_video'+str(q_type))
                question.d_video=d_video
                
            if 'd_audio'+str(q_type) in request.FILES:
                d_audio = request.FILES['d_audio'+str(q_type)]
                question.d_audio=d_audio

        elif q_type==5:
            pass

        # SETTING ANSWER DATA
        if q_type==1:
            question.answer = request.POST.get('answer1')

        elif q_type==2:
            question.answer = request.POST.get('answer2')
        
        elif q_type==3:
            question.answer = ','.join(request.POST.getlist('answer3'))
        
        elif q_type==4:
            resultString = request.POST.get('answerA')+','+request.POST.get('answerB')+','+request.POST.get('answerC')+','+request.POST.get('answerD')
            question.answer = resultString

        elif q_type==5:
            pass
            
        question.save()


        return redirect('/main/home')

@login_required
def viewQuiz(request):
    if request.method == 'GET':
        quiz_id = request.GET['id']
        quiz = Quiz.objects.select_related('tutor').get(pk=quiz_id)
        questions = Question.objects.filter(quiz_id=quiz_id)
        context = {
            'quiz': quiz,
            'questions': questions,
        }
        template = 'main/viewQuiz.html'
        return render(request, template, context)

def takeQuiz(request):
    if request.method=='GET':
        quiz_id = request.GET['id']
        quiz = Quiz.objects.select_related('tutor').get(pk=quiz_id)
        questions = Question.objects.filter(quiz=quiz)
        question_count = questions.count()
        question = None
        if question_count > 0:
            question = questions[0]

        context = {
            'quiz': quiz,
            'q': question,
            'question_no': 1,
        }
        template = 'main/takeQuiz.html'
        return render(request, template, context)
    else:
        quiz_id = request.POST.get('quiz_id')
        quiz = Quiz.objects.select_related('tutor').get(pk=quiz_id)
        q_type = int(request.POST.get('question_type'))
        question_no = int(request.POST.get('question_no'))
        questions = Question.objects.filter(quiz=quiz)
        question_count = questions.count()
        last_question=False

        attempt = Attempt()
        attempt.question_id = request.POST.get('question_id')
        attempt.student = request.user

        if q_type==1:
            attempt.answer = request.POST.get('answer1')

        elif q_type==2:
            attempt.answer = request.POST.get('answer2')
        
        elif q_type==3:
            attempt.answer = ','.join(request.POST.getlist('answer3'))
        
        elif q_type==4:
            resultString = request.POST.get('answerA')+','+request.POST.get('answerB')+','+request.POST.get('answerC')+','+request.POST.get('answerD')
            attempt.answer = resultString

        elif q_type==5:
            pass

        attempt.save()

        if int(question_no) == (question_count-1):
            last_question = True
        elif int(question_no) == question_count:
            return redirect('/main/viewResult/?s_id='+str(request.user.id)+'&q_id='+str(quiz.id))
        
        question = questions[question_no]
        context = {
            'last_question': last_question,
            'q': question,
            'quiz': quiz,
            'question_no': question_no + 1,
        }
        template = 'main/takeQuiz.html'
        return render(request, template, context)

def viewResult(request):
    quiz_id = request.GET['q_id']
    s_id = request.GET['s_id']
    quiz = Quiz.objects.select_related('tutor').get(pk=quiz_id)
    question_ids = Question.objects.filter(quiz_id=quiz_id).values_list('id', flat=True)
    attempts = Attempt.objects.select_related('question').filter(student_id=s_id, question_id__in=question_ids)
    score = 0
    for a in attempts:
        if a.answer==a.question.answer:
            score += a.question.marks
    print(score)
    context = {
        'score': score,
        'attempts': attempts,
        'quiz': quiz
    }
    template = 'main/viewResult.html'
    return render(request, template, context)