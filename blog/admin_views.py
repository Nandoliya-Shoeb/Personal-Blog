"""
Custom Django Admin Dashboard Views
====================================
Modern, professional admin dashboard for blog management system.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db.models import Count, Q
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import Post, Category, Comment
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
import json


def admin_required(view_func):
    """
    Decorator to check if user is admin/staff.
    Non-authenticated or non-staff users are redirected to unified login.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('accounts:login')  # Use unified login
        return view_func(request, *args, **kwargs)
    return wrapper


# ============================================================================
# DASHBOARD - HOME PAGE
# ============================================================================

@admin_required
def admin_dashboard(request):
    """Main dashboard with statistics"""
    
    # Get statistics
    total_posts = Post.objects.count()
    published_posts = Post.objects.filter(is_published=True).count()
    draft_posts = Post.objects.filter(is_published=False).count()
    
    total_categories = Category.objects.count()
    total_comments = Comment.objects.count()
    approved_comments = Comment.objects.filter(is_approved=True).count()
    
    total_users = User.objects.count()
    total_views = Post.objects.aggregate(total=__import__('django.db.models', fromlist=['Sum']).Sum('views_count'))['total'] or 0
    
    # Recent posts
    recent_posts = Post.objects.select_related('author', 'category').order_by('-created_at')[:5]
    
    # Recent comments
    recent_comments = Comment.objects.select_related('author', 'post').order_by('-created_at')[:5]
    
    # Top categories
    top_categories = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:5]
    
    # Data for chart
    chart_data = {
        'published': published_posts,
        'draft': draft_posts,
        'total': total_posts,
    }
    
    context = {
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'total_categories': total_categories,
        'total_comments': total_comments,
        'approved_comments': approved_comments,
        'pending_comments': total_comments - approved_comments,
        'total_users': total_users,
        'total_views': total_views,
        'recent_posts': recent_posts,
        'recent_comments': recent_comments,
        'top_categories': top_categories,
        'chart_data': json.dumps(chart_data),
        'page': 'dashboard',
    }
    
    return render(request, 'admin_dashboard/dashboard.html', context)


# ============================================================================
# POSTS MANAGEMENT
# ============================================================================

@admin_required
def admin_posts(request):
    """Posts management page"""
    
    # Get all posts
    posts = Post.objects.select_related('author', 'category').order_by('-created_at')
    
    # Search
    search = request.GET.get('search', '')
    if search:
        posts = posts.filter(
            Q(title__icontains=search) | Q(content__icontains=search)
        )
    
    # Filter by status
    status = request.GET.get('status', '')
    if status == 'published':
        posts = posts.filter(is_published=True)
    elif status == 'draft':
        posts = posts.filter(is_published=False)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(posts, 10)
    page = request.GET.get('page', 1)
    posts = paginator.get_page(page)
    
    context = {
        'posts': posts,
        'search': search,
        'status': status,
        'page': 'posts',
    }
    
    return render(request, 'admin_dashboard/posts.html', context)


@admin_required
def admin_post_edit(request, post_id):
    """Edit post"""
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        post.title = request.POST.get('title', post.title)
        post.content = request.POST.get('content', post.content)
        post.is_published = request.POST.get('is_published') == 'on'
        
        category_id = request.POST.get('category')
        if category_id:
            post.category_id = category_id
        
        post.save()
        messages.success(request, f'Post "{post.title}" updated successfully!')
        return redirect('admin_posts')
    
    categories = Category.objects.all()
    context = {
        'post': post,
        'categories': categories,
        'page': 'posts',
    }
    
    return render(request, 'admin_dashboard/post_edit.html', context)


@admin_required
@require_http_methods(['POST'])
def admin_post_delete(request, post_id):
    """Delete post"""
    post = get_object_or_404(Post, id=post_id)
    title = post.title
    post.delete()
    messages.success(request, f'Post "{title}" deleted successfully!')
    return redirect('admin_posts')


@admin_required
@require_http_methods(['POST'])
def admin_post_publish(request, post_id):
    """Publish/unpublish post"""
    post = get_object_or_404(Post, id=post_id)
    action = request.POST.get('action')
    
    if action == 'publish':
        post.is_published = True
        messages.success(request, f'Post "{post.title}" published!')
    elif action == 'draft':
        post.is_published = False
        messages.success(request, f'Post "{post.title}" moved to draft!')
    
    post.save()
    return redirect('admin_posts')


# ============================================================================
# CATEGORIES MANAGEMENT
# ============================================================================

@admin_required
def admin_categories(request):
    """Categories management page"""
    categories = Category.objects.annotate(
        post_count=Count('posts')
    ).order_by('-post_count')
    
    context = {
        'categories': categories,
        'page': 'categories',
    }
    
    return render(request, 'admin_dashboard/categories.html', context)


