from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard Home
    path('', views.DashboardHomeView.as_view(), name='index'),
    
    # Content Management
    path('content/', views.ContentListView.as_view(), name='content_list'),
    path('content/create/', views.ContentCreateView.as_view(), name='content_create'),
    path('content/<int:pk>/edit/', views.ContentUpdateView.as_view(), name='content_edit'),
    path('content/<int:pk>/delete/', views.ContentDeleteView.as_view(), name='content_delete'),
    
    # Category Management
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # Tag Management
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('tags/create/', views.tag_create, name='tag_create'),
    path('tags/<int:pk>/update/', views.tag_update, name='tag_update'),
    path('tags/<int:pk>/delete/', views.TagDeleteView.as_view(), name='tag_delete'),
    
    # User Management
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    
    # Settings
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('settings/site/', views.update_site_settings, name='update_site_settings'),
    path('settings/social/', views.update_social_links, name='update_social_links'),
    path('settings/maintenance/', views.toggle_maintenance_mode, name='toggle_maintenance_mode'),
]