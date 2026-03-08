from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, PostSearchForm


# ============================================
# POST VIEWS
# ============================================

def post_list(request):
    """View all blog posts with pagination"""
    posts = Post.objects.filter(is_published=True).prefetch_related('author', 'category')
    categories = Category.objects.all()
    
    # Search functionality
    search_form = PostSearchForm(request.GET)
    query = request.GET.get('q', '').strip()
    
    if query:
        # Search in title and content
        posts = posts.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(posts, 6)  # 6 posts per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'posts': page_obj.object_list,
        'categories': categories,
        'search_form': search_form,
        'query': query,
        'total_posts': paginator.count,
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    """View single blog post with comments"""
    post = get_object_or_404(Post, slug=slug, is_published=True)
    
    # Increment view count
    post.views_count += 1
    post.save(update_fields=['views_count'])
    
    # Get approved comments
    comments = post.comments.filter(is_approved=True)
    comment_form = CommentForm()
    
    # Prepare context
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'can_edit': request.user == post.author,
        'can_delete': request.user == post.author or request.user.is_staff,
    }
    return render(request, 'blog/post_detail.html', context)


def category_posts(request, slug):
    """View posts from specific category"""
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(
        category=category,
        is_published=True
    ).prefetch_related('author')
    
    # Pagination
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'posts': page_obj.object_list,
        'total_posts': paginator.count,
    }
    return render(request, 'blog/category_posts.html', context)


@login_required(login_url='accounts:login')
def create_post(request):
    """Create new blog post"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('blog:post_detail', slug=post.slug)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = PostForm()
    
    context = {'form': form, 'title': 'Create New Post'}
    return render(request, 'blog/post_form.html', context)


@login_required(login_url='accounts:login')
def edit_post(request, slug):
    """Edit existing blog post"""
    post = get_object_or_404(Post, slug=slug)
    
    # Check if user is author or staff
    if request.user != post.author and not request.user.is_staff:
        messages.error(request, 'You cannot edit this post.')
        return redirect('blog:post_detail', slug=slug)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('blog:post_detail', slug=post.slug)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = PostForm(instance=post)
    
    context = {'form': form, 'post': post, 'title': 'Edit Post'}
    return render(request, 'blog/post_form.html', context)


@login_required(login_url='accounts:login')
def delete_post(request, slug):
    """Delete blog post"""
    post = get_object_or_404(Post, slug=slug)
    
    # Check if user is author or staff
    if request.user != post.author and not request.user.is_staff:
        messages.error(request, 'You cannot delete this post.')
        return redirect('blog:post_detail', slug=slug)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('blog:post_list')
    
    context = {'post': post}
    return render(request, 'blog/post_confirm_delete.html', context)


# ============================================
# COMMENT VIEWS
# ============================================

@login_required(login_url='accounts:login')
def add_comment(request, slug):
    """Add comment to a blog post"""
    post = get_object_or_404(Post, slug=slug)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('blog:post_detail', slug=post.slug)
        else:
            for error in form.errors.get('content', []):
                messages.error(request, error)
            return redirect('blog:post_detail', slug=post.slug)
    
    return redirect('blog:post_detail', slug=post.slug)


@login_required(login_url='accounts:login')
def delete_comment(request, comment_id):
    """Delete a comment (author or admin only)"""
    comment = get_object_or_404(Comment, id=comment_id)
    post_slug = comment.post.slug
    
    # Check if user is author or staff
    if request.user != comment.author and not request.user.is_staff:
        messages.error(request, 'You cannot delete this comment.')
        return redirect('blog:post_detail', slug=post_slug)
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
        return redirect('blog:post_detail', slug=post_slug)
    
    context = {'comment': comment}
    return render(request, 'blog/comment_confirm_delete.html', context)


# ============================================
# DASHBOARD VIEW (For user's posts)
# ============================================

@login_required(login_url='accounts:login')
def my_posts(request):
    """View user's own blog posts"""
    posts = Post.objects.filter(author=request.user).prefetch_related('category')
    
    # Pagination
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'posts': page_obj.object_list,
        'total_posts': paginator.count,
    }
    return render(request, 'blog/my_posts.html', context)
