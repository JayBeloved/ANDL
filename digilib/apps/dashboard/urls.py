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
    
    # Quote Management
    path('quotes/', views.QuoteListView.as_view(), name='quote_list'),
    path('quotes/create/', views.QuoteCreateView.as_view(), name='quote_create'),
    path('quotes/<int:pk>/edit/', views.QuoteUpdateView.as_view(), name='quote_edit'),
    path('quotes/<int:pk>/delete/', views.QuoteDeleteView.as_view(), name='quote_delete'),
    
    # Quote Categories
    path('quote-categories/', views.QuoteCategoryListView.as_view(), name='quote_category_list'),
    path('quote-categories/create/', views.quote_category_create, name='quote_category_create'),
    path('quote-categories/<int:pk>/update/', views.quote_category_update, name='quote_category_update'),
    path('quote-categories/<int:pk>/delete/', views.QuoteCategoryDeleteView.as_view(), name='quote_category_delete'),
    
    # Background Images
    path('backgrounds/', views.BackgroundImageListView.as_view(), name='background_list'),
    path('backgrounds/create/', views.BackgroundImageCreateView.as_view(), name='background_create'),
    path('backgrounds/<int:pk>/update/', views.BackgroundImageUpdateView.as_view(), name='background_update'),
    path('backgrounds/<int:pk>/toggle/', views.background_toggle, name='background_toggle'),
    path('backgrounds/<int:pk>/delete/', views.BackgroundImageDeleteView.as_view(), name='background_delete'),
    
    # Category Management
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # Subcategory Management
    path('subcategories/', views.SubcategoryListView.as_view(), name='subcategory_list'),
    path('subcategories/create/', views.subcategory_create, name='subcategory_create'),
    path('subcategories/<int:pk>/update/', views.subcategory_update, name='subcategory_update'),
    path('subcategories/<int:pk>/delete/', views.SubcategoryDeleteView.as_view(), name='subcategory_delete'),
    
    # API endpoints
    path('api/subcategories/<int:category_id>/', views.get_subcategories, name='get_subcategories'),
    
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
    
    # Database Management
    path('settings/database/export/', views.export_database, name='export_database'),
    path('settings/database/import/', views.import_database, name='import_database'),
    path('settings/database/restore/<str:filename>/', views.restore_database_backup, name='restore_database_backup'),
]