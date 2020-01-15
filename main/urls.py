"""Quiz URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views as main_views

urlpatterns = [
    path('home/', main_views.home, name='home'),
    path('login/', main_views.user_login, name='login'),
    path('logout/', main_views.user_logout, name='logout'),
    path('register/', main_views.register, name='register'),
    path('createQuiz/', main_views.createQuiz, name='createQuiz'),
    path('viewQuiz/', main_views.viewQuiz, name='viewQuiz'),
    path('takeQuiz/', main_views.takeQuiz, name='takeQuiz'),
    path('addQuestion/', main_views.addQuestion, name='addQuestion'),
    path('viewResult/', main_views.viewResult, name="viewResult"),
]