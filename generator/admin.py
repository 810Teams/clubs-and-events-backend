'''
    Generator Application Django Admin
    generator/admin.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib import admin

from generator.models import QRCode, JoinKey, GeneratedDocx


class QRCodeAdmin(admin.ModelAdmin):
    ''' QR code admin '''
    list_display = ('id', 'url', 'image', 'event', 'created_at', 'created_by')
    readonly_fields = ('image', 'created_at', 'created_by')

    def get_readonly_fields(self, request, obj=None):
        ''' Get read-only fields '''
        if obj is not None:
            return ('url', 'image', 'event', 'created_at', 'created_by')
        return self.readonly_fields


class JoinKeyAdmin(admin.ModelAdmin):
    ''' Join key admin '''
    list_display = ('id', 'key', 'event', 'created_at', 'created_by')
    readonly_fields = ('created_at', 'created_by')

    def get_readonly_fields(self, request, obj=None):
        ''' Get read-only fields '''
        if obj is not None:
            return ('key', 'event') + self.readonly_fields
        return self.readonly_fields


class GeneratedDocxAdmin(admin.ModelAdmin):
    ''' Generated docx admin '''
    list_display = ('id', 'club', 'document', 'created_at', 'created_by', 'updated_at', 'updated_by')
    readonly_fields = ('document', 'created_by', 'updated_by')

    def get_readonly_fields(self, request, obj=None):
        ''' Get read-only fields '''
        if obj is not None:
            return ('club',) + self.readonly_fields
        return self.readonly_fields


admin.site.register(QRCode, QRCodeAdmin)
admin.site.register(JoinKey, JoinKeyAdmin)
admin.site.register(GeneratedDocx, GeneratedDocxAdmin)
