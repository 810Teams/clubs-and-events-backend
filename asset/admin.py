from django.contrib import admin

from asset.models import AlbumImage, Announcement, Album, Comment


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['id', 'partial_text', 'created_at', 'created_by', 'community']

    def partial_text(self, obj):
        if len(obj.text) <= 64:
            return obj.text
        return obj.text[:64] + '...'


class AlbumImageInline(admin.StackedInline):
    model = AlbumImage
    extra = 1


class AlbumAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'photos', 'created_at', 'created_by', 'community', 'community_event']
    inlines = [AlbumImageInline]

    def photos(self, obj):
        return len(AlbumImage.objects.filter(album=obj.id))


class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'partial_text', 'written_by', 'created_at', 'created_by', 'event']

    def partial_text(self, obj):
        if len(obj.text) <= 64:
            return obj.text
        return obj.text[:64] + '...'


admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Comment, CommentAdmin)
