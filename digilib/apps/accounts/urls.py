from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('dashboard/', views.AdminDashboardView.as_view(), name='dashboard'),
    path('profile/', views.AdminProfileView.as_view(), name='profile'),
    path('password/', views.AdminPasswordChangeView.as_view(), name='password_change'),
]