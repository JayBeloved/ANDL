from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('category/<slug:category_slug>/subcategory/<slug:slug>/', views.SubCategoryView.as_view(), name='subcategory'),
    path('tag/<slug:slug>/', views.TagView.as_view(), name='tag'),
    path('content/<slug:slug>/', views.ContentDetailView.as_view(), name='content_detail'),
    path('content/<slug:slug>/download/', views.download_content, name='download_content'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<slug:slug>/', views.BookDetailView.as_view(), name='book_detail'),
    path('book/<slug:slug>/download/', views.download_book, name='download_book'),
    path('quotes/', views.QuoteListView.as_view(), name='quotes'),
    path('quote/<int:quote_id>/share/', views.QuoteShareView.as_view(), name='quote_share'),
    path('quote/<int:quote_id>/generate-image/', views.generate_quote_image, name='generate_quote_image'),
]