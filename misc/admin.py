'''
    Miscellaneous Application Django Admin
    misc/admin.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib import admin

from core.utils.files import get_image_size
from core.utils.general import truncate
from misc.models import FAQ


class FAQAdmin(admin.ModelAdmin):
    ''' Frequently asked question (FAQ) admin '''
    list_display = ('id', 'partial_question', 'image_size', 'created_at', 'created_by', 'updated_at', 'updated_by')
    readonly_fields = ('created_by', 'updated_by')
    list_per_page = 20

    def partial_question(self, obj):
        ''' Get truncated text at max length of 32 '''
        return truncate(obj.question, max_length=32)

    def image_size(self, obj):
        ''' Get announcement image size and dimensions '''
        try:
            return get_image_size(obj.image)
        except ValueError:
            return str()
        except FileNotFoundError:
            return 'FileNotFoundError'


admin.site.register(FAQ, FAQAdmin)
