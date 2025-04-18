from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.apps import apps

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = fields

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = apps.get_model('core', 'Category')
        fields = ['id', 'name', 'description', 'slug']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = apps.get_model('core', 'Tag')
        fields = ['id', 'name', 'slug']

class ContentListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = apps.get_model('core', 'Content')
        fields = [
            'id', 'title', 'slug', 'summary', 'author', 'category', 'tags',
            'content_type', 'featured_image', 'status', 'publication_date',
            'created_at', 'updated_at', 'views_count', 'downloads_count'
        ]

class ContentDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = apps.get_model('core', 'Content')
        fields = [
            'id', 'title', 'slug', 'summary', 'content', 'author', 'category', 'tags',
            'content_type', 'featured_image', 'external_links', 'spotify_link', 
            'youtube_link', 'download_link', 'status', 'publication_date',
            'created_at', 'updated_at', 'views_count', 'downloads_count'
        ]