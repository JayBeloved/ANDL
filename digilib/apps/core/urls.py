from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('tag/<slug:slug>/', views.TagView.as_view(), name='tag'),
    path('content/<slug:slug>/', views.ContentDetailView.as_view(), name='content_detail'),
    path('content/<slug:slug>/download/', views.download_content, name='download_content'),
]