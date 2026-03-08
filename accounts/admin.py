from django.contrib import admin
from django.contrib.auth.models import User

# The User model is already registered by default in Django admin
# But we can explicitly register it here with customization if needed
admin.site.site_header = "Personal Blog Admin"
admin.site.site_title = "Personal Blog"
