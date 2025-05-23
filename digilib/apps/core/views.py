from django.db.models import Q, Count
from django.views.generic import ListView, DetailView, TemplateView, View
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.apps import apps
from django.utils.functional import cached_property
from django.urls import reverse
from .models import Content, Category, SubCategory, Tag, Quote, QuoteCategory, BackgroundImage, Book
import json
from PIL import Image, ImageDraw, ImageFont
import io
import base64


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
    def subcategory_model(self):
        return apps.get_model('core', 'SubCategory')
        
    @cached_property
    def quote_model(self):
        return apps.get_model('core', 'Quote')
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
        
        # Get quotes from the standalone Quote model
        context['quotes'] = Quote.objects.filter(status='PUBLISHED').order_by('-created_at')[:12]
        
        # Get categories with subcategories
        categories = Category.objects.annotate(content_count=Count('contents'))
        for category in categories:
            category.subcategories_list = SubCategory.objects.filter(parent_category=category).annotate(
                content_count=Count('contents')
            )
        context['categories'] = categories
        
        # Get quote categories
        context['quote_categories'] = QuoteCategory.objects.all()
        
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
        self.subcategory = None
        
        # Check if subcategory is specified
        subcategory_slug = self.kwargs.get('subcategory_slug')
        if subcategory_slug:
            self.subcategory = get_object_or_404(SubCategory, slug=subcategory_slug, parent_category=self.category)
            return Content.objects.filter(
                category=self.category,
                subcategory=self.subcategory,
                status='PUBLISHED'
            ).select_related('category', 'subcategory', 'author').prefetch_related('tags')
        
        return Content.objects.filter(
            category=self.category,
            status='PUBLISHED'
        ).select_related('category', 'subcategory', 'author').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['subcategory'] = self.subcategory
        
        # Get all subcategories for this category
        context['subcategories'] = SubCategory.objects.filter(
            parent_category=self.category
        ).annotate(content_count=Count('contents'))
        
        # Get all categories for the sidebar
        categories = Category.objects.all().annotate(content_count=Count('contents'))
        for category in categories:
            category.subcategories_list = SubCategory.objects.filter(parent_category=category).annotate(
                content_count=Count('contents')
            )
        context['categories'] = categories
        
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
        ).select_related('category', 'subcategory', 'author').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        
        # Get all categories with subcategories for the sidebar
        categories = Category.objects.all().annotate(content_count=Count('contents'))
        for category in categories:
            category.subcategories_list = SubCategory.objects.filter(parent_category=category).annotate(
                content_count=Count('contents')
            )
        context['categories'] = categories
        
        return context


class SubCategoryView(ListView):
    model = Content
    template_name = 'core/subcategory.html'
    context_object_name = 'contents'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        self.subcategory = get_object_or_404(
            SubCategory, 
            slug=self.kwargs['slug'],
            parent_category=self.category
        )
        return Content.objects.filter(
            category=self.category,
            subcategory=self.subcategory,
            status='PUBLISHED'
        ).select_related('category', 'subcategory', 'author').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['subcategory'] = self.subcategory
        
        # Get all subcategories for this category
        context['subcategories'] = SubCategory.objects.filter(
            parent_category=self.category
        ).annotate(content_count=Count('contents'))
        
        # Get all categories with subcategories for the sidebar
        categories = Category.objects.all().annotate(content_count=Count('contents'))
        for category in categories:
            category.subcategories_list = SubCategory.objects.filter(parent_category=category).annotate(
                content_count=Count('contents')
            )
        context['categories'] = categories
        
        return context

