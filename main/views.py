from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from .models import *

# Create your views here.
def enroll(request):
    course_id = request.GET['id']
    enrollment = Enrollment()
    enrollment.course_id = course_id
    enrollment.student = request.user
    enrollment.save()
    return redirect('/main/home')

def home(request):
    if request.user.is_authenticated and request.user.role == 3:
        # student
        courses = Course.objects.select_related('tutor').all()
        enrolled_courses = list(Enrollment.objects.filter(student = request.user).values_list('course_id', flat=True).distinct())
        context = {
            'courses': courses,
            'enrolled_courses': enrolled_courses,
        }
        template = 'main/home.html'
        return render(request, template, context)
    else:
        courses = Course.objects.select_related('tutor').all()
        context = {
            'courses': courses,
        }
        template = 'main/home.html'
        return render(request, template, context)

@login_required
def viewCourse(request):
    course_id = request.GET['id']
    course = Course.objects.select_related('tutor').get(pk=course_id)
    if request.user.is_authenticated and request.user.role == 3:
        # student
        quizzes = Quiz.objects.filter(course_id = course_id, disabled=0)
        print(quizzes)
        attempted_quizzes = list(Attempt.objects.select_related('question__quiz__course').filter(student = request.user, question__quiz__course_id=course_id).values_list('question__quiz', flat=True).distinct())
        print(attempted_quizzes)
        enrollment = list(Enrollment.objects.filter(course_id=course_id, student_id=request.user.id))
        enrolled = True
        if enrollment == []:
            enrolled = False

        results = {}
        passed_count = 0
        for qid in attempted_quizzes:
            quiz = Quiz.objects.get(pk=qid)
            question_ids = Question.objects.filter(quiz_id=qid).values_list('id', flat=True)
            attempts = Attempt.objects.select_related('question').filter(student = request.user, question_id__in=question_ids)
            score = 0
            for a in attempts:
                if a.answer==a.question.answer:
                    score += a.question.marks
            if score >= quiz.pass_marks:
                results[qid] = True
                passed_count += 1
            else:
                results[qid] = False
        print(results)

        total_quiz_count = quizzes.count()

        percent = int((passed_count/total_quiz_count)*100)
        context = {
            'course': course,
            'quizzes': quizzes,
            'attempted_quizzes': attempted_quizzes,
            'enrolled': enrolled,
            'percent': percent,
            'show': False,
        }
        template = 'main/viewCourse.html'
        return render(request, template, context)
    else:
        quizzes = Quiz.objects.filter(course_id = course_id)
        show = False
        if request.user.is_authenticated and (request.user.role == 1 or request.user.role == 2):
            show = True
        context = {
            'course': course,
            'quizzes': quizzes,
            'show': show,
        }
        template = 'main/viewCourse.html'
        return render(request, template, context)

def editQuiz(request):
    if request.method=='GET':
        quiz_id = int(request.GET['id'])
        quiz = Quiz.objects.get(pk=quiz_id)
        quizForm = createQuizForm(instance=quiz)
    else:
        quiz_id = int(request.POST.get('id'))
        quiz = Quiz.objects.get(pk=quiz_id)
        quizForm = createQuizForm(request.POST, instance=quiz)
        if quizForm.is_valid():
            print('form is valid')
            quiz = quizForm.save(commit=False)
            quiz.tutor = request.user
            quiz.save()
            return redirect('/main/home')
        else:
            print('form is invalid')
    context = {
        'form': quizForm,
        'quiz_id': quiz_id
    }
    template = 'main/editQuiz.html'
    return render(request, template, context)

def disableQuiz(request):
    quiz_id = request.GET['id']
    quiz = Quiz.objects.get(pk=quiz_id)
    quiz.disabled = True
    quiz.save()
    return redirect('/main/viewCourse/?id='+str(quiz.course_id))
    
def enableQuiz(request):
    quiz_id = request.GET['id']
    quiz = Quiz.objects.get(pk=quiz_id)
    quiz.disabled = False
    quiz.save()
    return redirect('/main/viewCourse/?id='+str(quiz.course_id))

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
        course_id = request.GET['id']
    else:
        print(request.POST)
        course_id = request.POST.get('course_id')
        quizForm = createQuizForm(request.POST)
        if quizForm.is_valid():
            print('form is valid')
            quiz = quizForm.save(commit=False)
            quiz.tutor = request.user
            quiz.course_id = course_id
            quiz.save()
            return redirect('/main/addQuestion/?id='+str(quiz.id))
        else:
            print('form is invalid')
    context = {
        'form': quizForm,
        'course_id': course_id,
    }
    template = 'main/createQuiz.html'
    return render(request, template, context)

