
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import *
from django import forms
import json

def home(request):
    menu_lists = MenuList.objects.filter(is_active=True)
    return render(request, 'main/home.html', {'menu_lists': menu_lists})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'main/register.html', {'form': form})

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['menu', 'start_date', 'end_date', 'time_slot', 'payment_mode', 'want_notifications', 'selected_days']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'selected_days': forms.CheckboxSelectMultiple(choices=[(i, day) for i, day in enumerate(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])])
        }

@login_required
def subscribe(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.customer = request.user.customerprofile
            sub.save()
            messages.success(request, 'Subscription created successfully!')
            return redirect('profile')
    else:
        form = SubscriptionForm()
    return render(request, 'main/subscribe.html', {'form': form})

@login_required
def profile(request):
    subscriptions = Subscription.objects.filter(customer=request.user.customerprofile)
    return render(request, 'main/profile.html', {'subscriptions': subscriptions})
