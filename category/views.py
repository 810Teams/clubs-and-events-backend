'''
    Category Application Views
    category/views.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from rest_framework import viewsets

from category.models import ClubType, EventType, EventSeries
from category.serializers import ClubTypeSerializer, EventTypeSerializer, EventSeriesSerializer


class ClubTypeViewSet(viewsets.ModelViewSet):
    ''' Club type view set '''
    queryset = ClubType.objects.all()
    serializer_class = ClubTypeSerializer
    http_method_names = ('get', 'head', 'options')


class EventTypeViewSet(viewsets.ModelViewSet):
    ''' Event type view set '''
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer
    http_method_names = ('get', 'head', 'options')


class EventSeriesViewSet(viewsets.ModelViewSet):
    ''' Event series view set '''
    queryset = EventSeries.objects.all()
    serializer_class = EventSeriesSerializer
    http_method_names = ('get', 'head', 'options')
