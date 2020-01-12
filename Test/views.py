from django.shortcuts import render, redirect
from .forms import *
from .models import *

# Create your views here.
def store(request): 
  
    if request.method == 'POST': 
        form = HotelForm(request.POST, request.FILES) 
  
        if form.is_valid(): 
            form.save() 
            return redirect('store/') 
    else: 
        form = HotelForm() 
    return render(request, 'Test/store.html', {'form' : form}) 
  


def retrieve(request):
    hotels = Hotel.objects.get(pk=1)
    context = {
        'Hotel': hotels
    }
    return render(request, 'Test/retrieve.html', context)