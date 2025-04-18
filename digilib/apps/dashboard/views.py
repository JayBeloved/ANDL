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

User = get_user_model()

# Helper function to check if user is staff
def is_staff(user):
    return user.is_staff

# Dashboard Home
class DashboardHomeView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/index.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Content = apps.get_model('core', 'Content')
        
        # Get counts
        context['content_count'] = Content.objects.count()
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
        return context

class ContentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    success_url = reverse_lazy('dashboard:content_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_object(self):
        Content = apps.get_model('core', 'Content')
        return get_object_or_404(Content, pk=self.kwargs['pk'])
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Content deleted successfully!')
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
@user_passes_test(is_staff)
def update_site_settings(request):
    if request.method == 'POST':
        try:
            from digilib.apps.core.models import SiteSettings
            site_settings = SiteSettings.objects.first()
            if not site_settings:
                site_settings = SiteSettings()
            
            site_settings.site_title = request.POST.get('site_title')
            site_settings.site_description = request.POST.get('site_description')
            site_settings.contact_email = request.POST.get('contact_email')
            site_settings.items_per_page = int(request.POST.get('items_per_page', 12))
            site_settings.save()
            
            messages.success(request, 'Site settings updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating site settings: {str(e)}')
    
    return redirect('dashboard:settings')

@login_required
@user_passes_test(is_staff)
def update_social_links(request):
    if request.method == 'POST':
        try:
            from digilib.apps.core.models import SocialLinks
            social_links = SocialLinks.objects.first()
            if not social_links:
                social_links = SocialLinks()
            
            social_links.facebook = request.POST.get('facebook', '')
            social_links.twitter = request.POST.get('twitter', '')
            social_links.instagram = request.POST.get('instagram', '')
            social_links.youtube = request.POST.get('youtube', '')
            social_links.save()
            
            messages.success(request, 'Social links updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating social links: {str(e)}')
    
    return redirect('dashboard:settings')

@login_required
@user_passes_test(is_staff)
def toggle_maintenance_mode(request):
    if request.method == 'POST':
        try:
            from django.conf import settings
            
            # Toggle maintenance mode
            current_mode = getattr(settings, 'MAINTENANCE_MODE', False)
            new_mode = not current_mode
            
            # Update maintenance message
            maintenance_message = request.POST.get('maintenance_message', 'We are currently performing maintenance. Please check back soon.')
            
            # In a real application, you would update these settings in a database or settings file
            # For this example, we'll just show a success message
            
            messages.success(request, f'Maintenance mode has been {"enabled" if new_mode else "disabled"}.')
        except Exception as e:
            messages.error(request, f'Error updating maintenance mode: {str(e)}')
    
    return redirect('dashboard:settings')