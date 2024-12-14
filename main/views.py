
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import *
from django import forms

def home(request):
    try:
        items = Item.objects.filter(is_active=True)
        return render(request, 'main/home.html', {'items': items})
    except:
        return render(request, 'main/home.html', {'items': []})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            CustomerProfile.objects.create(user=user)  # Create profile for user
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
            'start_date': forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today().isoformat()}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today().isoformat()}),
            'selected_days': forms.CheckboxSelectMultiple(choices=[(str(i), day) for i, day in enumerate(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])]),
            'payment_mode': forms.RadioSelect(),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        selected_days = cleaned_data.get('selected_days')

        if not selected_days:
            raise forms.ValidationError('Please select at least one day')
            
        if start_date and end_date:
            if start_date < datetime.date.today():
                raise forms.ValidationError('Start date cannot be in the past')
            if (end_date - start_date).days > 30:
                raise forms.ValidationError('Subscription cannot exceed 30 days')
        return cleaned_data

@login_required
def subscribe(request):
    try:
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
    except Exception as e:
        messages.error(request, str(e))
        return redirect('home')

@login_required
def profile(request):
    try:
        subscriptions = Subscription.objects.filter(customer=request.user.customerprofile)
        notifications = Notification.objects.filter(customer=request.user.customerprofile).order_by('-created_at')[:5]
        delivery_status = DeliveryStatus.objects.filter(subscription__customer=request.user.customerprofile)
        return render(request, 'main/profile.html', {
            'subscriptions': subscriptions,
            'notifications': notifications,
            'delivery_status': delivery_status
        })
    except CustomerProfile.DoesNotExist:
        CustomerProfile.objects.create(user=request.user)
        return render(request, 'main/profile.html', {'subscriptions': [], 'notifications': [], 'delivery_status': []})

def menu_preview(request, menu_id):
    menu = MenuList.objects.get(id=menu_id)
    return render(request, 'main/menu_preview.html', {'menu': menu})
def subscription_report(request):
    all_subscriptions = Subscription.objects.select_related('customer', 'menu', 'time_slot').all()
    return render(request, 'main/subscription_report.html', {'subscriptions': all_subscriptions})
