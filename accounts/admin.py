from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Customizing User Admin to make email readonly
class CustomUserAdmin(UserAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return self.readonly_fields + ('email',)
        return self.readonly_fields

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.site_header = "Personal Blog Admin"
admin.site.site_title = "Personal Blog"
