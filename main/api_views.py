
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
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

class LogoutView(APIView):
    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
