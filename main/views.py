
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
    phone = forms.CharField(max_length=15)
    building_name = forms.CharField(max_length=200)
    floor_number = forms.CharField(max_length=10)
    flat_number = forms.CharField(max_length=10)

    class Meta:
        model = Subscription
        fields = ['item', 'start_date', 'end_date', 'time_slot', 'payment_mode', 'want_notifications', 'selected_days']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today().isoformat()}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today().isoformat()}),
            'selected_days': forms.CheckboxSelectMultiple(choices=[(str(i), day) for i, day in enumerate(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])]),
            'payment_mode': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.customerprofile:
            self.fields['phone'].initial = user.customerprofile.phone
            self.fields['building_name'].initial = user.customerprofile.building_name
            self.fields['floor_number'].initial = user.customerprofile.floor_number
            self.fields['flat_number'].initial = user.customerprofile.flat_number

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
            form = SubscriptionForm(request.POST, user=request.user)
            if form.is_valid():
                # Update customer profile
                profile = request.user.customerprofile
                profile.phone = form.cleaned_data['phone']
                profile.building_name = form.cleaned_data['building_name']
                profile.floor_number = form.cleaned_data['floor_number']
                profile.flat_number = form.cleaned_data['flat_number']
                profile.save()

                # Create subscription
                sub = form.save(commit=False)
                sub.customer = profile
                sub.save()
                messages.success(request, 'Subscription created successfully!')
                return redirect('profile')
        else:
            form = SubscriptionForm(user=request.user)
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
from django.http import HttpResponse
import csv

def subscription_report(request):
    subscriptions = Subscription.objects.select_related(
        'customer', 'menu', 'time_slot'
    ).prefetch_related('deliverystatus_set').all()
    
    status_filter = request.GET.get('status')
    payment_filter = request.GET.get('payment')
    today = datetime.date.today()
    
    if status_filter == 'active':
        subscriptions = subscriptions.filter(end_date__gte=today)
    elif status_filter == 'expired':
        subscriptions = subscriptions.filter(end_date__lt=today)
        
    if payment_filter:
        subscriptions = subscriptions.filter(payment_mode=payment_filter)
    
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="subscriptions.csv"'
        writer = csv.writer(response)
        writer.writerow(['Customer', 'Menu', 'Time Slot', 'Start Date', 'End Date', 
                        'Payment Mode', 'Status', 'Total Deliveries', 'Pending', 'Completed'])
        
        for sub in subscriptions:
            writer.writerow([
                sub.customer.user.username,
                sub.menu.name,
                str(sub.time_slot),
                sub.start_date,
                sub.end_date,
                sub.get_payment_mode_display(),
                'Active' if sub.end_date >= today else 'Expired',
                sub.deliverystatus_set.count(),
                sub.deliverystatus_set.filter(status='pending').count(),
                sub.deliverystatus_set.filter(status='delivered').count()
            ])
        return response
        
    context = {
        'subscriptions': subscriptions,
        'payment_choices': Subscription.PAYMENT_CHOICES,
        'today': today
    }
    return render(request, 'main/subscription_report.html', context)
