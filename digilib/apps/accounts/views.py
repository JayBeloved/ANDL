from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib import messages
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView
from .forms import CustomAuthenticationForm, AdminProfileForm
from digilib.apps.core.models import Content, Category, Tag

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().get_full_name() or form.get_user().username}!')
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    next_page = 'core:home'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'accounts/dashboard.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Content statistics
        context['total_content'] = Content.objects.count()
        context['published_content'] = Content.objects.filter(status='PUBLISHED').count()
        context['draft_content'] = Content.objects.filter(status='DRAFT').count()
        
        # Content by type
        context['content_by_type'] = Content.objects.values('content_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Most viewed content
        context['most_viewed'] = Content.objects.filter(
            status='PUBLISHED'
        ).order_by('-views_count')[:5]
        
        # Most downloaded content
        context['most_downloaded'] = Content.objects.filter(
            status='PUBLISHED'
        ).order_by('-downloads_count')[:5]
        
        # Category statistics
        context['categories'] = Category.objects.annotate(
            content_count=Count('contents')
        ).order_by('-content_count')
        
        # Recent content
        context['recent_content'] = Content.objects.order_by('-created_at')[:5]
        
        return context

class AdminProfileView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'accounts/profile.html'
    form_class = AdminProfileForm
    success_url = reverse_lazy('accounts:profile')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated successfully.')
        return super().form_valid(form)

class AdminPasswordChangeView(LoginRequiredMixin, UserPassesTestMixin, PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:dashboard')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been changed successfully.')
        return super().form_valid(form)