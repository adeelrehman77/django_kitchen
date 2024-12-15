
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import ItemSerializer, CustomerProfileSerializer, SubscriptionSerializer, DeliveryStatusSerializer
from .models import Item, CustomerProfile, Subscription, DeliveryStatus

class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Item.objects.filter(is_active=True)
    serializer_class = ItemSerializer

class CustomerProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerProfileSerializer
    
    def get_queryset(self):
        return CustomerProfile.objects.filter(user=self.request.user)

class SubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer
    
    def get_queryset(self):
        return Subscription.objects.filter(customer__user=self.request.user)

class DeliveryStatusViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DeliveryStatusSerializer
    
    def get_queryset(self):
        return DeliveryStatus.objects.filter(subscription__customer__user=self.request.user)
