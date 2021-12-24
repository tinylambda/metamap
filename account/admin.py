from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin

from account.models import User


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff')
    ordering = ('email', )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


admin.site.register(User, CustomUserAdmin)
