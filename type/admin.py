from django.contrib import admin

from type.models import ClubType, EventType, EventSeries


class ClubTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'title_th', 'title_en']


class EventTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'title_th', 'title_en']


class EventSeriesAdmin(admin.ModelAdmin):
    list_display = ['id', 'title_th', 'title_en']


admin.site.register(ClubType, ClubTypeAdmin)
admin.site.register(EventType, EventTypeAdmin)
admin.site.register(EventSeries, EventSeriesAdmin)
