from django.contrib import admin

from user.models import EmailPreference, Profile, StudentCommitteeAuthority

import datetime

class EmailPreferenceInline(admin.StackedInline):
    model = EmailPreference


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'nickname', 'birthdate', 'last_online', 'is_lecturer']
    inlines = [EmailPreferenceInline]


class StudentCommitteeAuthorityAdmin(admin.ModelAdmin):
    list_display = ['profile', 'start_date', 'end_date', 'is_active']

    def is_active(self, obj):
        return obj.start_date <= datetime.datetime.now().date() <= obj.end_date

    is_active.boolean = True


admin.site.register(Profile, ProfileAdmin)
admin.site.register(StudentCommitteeAuthority, StudentCommitteeAuthorityAdmin)
