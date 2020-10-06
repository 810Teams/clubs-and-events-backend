from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from user.models import EmailPreference, StudentCommitteeAuthority

import datetime


class AlwaysChangedModelForm(forms.ModelForm):
    def has_changed(self):
        return True


class EmailPreferenceInline(admin.StackedInline):
    model = EmailPreference
    form = AlwaysChangedModelForm
    extra = 1


class UserAdmin(BaseUserAdmin):
    list_display = ['id', 'username', 'name', 'email', 'is_lecturer', 'is_active', 'is_staff', 'is_superuser']
    inlines = [EmailPreferenceInline]

    fieldsets = (
        (None, {'fields': ('username', 'name', 'email', 'password')}),
        (_('Profile'), {'fields': ('nickname', 'bio', 'profile_picture', 'cover_photo', 'birthdate')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at', 'last_login')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
    )

    add_fieldsets = (
        (None, {'fields': ('username', 'name', 'email', 'password1', 'password2')}),
        (_('Profile'), {'fields': ('nickname', 'bio', 'profile_picture', 'cover_photo', 'birthdate')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
    )

    def get_readonly_fields(self, request, obj=None):
        return ['created_at', 'updated_at', 'last_login']

    def is_lecturer(self, obj):
        return obj.groups.filter(name='lecturer').exists()

    is_lecturer.boolean = True


class EmailPreferenceAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'receive_own_club', 'receive_own_event', 'receive_own_lab',
                    'receive_other_events']

    def name(self, obj):
        return obj.user.name


class StudentCommitteeAuthorityAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'start_date', 'end_date', 'is_active']

    def is_active(self, obj):
        return obj.start_date <= datetime.datetime.now().date() <= obj.end_date

    is_active.boolean = True


admin.site.register(get_user_model(), UserAdmin)
admin.site.register(EmailPreference, EmailPreferenceAdmin)
admin.site.register(StudentCommitteeAuthority, StudentCommitteeAuthorityAdmin)