class ContentDetailView(DetailView):
    model = Content
    template_name = 'core/content_detail.html'
    context_object_name = 'content'

    def get_queryset(self):
        return Content.objects.filter(
            status='PUBLISHED'
        ).select_related('category', 'subcategory', 'author').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content = self.get_object()

        # Get related content based on category, subcategory and tags
        related_query = Q(category=content.category)
        if content.subcategory:
            related_query |= Q(subcategory=content.subcategory)
        if content.tags.exists():
            related_query |= Q(tags__in=content.tags.all())
            
        context['related_contents'] = Content.objects.filter(
            related_query,
            status='PUBLISHED'
        ).exclude(id=content.id).distinct()[:3]

        # Add meta tags for SEO
        context['meta_description'] = content.summary[:160]
        context['meta_keywords'] = ', '.join([tag.name for tag in content.tags.all()])
        context['meta_title'] = content.title

        # Get categories with subcategories for the sidebar
        categories = Category.objects.annotate(content_count=Count('contents'))
        for category in categories:
            category.subcategories_list = SubCategory.objects.filter(parent_category=category).annotate(
                content_count=Count('contents')
            )
        context['categories'] = categories
        
        # If this is a quote, get the quote object
        if content.content_type == 'QUOTE':
            try:
                context['quote'] = Quote.objects.get(content=content)
            except Quote.DoesNotExist:
                pass

        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Increment the view count
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj


class BookListView(ListView):
    model = Book
    template_name = 'core/books.html'
    context_object_name = 'books'
    paginate_by = 12

    def get_queryset(self):
        queryset = Book.objects.filter(status='PUBLISHED')
        
        # Handle search
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author_name__icontains=search_query) |
                Q(synopsis__icontains=search_query)
            )
        
        # Handle category filter
        category_slug = self.request.GET.get('category', '')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Handle tag filter
        tag_slug = self.request.GET.get('tag', '')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        return queryset.select_related('category', 'subcategory').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get categories for filtering
        context['categories'] = Category.objects.all()
        
        # Get all tags for filtering
        context['tags'] = Tag.objects.all()
        
        return context


class BookDetailView(DetailView):
    model = Book
    template_name = 'core/book_detail.html'
    context_object_name = 'book'

    def get_queryset(self):
        return Book.objects.filter(
            status='PUBLISHED'
        ).select_related('category', 'subcategory').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()

        # Get related books based on category, subcategory and tags
        related_query = Q(category=book.category)
        if book.subcategory:
            related_query |= Q(subcategory=book.subcategory)
        if book.tags.exists():
            related_query |= Q(tags__in=book.tags.all())
            
        context['related_books'] = Book.objects.filter(
            related_query,
            status='PUBLISHED'
        ).exclude(id=book.id).distinct()[:3]

        # Add meta tags for SEO
        context['meta_description'] = book.synopsis[:160]
        context['meta_keywords'] = ', '.join([tag.name for tag in book.tags.all()])
        context['meta_title'] = book.title

        # Get categories with subcategories for the sidebar
        categories = Category.objects.annotate(content_count=Count('contents'))
        for category in categories:
            category.subcategories_list = SubCategory.objects.filter(parent_category=category).annotate(
                content_count=Count('contents')
            )
        context['categories'] = categories
        
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Increment the view count
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj


@require_POST
@login_required
def download_book(request, slug):
    book = get_object_or_404(Book, slug=slug, status='PUBLISHED')
    book.downloads_count += 1
    book.save(update_fields=['downloads_count'])
    return JsonResponse({'success': True, 'download_count': book.downloads_count})


class QuoteListView(ListView):
    model = Quote
    template_name = 'core/quotes.html'
    context_object_name = 'quotes'
    paginate_by = 24

    def get_queryset(self):
        queryset = Quote.objects.filter(status='PUBLISHED')
        
        # Handle search
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(quote_text__icontains=search_query)
            )
        
        # Handle category filter
        category_slug = self.request.GET.get('category', '')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Handle tag filter
        tag_slug = self.request.GET.get('tag', '')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        return queryset.select_related('author', 'category', 'default_background').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get quote categories
        context['quote_categories'] = QuoteCategory.objects.all()
        
        # Get all tags for filtering
        context['tags'] = Tag.objects.filter(quote_tags__isnull=False).distinct()
        
        return context


