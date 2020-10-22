'''
    Asset Application Django Admin
    asset/admin.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib import admin

from asset.models import AlbumImage, Announcement, Album, Comment
from core.utils import truncate


class AnnouncementAdmin(admin.ModelAdmin):
    ''' Announcement admin '''
    list_display = ('id', 'partial_text', 'is_publicly_visible', 'community', 'created_at', 'created_by', 'updated_at',
                    'updated_by')
    readonly_fields = ('created_by', 'updated_by')

    def get_readonly_fields(self, request, obj=None):
        ''' Get read-only fields '''
        if obj is not None:
            return ('community',) + self.readonly_fields
        return self.readonly_fields

    def partial_text(self, obj):
        ''' Get truncated text at max length of 64 '''
        return truncate(obj.text, max_length=64)


class AlbumImageInline(admin.StackedInline):
    ''' Album image inline '''
    readonly_fields = ('created_by',)
    model = AlbumImage
    extra = 0


class AlbumAdmin(admin.ModelAdmin):
    ''' Album admin '''
    list_display = ('id', 'name', 'photos', 'community', 'community_event', 'created_at', 'created_by', 'updated_at',
                    'updated_by')
    readonly_fields = ('created_by', 'updated_by')
    inlines = (AlbumImageInline,)

    def get_readonly_fields(self, request, obj=None):
        ''' Get read-only fields '''
        if obj is not None:
            return ('community',) + self.readonly_fields
        return self.readonly_fields

    def photos(self, obj):
        ''' Get photos amount '''
        return len(AlbumImage.objects.filter(album=obj.id))


class CommentAdmin(admin.ModelAdmin):
    ''' Comment admin '''
    list_display = ('id', 'partial_text', 'written_by', 'event', 'created_at', 'created_by')
    readonly_fields = ('ip_address', 'created_by')

    def get_readonly_fields(self, request, obj=None):
        ''' Get read-only fields '''
        if obj is not None:
            return ('event',) + self.readonly_fields
        return self.readonly_fields

    def partial_text(self, obj):
        ''' Get truncated text at the length of 64 '''
        return truncate(obj.text, max_length=64)


admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Comment, CommentAdmin)
