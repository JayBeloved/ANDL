from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ContentViewSet, CategoryViewSet, TagViewSet

router = DefaultRouter()
router.register(r'contents', ContentViewSet, basename='content')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
]