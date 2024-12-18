
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import *
from delivery.models import Route
from django import forms

def home(request):
    try:
        items = Item.objects.filter(is_active=True)
        home_contents = HomeContent.objects.filter(is_active=True).order_by('-priority')[:2]
        return render(request, 'main/home.html', {
            'items': items,
            'home_contents': home_contents
        })
    except Exception as e:
        return render(request, 'main/home.html', {'items': [], 'home_content': None})

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
    DAYS_CHOICES = [
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ]

    # Customer Information Fields (Read-only)
    customer_name = forms.CharField(disabled=True, required=False)
    customer_phone = forms.CharField(disabled=True, required=False)
    customer_address = forms.CharField(disabled=True, required=False)
    wallet_balance = forms.DecimalField(disabled=True, required=False)
    
    selected_days = forms.MultipleChoiceField(
        choices=DAYS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['items'].queryset = Item.objects.filter(is_active=True)
        self.fields['items'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Subscription
        fields = ['items', 'start_date', 'end_date', 'time_slot', 'payment_mode', 'want_notifications', 'selected_days']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today().isoformat()}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today().isoformat()}),
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
                sub.status = 'pending'
                
                # Calculate subscription cost
                total_days = sum(1 for day in form.cleaned_data['selected_days'])
                total_weeks = ((form.cleaned_data['end_date'] - form.cleaned_data['start_date']).days + 1) // 7
                total_deliveries = total_days * total_weeks
                total_cost = total_deliveries * 50  # Fixed price per delivery
                
                if form.cleaned_data['payment_mode'] != 'cash' and request.user.customerprofile.wallet_balance < total_cost:
                    messages.error(request, f'Insufficient wallet balance. Required: {total_cost}')
                    return redirect('wallet_topup')
                    
                sub.save()
                messages.success(request, 'Subscription created successfully!')
                return redirect('profile')
        else:
            form = SubscriptionForm()
            # Pre-fill customer information
            customer = request.user.customerprofile
            form.initial.update({
                'customer_name': request.user.get_full_name(),
                'customer_phone': customer.phone,
                'customer_address': customer.full_address,
                'wallet_balance': customer.wallet_balance
            })
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
        transactions = WalletTransaction.objects.filter(customer=request.user.customerprofile).order_by('-created_at')
        return render(request, 'main/profile.html', {
            'subscriptions': subscriptions,
            'notifications': notifications,
            'delivery_status': delivery_status,
            'transactions': transactions
        })
    except CustomerProfile.DoesNotExist:
        CustomerProfile.objects.create(user=request.user)
        return render(request, 'main/profile.html', {'subscriptions': [], 'notifications': [], 'delivery_status': []})

@login_required
def wallet_topup(request):
    if request.method == 'POST':
        try:
            amount = decimal.Decimal(request.POST.get('amount', 0))
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")
                
            request.user.customerprofile.add_transaction(
                amount=amount,
                transaction_type='credit',
                description='Wallet top-up'
            )
            messages.success(request, f'Successfully added {amount} to wallet')
            
        except (ValueError, decimal.InvalidOperation) as e:
            messages.error(request, str(e))
            
        return redirect('profile')
        
    return render(request, 'main/wallet_topup.html')

@login_required
def transaction_history(request):
    transactions = WalletTransaction.objects.filter(
        customer=request.user.customerprofile
    )
    
    # Filter by transaction type
    tx_type = request.GET.get('type')
    if tx_type in ['credit', 'debit']:
        transactions = transactions.filter(transaction_type=tx_type)
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        transactions = transactions.filter(created_at__date__gte=start_date)
    if end_date:
        transactions = transactions.filter(created_at__date__lte=end_date)
        
    transactions = transactions.order_by('-created_at')
    
    context = {
        'transactions': transactions,
        'tx_type': tx_type,
        'start_date': start_date,
        'end_date': end_date
    }
    return render(request, 'main/transaction_history.html', context)

def menu_preview(request, menu_id):
    menu = MenuList.objects.get(id=menu_id)
    return render(request, 'main/menu_preview.html', {'menu': menu})
from django.http import HttpResponse
import csv

import xlwt
from django.http import HttpResponse

def subscription_report(request):
    subscriptions = Subscription.objects.select_related(
        'customer', 'menu', 'time_slot'
    ).prefetch_related('deliverystatus_set').all()
    
    if request.GET.get('export') == 'excel':
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="subscriptions.xls"'
        
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Subscriptions')
        
        row_num = 0
        columns = ['Customer', 'Menu', 'Time Slot', 'Start Date', 'End Date', 
                  'Payment Mode', 'Status', 'Total Deliveries', 'Pending', 'Completed']
        
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
    
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
from django.db.models import Count
from django.utils import timezone

@login_required
def delivery_summary(request):
    # Get filter parameters
    selected_date = request.GET.get('date', timezone.now().date())
    if isinstance(selected_date, str):
        selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
    
    category = request.GET.get('category')
    route = request.GET.get('route')
    
    # Base query
    deliveries = DeliveryStatus.objects.select_related(
        'subscription', 'subscription__customer', 'subscription__customer__route'
    ).prefetch_related('subscription__items')
    
    # Apply filters
    deliveries = deliveries.filter(date=selected_date)
    
    if category:
        deliveries = deliveries.filter(subscription__items__category__name=category)
    
    if route:
        deliveries = deliveries.filter(subscription__customer__route_id=route)
    
    # Get product summary
    product_summary = []
    items_count = {}
    
    for delivery in deliveries:
        for item in delivery.subscription.items.all():
            if item.id not in items_count:
                items_count[item.id] = {
                    'name': item.name,
                    'category': item.category.name,
                    'count': 0
                }
            items_count[item.id]['count'] += 1
    
    # Convert to list for template
    product_summary = list(items_count.values())
    
    # Get status summary
    status_summary = deliveries.values('status').annotate(
        count=Count('id')
    )
    
    # Get time slot summary
    time_slot_summary = deliveries.values(
        'subscription__time_slot__name',
        'subscription__time_slot__custom_name'
    ).annotate(count=Count('id'))
    
    context = {
        'selected_date': selected_date,
        'product_summary': product_summary,
        'status_summary': status_summary,
        'time_slot_summary': time_slot_summary,
        'total_deliveries': deliveries.count(),
        'categories': Category.objects.all(),
        'routes': Route.objects.all()
    }
    
    return render(request, 'main/delivery_summary.html', context)
