from django.contrib import admin
from django.utils.html import format_html
from django.apps import apps

# Get models using apps.get_model to avoid circular imports
Category = apps.get_model('core', 'Category')
SubCategory = apps.get_model('core', 'SubCategory')
Tag = apps.get_model('core', 'Tag')
Quote = apps.get_model('core', 'Quote')
Content = apps.get_model('core', 'Content')
QuoteCategory = apps.get_model('core', 'QuoteCategory')
BackgroundImage = apps.get_model('core', 'BackgroundImage')
Book = apps.get_model('core', 'Book')
SiteSettings = apps.get_model('core', 'SiteSettings')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image_preview')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Image'


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_category', 'description', 'image_preview')
    list_filter = ('parent_category',)
    search_fields = ('name', 'description', 'parent_category__name')
    prepopulated_fields = {'slug': ('name',)}
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Image'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'subcategory', 'content_type', 
                   'status', 'publication_date', 'views_count', 'image_preview')
    list_filter = ('status', 'content_type', 'category', 'subcategory', 'tags')
    search_fields = ('title', 'summary', 'content')
    filter_horizontal = ('tags',)
    
    fieldsets = (
        (None, {
            'fields': ('title', 'author', 'summary', 'content')
        }),
        ('Media', {
            'fields': ('featured_image', 'image_preview_large')
        }),
        ('Categorization', {
            'fields': ('category', 'subcategory', 'tags', 'content_type')
        }),
        ('External Links', {
            'fields': ('external_links', 'spotify_link', 'youtube_link', 'download_link')
        }),
        ('Publication', {
            'fields': ('status', 'publication_date')
        }),
        ('Statistics', {
            'fields': ('views_count', 'downloads_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('created_at', 'updated_at')
        return self.readonly_fields
    
    def image_preview(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.featured_image.url)
        return "-"
    image_preview.short_description = 'Image'
    
    def image_preview_large(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" width="300" style="max-height: 200px; object-fit: contain;" />', obj.featured_image.url)
        return "-"
    image_preview_large.short_description = 'Image Preview'


@admin.register(QuoteCategory)
class QuoteCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image_preview', 'get_quotes_count')
    search_fields = ('name', 'description')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Image'
    
    def get_quotes_count(self, obj):
        return obj.quotes.count()
    get_quotes_count.short_description = 'Quotes Count'


@admin.register(BackgroundImage)
class BackgroundImageAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image_preview', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Image'


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('quote_text_preview', 'author', 'category', 'status', 'featured', 'shares_count', 'views_count', 'created_at')
    list_filter = ('status', 'featured', 'category', 'tags', 'default_background')
    search_fields = ('quote_text', 'author__username', 'author__email')
    filter_horizontal = ('tags',)
    actions = ['make_published', 'make_draft', 'toggle_featured']
    readonly_fields = ('shares_count', 'views_count', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('quote_text', 'author', 'category', 'tags', 'status', 'featured')
        }),
        ('Appearance', {
            'fields': ('default_background', 'default_text_position', 'default_font_style', 
                     'default_font_size', 'default_font_color')
        }),
        ('Custom Positioning', {
            'fields': ('custom_x_position', 'custom_y_position'),
            'classes': ('collapse',),
        }),
        ('Statistics', {
            'fields': ('shares_count', 'views_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def quote_text_preview(self, obj):
        if len(obj.quote_text) > 50:
            return f"{obj.quote_text[:50]}..."
        return obj.quote_text
    quote_text_preview.short_description = 'Quote Text'
    
    def make_published(self, request, queryset):
        queryset.update(status='PUBLISHED')
    make_published.short_description = "Mark selected quotes as published"
    
    def make_draft(self, request, queryset):
        queryset.update(status='DRAFT')
    make_draft.short_description = "Mark selected quotes as draft"
    
    def toggle_featured(self, request, queryset):
        for quote in queryset:
            quote.featured = not quote.featured
            quote.save()
    toggle_featured.short_description = "Toggle featured status"


# Register the Book model
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_name', 'category', 'publication_date', 'status', 'featured', 'views_count', 'downloads_count', 'cover_preview')
    list_filter = ('status', 'featured', 'category', 'subcategory', 'tags')
    search_fields = ('title', 'author_name', 'synopsis', 'publisher', 'isbn')
    filter_horizontal = ('tags',)
    readonly_fields = ('views_count', 'downloads_count', 'created_at', 'updated_at', 'cover_preview_large', 'slug')
    actions = ['make_published', 'make_draft', 'toggle_featured']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'author_name', 'synopsis')
        }),
        ('Book Details', {
            'fields': ('publication_date', 'publisher', 'isbn', 'pages')
        }),
        ('Media', {
            'fields': ('cover_image', 'cover_preview_large', 'pdf_file')
        }),
        ('Categorization', {
            'fields': ('category', 'subcategory', 'tags')
        }),
        ('Publication', {
            'fields': ('status', 'featured')
        }),
        ('Statistics', {
            'fields': ('views_count', 'downloads_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'slug'),
            'classes': ('collapse',)
        }),
    )
    
    def cover_preview(self, obj):
        if hasattr(obj, 'cover_image') and obj.cover_image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.cover_image.url)
        return "-"
    cover_preview.short_description = 'Cover'
    
    def cover_preview_large(self, obj):
        if hasattr(obj, 'cover_image') and obj.cover_image:
            return format_html('<img src="{}" width="300" style="max-height: 200px; object-fit: contain;" />', obj.cover_image.url)
        return "-"
    cover_preview_large.short_description = 'Cover Preview'

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields
        return ('views_count', 'downloads_count', 'created_at', 'updated_at', 'cover_preview_large')
    
    def make_published(self, request, queryset):
        queryset.update(status='PUBLISHED')
    make_published.short_description = "Mark selected books as published"
    
    def make_draft(self, request, queryset):
        queryset.update(status='DRAFT')
    make_draft.short_description = "Mark selected books as draft"
    
    def toggle_featured(self, request, queryset):
        for book in queryset:
            book.featured = not book.featured
            book.save()
    toggle_featured.short_description = "Toggle featured status"
    


# Register the SiteSettings model
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_title', 'contact_email', 'maintenance_mode', 'last_db_backup')
    fieldsets = (
        ('Site Information', {
            'fields': ('site_title', 'site_description', 'contact_email', 'items_per_page')
        }),
        ('Maintenance', {
            'fields': ('maintenance_mode', 'maintenance_message')
        }),
        ('Backup', {
            'fields': ('last_db_backup',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('last_db_backup',)
    
    def has_add_permission(self, request):
        # Only allow one instance of SiteSettings
        return SiteSettings.objects.count() == 0
        