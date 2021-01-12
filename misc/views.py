'''
    Miscellaneous Application Views
    misc/views.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from rest_framework import viewsets, filters, permissions

from misc.models import FAQ
from misc.serializers import FAQSerializer


class FAQViewSet(viewsets.ModelViewSet):
    ''' Frequently asked question (FAQ) view set '''
    queryset = FAQ.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FAQSerializer
    http_method_names = ('get', 'head', 'options')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('question', 'answer')
