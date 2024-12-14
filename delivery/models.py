
from django.db import models
from django.contrib.auth.models import User

class Hub(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, help_text="Unique hub identifier")
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    capacity = models.IntegerField(default=100, help_text="Maximum number of orders per day")
    operating_hours = models.CharField(max_length=100, help_text="e.g., '9:00 AM - 6:00 PM'")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Zone(models.Model):
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, help_text="Unique zone identifier")
    description = models.TextField(blank=True)
    coverage_area = models.TextField(help_text="Description of area covered")
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_delivery_time = models.IntegerField(help_text="Minimum delivery time in minutes")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.hub.name} - {self.name}"

class Route(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ]
    
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, help_text="Unique route identifier")
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    estimated_delivery_time = models.IntegerField(help_text="Estimated delivery time in minutes")
    max_orders = models.IntegerField(default=20, help_text="Maximum orders per route")
    start_location = models.CharField(max_length=200)
    end_location = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.zone.name} - {self.name}"

class Driver(models.Model):
    VEHICLE_CHOICES = [
        ('bike', 'Bike'),
        ('scooter', 'Scooter'),
        ('car', 'Car'),
        ('van', 'Van')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=10, unique=True)
    phone = models.CharField(max_length=15)
    alternate_phone = models.CharField(max_length=15, blank=True)
    license_number = models.CharField(max_length=50)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_CHOICES, default='bike')
    vehicle_number = models.CharField(max_length=20, blank=True)
    assigned_route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    joining_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()} ({self.assigned_route})"
