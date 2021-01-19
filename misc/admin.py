'''
    Miscellaneous Application Django Admin
    misc/admin.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib import admin

from core.utils.files import get_image_size
from core.utils.general import truncate
from misc.models import FAQ, Vote


class FAQAdmin(admin.ModelAdmin):
    ''' Frequently asked question (FAQ) admin '''
    list_display = ('id', 'partial_question', 'image_size', 'created_at', 'created_by', 'updated_at', 'updated_by')
    readonly_fields = ('created_by', 'updated_by')
    list_per_page = 20

    def partial_question(self, obj):
        ''' Get truncated question at max length of 32 '''
        return truncate(obj.question, max_length=32)

    def image_size(self, obj):
        ''' Get announcement image size and dimensions '''
        try:
            return get_image_size(obj.image)
        except ValueError:
            return str()
        except FileNotFoundError:
            return 'FileNotFoundError'


class VoteAdmin(admin.ModelAdmin):
    ''' Vote admin '''
    list_display = ('id', 'voted_for', 'partial_comment', 'voted_by', 'created_at')
    list_per_page = 20

    def partial_comment(self, obj):
        ''' Get truncated comment at max length of 32 '''
        return truncate(obj.comment, max_length=32)


admin.site.register(FAQ, FAQAdmin)
admin.site.register(Vote, VoteAdmin)
