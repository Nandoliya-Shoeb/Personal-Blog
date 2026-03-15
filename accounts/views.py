from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, CustomPasswordChangeForm, UserProfileForm, ProfileForm
import random
# Register View - Create new user account
def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Generate 4-digit OTP
            otp = str(random.randint(1000, 9999))
            
            # Store user data in session INSTEAD of database
            request.session['registration_data'] = {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'password': user.password, # This is already hashed by the form
            }
            request.session['registration_otp'] = otp

            mail_subject = 'Your OTP for Blog Registration'
            message = render_to_string('acc_active_email.html', {
                'username': user.username,
                'otp': otp,
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send() # Email is sent here
            messages.success(request, 'Successfully registered! Please check your email inbox for the OTP to verify your account.')
            return redirect('accounts:verify_otp')
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


# Activate account via email verification link
def activate(request, uidb64, token):
    """Activates the user account when verification link is clicked"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Thank you for your email confirmation. Your account is now active, please login.')
    else:
        messages.error(request, 'Activation link is invalid or has expired!')
        
    return redirect('accounts:login')

def verify_otp(request):
    """Verifies the OTP sent to user's email during registration.
    Blocks direct URL access - only accessible after registration."""
    # BLOCK: Redirect to register if there is no active registration session
    if 'registration_data' not in request.session or 'registration_otp' not in request.session:
        messages.error(request, 'No active registration session found. Please register again.')
        return redirect('accounts:register')
        
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        session_otp = request.session.get('registration_otp')
        registration_data = request.session.get('registration_data')
        
        if otp_entered == session_otp and registration_data:
            # Before saving, verify nothing was somehow created in DB with same details
            if User.objects.filter(username=registration_data['username']).exists() or \
               User.objects.filter(email=registration_data['email']).exists():
                messages.error(request, 'An account with this username or email already exists.')
                return redirect('accounts:register')
                
            # Create user now that OTP is verified
            user = User(
                username=registration_data['username'],
                email=registration_data['email'],
                first_name=registration_data['first_name'],
                last_name=registration_data['last_name'],
                password=registration_data['password'],
                is_active=True
            )
            user.save()
            
            # Clear session
            del request.session['registration_otp']
            del request.session['registration_data']
            
            messages.success(request, 'Email verified successfully! You can now login.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            
    return render(request, 'verify_otp.html')


def resend_otp(request):
    """Resends a fresh OTP to the user's email without re-registering."""
    # BLOCK: Only accessible if there is an active registration session
    if 'registration_data' not in request.session:
        messages.error(request, 'No active registration session found. Please register again.')
        return redirect('accounts:register')

    if request.method == 'POST':
        registration_data = request.session.get('registration_data')

        # Generate a fresh 4-digit OTP
        otp = str(random.randint(1000, 9999))
        request.session['registration_otp'] = otp  # overwrite old OTP

        mail_subject = 'Your New OTP for Blog Registration'
        message = render_to_string('acc_active_email.html', {
            'username': registration_data['username'],
            'otp': otp,
        })
        to_email = registration_data['email']
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()

        messages.success(request, f'A new OTP has been sent to {to_email}. Please check your inbox.')
    
    return redirect('accounts:verify_otp')
