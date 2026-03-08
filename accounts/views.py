from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, CustomPasswordChangeForm, UserProfileForm, ProfileForm


# Register View - Create new user account
def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('accounts:login')
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegisterForm()
    
    context = {'form': form}
    return render(request, 'register.html', context)


# Login View - Unified authentication for both admin and normal users
def login_view(request):
    """
    Unified login view for all users.
    - Admin/Staff users are redirected to admin dashboard
    - Normal users are redirected to blog dashboard
    """
    # If already logged in, redirect to appropriate location
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')  # Send admin to dashboard
        else:
            return redirect('accounts:profile')  # Send normal users to profile
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Authenticate user
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Log the user in
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                
                # ROLE-BASED REDIRECT
                if user.is_staff:
                    # Send admin/staff to admin dashboard
                    return redirect('admin_dashboard')
                else:
                    # Send normal users to their profile
                    return redirect('accounts:profile')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    context = {'form': form}
    return render(request, 'login.html', context)


# Logout View
def logout_view(request):
    """User logout view"""
    if request.user.is_authenticated:
        messages.success(request, 'You have been logged out successfully.')
        logout(request)
    return redirect('accounts:login')


# Profile View - Display user profile (requires login)
@login_required(login_url='accounts:login')
def profile(request):
    """User profile view"""
    from .models import Profile
    profile_obj, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid() and p_form.is_valid():
            form.save()
            p_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
        p_form = ProfileForm(instance=profile_obj)
    
    context = {
        'form': form,
        'p_form': p_form,
        'user': request.user
    }
    return render(request, 'profile.html', context)


# Change Password View (requires login)
@login_required(login_url='accounts:login')
def change_password(request):
    """Change password view"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update session to prevent logout after password change
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('accounts:profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    context = {'form': form}
    return render(request, 'change_password.html', context)
