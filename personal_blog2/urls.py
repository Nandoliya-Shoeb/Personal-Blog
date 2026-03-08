"""
URL configuration for personal_blog2 project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as account_views

urlpatterns = [
    # Admin dashboard routes
    path('', include('blog.admin_urls')),

    # Accounts routes (login, register, profile, logout, change password)
    path('accounts/', include('accounts.urls')),

    # Blog routes (posts, comments, categories)
    path('blog/', include('blog.urls')),

    # Django Allauth routes (Google OAuth, social login)
    path('auth/', include('allauth.urls')),

    # Root redirect - login if not authenticated
    path('', account_views.login_view, name='home'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
