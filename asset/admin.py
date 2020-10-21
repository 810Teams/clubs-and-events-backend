from django.contrib import admin

from asset.models import AlbumImage, Announcement, Album, Comment
from core.utils import truncate


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id', 'partial_text', 'community', 'created_at', 'created_by', 'updated_at', 'updated_by')
    readonly_fields = ('created_by', 'updated_by')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ('community',) + self.readonly_fields
        return self.readonly_fields

    def partial_text(self, obj):
        return truncate(obj.text)


class AlbumImageInline(admin.StackedInline):
    readonly_fields = ('created_by',)
    model = AlbumImage
    extra = 0


class AlbumAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'photos', 'community', 'community_event', 'created_at', 'created_by', 'updated_at',
                    'updated_by')
    readonly_fields = ('created_by', 'updated_by')
    inlines = (AlbumImageInline,)

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ('community',) + self.readonly_fields
        return self.readonly_fields

    def photos(self, obj):
        return len(AlbumImage.objects.filter(album=obj.id))


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'partial_text', 'written_by', 'event', 'created_at', 'created_by')
    readonly_fields = ('ip_address', 'created_by')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ('event',) + self.readonly_fields
        return self.readonly_fields

    def partial_text(self, obj):
        return truncate(obj.text)


admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Comment, CommentAdmin)
