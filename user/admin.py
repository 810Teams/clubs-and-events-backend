from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from user.models import EmailPreference, User, StudentCommitteeAuthority

import datetime


class EmailPreferenceInline(admin.StackedInline):
    model = EmailPreference


class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'name', 'email', 'is_active', 'is_staff', 'is_superuser']
    inlines = [EmailPreferenceInline]

    fieldsets = (
        (None, {'fields': ('username', 'name', 'email', 'password')}),
        ('Profile', {'fields': ('nickname', 'bio', 'profile_picture', 'cover_photo', 'birthdate')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'last_login')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
    )

    add_fieldsets = (
        (None, {'fields': ('username', 'name', 'email', 'password1', 'password2')}),
        ('Profile', {'fields': ('nickname', 'bio', 'profile_picture', 'cover_photo', 'birthdate')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
    )

    def get_readonly_fields(self, request, obj=None):
        return ['created_at', 'updated_at', 'last_login']


class StudentCommitteeAuthorityAdmin(admin.ModelAdmin):
    list_display = ['user', 'start_date', 'end_date', 'is_active']

    def is_active(self, obj):
        return obj.start_date <= datetime.datetime.now().date() <= obj.end_date

    is_active.boolean = True


admin.site.register(User, UserAdmin)
admin.site.register(StudentCommitteeAuthority, StudentCommitteeAuthorityAdmin)
