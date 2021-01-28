'''
    Asset Application Django Admin
    asset/admin.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib import admin

from asset.models import AlbumImage, Announcement, Album, Comment
from core.utils.files import get_image_size, simplify_file_size
from core.utils.general import truncate


class AnnouncementAdmin(admin.ModelAdmin):
    ''' Announcement admin '''
    list_display = ('id', 'partial_text', 'image_size', 'is_publicly_visible', 'community', 'created_at', 'created_by',
                    'updated_at', 'updated_by')
    readonly_fields = ('created_by', 'updated_by')
    list_per_page = 20

    def get_readonly_fields(self, request, obj=None):
        ''' Get read-only fields '''
        if obj is not None:
            return ('community',) + self.readonly_fields
        return self.readonly_fields

    def partial_text(self, obj):
        ''' Get truncated text at max length of 64 '''
        return truncate(obj.text, max_length=64)

    def image_size(self, obj):
        ''' Get announcement image size and dimensions '''
        try:
            return get_image_size(obj.image)
        except ValueError:
            return str()
        except FileNotFoundError:
            return 'FileNotFoundError'


class AlbumImageInline(admin.StackedInline):
    ''' Album image inline '''
    readonly_fields = ('size', 'created_by',)
    model = AlbumImage
    extra = 0

    def has_change_permission(self, request, obj=None):
        ''' Restrict change permission '''
        return False

    def size(self, obj):
        ''' Get image size '''
        try:
            return get_image_size(obj.image)
        except ValueError:
            return str()
        except FileNotFoundError:
            return 'FileNotFoundError'


class AlbumAdmin(admin.ModelAdmin):
    ''' Album admin '''
    list_display = ('id', 'name', 'photos', 'storage', 'community', 'community_event', 'created_at', 'created_by',
                    'updated_at', 'updated_by')
    readonly_fields = ('storage', 'created_by', 'updated_by')
    inlines = (AlbumImageInline,)
    list_per_page = 20

    def get_readonly_fields(self, request, obj=None):
        ''' Get read-only fields '''
        if obj is not None:
            return ('community',) + self.readonly_fields
        return self.readonly_fields

    def photos(self, obj):
        ''' Get photos amount '''
        return len(AlbumImage.objects.filter(album_id=obj.id))

    def storage(self, obj):
        ''' Get storage space used '''
        try:
            return simplify_file_size(sum([i.image.size for i in AlbumImage.objects.filter(album_id=obj.id)]), unit='B')
        except ValueError:
            return str()
        except FileNotFoundError:
            return 'FileNotFoundError'


class CommentAdmin(admin.ModelAdmin):
    ''' Comment admin '''
    list_display = ('id', 'partial_text', 'written_by', 'event', 'is_active', 'created_at', 'created_by')
    readonly_fields = ('ip_address', 'created_by')
    list_per_page = 20

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
