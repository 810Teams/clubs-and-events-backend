from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.response import Response

from category.models import ClubType, EventType, EventSeries
from category.serializers import ClubTypeSerializer, EventTypeSerializer, EventSeriesSerializer


class ClubTypeView(generics.RetrieveAPIView):
    ''' Club type view '''
    queryset = ClubType.objects.all()
    serializer_class = ClubTypeSerializer

    def retrieve(self, request, *args, **kwargs):
        ''' Retrieve club type by primary key '''
        serializer = ClubTypeSerializer(self.get_object(), many=False)
        return Response(serializer.data)


class AllClubTypeView(generics.ListAPIView):
    ''' All Club types view '''
    queryset = ClubType.objects.all()
    serializer_class = ClubTypeSerializer

    def list(self, request, *args, **kwargs):
        ''' List all club types '''
        serializer = ClubTypeSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class EventTypeView(generics.RetrieveAPIView):
    ''' Event type view '''
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer

    def retrieve(self, request, *args, **kwargs):
        ''' Retrieve event type by primary key '''
        serializer = EventTypeSerializer(self.get_object(), many=False)
        return Response(serializer.data)


class AllEventTypeView(generics.ListAPIView):
    ''' All event types view '''
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer

    def list(self, request, *args, **kwargs):
        ''' List all event types '''
        serializer = EventTypeSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class EventSeriesView(generics.RetrieveAPIView):
    ''' Event series view '''
    queryset = EventSeries.objects.all()
    serializer_class = EventSeriesSerializer

    def retrieve(self, request, *args, **kwargs):
        ''' Retrieve event series by primary key '''
        serializer = EventSeriesSerializer(self.get_object(), many=False)
        return Response(serializer.data)


class AllEventSeriesView(generics.ListAPIView):
    ''' All event series view '''
    queryset = EventSeries.objects.all()
    serializer_class = EventSeriesSerializer

    def list(self, request, *args, **kwargs):
        ''' Retrieve all event series '''
        serializer = EventSeriesSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)