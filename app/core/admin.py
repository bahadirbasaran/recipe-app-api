from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from core import models


class UserAdmin(BaseUserAdmin):
    """Custom User Admin"""

    ordering = ['id']
    list_display = ['email', 'name']

    # Each tuple in the fieldsets is a section. Sections start with titles.
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Important Dates'), {'fields': ('last_login',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )

# Django-admin rovides a web interface for performing CRUD actions on models
# by default. In case of adding new/custom models like the User model here,
# they should be registered to be accessible thorough the admin site.
admin.site.register(models.User, UserAdmin)
