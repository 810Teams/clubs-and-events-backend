from django.contrib import admin

from generator.models import QRCode, JoinKey


class QRCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'image', 'community', 'created_at', 'created_by')
    readonly_fields = ('image', 'community', 'created_at', 'created_by')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ('url',) + self.readonly_fields
        return self.readonly_fields


class JoinKeyAdmin(admin.ModelAdmin):
    list_display = ('id', 'key', 'event', 'created_at', 'created_by')
    readonly_fields = ('created_at', 'created_by')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ('key', 'event') + self.readonly_fields
        return self.readonly_fields


admin.site.register(QRCode, QRCodeAdmin)
admin.site.register(JoinKey, JoinKeyAdmin)
