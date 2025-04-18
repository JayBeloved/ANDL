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
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


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
        ('WRITE_UP', 'Write-Up'),
    ]
    
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