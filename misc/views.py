'''
    Miscellaneous Application Views
    misc/views.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from rest_framework import viewsets, filters, permissions

from misc.models import FAQ, Vote
from misc.serializers import FAQSerializer, ExistingVoteSerializer, NotExistingVoteSerializer


class FAQViewSet(viewsets.ModelViewSet):
    ''' Frequently asked question (FAQ) view set '''
    queryset = FAQ.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FAQSerializer
    http_method_names = ('get', 'head', 'options')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('question', 'answer')


class VoteViewSet(viewsets.ModelViewSet):
    ''' Vote view set '''
    queryset = Vote.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('get', 'post', 'head', 'options')

    def get_serializer_class(self):
        ''' Get serializer class '''
        if self.request.method == 'POST':
            return NotExistingVoteSerializer
        return ExistingVoteSerializer
