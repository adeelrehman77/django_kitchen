from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from main import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('wallet/topup/', views.wallet_topup, name='wallet_topup'),
    path('wallet/transactions/', views.transaction_history, name='transaction_history'),
    path('', views.home, name='home'),
    path('subscription-report/', views.subscription_report, name='subscription_report'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('menu/<int:menu_id>/', views.menu_preview, name='menu_preview'),
path('delivery-summary/', views.delivery_summary, name='delivery_summary'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
