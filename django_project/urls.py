
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('menu/<int:menu_id>/', views.menu_preview, name='menu_preview'),
]