@login_required
def addQuestion(request):
    if request.method=='GET':
        if 'id' not in request.GET:
            return redirect('/main/home')
        quiz_id = request.GET['id']
        quiz = Quiz.objects.get(pk=quiz_id)
        difficulty = None
        if quiz.quiz_type == 'adaptive':
            difficulty = "easy"
        context = {
            'quiz': quiz,
            'question_no': 1,
            'difficulty': difficulty,
        }
        template = 'main/addQuestion.html'
        return render(request, template, context)
    else:
        question = Question()
        quiz_id = int(request.POST.get('quiz_id'))
        quiz = Quiz.objects.get(pk=quiz_id)
        question.quiz=quiz
        question.q_text = request.POST.get('q_text')
        question.q_type = request.POST.get('q_type')
        question.marks = request.POST.get('marks')
        question_no = int(request.POST.get('question_no'))
        question_count = quiz.no_questions
         
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
            question.a2_text = request.POST.get('a2_text'+str(q_type))

            if 'a2_image'+str(q_type) in request.FILES:
                a2_image = request.FILES['a2_image'+str(q_type)]
                question.a2_image=a2_image

            if 'a2_video'+str(q_type) in request.POST:
                a2_video = request.POST.get('a2_video'+str(q_type))
                question.a2_video=a2_video
                
            if 'a2_audio'+str(q_type) in request.FILES:
                a2_audio = request.FILES['a2_audio'+str(q_type)]
                question.a2_audio=a_audio
                
            question.b2_text = request.POST.get('b2_text'+str(q_type))
            
            if 'b2_image'+str(q_type) in request.FILES:
                b2_image = request.FILES['b2_image'+str(q_type)]
                question.b2_image=b2_image

            if 'b2_video'+str(q_type) in request.POST:
                b2_video = request.POST.get('b2_video'+str(q_type))
                question.b2_video=b2_video
                
            if 'b2_audio'+str(q_type) in request.FILES:
                b2_audio = request.FILES['b2_audio'+str(q_type)]
                question.b2_audio=b2_audio
                
            question.c2_text = request.POST.get('c2_text'+str(q_type))
            
            if 'c2_image'+str(q_type) in request.FILES:
                c2_image = request.FILES['c2_image'+str(q_type)]
                question.c2_image=c2_image

            if 'c2_video'+str(q_type) in request.POST:
                c2_video = request.POST.get('c2_video'+str(q_type))
                question.c2_video=c2_video
                
            if 'c2_audio'+str(q_type) in request.FILES:
                c2_audio = request.FILES['c2_audio'+str(q_type)]
                question.c2_audio=c2_audio
                
            question.d2_text = request.POST.get('d2_text'+str(q_type))
            
            if 'd2_image'+str(q_type) in request.FILES:
                d2_image = request.FILES['d2_image'+str(q_type)]
                question.d2_image=d2_image

            if 'd2_video'+str(q_type) in request.POST:
                d2_video = request.POST.get('d2_video'+str(q_type))
                question.d2_video=d2_video
                
            if 'd2_audio'+str(q_type) in request.FILES:
                d2_audio = request.FILES['d2_audio'+str(q_type)]
                question.d2_audio=d2_audio

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
            resultString = request.POST.get('answerma')+','+request.POST.get('answermb')+','+request.POST.get('answermc')+','+request.POST.get('answermd')
            question.answer = resultString
            
        print(request.POST.get('difficulty'))
        question.difficulty = request.POST.get('difficulty')
        question.save()
        
        difficulty = None

        if quiz.quiz_type == 'normal':
            if question_count == question_no:
                return redirect('/main/home')
        else:
            easy_question_count = question_count
            medium_question_count = (question_count - 3) if question_count >= 3 else 0
            hard_question_count = (question_count - 6) if question_count >= 6 else 0
            total = easy_question_count + medium_question_count + hard_question_count

            if total == question_no:
                return redirect('/main/home')

            if question_no < easy_question_count:
                difficulty = "easy"
            elif question_no < (question_count + medium_question_count):
                difficulty = "medium"
            else:
                difficulty = "hard"

        context = {
            'quiz': quiz,
            'question_no': question_no+1,
            'difficulty': difficulty,
        }
        template = 'main/addQuestion.html'
        return render(request, template, context)

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

