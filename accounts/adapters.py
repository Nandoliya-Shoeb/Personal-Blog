"""
Custom Social Account Adapter for Google OAuth.
Handles redirect after Google login.
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to control behavior after Google OAuth login.
    - Normal users go to profile
    - Staff/Admin users go to admin dashboard
    """

    def get_login_redirect_url(self, request):
        """Redirect user based on their role after Google login."""
        if request.user.is_authenticated:
            if request.user.is_staff:
                return '/admin-panel/'  # Admin dashboard
            else:
                return '/accounts/profile/'  # User profile
        return '/accounts/login/'

    def save_user(self, request, sociallogin, form=None):
        """Save user data from Google profile."""
        user = super().save_user(request, sociallogin, form)
        # Get data from Google profile
        data = sociallogin.account.extra_data
        if 'given_name' in data:
            user.first_name = data['given_name']
        if 'family_name' in data:
            user.last_name = data['family_name']
        user.save()
        return user
