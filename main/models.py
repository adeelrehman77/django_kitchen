
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
    
    def __str__(self):
        return self.name

class MenuList(models.Model):
    name = models.CharField(max_length=100)
    items = models.ManyToManyField(Item)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    def __str__(self):
        return f"{self.start_time} - {self.end_time}"

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    location = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Subscription(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('card', 'Credit Card'),
    ]
    
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    menu = models.ForeignKey(MenuList, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
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

    def __str__(self):
        return f"{self.customer.user.username}'s subscription"
