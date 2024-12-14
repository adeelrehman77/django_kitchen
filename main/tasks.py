
from datetime import date
from .models import DeliveryStatus

def mark_deliveries_complete():
    today = date.today()
    pending_deliveries = DeliveryStatus.objects.filter(
        date=today,
        status='pending'
    )
    pending_deliveries.update(status='delivered')
