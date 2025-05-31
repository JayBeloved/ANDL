import os
import csv
import io
from django.shortcuts import render
from django.views.generic import FormView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from django.apps import apps
from django.core.files.storage import FileSystemStorage# digilib/apps/dashboard/views.py
from django import forms
from django.conf import settings
from django.http import FileResponse
import sqlite3
import datetime

from django.http import JsonResponse, HttpResponse
from digilib.apps.core.models import Category, SubCategory, QuoteCategory, BackgroundImage
from django.shortcuts import get_object_or_404

User = get_user_model()

# Helper function to check if user is staff
def is_staff(user):
    return user.is_staff


# Form for selecting the model to export
class ExportTemplateForm(forms.Form):
    MODEL_CHOICES = [
        ('Category', 'Category'),
        ('SubCategory', 'Sub Category'),
        ('Tag', 'Tag'),
        ('Content', 'Content'),
        ('Quote', 'Quote'),
        ('QuoteCategory', 'Quote Category'),
        ('SiteSettings', 'Site Settings'),
        ('SocialLinks', 'Social Links'),
    ]
    model = forms.ChoiceField(choices=MODEL_CHOICES, label='Select Model to Export')

# Form for selecting the model to import
class ImportTemplateForm(forms.Form):
    MODEL_CHOICES = [
        ('Category', 'Category'),
        ('SubCategory', 'Sub Category'),
        ('Tag', 'Tag'),
        ('Content', 'Content'),
        ('Quote', 'Quote'),
        ('QuoteCategory', 'Quote Category'),
        ('SiteSettings', 'Site Settings'),
        ('SocialLinks', 'Social Links'),
    ]
    model = forms.ChoiceField(choices=MODEL_CHOICES, label='Select Model to Import')
    csv_file = forms.FileField(label='CSV File', help_text='Select the CSV file to import')

# Dashboard Home
class DashboardHomeView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/index.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Content = apps.get_model('core', 'Content')
        Quote = apps.get_model('core', 'Quote')
        
        # Get counts
        context['content_count'] = Content.objects.count()
        context['quote_count'] = Quote.objects.count()
        context['total_views'] = Content.objects.aggregate(Sum('views_count'))['views_count__sum'] or 0
        context['total_downloads'] = Content.objects.aggregate(Sum('downloads_count'))['downloads_count__sum'] or 0
        context['user_count'] = User.objects.count()
        
        # Calculate growth percentages
        now = timezone.now()
        month_ago = now - timedelta(days=30)
        two_months_ago = now - timedelta(days=60)
        
        # Content growth
        current_month_content = Content.objects.filter(created_at__gte=month_ago).count()
        prev_month_content = Content.objects.filter(created_at__gte=two_months_ago, created_at__lt=month_ago).count()
        context['content_growth'] = calculate_growth(current_month_content, prev_month_content)
        
        # Quote growth
        current_month_quotes = Quote.objects.filter(created_at__gte=month_ago).count()
        prev_month_quotes = Quote.objects.filter(created_at__gte=two_months_ago, created_at__lt=month_ago).count()
        context['quote_growth'] = calculate_growth(current_month_quotes, prev_month_quotes)
        
        # Views growth
        current_month_views = Content.objects.filter(created_at__gte=month_ago).aggregate(Sum('views_count'))['views_count__sum'] or 0
        prev_month_views = Content.objects.filter(created_at__gte=two_months_ago, created_at__lt=month_ago).aggregate(Sum('views_count'))['views_count__sum'] or 0
        context['views_growth'] = calculate_growth(current_month_views, prev_month_views)
        
        # Downloads growth
        current_month_downloads = Content.objects.filter(created_at__gte=month_ago).aggregate(Sum('downloads_count'))['downloads_count__sum'] or 0
        prev_month_downloads = Content.objects.filter(created_at__gte=two_months_ago, created_at__lt=month_ago).aggregate(Sum('downloads_count'))['downloads_count__sum'] or 0
        context['downloads_growth'] = calculate_growth(current_month_downloads, prev_month_downloads)
        
        # User growth
        current_month_users = User.objects.filter(date_joined__gte=month_ago).count()
        prev_month_users = User.objects.filter(date_joined__gte=two_months_ago, date_joined__lt=month_ago).count()
        context['user_growth'] = calculate_growth(current_month_users, prev_month_users)
        
        # Recent and popular content
        context['recent_content'] = Content.objects.order_by('-created_at')[:5]
        context['popular_content'] = Content.objects.order_by('-views_count')[:5]
        
        # Recent and popular quotes
        context['recent_quotes'] = Quote.objects.order_by('-created_at')[:5]
        context['popular_quotes'] = Quote.objects.order_by('-views_count')[:5]
        
        return context

