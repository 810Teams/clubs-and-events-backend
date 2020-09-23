from rest_framework import serializers

from category.models import ClubType, EventType, EventSeries


class ClubTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubType
        fields = '__all__'


class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventType
        fields = '__all__'


class EventSeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSeries
        fields = '__all__'
