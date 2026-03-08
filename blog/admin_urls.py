"""
Django URL Configuration for Custom Admin Dashboard
Note: Login is handled by unified accounts:login view
"""

from django.urls import path
from . import admin_views

urlpatterns = [
    # Dashboard (login handled by unified accounts:login)
    path('admin/', admin_views.admin_dashboard, name='admin_dashboard'),
    
    # Posts
    path('admin/posts/', admin_views.admin_posts, name='admin_posts'),
    path('admin/posts/<int:post_id>/edit/', admin_views.admin_post_edit, name='admin_post_edit'),
    path('admin/posts/<int:post_id>/delete/', admin_views.admin_post_delete, name='admin_post_delete'),
    path('admin/posts/<int:post_id>/publish/', admin_views.admin_post_publish, name='admin_post_publish'),
    
    # Categories
    path('admin/categories/', admin_views.admin_categories, name='admin_categories'),
    path('admin/categories/add/', admin_views.admin_category_add, name='admin_category_add'),
    path('admin/categories/<int:category_id>/edit/', admin_views.admin_category_edit, name='admin_category_edit'),
    path('admin/categories/<int:category_id>/delete/', admin_views.admin_category_delete, name='admin_category_delete'),
    
    # Comments
    path('admin/comments/', admin_views.admin_comments, name='admin_comments'),
    path('admin/comments/<int:comment_id>/approve/', admin_views.admin_comment_approve, name='admin_comment_approve'),
    path('admin/comments/<int:comment_id>/reject/', admin_views.admin_comment_reject, name='admin_comment_reject'),
    path('admin/comments/<int:comment_id>/delete/', admin_views.admin_comment_delete, name='admin_comment_delete'),
    
    # Users
    path('admin/users/', admin_views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/edit/', admin_views.admin_user_edit, name='admin_user_edit'),
    
    # Analytics
    path('admin/analytics/', admin_views.admin_analytics, name='admin_analytics'),
]
