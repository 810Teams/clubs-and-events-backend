'''
    Miscellaneous Application Views
    misc/views.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.core.exceptions import ValidationError
from rest_framework import viewsets, filters, permissions, generics
from rest_framework.response import Response

from membership.models import Membership
from misc.models import FAQ, Vote
from misc.serializers import FAQSerializer, ExistingVoteSerializer, NotExistingVoteSerializer, OwnVoteSerializer


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

    def list(self, request, *args, **kwargs):
        ''' List communities '''
        queryset = self.filter_queryset(self.get_queryset())

        try:
            query = request.query_params.get('voted_for_user')
            if query is not None:
                membership_ids = [i.id for i in Membership.objects.filter(user_id=query)]
                queryset = queryset.filter(voted_for_id__in=membership_ids)
        except (ValueError, ValidationError):
            queryset = None

        try:
            query = request.query_params.get('event')
            if query is not None:
                membership_ids = [i.id for i in Membership.objects.filter(community_id=query)]
                queryset = queryset.filter(voted_for_id__in=membership_ids)
        except (ValueError, ValidationError):
            queryset = None

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class MyVoteView(generics.ListAPIView):
    ''' My user view '''
    queryset = Vote.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OwnVoteSerializer

    def list(self, request, *args, **kwargs):
        ''' Retrieve own user '''
        membership_ids = [i.id for i in Membership.objects.filter(user_id=request.user.id)]
        votes = Vote.objects.filter(voted_for_id__in=membership_ids)

        serializer = self.get_serializer(votes, many=True)

        return Response(serializer.data)
