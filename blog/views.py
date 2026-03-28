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


# ============================================
# --- NEW SEO FEATURE ---
# ============================================

import json                                   # For parsing the JSON that Gemini returns
from google import genai                      # Official Google Gemini SDK (google-genai)
from django.conf import settings              # To securely read GEMINI_API_KEY
from django.http import JsonResponse          # To send JSON back to the browser
from django.views.decorators.http import require_POST  # Only allow POST requests


@login_required(login_url='accounts:login')   # Must be logged in to use this feature
@require_POST                                  # Must be a POST request (not a GET/browser visit)
def get_seo_suggestions(request, post_id):
    """
    Sends the post's title and content to Google Gemini AI and returns
    3 SEO title suggestions and 10 SEO tag suggestions as JSON.
    """
    try:
        # --- Fetch the post from the database ---
        # If post_id doesn't match any Post, return a clean error instead of crashing
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Post not found. Please check the post ID.'})

        # --- Configure the Gemini client with our API key from settings ---
        # The key is read from the .env file via settings.py — never hardcoded here
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        print("USING KEY:", settings.GEMINI_API_KEY[:10])

        # --- Build the prompt ---
        # We instruct Gemini to return ONLY JSON (no explanation, no markdown around it)
        prompt = f"""You are an SEO expert. Analyze the following blog post and return ONLY a valid JSON object with no extra text, no markdown fences, and no explanation.

Blog Post Title: {post.title}

Blog Post Content:
{post.content[:3000]}

Return this exact JSON structure:
{{
  "seo_titles": ["title1", "title2", "title3"],
  "seo_tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10"]
}}

Rules:
- seo_titles: exactly 3 compelling, keyword-rich titles (under 60 chars each)
- seo_tags: exactly 10 short, relevant SEO tags (1-3 words each)
- Output ONLY the JSON object, nothing else"""

        # --- Call Gemini API and get the response ---
        # gemini-2.5-flash is fully supported free-tier for your new API key
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        response_text = response.text.strip()

        # --- Strip markdown code fences if Gemini wrapped the JSON in them ---
        # Gemini sometimes returns ```json ... ``` even when told not to
        if response_text.startswith('```'):
            # Remove the opening fence (e.g. ```json or ```)
            response_text = response_text.split('\n', 1)[-1]
        if response_text.endswith('```'):
            # Remove the closing fence
            response_text = response_text.rsplit('```', 1)[0]
        response_text = response_text.strip()

        # --- Parse the cleaned JSON string into a Python dict ---
        data = json.loads(response_text)

        seo_titles = data.get('seo_titles', [])
        seo_tags   = data.get('seo_tags', [])

        # --- Save the first suggested title and tags back to the post ---
        # This lets us display them later without calling Gemini again
        if seo_titles:
            post.seo_title = seo_titles[0]
        if seo_tags:
            post.seo_tags = ', '.join(seo_tags)
        post.save(update_fields=['seo_title', 'seo_tags'])

        # --- Return success response to the browser ---
        return JsonResponse({
            'success': True,
            'seo_titles': seo_titles,
            'seo_tags': seo_tags,
        })

    except json.JSONDecodeError:
        # Gemini returned something that wasn't valid JSON
        return JsonResponse({'success': False, 'error': 'Gemini returned an unexpected format. Please try again.'})
    except Exception as e:
        # Catch-all: API key missing, network error, quota exceeded, etc.
        return JsonResponse({'success': False, 'error': f'Error contacting Gemini AI: {str(e)}'})

# --- END NEW SEO FEATURE ---
