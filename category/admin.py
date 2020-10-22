'''
    Category Application Django Admin
    category/admin.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib import admin

from category.models import ClubType, EventType, EventSeries


class ClubTypeAdmin(admin.ModelAdmin):
    ''' Club type admin '''
    list_display = ('id', 'title_th', 'title_en', 'created_at', 'updated_at')


class EventTypeAdmin(admin.ModelAdmin):
    ''' Event type admin '''
    list_display = ('id', 'title_th', 'title_en', 'created_at', 'updated_at')


class EventSeriesAdmin(admin.ModelAdmin):
    ''' Event series admin '''
    list_display = ('id', 'title_th', 'title_en', 'created_at', 'updated_at')


admin.site.register(ClubType, ClubTypeAdmin)
admin.site.register(EventType, EventTypeAdmin)
admin.site.register(EventSeries, EventSeriesAdmin)