@admin_required
def admin_category_add(request):
    """Add new category"""
    if request.method == 'POST':
        from .models import Category
        from django.utils.text import slugify
        
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        category = Category.objects.create(
            name=name,
            slug=slugify(name),
            description=description
        )
        
        messages.success(request, f'Category "{name}" created successfully!')
        return redirect('admin_categories')
    
    return render(request, 'admin_dashboard/category_add.html', {'page': 'categories'})


@admin_required
def admin_category_edit(request, category_id):
    """Edit category"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category.name = request.POST.get('name', category.name)
        category.description = request.POST.get('description', category.description)
        category.save()
        
        messages.success(request, f'Category "{category.name}" updated!')
        return redirect('admin_categories')
    
    context = {
        'category': category,
        'page': 'categories',
    }
    
    return render(request, 'admin_dashboard/category_edit.html', context)


@admin_required
@require_http_methods(['POST'])
def admin_category_delete(request, category_id):
    """Delete category"""
    category = get_object_or_404(Category, id=category_id)
    name = category.name
    category.delete()
    messages.success(request, f'Category "{name}" deleted!')
    return redirect('admin_categories')


# ============================================================================
# COMMENTS MODERATION
# ============================================================================

@admin_required
def admin_comments(request):
    """Comments moderation page"""
    comments = Comment.objects.select_related('author', 'post').order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status', '')
    if status == 'approved':
        comments = comments.filter(is_approved=True)
    elif status == 'pending':
        comments = comments.filter(is_approved=False)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(comments, 10)
    page = request.GET.get('page', 1)
    comments = paginator.get_page(page)
    
    context = {
        'comments': comments,
        'status': status,
        'page': 'comments',
    }
    
    return render(request, 'admin_dashboard/comments.html', context)


@admin_required
@require_http_methods(['POST'])
def admin_comment_approve(request, comment_id):
    """Approve comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    comment.is_approved = True
    comment.save()
    messages.success(request, 'Comment approved!')
    return redirect('admin_comments')


@admin_required
@require_http_methods(['POST'])
def admin_comment_reject(request, comment_id):
    """Reject comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    comment.is_approved = False
    comment.save()
    messages.success(request, 'Comment rejected!')
    return redirect('admin_comments')


@admin_required
@require_http_methods(['POST'])
def admin_comment_delete(request, comment_id):
    """Delete comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    messages.success(request, 'Comment deleted!')
    return redirect('admin_comments')


# ============================================================================
# USERS MANAGEMENT
# ============================================================================

@admin_required
def admin_users(request):
    """Users management page"""
    users = User.objects.annotate(
        post_count=Count('blog_posts'),
        comment_count=Count('blog_comments')
    ).order_by('-date_joined')
    
    context = {
        'users': users,
        'page': 'users',
    }
    
    return render(request, 'admin_dashboard/users.html', context)


@admin_required
def admin_user_edit(request, user_id):
    """Edit user"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_active = request.POST.get('is_active') == 'on'
        user.save()
        
        messages.success(request, f'User "{user.username}" updated!')
        return redirect('admin_users')
    
    post_count = user.blog_posts.count()
    comment_count = user.blog_comments.count()
    
    context = {
        'edit_user': user,
        'post_count': post_count,
        'comment_count': comment_count,
        'page': 'users',
    }
    
    return render(request, 'admin_dashboard/user_edit.html', context)


# ============================================================================
# ANALYTICS
# ============================================================================

@admin_required
def admin_analytics(request):
    """Analytics page with charts"""
    
    # Category distribution
    category_data = Category.objects.annotate(
        post_count=Count('posts')
    ).order_by('-post_count')[:5]
    
    category_labels = [c.name for c in category_data]
    category_counts = [c.post_count for c in category_data]
    
    # Posts per month (last 6 months)
    now = timezone.now()
    posts_by_month = []
    labels_month = []
    
    for i in range(6, -1, -1):
        date = now - timedelta(days=30*i)
        count = Post.objects.filter(
            created_at__year=date.year,
            created_at__month=date.month
        ).count()
        posts_by_month.append(count)
        labels_month.append(date.strftime('%b'))
    
    # Comments per month
    comments_by_month = []
    for i in range(6, -1, -1):
        date = now - timedelta(days=30*i)
        count = Comment.objects.filter(
            created_at__year=date.year,
            created_at__month=date.month
        ).count()
        comments_by_month.append(count)
    
    # Top authors
    top_authors = User.objects.annotate(
        post_count=Count('blog_posts')
    ).filter(post_count__gt=0).order_by('-post_count')[:5]
    
    context = {
        'category_labels': json.dumps(category_labels),
        'category_counts': json.dumps(category_counts),
        'posts_by_month': json.dumps(posts_by_month),
        'comments_by_month': json.dumps(comments_by_month),
        'labels_month': json.dumps(labels_month),
        'top_authors': top_authors,
        'page': 'analytics',
    }
    
    return render(request, 'admin_dashboard/analytics.html', context)
