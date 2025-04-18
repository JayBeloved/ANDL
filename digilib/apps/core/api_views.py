from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django.apps import apps
from .serializers import ContentListSerializer, ContentDetailSerializer, CategorySerializer, TagSerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        Category = apps.get_model('core', 'Category')
        return Category.objects.all()
    
    @action(detail=True)
    def contents(self, request, slug=None):
        Content = apps.get_model('core', 'Content')
        category = self.get_object()
        contents = Content.objects.filter(
            category=category,
            status='PUBLISHED'
        )
        page = self.paginate_queryset(contents)
        if page is not None:
            serializer = ContentListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ContentListSerializer(contents, many=True, context={'request': request})
        return Response(serializer.data)

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    def get_queryset(self):
        Tag = apps.get_model('core', 'Tag')
        return Tag.objects.all()
    
    @action(detail=True)
    def contents(self, request, slug=None):
        Content = apps.get_model('core', 'Content')
        tag = self.get_object()
        contents = Content.objects.filter(
            tags=tag,
            status='PUBLISHED'
        )
        page = self.paginate_queryset(contents)
        if page is not None:
            serializer = ContentListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ContentListSerializer(contents, many=True, context={'request': request})
        return Response(serializer.data)

class ContentViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['content_type', 'category__slug', 'tags__slug']
    search_fields = ['title', 'summary', 'content']
    ordering_fields = ['publication_date', 'views_count', 'downloads_count', 'created_at']
    ordering = ['-publication_date']
    
    def get_queryset(self):
        Content = apps.get_model('core', 'Content')
        return Content.objects.filter(status='PUBLISHED')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ContentDetailSerializer
        return ContentListSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Check if increment_views method exists, otherwise increment manually
        if hasattr(instance, 'increment_views'):
            instance.increment_views()
        else:
            instance.views_count += 1
            instance.save(update_fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False)
    def featured(self, request):
        Content = apps.get_model('core', 'Content')
        featured = Content.objects.filter(
            status='PUBLISHED'
        ).order_by('-views_count')[:5]
        serializer = ContentListSerializer(featured, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False)
    def recent(self, request):
        Content = apps.get_model('core', 'Content')
        recent = Content.objects.filter(
            status='PUBLISHED'
        ).order_by('-publication_date')[:5]
        serializer = ContentListSerializer(recent, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False)
    def search(self, request):
        Content = apps.get_model('core', 'Content')
        query = request.query_params.get('q', '')
        if not query:
            return Response({'results': []})
            
        results = Content.objects.filter(
            Q(title__icontains=query) | 
            Q(summary__icontains=query) | 
            Q(content__icontains=query),
            status='PUBLISHED'
        )
        page = self.paginate_queryset(results)
        if page is not None:
            serializer = ContentListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ContentListSerializer(results, many=True, context={'request': request})
        return Response(serializer.data)