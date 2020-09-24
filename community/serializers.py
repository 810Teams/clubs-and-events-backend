from django.utils.translation import gettext as _
from rest_framework import serializers

from community.models import Club, Event, CommunityEvent, Lab


class OfficialClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = '__all__'
        read_only_fields = ('is_official',)


class UnofficialClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ('name_th', 'name_en', 'description', 'logo', 'banner', 'club_type', 'founded_date', 'status')
        read_only_fields = ('is_official',)


class ApprovedEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ('is_approved',)


class UnapprovedEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('name_th', 'name_en', 'description', 'logo', 'banner', 'event_type', 'event_series', 'location',
                  'start_date', 'end_date', 'start_time', 'end_time', 'is_cancelled')
        read_only_fields = ('is_approved',)


class CommunityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityEvent
        fields = '__all__'


class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lab
        fields = '__all__'

    def create(self, validated_data):
        if 'url_id' in validated_data.keys() and validated_data['url_id'].strip() == '':
            validated_data['url_id'] = None
        if 'room' in validated_data.keys() and validated_data['room'].strip() == '':
            validated_data['room'] = None

        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if 'url_id' in validated_data.keys() and validated_data['url_id'].strip() == '':
            validated_data['url_id'] = None
        if 'room' in validated_data.keys() and validated_data['room'].strip() == '':
            validated_data['room'] = None

        instance.__dict__.update(**validated_data)
        instance.save()

        return instance
