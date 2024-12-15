
from rest_framework import serializers
from .models import Item, CustomerProfile, Subscription, DeliveryStatus

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'price', 'image']

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ['phone', 'building_name', 'floor_number', 'flat_number', 'wallet_balance']

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['items', 'start_date', 'end_date', 'status', 'time_slot', 'payment_mode', 'selected_days']

class DeliveryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryStatus
        fields = ['subscription', 'date', 'status', 'notes']
