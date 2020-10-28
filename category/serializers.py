'''
    Category Application Serializers
    category/serializers.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from rest_framework import serializers

from category.models import ClubType, EventType, EventSeries


class ClubTypeSerializer(serializers.ModelSerializer):
    ''' Club type serializer '''
    class Meta:
        ''' Meta '''
        model = ClubType
        exclude = ('created_at', 'updated_at', 'created_by', 'updated_by')


class EventTypeSerializer(serializers.ModelSerializer):
    ''' Event type serializer '''
    class Meta:
        ''' Meta '''
        model = EventType
        exclude = ('created_at', 'updated_at', 'created_by', 'updated_by')


class EventSeriesSerializer(serializers.ModelSerializer):
    ''' Event type serializer '''
    class Meta:
        ''' Meta '''
        model = EventSeries
        exclude = ('created_at', 'updated_at', 'created_by', 'updated_by')