def viewResults(request):
    quiz_id = int(request.GET['id'])
    questions = Question.objects.filter(quiz_id = quiz_id)
    question_ids = questions.values_list('id', flat=True)
    print(question_ids)
    attempts = Attempt.objects.select_related('question', 'student').filter(question_id__in=question_ids)
    data = {}
    for attempt in attempts:
        l = []
        if attempt.student_id not in data.keys():
            l.append(attempt.student.first_name)
            l.append(0)
            data[attempt.student_id] = l
        
        if attempt.question.answer == attempt.answer:
            data[attempt.student_id][1] += attempt.question.marks

    print(data)
    context = {
        'data': data,
        'quiz_id': quiz_id,
    }
    print(data)
    template = "main/viewResults.html"
    return render(request, template, context)

def takeQuiz(request):
    if request.method=='GET':

        if request.session.has_key('correct'):
            del request.session['correct']
            del request.session['easy']
            del request.session['medium']
            del request.session['hard']

            request.session.modified = True

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
            'minutes': quiz.time,
            'endTime': -10,
        }
        template = 'main/takeQuiz.html'
        return render(request, template, context)
    else:
        quiz_id = request.POST.get('quiz_id')
        quiz = Quiz.objects.select_related('tutor').get(pk=quiz_id)
        q_type = int(request.POST.get('question_type'))
        question_no = int(request.POST.get('question_no'))
        questions = Question.objects.filter(quiz=quiz)
        question_count = quiz.no_questions
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
            resultString = request.POST.get('answerma')+','+request.POST.get('answermb')+','+request.POST.get('answermc')+','+request.POST.get('answermd')
            attempt.answer = resultString

        attempt.save()

        if int(question_no) == (question_count-1):
            last_question = True
        elif int(question_no) == question_count:
            return redirect('/main/viewResult/?s_id='+str(request.user.id)+'&q_id='+str(quiz.id))
        
        # print('question_no: '+str(question_no)+', question_count: '+str(question_count))
        question = questions[question_no]

        if quiz.quiz_type == 'adaptive':
            if request.session.has_key('correct'):
                print('session present')
                correct = request.session['correct']
                if(checkAnswer(attempt)):
                    correct += 1
                    if correct == 3:
                        request.session['stage'] = levelUp(request.session['stage'])
                        correct = 0
                        print('level up')
                    request.session['correct'] = correct
                else:
                    request.session['correct'] = 0
                    request.session['stage'] = levelDown(request.session['stage'])     
                    print('level down')
                request.session[request.session['stage']] += 1              
            else:
                print('creating session')
                request.session['stage'] = 'easy'
                request.session['easy'] = 1
                request.session['medium'] = -1
                request.session['hard'] = -1
                if(checkAnswer(attempt)):
                    request.session['correct'] = 1
                else:
                    request.session['correct'] = 0
                    
            question = questions.filter(difficulty=request.session['stage'])[request.session[request.session['stage']]]
                
        context = {
            'last_question': last_question,
            'q': question,
            'quiz': quiz,
            'question_no': question_no + 1,
            'endTime': request.POST.get('endTime'),
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

def viewSolution(request):
    quiz_id = request.GET['qid']
    quiz = Quiz.objects.get(pk=quiz_id)
    sid = request.GET['sid']
    answers = {}
    questions = Question.objects.filter(quiz_id = quiz_id)
    for q in questions:
        a = q.attempt_set.filter(student=sid)
        if len(a) != 0:
            answers[q.id] = a[0].answer

    print(answers)

    context = {
        'questions': questions,
        'quiz': quiz,
        'answers': answers,
    }
    template = 'main/viewSolution.html'
    return render(request, template, context)

def editQuestion(request):
    if request.method=="GET":
        question_id = int(request.GET['id'])
        question = Question.objects.get(pk=question_id)

        context = {
            'q': question,
        }
        template = 'main/editQuestion.html'
        return render(request, template, context)
    else:
        question_id = int(request.POST.get('question_id'))
        question = Question.objects.get(pk=question_id)

        question.q_text = request.POST.get('q_text')
        question.q_type = request.POST.get('q_type')
        question.marks = request.POST.get('marks')
         
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
                
            question.d2_text = request.POST.get('d2_text'+str(q_type))
            
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
            question.a2_text = request.POST.get('a2_text'+str(q_type))

            if 'a2_image'+str(q_type) in request.FILES:
                a2_image = request.FILES['a2_image'+str(q_type)]
                question.a2_image=a2_image

            if 'a2_video'+str(q_type) in request.POST:
                a2_video = request.POST.get('a2_video'+str(q_type))
                question.a2_video=a2_video
                
            if 'a2_audio'+str(q_type) in request.FILES:
                a2_audio = request.FILES['a2_audio'+str(q_type)]
                question.a2_audio=a_audio
                
            question.b2_text = request.POST.get('b2_text'+str(q_type))
            
            if 'b2_image'+str(q_type) in request.FILES:
                b2_image = request.FILES['b2_image'+str(q_type)]
                question.b2_image=b2_image

            if 'b2_video'+str(q_type) in request.POST:
                b2_video = request.POST.get('b2_video'+str(q_type))
                question.b2_video=b2_video
                
            if 'b2_audio'+str(q_type) in request.FILES:
                b2_audio = request.FILES['b2_audio'+str(q_type)]
                question.b2_audio=b2_audio
                
            question.c2_text = request.POST.get('c2_text'+str(q_type))
            
            if 'c2_image'+str(q_type) in request.FILES:
                c2_image = request.FILES['c2_image'+str(q_type)]
                question.c2_image=c2_image

            if 'c2_video'+str(q_type) in request.POST:
                c2_video = request.POST.get('c2_video'+str(q_type))
                question.c2_video=c2_video
                
            if 'c2_audio'+str(q_type) in request.FILES:
                c2_audio = request.FILES['c2_audio'+str(q_type)]
                question.c2_audio=c2_audio
                
            question.d2_text = request.POST.get('d2_text'+str(q_type))
            
            if 'd2_image'+str(q_type) in request.FILES:
                d2_image = request.FILES['d2_image'+str(q_type)]
                question.d2_image=d2_image

            if 'd2_video'+str(q_type) in request.POST:
                d2_video = request.POST.get('d2_video'+str(q_type))
                question.d2_video=d2_video
                
            if 'd2_audio'+str(q_type) in request.FILES:
                d2_audio = request.FILES['d2_audio'+str(q_type)]
                question.d2_audio=d2_audio

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
            resultString = request.POST.get('answerma')+','+request.POST.get('answermb')+','+request.POST.get('answermc')+','+request.POST.get('answermd')
            question.answer = resultString
            
        question.save()

        return redirect("/main/viewQuiz/?id="+str(question.quiz_id))

@login_required
def createCourse(request):
    if request.method=='GET':
        context = {

        }
        template = 'main/createCourse.html'
        return render(request, template, context)
    else:
        course = Course()
        course.name = request.POST.get('name')
        course.tutor = request.user
        course.save()
        if request.POST.get('action') == 'home':
            return redirect('/main/home')
        else:
            return redirect('/main/createQuiz/?id='+str(course.id))

def checkAnswer(attempt):
    print('your: '+attempt.answer+', correct: '+attempt.question.answer)
    if attempt.question.answer == attempt.answer:
        return True
    else:
        return False

def levelUp(stage):
    if stage == 'easy':
        return 'medium'
    elif stage == 'medium':
        return 'hard'
    else:
        return 'hard'

def levelDown(stage):
    if stage == 'hard':
        return 'medium'
    elif stage == 'medium':
        return 'easy'
    else:
        return 'easy'

def deleteCourse(request):
    course_id = request.GET['id']
    course = Course.objects.get(pk=course_id)
    course.delete()
    return redirect('/main/home')

def deleteQuiz(request):
    quiz_id = request.GET['id']
    quiz = Quiz.objects.get(pk=quiz_id)
    quiz.delete()
    return redirect('/main/home')