class QuoteShareView(View):
    template_name = 'core/quote_share.html'
    
    def get(self, request, quote_id, *args, **kwargs):
        quote = get_object_or_404(Quote, id=quote_id, status='PUBLISHED')
        
        
        # Increment view count
        quote.views_count += 1
        quote.save(update_fields=['views_count'])
        
        # Get all active background images
        backgrounds = BackgroundImage.objects.filter(is_active=True)
        
        # Get font options
        font_styles = Quote.FONT_STYLE_CHOICES
        text_positions = Quote.TEXT_POSITION_CHOICES
        
        context = {
            'quote': quote,
            'backgrounds': backgrounds,
            'default_background': quote.default_background.id if quote.default_background else None,
            'font_styles': font_styles,
            'text_positions': text_positions,
            'default_font_style': quote.default_font_style,
            'default_font_size': quote.default_font_size,
            'default_font_color': quote.default_font_color,
            'default_text_position': quote.default_text_position,
            'custom_x_position': quote.custom_x_position,
            'custom_y_position': quote.custom_y_position,
        }
        return render(request, self.template_name, context)


@require_POST
def generate_quote_image(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)

    
    # Get customization options from request
    background_id = request.POST.get('background_id')
    font_style = request.POST.get('font_style', quote.default_font_style)
    font_size = int(request.POST.get('font_size', quote.default_font_size))
    font_color = request.POST.get('font_color', quote.default_font_color)
    text_position = request.POST.get('text_position', quote.default_text_position)
    custom_x = request.POST.get('custom_x')
    custom_y = request.POST.get('custom_y')
    
    # Increment share count
    quote.shares_count += 1
    quote.save(update_fields=['shares_count'])
    
    # When loading background image, use image.url instead of image_url
    try:
        if background_id:
            background = BackgroundImage.objects.get(id=background_id, is_active=True)
        elif quote.default_background:
            background = quote.default_background
        else:
            # Fallback to first available background
            background = BackgroundImage.objects.filter(is_active=True).first()
        
        if not background:
            return JsonResponse({'error': 'No background image available'}, status=400)
    except BackgroundImage.DoesNotExist:
        return JsonResponse({'error': 'Background not found'}, status=400)
    
    try:
        # Open the background image from the file system instead of URL
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        img = Image.open(background.image.path)
        
        # Create a drawing context
        draw = ImageDraw.Draw(img)
        
        # Load font based on selected style
        # Use custom fonts from the static/fonts directory
        import os
        from django.conf import settings
        
        font_mapping = {
            'ARIAL': 'arial.ttf',
            'TIMES': 'times.ttf',
            'DAILYQUOTES': 'DailyQuotes.otf',
            'LATO-BOLD': 'Lato-Bold.ttf',
            'LATO-ITALIC': 'Lato-Italic.ttf',
            'POPPINS-ITALIC': 'Poppins-Italic.ttf',
            'POPPINS-THIN': 'Poppins-Thin.ttf',
            'LATO-REGULAR': 'Lato-Regular.ttf',
            'POPPINS-REGULAR': 'Poppins-Regular.ttf',
            'QUOTE': 'Quote.ttf'
        }
        
        try:
            # Try to load the selected font from the static/fonts directory
            font_file = font_mapping.get(font_style, 'arial.ttf')
            font_path = os.path.join(settings.STATIC_ROOT, 'fonts', font_file)
            
            # If STATIC_ROOT is not set or the file doesn't exist there, try STATICFILES_DIRS
            if not os.path.exists(font_path):
                for static_dir in settings.STATICFILES_DIRS:
                    alt_path = os.path.join(static_dir, 'fonts', font_file)
                    if os.path.exists(alt_path):
                        font_path = alt_path
                        break
            
            font = ImageFont.truetype(font_path, font_size)
        except Exception as e:
            # Fallback to default font
            print(f"Font error: {e}")
            font = ImageFont.load_default()
        
        # Convert hex color to RGB
        font_color_rgb = tuple(int(font_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        # Calculate text position based on selection
        width, height = img.size
        text = quote.quote_text
        
        # Wrap text to fit width
        lines = []
        words = text.split()
        current_line = words[0] if words else ""
        for word in words[1:]:
            test_line = current_line + ' ' + word
            # Use font to get actual text width
            text_width = draw.textlength(test_line, font=font)
            if text_width < width - 200:  # 50px margin on each side
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
        
        # Calculate total text height
        line_height = font_size * 1.2  # Add some line spacing
        total_text_height = len(lines) * line_height
        
        # Determine text position
        if text_position == 'CENTER':
            x_start = width // 2
            y_start = (height - total_text_height) // 2
            text_align = "center"
        elif text_position == 'TOP':
            x_start = width // 2
            y_start = 50  # 50px from top
            text_align = "center"
        elif text_position == 'BOTTOM':
            x_start = width // 2
            y_start = height - total_text_height - 150  # 150px from bottom to leave room for author
            text_align = "center"
        elif text_position == 'CUSTOM' and custom_x and custom_y:
            x_start = int(custom_x)
            y_start = int(custom_y)
            text_align = "left"
        else:
            # Default to center if custom position is invalid
            x_start = width // 2
            y_start = (height - total_text_height) // 2
            text_align = "center"
        
        # Draw the quote text
        y_position = y_start
        for line in lines:
            if text_align == "center":
                # Center align text
                text_width = draw.textlength(line, font=font)
                x_position = x_start - (text_width // 2)
            else:
                x_position = x_start
                
            draw.text((x_position, y_position), line, font=font, fill=font_color_rgb)
            y_position += line_height
        
        # Note: We don't need to add author name and website text as they're pre-designed on the background image
        
        # Save the image to a BytesIO object
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Convert to base64 for embedding in HTML
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return JsonResponse({
            'image': f'data:image/png;base64,{img_str}',
            'success': True
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
def download_content(request, slug):
    content = get_object_or_404(Content, slug=slug, status='PUBLISHED')
    content.downloads_count += 1
    content.save(update_fields=['downloads_count'])
    return JsonResponse({'success': True, 'download_count': content.downloads_count})


class AboutView(TemplateView):
    """View for the About Niyi Makinde page"""
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get categories with subcategories for the sidebar
        categories = Category.objects.annotate(content_count=Count('contents'))
        for category in categories:
            category.subcategories_list = SubCategory.objects.filter(parent_category=category).annotate(
                content_count=Count('contents')
            )
        context['categories'] = categories
        return context


class NapmonView(TemplateView):
    """View for the NAPMON (New Apostolic and Prophetic Movement of Nigeria) page"""
    template_name = 'core/about_napmon.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get categories with subcategories for the sidebar
        categories = Category.objects.annotate(content_count=Count('contents'))
        for category in categories:
            category.subcategories_list = SubCategory.objects.filter(parent_category=category).annotate(
                content_count=Count('contents')
            )
        context['categories'] = categories
        return context


# Add this to the existing views.py file after the other view classes

class ConnectGlobalView(TemplateView):
    """View for the Connect Global page"""
    template_name = 'core/about_connect.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get categories with subcategories for the sidebar
        categories = Category.objects.annotate(content_count=Count('contents'))
        for category in categories:
            category.subcategories_list = SubCategory.objects.filter(parent_category=category).annotate(
                content_count=Count('contents')
            )
        context['categories'] = categories
        return context


# Add this to the existing views.py file after the other view classes

class RebirthGlobalView(TemplateView):
    """View for the Rebirth Global Church page"""
    template_name = 'core/about_rebirth.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get categories with subcategories for the sidebar
        categories = Category.objects.annotate(content_count=Count('contents'))
        for category in categories:
            category.subcategories_list = SubCategory.objects.filter(parent_category=category).annotate(
                content_count=Count('contents')
            )
        context['categories'] = categories
        return context



class MinistryView(TemplateView):
    """View for the Ministry page showcasing all ministries"""
    template_name = 'core/ministry.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get ministry category
        try:
            ministry_category = Category.objects.get(slug='ministry')
            
            # Get subcategories for ministry
            subcategories = SubCategory.objects.filter(
                parent_category=ministry_category
            ).annotate(content_count=Count('contents'))
            
            context['subcategories'] = subcategories
            context['ministry_category'] = ministry_category
        except Category.DoesNotExist:
            context['subcategories'] = []
            context['ministry_category'] = None
        
        # Get categories with subcategories for the sidebar
        categories = Category.objects.annotate(content_count=Count('contents'))
        for category in categories:
            category.subcategories_list = SubCategory.objects.filter(parent_category=category).annotate(
                content_count=Count('contents')
            )
        context['categories'] = categories
        
        return context