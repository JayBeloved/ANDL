from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.apps import apps

class ContentSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8
    
    def items(self):        
        Content = apps.get_model('core', 'Content')        
        return Content.objects.filter(status='PUBLISHED')
    
    def lastmod(self, obj):
        return obj.updated_at

class CategorySitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7
    
    def items(self):        
        Category = apps.get_model('core', 'Category')        
        return Category.objects.all()
    
    def lastmod(self, obj):        
        Content = apps.get_model('core', 'Content')        
        try:
            return obj.contents.latest('updated_at').updated_at
        except Content.DoesNotExist:
            return None

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'
    
    def items(self):
        return ['core:home', 'core:search']
    
    def location(self, item):
        return reverse(item)