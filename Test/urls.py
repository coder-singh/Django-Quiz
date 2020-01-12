

from django.urls import path
from . import views

urlpatterns = [
    path('store/', views.store),
    path('retrieve/', views.retrieve),
]