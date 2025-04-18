from django.contrib import admin
from django.utils.html import format_html
from django.apps import apps

# Get models using apps.get_model to avoid circular imports
Category = apps.get_model('core', 'Category')
Tag = apps.get_model('core', 'Tag')
Content = apps.get_model('core', 'Content')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'content_type', 
                   'status', 'publication_date', 'views_count', 'image_preview')
    list_filter = ('status', 'content_type', 'category', 'tags')
    search_fields = ('title', 'summary', 'content')
    date_hierarchy = 'publication_date'
    filter_horizontal = ('tags',)
    readonly_fields = ('views_count', 'downloads_count', 'created_at', 'updated_at', 'image_preview_large')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'author', 'summary', 'content')
        }),
        ('Media', {
            'fields': ('featured_image', 'image_preview_large')
        }),
        ('Categorization', {
            'fields': ('category', 'tags', 'content_type')
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