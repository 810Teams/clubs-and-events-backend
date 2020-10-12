from datetime import datetime
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from user.models import EmailPreference, StudentCommitteeAuthority


class AlwaysChangedModelForm(forms.ModelForm):
    def has_changed(self):
        return True


class EmailPreferenceInline(admin.StackedInline):
    model = EmailPreference
    form = AlwaysChangedModelForm
    extra = 1


class StudentCommitteeAuthorityInline(admin.StackedInline):
    model = StudentCommitteeAuthority
    extra = 0
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'name', 'is_lecturer', 'is_active', 'is_staff', 'is_superuser')
    inlines = (EmailPreferenceInline, StudentCommitteeAuthorityInline)
    readonly_fields = ('last_login', 'created_at', 'created_by', 'updated_at', 'updated_by')

    fieldsets = (
        (None, {'fields': ('username', 'name', 'password')}),
        (_('Profile'), {'fields': ('nickname', 'bio', 'profile_picture', 'cover_photo', 'birthdate')}),
        (_('Timestamps'), {'fields': ('last_login', 'created_at', 'created_by', 'updated_at', 'updated_by')}),
        (_('Permissions'), {'fields': ('is_lecturer', 'is_active', 'is_staff', 'is_superuser', 'groups')}),
    )

    add_fieldsets = (
        (None, {'fields': ('username', 'name', 'password1', 'password2')}),
        (_('Profile'), {'fields': ('nickname', 'bio', 'profile_picture', 'cover_photo', 'birthdate')}),
        (_('Permissions'), {'fields': ('is_lecturer', 'is_active', 'is_staff', 'is_superuser', 'groups')}),
    )


class EmailPreferenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'receive_request', 'receive_announcement', 'receive_community_event',
                    'receive_event')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ('user',) + self.readonly_fields
        return self.readonly_fields

    def name(self, obj):
        return obj.user.name


class StudentCommitteeAuthorityAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'start_date', 'end_date', 'is_active')
    readonly_fields = ('created_by', 'updated_by')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ('user',) + self.readonly_fields
        return self.readonly_fields

    def is_active(self, obj):
        return obj.start_date <= datetime.now().date() <= obj.end_date

    is_active.boolean = True


admin.site.register(get_user_model(), UserAdmin)
admin.site.register(EmailPreference, EmailPreferenceAdmin)
admin.site.register(StudentCommitteeAuthority, StudentCommitteeAuthorityAdmin)
