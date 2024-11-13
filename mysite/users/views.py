from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            firstname = form.cleaned_data.get('first_name')
            lastname = form.cleaned_data.get('last_name')
            messages.success(request, f'Welcome {firstname} {lastname}! Your account has been created!')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'users/profile.html')