from django.db.models import Q, Count
from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.apps import apps
from django.utils.functional import cached_property
from .models import Content, Category, Tag


class HomeView(ListView):
    model = Content
    template_name = 'core/home.html'
    context_object_name = 'contents'
    paginate_by = 12
    
    @cached_property
    def content_model(self):
        return apps.get_model('core', 'Content')
    
    @cached_property
    def category_model(self):
        return apps.get_model('core', 'Category')
    
    @cached_property
    def tag_model(self):
        return apps.get_model('core', 'Tag')
        paginate_by = 12

    def get_queryset(self):
        return Content.objects.filter(
            status='PUBLISHED'
        ).select_related('category', 'author').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get featured content
        context['featured_contents'] = self.get_queryset().order_by('-views_count')[:6]
        
        # Get content by type
        context['sermons'] = self.get_queryset().filter(content_type='SERMON')[:6]
        context['books'] = self.get_queryset().filter(content_type='BOOK')[:6]
        context['articles'] = self.get_queryset().filter(content_type='WRITE_UP')[:6]
        
        # Get categories
        context['categories'] = Category.objects.annotate(content_count=Count('contents'))
        
        # Get popular tags
        context['popular_tags'] = Tag.objects.annotate(
            content_count=Count('contents')
        ).order_by('-content_count')[:10]
        
        return context

class SearchView(ListView):
    model = Content
    template_name = 'core/search.html'
    context_object_name = 'contents'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            # Using Q objects for complex queries
            return Content.objects.filter(
                Q(title__icontains=query) |
                Q(summary__icontains=query) |
                Q(category__name__icontains=query) |
                Q(tags__name__icontains=query),
                status='PUBLISHED'
            ).select_related('category', 'author').prefetch_related('tags').distinct()
        return Content.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['categories'] = Category.objects.all()
        return context

class CategoryView(ListView):
    model = Content
    template_name = 'core/category.html'
    context_object_name = 'contents'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Content.objects.filter(
            category=self.category,
            status='PUBLISHED'
        ).select_related('category', 'author').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.all()
        return context

class TagView(ListView):
    model = Content
    template_name = 'core/tag.html'
    context_object_name = 'contents'
    paginate_by = 12

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Content.objects.filter(
            tags=self.tag,
            status='PUBLISHED'
        ).select_related('category', 'author').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        context['categories'] = Category.objects.all()
        return context

class ContentDetailView(DetailView):
    model = Content
    template_name = 'core/content_detail.html'
    context_object_name = 'content'

    def get_queryset(self):
        return Content.objects.filter(
            status='PUBLISHED'
        ).select_related('category', 'author').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content = self.get_object()

        # Get related content based on category and tags
        context['related_contents'] = Content.objects.filter(
            Q(category=content.category) | Q(tags__in=content.tags.all()),
            status='PUBLISHED'
        ).exclude(id=content.id).distinct()[:3]

        # Add meta tags for SEO
        context['meta_description'] = content.summary[:160]
        context['meta_keywords'] = ', '.join([tag.name for tag in content.tags.all()])
        context['meta_title'] = content.title

        # Get categories with content count
        context['categories'] = Category.objects.annotate(content_count=Count('contents'))

        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Increment the view count
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj

@require_POST
@login_required
def download_content(request, slug):
    content = get_object_or_404(Content, slug=slug, status='PUBLISHED')
    content.downloads_count += 1
    content.save(update_fields=['downloads_count'])
    return JsonResponse({'success': True, 'download_count': content.downloads_count})