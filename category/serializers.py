'''
    Category Application
    category/
    @author Teerapat Kraisrisirikul (810Teams)
'''

from rest_framework import serializers

from category.models import ClubType, EventType, EventSeries


class ClubTypeSerializer(serializers.ModelSerializer):
    ''' Club type serializer '''
    class Meta:
        ''' Meta '''
        model = ClubType
        fields = '__all__'


class EventTypeSerializer(serializers.ModelSerializer):
    ''' Event type serializer '''
    class Meta:
        ''' Meta '''
        model = EventType
        fields = '__all__'


class EventSeriesSerializer(serializers.ModelSerializer):
    ''' Event type serializer '''
    class Meta:
        ''' Meta '''
        model = EventSeries
        fields = '__all__'
