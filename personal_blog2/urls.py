"""
URL configuration for personal_blog2 project.
"""
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as account_views
from django.views.generic import RedirectView
from django.shortcuts import render

# Custom 404 handler
def custom_404(request, exception=None):
    return render(request, '404.html', status=404)

handler404 = custom_404

urlpatterns = [
    # Admin dashboard routes
    path('', include('blog.admin_urls')),

    # Dashboard redirect (redirects to login)
    path('dashboard/', RedirectView.as_view(pattern_name='accounts:login', permanent=False)),
    path('dashboard', RedirectView.as_view(pattern_name='accounts:login', permanent=False)),

    # Accounts routes (login, register, profile, logout, change password)
    path('accounts/', include('accounts.urls')),

    # Blog routes (posts, comments, categories)
    path('blog/', include('blog.urls')),

    # Django Allauth routes (Google OAuth, social login)
    path('auth/', include('allauth.urls')),

    # Root redirect - login if not authenticated
    path('', account_views.login_view, name='home'),

    # Catch-all: any unknown URL → custom 404 page (works even with DEBUG=True)
    re_path(r'^.*$', custom_404),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