# Helper function to calculate growth percentage
def calculate_growth(current, previous):
    if previous == 0:
        return 100 if current > 0 else 0
    return ((current - previous) / previous) * 100

# Content Management
class ContentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'dashboard/content_list.html'
    context_object_name = 'content_list'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        Content = apps.get_model('core', 'Content')
        queryset = Content.objects.all().select_related('category', 'author').prefetch_related('tags')
        
        # Apply filters
        q = self.request.GET.get('q')
        content_type = self.request.GET.get('content_type')
        status = self.request.GET.get('status')
        category = self.request.GET.get('category')
        
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | 
                Q(summary__icontains=q) | 
                Q(content__icontains=q)
            )
        
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if category:
            queryset = queryset.filter(category_id=category)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Category = apps.get_model('core', 'Category')
        context['categories'] = Category.objects.all()
        return context

class ContentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'dashboard/content_form.html'
    success_url = reverse_lazy('dashboard:content_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_form_class(self):
        from django import forms
        Content = apps.get_model('core', 'Content')
        
        class ContentForm(forms.ModelForm):
            class Meta:
                model = Content
                fields = ['title', 'summary', 'content', 'category', 'tags', 'content_type',
                          'featured_image', 'spotify_link', 'youtube_link', 'download_link',
                          'status', 'publication_date']
                widgets = {
                    'publication_date': forms.DateTimeInput(attrs={'class': 'datepicker'}),
                }
        
        return ContentForm
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Content created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Category = apps.get_model('core', 'Category')
        Tag = apps.get_model('core', 'Tag')
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        return context

class ContentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'dashboard/content_form.html'
    success_url = reverse_lazy('dashboard:content_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_object(self):
        Content = apps.get_model('core', 'Content')
        return get_object_or_404(Content, pk=self.kwargs['pk'])
    
    def get_form_class(self):
        from django import forms
        Content = apps.get_model('core', 'Content')
        
        class ContentForm(forms.ModelForm):
            class Meta:
                model = Content
                fields = ['title', 'summary', 'content', 'category', 'tags', 'content_type',
                          'featured_image', 'spotify_link', 'youtube_link', 'download_link',
                          'status', 'publication_date']
                widgets = {
                    'publication_date': forms.DateTimeInput(attrs={'class': 'datepicker'}),
                }
        
        return ContentForm
    
    def form_valid(self, form):
        messages.success(self.request, 'Content updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Category = apps.get_model('core', 'Category')
        Tag = apps.get_model('core', 'Tag')
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        SiteSettings = apps.get_model('core', 'SiteSettings')
        
        # Get or create site settings
        site_settings, created = SiteSettings.objects.get_or_create(pk=1)
        context['site_settings'] = site_settings
        
        # Get social links (assuming you have a model for this)
        try:
            SocialLinks = apps.get_model('core', 'SocialLinks')
            social_links, created = SocialLinks.objects.get_or_create(pk=1)
            context['social_links'] = social_links
        except LookupError:
            # If the model doesn't exist, provide empty context
            context['social_links'] = {}
        
        context['maintenance_mode'] = site_settings.maintenance_mode
        context['maintenance_message'] = site_settings.maintenance_message
        
        # Add backup info
        context['last_backup'] = site_settings.last_db_backup
        
        # Get list of available backups
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        context['available_backups'] = []
        
        if os.path.exists(backup_dir):
            for file in os.listdir(backup_dir):
                if file.endswith('.sqlite3'):
                    file_path = os.path.join(backup_dir, file)
                    file_stats = os.stat(file_path)
                    context['available_backups'].append({
                        'name': file,
                        'size': file_stats.st_size // 1024,  # Size in KB
                        'date': datetime.datetime.fromtimestamp(file_stats.st_mtime)
                    })
            
            # Sort backups by date (newest first)
            context['available_backups'].sort(key=lambda x: x['date'], reverse=True)
        
        return context

class ContentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = 'dashboard/content_confirm_delete.html'
    success_url = reverse_lazy('dashboard:content_list')

    def test_func(self):
        return self.request.user.is_staff

    def get_object(self):
        Content = apps.get_model('core', 'Content')
        return get_object_or_404(Content, pk=self.kwargs['pk'])


# Quote Management
class QuoteListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'dashboard/quote_list.html'
    context_object_name = 'quote_list'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        Quote = apps.get_model('core', 'Quote')
        queryset = Quote.objects.all().select_related('category', 'author', 'default_background').prefetch_related('tags')
        
        # Apply filters
        q = self.request.GET.get('q')
        status = self.request.GET.get('status')
        category = self.request.GET.get('category')
        featured = self.request.GET.get('featured')
        
        if q:
            queryset = queryset.filter(Q(quote_text__icontains=q))
        
        if status:
            queryset = queryset.filter(status=status)
        
        if category:
            queryset = queryset.filter(category_id=category)
            
        if featured:
            queryset = queryset.filter(featured=True)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        QuoteCategory = apps.get_model('core', 'QuoteCategory')
        context['quote_categories'] = QuoteCategory.objects.all()
        return context


class QuoteCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'dashboard/quote_form.html'
    success_url = reverse_lazy('dashboard:quote_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_form_class(self):
        from django import forms
        Quote = apps.get_model('core', 'Quote')
        
        class QuoteForm(forms.ModelForm):
            class Meta:
                model = Quote
                fields = ['quote_text', 'category', 'tags', 'default_background',
                          'default_text_position', 'default_font_style', 'default_font_size',
                          'default_font_color', 'custom_x_position', 'custom_y_position',
                          'featured', 'status']

        
        return QuoteForm
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Quote created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        QuoteCategory = apps.get_model('core', 'QuoteCategory')
        Tag = apps.get_model('core', 'Tag')
        BackgroundImage = apps.get_model('core', 'BackgroundImage')
        context['quote_categories'] = QuoteCategory.objects.all()
        context['tags'] = Tag.objects.all()
        context['backgrounds'] = BackgroundImage.objects.filter(is_active=True)
        context['form_title'] = 'Create New Quote'
        context['submit_text'] = 'Create Quote'
        return context


class QuoteUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'dashboard/quote_form.html'
    success_url = reverse_lazy('dashboard:quote_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_object(self):
        Quote = apps.get_model('core', 'Quote')
        return get_object_or_404(Quote, pk=self.kwargs['pk'])
    
    def get_form_class(self):
        from django import forms
        Quote = apps.get_model('core', 'Quote')
        
        class QuoteForm(forms.ModelForm):
            class Meta:
                model = Quote
                fields = ['quote_text', 'category', 'tags', 'default_background',
                          'default_text_position', 'default_font_style', 'default_font_size',
                          'default_font_color', 'custom_x_position', 'custom_y_position',
                          'featured', 'status']
        
        return QuoteForm
    
    def form_valid(self, form):
        messages.success(self.request, 'Quote updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        QuoteCategory = apps.get_model('core', 'QuoteCategory')
        Tag = apps.get_model('core', 'Tag')
        BackgroundImage = apps.get_model('core', 'BackgroundImage')
        context['quote_categories'] = QuoteCategory.objects.all()
        context['tags'] = Tag.objects.all()
        context['backgrounds'] = BackgroundImage.objects.filter(is_active=True)        
        context['form_title'] = 'Edit Quote'
        context['submit_text'] = 'Update Quote'        
        return context


class QuoteDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    success_url = reverse_lazy('dashboard:quote_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_object(self):
        Quote = apps.get_model('core', 'Quote')
        return get_object_or_404(Quote, pk=self.kwargs['pk'])
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Quote deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Category Management
class CategoryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'dashboard/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        Category = apps.get_model('core', 'Category')
        return Category.objects.annotate(content_count=Count('contents')).order_by('name')

@login_required
@user_passes_test(is_staff)
def category_create(request):
    Category = apps.get_model('core', 'Category')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            Category.objects.create(name=name, description=description)
            messages.success(request, 'Category created successfully!')
        else:
            messages.error(request, 'Name is required.')
    
    return redirect('dashboard:category_list')

@login_required
@user_passes_test(is_staff)
def category_update(request, pk):
    Category = apps.get_model('core', 'Category')
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            category.name = name
            category.description = description
            category.save()
            messages.success(request, 'Category updated successfully!')
        else:
            messages.error(request, 'Name is required.')
    
    return redirect('dashboard:category_list')

class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    success_url = reverse_lazy('dashboard:category_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_object(self):
        Category = apps.get_model('core', 'Category')
        return get_object_or_404(Category, pk=self.kwargs['pk'])
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Category deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Tag Management
class TagListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'dashboard/tag_list.html'
    context_object_name = 'tags'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        Tag = apps.get_model('core', 'Tag')
        queryset = Tag.objects.annotate(content_count=Count('contents')).order_by('name')
        
        # Apply search filter
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(name__icontains=q)
        
        return queryset

@login_required
@user_passes_test(is_staff)
def tag_create(request):
    Tag = apps.get_model('core', 'Tag')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        
        if name:
            Tag.objects.create(name=name)
            messages.success(request, 'Tag created successfully!')
        else:
            messages.error(request, 'Name is required.')
    
    return redirect('dashboard:tag_list')

@login_required
@user_passes_test(is_staff)
def tag_update(request, pk):
    Tag = apps.get_model('core', 'Tag')
    tag = get_object_or_404(Tag, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        
        if name:
            tag.name = name
            tag.save()
            messages.success(request, 'Tag updated successfully!')
        else:
            messages.error(request, 'Name is required.')
    
    return redirect('dashboard:tag_list')

class TagDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    success_url = reverse_lazy('dashboard:tag_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_object(self):
        Tag = apps.get_model('core', 'Tag')
        return get_object_or_404(Tag, pk=self.kwargs['pk'])
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Tag deleted successfully!')
        return super().delete(request, *args, **kwargs)

# User Management
class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'dashboard/user_list.html'
    context_object_name = 'users'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')
        
        # Apply filters
        q = self.request.GET.get('q')
        is_staff = self.request.GET.get('is_staff')
        is_active = self.request.GET.get('is_active')
        
        if q:
            queryset = queryset.filter(
                Q(username__icontains=q) | 
                Q(email__icontains=q) | 
                Q(first_name__icontains=q) | 
                Q(last_name__icontains=q)
            )
        
        if is_staff == 'true':
            queryset = queryset.filter(is_staff=True)
        elif is_staff == 'false':
            queryset = queryset.filter(is_staff=False)
        
        if is_active == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active=False)
        
        return queryset

class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'dashboard/user_form.html'
    success_url = reverse_lazy('dashboard:user_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_form_class(self):
        from django import forms
        from django.contrib.auth.forms import UserCreationForm
        
        class CustomUserCreationForm(UserCreationForm):
            class Meta:
                model = User
                fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']
            
            # Only superusers can create superusers
            if self.request.user.is_superuser:
                is_superuser = forms.BooleanField(required=False, initial=False)
                Meta.fields.append('is_superuser')
        
        return CustomUserCreationForm
    
    def form_valid(self, form):
        messages.success(self.request, 'User created successfully!')
        return super().form_valid(form)

class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'dashboard/user_form.html'
    success_url = reverse_lazy('dashboard:user_list')
    
    def test_func(self):
        # Staff can edit other users, but only superusers can edit superusers
        user = self.get_object()
        if user.is_superuser and not self.request.user.is_superuser:
            return False
        return self.request.user.is_staff
    
    def get_object(self):
        return get_object_or_404(User, pk=self.kwargs['pk'])
    
    def get_form_class(self):
        from django import forms
        
        class UserEditForm(forms.ModelForm):
            class Meta:
                model = User
                fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']
            
            # Only superusers can edit superuser status
            if self.request.user.is_superuser:
                is_superuser = forms.BooleanField(required=False)
                Meta.fields.append('is_superuser')
        
        return UserEditForm
    
    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully!')
        return super().form_valid(form)

class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    success_url = reverse_lazy('dashboard:user_list')
    
    def test_func(self):
        # Only superusers can delete superusers
        user = self.get_object()
        if user.is_superuser and not self.request.user.is_superuser:
            return False
        # Users cannot delete themselves
        if user == self.request.user:
            return False
        return self.request.user.is_staff
    
    def get_object(self):
        return get_object_or_404(User, pk=self.kwargs['pk'])
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'User deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Subcategory Management
@login_required
@user_passes_test(is_staff)
def subcategory_create(request):
    Subcategory = apps.get_model('core', 'Subcategory')
    Category = apps.get_model('core', 'Category')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        category_id = request.POST.get('parent_category')
        # is_active = request.POST.get('is_active') == 'on'
        
        if name and category_id:
            category = get_object_or_404(Category, pk=category_id)
            Subcategory.objects.create(
                name=name, 
                description=description, 
                parent_category=category,
                # is_active=is_active
            )
            messages.success(request, 'Subcategory created successfully!')
        else:
            messages.error(request, 'Name and category are required.')
    
    return redirect('dashboard:subcategory_list')

@login_required
@user_passes_test(is_staff)
def subcategory_update(request, pk):
    Subcategory = apps.get_model('core', 'Subcategory')
    Category = apps.get_model('core', 'Category')
    subcategory = get_object_or_404(Subcategory, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        is_active = request.POST.get('is_active') == 'on'
        
        if name and category_id:
            category = get_object_or_404(Category, pk=category_id)
            subcategory.name = name
            subcategory.description = description
            subcategory.category = category
            subcategory.is_active = is_active
            subcategory.save()
            messages.success(request, 'Subcategory updated successfully!')
        else:
            messages.error(request, 'Name and category are required.')
    
    return redirect('dashboard:subcategory_list')

class SubcategoryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'dashboard/subcategory_list.html'
    context_object_name = 'subcategories'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        Subcategory = apps.get_model('core', 'Subcategory')
        return Subcategory.objects.select_related('parent_category').annotate(content_count=Count('contents')).order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Category = apps.get_model('core', 'Category')
        context['categories'] = Category.objects.all()
        return context

class SubcategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'dashboard/subcategory_form.html'
    success_url = reverse_lazy('dashboard:subcategory_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_form_class(self):
        from django import forms
        Subcategory = apps.get_model('core', 'Subcategory')
        
        class SubcategoryForm(forms.ModelForm):
            class Meta:
                model = Subcategory
                fields = ['name', 'description', 'category', 'is_active']
        
        return SubcategoryForm
    
    def form_valid(self, form):
        messages.success(self.request, 'Subcategory created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Category = apps.get_model('core', 'Category')
        context['categories'] = Category.objects.all()
        context['form_title'] = 'Create New Subcategory'
        context['submit_text'] = 'Create Subcategory'
        return context

class SubcategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'dashboard/subcategory_form.html'
    success_url = reverse_lazy('dashboard:subcategory_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_object(self):
        Subcategory = apps.get_model('core', 'Subcategory')
        return get_object_or_404(Subcategory, pk=self.kwargs['pk'])
    
    def get_form_class(self):
        from django import forms
        Subcategory = apps.get_model('core', 'Subcategory')
        
        class SubcategoryForm(forms.ModelForm):
            class Meta:
                model = Subcategory
                fields = ['name', 'description', 'category', 'is_active']
        
        return SubcategoryForm
    
    def form_valid(self, form):
        messages.success(self.request, 'Subcategory updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Category = apps.get_model('core', 'Category')
        context['categories'] = Category.objects.all()
        context['form_title'] = 'Edit Subcategory'
        context['submit_text'] = 'Update Subcategory'
        return context

class SubcategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    success_url = reverse_lazy('dashboard:subcategory_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_object(self):
        Subcategory = apps.get_model('core', 'Subcategory')
        return get_object_or_404(Subcategory, pk=self.kwargs['pk'])
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Subcategory deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Quote Category Management
class QuoteCategoryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'dashboard/quote_category_list.html'
    context_object_name = 'quote_categories'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        QuoteCategory = apps.get_model('core', 'QuoteCategory')
        return QuoteCategory.objects.annotate(quote_count=Count('quotes')).order_by('name')

@login_required
@user_passes_test(is_staff)
def quote_category_create(request):
    QuoteCategory = apps.get_model('core', 'QuoteCategory')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            QuoteCategory.objects.create(name=name, description=description)
            messages.success(request, 'Quote category created successfully!')
        else:
            messages.error(request, 'Name is required.')
    
    return redirect('dashboard:quote_category_list')

@login_required
@user_passes_test(is_staff)
def quote_category_update(request, pk):
    QuoteCategory = apps.get_model('core', 'QuoteCategory')
    quote_category = get_object_or_404(QuoteCategory, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            quote_category.name = name
            quote_category.description = description
            quote_category.save()
            messages.success(request, 'Quote category updated successfully!')
        else:
            messages.error(request, 'Name is required.')
    
    return redirect('dashboard:quote_category_list')

class QuoteCategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    success_url = reverse_lazy('dashboard:quote_category_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_object(self):
        QuoteCategory = apps.get_model('core', 'QuoteCategory')
        return get_object_or_404(QuoteCategory, pk=self.kwargs['pk'])
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Quote category deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Background Image Management
class BackgroundImageListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'dashboard/background_list.html'
    context_object_name = 'backgrounds'
    paginate_by = 12
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        BackgroundImage = apps.get_model('core', 'BackgroundImage')
        queryset = BackgroundImage.objects.all().order_by('-created_at')
        
        # Apply filters
        is_active = self.request.GET.get('is_active')
        
        if is_active == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active=False)
        
        return queryset

class BackgroundImageCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'dashboard/background_form.html'
    success_url = reverse_lazy('dashboard:background_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_form_class(self):
        from django import forms
        BackgroundImage = apps.get_model('core', 'BackgroundImage')
        
        class BackgroundImageForm(forms.ModelForm):
            class Meta:
                model = BackgroundImage
                fields = ['name', 'description', 'image', 'is_active']
                widgets = {
                    'name': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary'}),
                    'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary'}),
                }
                labels = {
                    'name': 'Title',
                    'image': 'Background Image',
                }
                help_texts = {
                    'image': 'Upload an image (1080x1080 px recommended)',
                }
        
        return BackgroundImageForm
    
    def form_valid(self, form):
        messages.success(self.request, 'Background image added successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Add New Background Image'
        context['submit_text'] = 'Add Background'
        return context

class BackgroundImageUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'dashboard/background_form.html'
    success_url = reverse_lazy('dashboard:background_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_object(self):
        BackgroundImage = apps.get_model('core', 'BackgroundImage')
        return get_object_or_404(BackgroundImage, pk=self.kwargs['pk'])
    
    def get_form_class(self):
        from django import forms
        BackgroundImage = apps.get_model('core', 'BackgroundImage')
        
        class BackgroundImageForm(forms.ModelForm):
            class Meta:
                model = BackgroundImage
                fields = ['name', 'description', 'image', 'is_active']
                widgets = {
                    'name': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary'}),
                    'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary'}),
                }
                labels = {
                    'name': 'Title',
                    'image': 'Background Image',
                }
                help_texts = {
                    'image': 'Upload an image (1080x1080 px recommended)',
                }
        
        return BackgroundImageForm
    
    def form_valid(self, form):
        messages.success(self.request, 'Background image updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Edit Background Image'
        context['submit_text'] = 'Update Background'
        return context

class BackgroundImageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    success_url = reverse_lazy('dashboard:background_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_object(self):
        BackgroundImage = apps.get_model('core', 'BackgroundImage')
        return get_object_or_404(BackgroundImage, pk=self.kwargs['pk'])
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Background image deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
@user_passes_test(is_staff)
def background_toggle(request, pk):
    BackgroundImage = apps.get_model('core', 'BackgroundImage')
    background = get_object_or_404(BackgroundImage, pk=pk)
    
    # Toggle active status
    background.is_active = not background.is_active
    background.save()
    
    status = 'activated' if background.is_active else 'deactivated'
    messages.success(request, f'Background image {status} successfully!')
    
    return redirect('dashboard:background_list')

# Settings
class SettingsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/settings.html'
    
    def test_func(self):
        return self.request.user.is_staff
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get site settings from database or use defaults
        from django.conf import settings
        try:
            from digilib.apps.core.models import SiteSettings
            site_settings = SiteSettings.objects.first()
            if not site_settings:
                site_settings = SiteSettings.objects.create(
                    site_title='Apostle Niyi Digital Library',
                    site_description='A digital library of sermons, books, and articles',
                    contact_email='contact@example.com',
                    items_per_page=12
                )
        except:
            # If SiteSettings model doesn't exist yet, use dummy data
            site_settings = {
                'site_title': 'Apostle Niyi Digital Library',
                'site_description': 'A digital library of sermons, books, and articles',
                'contact_email': 'contact@example.com',
                'items_per_page': 12
            }
        
        # Get social links
        try:
            from digilib.apps.core.models import SocialLinks
            social_links = SocialLinks.objects.first()
            if not social_links:
                social_links = SocialLinks.objects.create()
        except:
            # If SocialLinks model doesn't exist yet, use dummy data
            social_links = {
                'facebook': '',
                'twitter': '',
                'instagram': '',
                'youtube': ''
            }
        
        # Get maintenance mode settings
        maintenance_mode = getattr(settings, 'MAINTENANCE_MODE', False)
        maintenance_message = getattr(settings, 'MAINTENANCE_MESSAGE', 'We are currently performing maintenance. Please check back soon.')
        
        context['site_settings'] = site_settings
        context['social_links'] = social_links
        context['maintenance_mode'] = maintenance_mode
        context['maintenance_message'] = maintenance_message
        
        return context

@login_required
@user_passes_test(lambda u: u.is_staff)
def update_site_settings(request):
    if request.method == 'POST':
        SiteSettings = apps.get_model('core', 'SiteSettings')
        site_settings, created = SiteSettings.objects.get_or_create(pk=1)
        
        site_settings.site_title = request.POST.get('site_title')
        site_settings.site_description = request.POST.get('site_description')
        site_settings.contact_email = request.POST.get('contact_email')
        site_settings.items_per_page = int(request.POST.get('items_per_page', 12))
        site_settings.save()
        
        messages.success(request, 'Site settings updated successfully!')
    
    return redirect('dashboard:settings')


@login_required
@user_passes_test(lambda u: u.is_staff)
def update_social_links(request):
    if request.method == 'POST':
        try:
            SocialLinks = apps.get_model('core', 'SocialLinks')
            social_links, created = SocialLinks.objects.get_or_create(pk=1)
            
            social_links.facebook = request.POST.get('facebook', '')
            social_links.twitter = request.POST.get('twitter', '')
            social_links.instagram = request.POST.get('instagram', '')
            social_links.youtube = request.POST.get('youtube', '')
            social_links.save()
            
            messages.success(request, 'Social links updated successfully!')
        except LookupError:
            messages.error(request, 'Social links model not found.')
    
    return redirect('dashboard:settings')


@login_required
@user_passes_test(lambda u: u.is_staff)
def toggle_maintenance_mode(request):
    if request.method == 'POST':
        SiteSettings = apps.get_model('core', 'SiteSettings')
        site_settings, created = SiteSettings.objects.get_or_create(pk=1)
        
        # Toggle maintenance mode
        site_settings.maintenance_mode = not site_settings.maintenance_mode
        
        # Update maintenance message if provided
        if 'maintenance_message' in request.POST:
            site_settings.maintenance_message = request.POST.get('maintenance_message')
        
        site_settings.save()
        
        status = 'enabled' if site_settings.maintenance_mode else 'disabled'
        messages.success(request, f'Maintenance mode {status} successfully!')
    
    return redirect('dashboard:settings')


@login_required
@user_passes_test(lambda u: u.is_staff)
def export_database(request):
    """Export the SQLite database as a backup file"""
    try:
        # Create backups directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'digilib_backup_{timestamp}.sqlite3'
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Get the path to the SQLite database file
        db_path = settings.DATABASES['default']['NAME']
        
        # Create a copy of the database
        with open(db_path, 'rb') as src_db:
            with open(backup_path, 'wb') as dst_db:
                dst_db.write(src_db.read())
        
        # Update last backup time
        SiteSettings = apps.get_model('core', 'SiteSettings')
        site_settings, created = SiteSettings.objects.get_or_create(pk=1)
        site_settings.last_db_backup = timezone.now()
        site_settings.save()
        
        # Serve the file for download
        response = FileResponse(open(backup_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{backup_filename}"'
        
        messages.success(request, 'Database exported successfully!')
        return response
    
    except Exception as e:
        messages.error(request, f'Error exporting database: {str(e)}')
        return redirect('dashboard:settings')


@login_required
@user_passes_test(lambda u: u.is_staff)
def import_database(request):
    """Import a SQLite database from a backup file"""
    if request.method == 'POST' and request.FILES.get('database_file'):
        try:
            uploaded_file = request.FILES['database_file']
            
            # Validate file extension
            if not uploaded_file.name.endswith('.sqlite3'):
                messages.error(request, 'Invalid file format. Please upload a .sqlite3 file.')
                return redirect('dashboard:settings')
            
            # Create backups directory if it doesn't exist
            backup_dir = os.path.join(settings.BASE_DIR, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            # Save the uploaded file
            fs = FileSystemStorage(location=backup_dir)
            filename = fs.save(uploaded_file.name, uploaded_file)
            uploaded_file_path = os.path.join(backup_dir, filename)
            
            # Validate that this is a valid SQLite database
            try:
                conn = sqlite3.connect(uploaded_file_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                conn.close()
                
                if not tables:
                    messages.error(request, 'The uploaded file is not a valid SQLite database.')
                    os.remove(uploaded_file_path)  # Remove invalid file
                    return redirect('dashboard:settings')
            except sqlite3.Error:
                messages.error(request, 'The uploaded file is not a valid SQLite database.')
                os.remove(uploaded_file_path)  # Remove invalid file
                return redirect('dashboard:settings')
            
            # Get the path to the current SQLite database file
            db_path = settings.DATABASES['default']['NAME']
            
            # Create a backup of the current database before replacing
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            current_backup_filename = f'digilib_before_import_{timestamp}.sqlite3'
            current_backup_path = os.path.join(backup_dir, current_backup_filename)
                    
            # Replace the current database with the uploaded one
            with open(uploaded_file_path, 'rb') as src_db:
                with open(db_path, 'wb') as dst_db:
                    dst_db.write(src_db.read())
            
            messages.success(request, 'Database imported successfully! The application will restart to apply changes.')
            
            # In a production environment, you might want to trigger an application restart here
            # This is a simplified example - in production you'd use a more robust approach
            # subprocess.Popen(['touch', settings.BASE_DIR + '/tmp/restart.txt'])
            
            return redirect('dashboard:settings')
        
        except Exception as e:
            messages.error(request, f'Error importing database: {str(e)}')
    
    return redirect('dashboard:settings')


@login_required
@user_passes_test(lambda u: u.is_staff)
def restore_database_backup(request, filename):
    """Restore the database from a specific backup file"""
    try:
        # Validate filename to prevent directory traversal
        if '..' in filename or '/' in filename:
            messages.error(request, 'Invalid backup filename.')
            return redirect('dashboard:settings')
        
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        backup_path = os.path.join(backup_dir, filename)
        
        # Check if the backup file exists
        if not os.path.exists(backup_path):
            messages.error(request, 'Backup file not found.')
            return redirect('dashboard:settings')
        
        # Get the path to the current SQLite database file
        db_path = settings.DATABASES['default']['NAME']
        
        # Create a backup of the current database before restoring
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        current_backup_filename = f'digilib_before_restore_{timestamp}.sqlite3'
        current_backup_path = os.path.join(backup_dir, current_backup_filename)
        
        with open(db_path, 'rb') as src_db:
            with open(current_backup_path, 'wb') as dst_db:
                dst_db.write(src_db.read())
        
        # Replace the current database with the selected backup
        with open(backup_path, 'rb') as src_db:
            with open(db_path, 'wb') as dst_db:
                dst_db.write(src_db.read())
        
        messages.success(request, f'Database restored from backup {filename} successfully!')
        
        # In a production environment, you might want to trigger an application restart here
        # subprocess.Popen(['touch', settings.BASE_DIR + '/tmp/restart.txt'])
        
    except Exception as e:
        messages.error(request, f'Error restoring database: {str(e)}')
    
    return redirect('dashboard:settings')


@login_required
@user_passes_test(is_staff)
def get_subcategories(request, category_id):
    from django.http import JsonResponse
    Subcategory = apps.get_model('core', 'Subcategory')
    
    subcategories = Subcategory.objects.filter(category_id=category_id, is_active=True).values('id', 'name')
    return JsonResponse(list(subcategories), safe=False)


class ExportTemplateView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'dashboard/export_template.html'
    form_class = ExportTemplateForm
    success_url = reverse_lazy('dashboard:export_template')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        model_name = form.cleaned_data['model']
        model = apps.get_model('core', model_name)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{model_name}_template.csv"'

        writer = csv.writer(response)
        headers = [field.name for field in model._meta.fields]
        writer.writerow(headers)

        return response




class ImportTemplateView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'dashboard/import_template.html'
    form_class = ImportTemplateForm
    success_url = reverse_lazy('dashboard:import_template')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        model_name = form.cleaned_data['model']
        csv_file = form.cleaned_data['csv_file']
        model = apps.get_model('core', model_name)

        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        for row in reader:
            # Convert user ID to User instance
            if 'author' in row:
                try:
                    user_id = int(row['author'])
                    row['author'] = User.objects.get(id=user_id)
                except (ValueError, User.DoesNotExist):
                    messages.error(self.request, f"Invalid user ID: {row['author']}")
                    continue

            # Convert quote category ID to QuoteCategory instance
            if 'category' in row:
                try:
                    category_id = int(row['category'])
                    row['category'] = QuoteCategory.objects.get(id=category_id)
                except (ValueError, QuoteCategory.DoesNotExist):
                    messages.error(self.request, f"Invalid quote category ID: {row['category']}")
                    continue

            # Convert default background ID to BackgroundImage instance
            if 'default_background' in row:
                try:
                    background_id = int(row['default_background'])
                    row['default_background'] = BackgroundImage.objects.get(id=background_id)
                except (ValueError, BackgroundImage.DoesNotExist):
                    messages.error(self.request, f"Invalid default background ID: {row['default_background']}")
                    continue

            # Handle null values for custom_x_position and custom_y_position
            if 'custom_x_position' in row and row['custom_x_position'] == '':
                row['custom_x_position'] = None
            if 'custom_y_position' in row and row['custom_y_position'] == '':
                row['custom_y_position'] = None

            # Create or update the model instance
            instance, created = model.objects.update_or_create(
                id=row.get('id'),  # Assuming 'id' is the primary key
                defaults=row
            )

        messages.success(self.request, f'{model_name} data imported successfully!')
        return super().form_valid(form)