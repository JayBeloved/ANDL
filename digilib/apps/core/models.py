from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
import json


class Category(models.Model):
    """Content categories like Finance, Spiritual Growth, etc."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, editable=False)
    image = models.ImageField(upload_to='categories/', blank=True, null=True, help_text="Category image for display in cards")
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['id']  # Order by ID instead of alphabetically
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class SubCategory(models.Model):
    """Sub-categories that belong to a parent category"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, editable=False)
    parent_category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='subcategories'
    )
    image = models.ImageField(upload_to='subcategories/', blank=True, null=True, help_text="Subcategory image for display in cards")
    
    class Meta:
        verbose_name = 'Sub Category'
        verbose_name_plural = 'Sub Categories'
        ordering = ['name']
        unique_together = ['name', 'parent_category']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.parent_category.slug}-{self.name}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.parent_category.name} - {self.name}"


class Tag(models.Model):
    """Content tags for granular filtering"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, editable=False)
    
    class Meta:
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Content(models.Model):
    """Main content model for all types of content"""
    CONTENT_TYPES = [
        ('SERMON', 'Sermon'),
        ('BOOK', 'Book'),
        ('WRITE_UP', 'Write-Up')]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contents'
    )
    summary = models.TextField(help_text="A brief excerpt or summary of the content")
    content = RichTextUploadingField(blank=True, null=True, help_text="Main content body")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='contents'
    )
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name='contents',
        blank=True,
        null=True
    )
    tags = models.ManyToManyField(Tag, related_name='contents', blank=True)
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPES,
        default='WRITE_UP'
    )
    featured_image = models.ImageField(upload_to='content/featured/', blank=True, null=True)
    external_links = models.JSONField(default=dict, blank=True, help_text="JSON field for external links")
    spotify_link = models.URLField(blank=True)
    youtube_link = models.URLField(blank=True)
    download_link = models.URLField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )
    publication_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0)
    downloads_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-publication_date', '-created_at']
        indexes = [
            models.Index(fields=['-publication_date', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['content_type']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('core:content_detail', kwargs={'slug': self.slug})
    
    def get_external_links(self):
        if isinstance(self.external_links, str):
            return json.loads(self.external_links)
        return self.external_links
    
    def __str__(self):
        return self.title

# c:\Archive\ANDL\digilib\apps\core\models.py
class BackgroundImage(models.Model):
    """Model for quote background images"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='backgrounds/', help_text="Background image for quotes (1080x1080 px recommended)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def image_url(self):
        """For backwards compatibility with code that uses image_url"""
        if self.image:
            return self.image.url
        return None


class QuoteCategory(models.Model):
    """Categories specifically for quotes"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, editable=False)
    image = models.ImageField(upload_to='quote_categories/', blank=True, null=True, help_text="Category image for display in cards")
    
    class Meta:
        verbose_name = 'Quote Category'
        verbose_name_plural = 'Quote Categories'
        ordering = ['id']  # Order by ID instead of alphabetically
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Book(models.Model):
    """Model for books and PDF collections"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, editable=False)
    author_name = models.CharField(max_length=100)
    synopsis = models.TextField(help_text="Brief description of the book")
    cover_image = models.ImageField(upload_to='books/covers/', help_text="Book cover image")
    pdf_file = models.FileField(upload_to='books/files/', help_text="PDF file for download")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='books'
    )
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name='books',
        blank=True,
        null=True
    )
    tags = models.ManyToManyField(Tag, related_name='books', blank=True)
    publication_date = models.DateField(blank=True, null=True)
    publisher = models.CharField(max_length=100, blank=True)
    isbn = models.CharField(max_length=20, blank=True, help_text="ISBN number if available")
    pages = models.PositiveIntegerField(blank=True, null=True, help_text="Number of pages")
    featured = models.BooleanField(default=False)
    status = models.CharField(
        max_length=10,
        choices=Content.STATUS_CHOICES,
        default='DRAFT'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0)
    downloads_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title


class SiteSettings(models.Model):
    """Site-wide settings model"""
    site_title = models.CharField(max_length=100, default="Apostle Niyi Digital Library")
    site_description = models.TextField(blank=True, default="Digital Library for Apostle Niyi Makinde's content")
    contact_email = models.EmailField(blank=True)
    items_per_page = models.PositiveIntegerField(default=12)
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True, default="We're currently performing maintenance. Please check back soon.")
    last_db_backup = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return "Site Settings"


class Quote(models.Model):
    """Standalone model for quotes with sharing capabilities"""
    TEXT_POSITION_CHOICES = [
        ('CENTER', 'Center'),
        ('TOP', 'Top'),
        ('BOTTOM', 'Bottom'),
        ('CUSTOM', 'Custom'),
    ]
    
    FONT_STYLE_CHOICES = [
        ('ARIAL', 'Arial'),
        ('TIMES', 'Times New Roman'),
        ('DAILYQUOTES', 'Daily Quotes'),
        ('LATO-BOLD', 'Lato Italic'),
        ('LATO-ITALIC', 'Lato Italic'),
        ('LATO-REGULAR', 'Lato Regular'),
        ('POPPINS-ITALIC', 'Poppins Italic'),
        ('POPPINS-REGULAR', 'Poppins Regular'),
        ('POPPINS-THIN', 'Poppins Thin'),
        ('QUOTE', 'Quote')
    ]
    
    quote_text = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='authored_quotes'
    )
    category = models.ForeignKey(
        QuoteCategory,
        on_delete=models.CASCADE,
        related_name='quotes',
        null=True,
        blank=True
    )
    tags = models.ManyToManyField(Tag, related_name='quote_tags', blank=True)
    default_background = models.ForeignKey(
        BackgroundImage,
        on_delete=models.SET_NULL,
        related_name='quotes',
        null=True,
        blank=True
    )
    default_text_position = models.CharField(
        max_length=10,
        choices=TEXT_POSITION_CHOICES,
        default='CENTER'
    )
    default_font_style = models.CharField(
        max_length=20,
        choices=FONT_STYLE_CHOICES,
        default='ARIAL'
    )
    default_font_size = models.PositiveIntegerField(default=36)
    default_font_color = models.CharField(max_length=7, default='#FFFFFF')
    custom_x_position = models.PositiveIntegerField(null=True, blank=True, help_text="X position in pixels (only used with CUSTOM position)")
    custom_y_position = models.PositiveIntegerField(null=True, blank=True, help_text="Y position in pixels (only used with CUSTOM position)")
    featured = models.BooleanField(default=False, help_text="Featured quotes will be displayed prominently")
    status = models.CharField(
        max_length=10,
        choices=Content.STATUS_CHOICES,  # Reuse the same status choices from Content model
        default='DRAFT'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shares_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Quote: {self.quote_text[:50]}..."