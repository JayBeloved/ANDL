"""URL configuration for ApostleNiyiDigitalLibrary project."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from digilib.apps.core.sitemaps import ContentSitemap, CategorySitemap, StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'content': ContentSitemap,
    'categories': CategorySitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('digilib.apps.accounts.urls')),
    path('api/', include('digilib.apps.core.api_urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('dashboard/', include('digilib.apps.dashboard.urls')),
    path('', include('digilib.apps.core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')))