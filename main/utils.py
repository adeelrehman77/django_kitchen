
import csv
from django.contrib.auth.models import User
from .models import Hub, Zone, Route, Driver

def bulk_upload_delivery_data(file_path, data_type):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        if data_type == 'hub':
            for row in reader:
                Hub.objects.create(
                    name=row['name'],
                    address=row['address'],
                    contact_number=row['contact_number']
                )
        elif data_type == 'zone':
            for row in reader:
                hub = Hub.objects.get(name=row['hub_name'])
                Zone.objects.create(
                    hub=hub,
                    name=row['name'],
                    description=row['description']
                )
        elif data_type == 'route':
            for row in reader:
                zone = Zone.objects.get(name=row['zone_name'])
                Route.objects.create(
                    zone=zone,
                    name=row['name'],
                    description=row['description'],
                    estimated_delivery_time=int(row['estimated_delivery_time'])
                )
