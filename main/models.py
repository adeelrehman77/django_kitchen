from django.db import models
from django.contrib.auth.models import User
import datetime

class Category(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Item(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='items/', null=True, blank=True)
    
    def __str__(self):
        return self.name

class MenuList(models.Model):
    name = models.CharField(max_length=100)
    items = models.ManyToManyField(Item)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class TimeSlot(models.Model):
    SLOT_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('custom', 'Custom'),
    ]
    name = models.CharField(max_length=50, choices=SLOT_CHOICES, default='custom')
    custom_name = models.CharField(max_length=50, blank=True, null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_time >= self.end_time:
            raise ValidationError('End time must be after start time')
        if self.name == 'custom' and not self.custom_name:
            raise ValidationError('Custom name is required for custom time slots')

    def __str__(self):
        if self.name == 'custom' and self.custom_name:
            return f"{self.custom_name}: {self.start_time} - {self.end_time}"
        return f"{self.get_name_display()}: {self.start_time} - {self.end_time}"

class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
    
    customer = models.ForeignKey('CustomerProfile', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    reference_id = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.customer.user.username}"

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    zone = models.ForeignKey('delivery.Zone', on_delete=models.SET_NULL, null=True)
    route = models.ForeignKey('delivery.Route', on_delete=models.SET_NULL, null=True)
    building_name = models.CharField(max_length=200, default='Not Specified')
    floor_number = models.CharField(max_length=10, default='0')
    flat_number = models.CharField(max_length=10, default='0')
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    @property
    def full_address(self):
        return f"{self.building_name}, Flat {self.flat_number}, Floor {self.floor_number}"
    
    @property
    def active_subscription(self):
        return self.subscription_set.filter(end_date__gte=datetime.date.today()).first()
        
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.zone})"
        
    def add_transaction(self, amount, transaction_type, description):
        """Process a wallet transaction and update balance"""
        import uuid
        
        if transaction_type == 'debit' and self.wallet_balance < amount:
            raise ValueError("Insufficient wallet balance")
            
        reference_id = str(uuid.uuid4())
        transaction = WalletTransaction.objects.create(
            customer=self,
            amount=amount,
            transaction_type=transaction_type,
            description=description,
            reference_id=reference_id
        )
        
        if transaction_type == 'credit':
            self.wallet_balance += amount
        else:
            self.wallet_balance -= amount
        self.save()
        
        return transaction

class Notification(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class DeliveryStatus(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ]
    subscription = models.ForeignKey('Subscription', on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Delivery Statuses"
        
    def __str__(self):
        return f"{self.subscription} - {self.date} - {self.status}"

class Subscription(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('card', 'Credit Card'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    menu = models.ForeignKey(MenuList, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    payment_mode = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    want_notifications = models.BooleanField(default=True)
    selected_days = models.JSONField()  # Store selected weekdays
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if (self.end_date - self.start_date).days > 30:
            raise ValidationError('Subscription duration cannot exceed 30 days')
        if self.end_date < self.start_date:
            raise ValidationError('End date must be after start date')
        if not self.selected_days:
            raise ValidationError('Please select at least one delivery day')
        if not all(day in ['0','1','2','3','4','5','6'] for day in self.selected_days):
            raise ValidationError('Invalid delivery days selected')
        
        # Check wallet balance for non-cash payments
        if self.payment_mode != 'cash':
            total_days = sum(1 for day in self.selected_days)
            total_weeks = ((self.end_date - self.start_date).days + 1) // 7
            total_deliveries = total_days * total_weeks
            total_cost = total_deliveries * 50  # Assuming fixed price per delivery
            
            if self.customer.wallet_balance < total_cost:
                raise ValidationError('Insufficient wallet balance for subscription')
            
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Create delivery status entries
            current_date = self.start_date
            while current_date <= self.end_date:
                if str(current_date.weekday()) in self.selected_days:
                    DeliveryStatus.objects.create(
                        subscription=self,
                        date=current_date,
                        status='pending'
                    )
                current_date += datetime.timedelta(days=1)
                
            # Handle payment if using wallet
            if self.payment_mode != 'cash':
                total_deliveries = self.deliverystatus_set.count()
                total_cost = total_deliveries * 50  # Fixed price per delivery
                
                self.customer.add_transaction(
                    amount=total_cost,
                    transaction_type='debit',
                    description=f'Subscription payment for {self.menu.name}'
                )

    def __str__(self):
        return f"{self.customer.user.username}'s subscription"