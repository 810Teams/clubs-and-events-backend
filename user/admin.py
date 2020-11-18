'''
    User Application Django Admin
    user/admin.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from datetime import datetime
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from core.utils.files import get_image_size
from user.models import EmailPreference, StudentCommitteeAuthority


class AlwaysChangedModelForm(forms.ModelForm):
    ''' A model form class used to set field as always updated '''
    def has_changed(self):
        return True


class EmailPreferenceInline(admin.StackedInline):
    ''' Email preference inline '''
    model = EmailPreference
    form = AlwaysChangedModelForm
    extra = 1


class StudentCommitteeAuthorityInline(admin.StackedInline):
    ''' Student committee authority inline '''
    model = StudentCommitteeAuthority
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')
    extra = 0
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    ''' User admin '''
    list_display = ('id', 'username', 'name', 'user_group', 'is_active', 'is_staff', 'is_superuser',
                    'profile_picture_size', 'cover_photo_size')
    inlines = (EmailPreferenceInline, StudentCommitteeAuthorityInline)
    readonly_fields = ('last_login', 'created_at', 'created_by', 'updated_at', 'updated_by')
    list_per_page = 20

    fieldsets = (
        (None, {'fields': ('username', 'name', 'password')}),
        (_('Profile'), {'fields': ('nickname', 'bio', 'profile_picture', 'cover_photo', 'birthdate')}),
        (_('Timestamps'), {'fields': ('last_login', 'created_at', 'created_by', 'updated_at', 'updated_by')}),
        (_('Permissions'), {'fields': ('user_group', 'is_active', 'is_staff', 'is_superuser')}),
    )

    add_fieldsets = (
        (None, {'fields': ('username', 'name', 'password1', 'password2')}),
        (_('Profile'), {'fields': ('nickname', 'bio', 'profile_picture', 'cover_photo', 'birthdate')}),
        (_('Permissions'), {'fields': ('user_group', 'is_active', 'is_staff', 'is_superuser')}),
    )

    def profile_picture_size(self, obj):
        ''' Get profile picture size and dimensions '''
        try:
            return get_image_size(obj.profile_picture)
        except ValueError:
            return str()
        except FileNotFoundError:
            return 'FileNotFoundError'

    def cover_photo_size(self, obj):
        ''' Get cover photo size and dimensions '''
        try:
            return get_image_size(obj.cover_photo)
        except ValueError:
            return str()
        except FileNotFoundError:
            return 'FileNotFoundError'


class EmailPreferenceAdmin(admin.ModelAdmin):
    ''' Email preference admin '''
    list_display = ('id', 'user', 'name', 'receive_request', 'receive_announcement', 'receive_community_event',
                    'receive_event', 'receive_invitation')
    list_per_page = 20

    def get_readonly_fields(self, request, obj=None):
        ''' Get read-only fields '''
        if obj is not None:
            return ('user',) + self.readonly_fields
        return self.readonly_fields

    def name(self, obj):
        ''' Get name of the user '''
        return obj.user.name


class StudentCommitteeAuthorityAdmin(admin.ModelAdmin):
    ''' Student committee authority admin '''
    list_display = ('id', 'user', 'start_date', 'end_date', 'is_active', 'created_at', 'created_by', 'updated_at',
                    'updated_by')
    readonly_fields = ('created_by', 'updated_by')
    list_per_page = 20

    def get_readonly_fields(self, request, obj=None):
        ''' Get read-only fields '''
        if obj is not None:
            return ('user',) + self.readonly_fields
        return self.readonly_fields

    def is_active(self, obj):
        ''' Get active status '''
        return obj.start_date <= datetime.now().date() <= obj.end_date

    is_active.boolean = True


admin.site.register(get_user_model(), UserAdmin)
admin.site.register(EmailPreference, EmailPreferenceAdmin)
admin.site.register(StudentCommitteeAuthority, StudentCommitteeAuthorityAdmin)
