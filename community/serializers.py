from django.utils.translation import gettext as _
from rest_framework import serializers

from community.models import Club, Event, CommunityEvent, Lab


class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = '__all__'

    def validate(self, data):
        errors = list()

        if not data['is_official']:
            if 'room' in data.keys() and data['room'] is not None and data['room'] != '':
                errors.append(serializers.ValidationError(
                    _('Unofficial clubs are not able to occupy a room.'),
                    code='unofficial_club_limitations'
                ))
            if 'url_id' in data.keys() and data['url_id'] is not None and data['url_id'] != '':
                errors.append(serializers.ValidationError(
                    _('Unofficial clubs are not able to set custom URL ID.'),
                    code='unofficial_club_limitations'
                ))
            if 'is_publicly_visible' in data.keys() and data['is_publicly_visible'] == True:
                errors.append(serializers.ValidationError(
                    _('Unofficial clubs cannot be publicly visible.'),
                    code='unofficial_club_limitations'
                ))

        if len(errors) > 0:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        if 'url_id' in validated_data.keys() and validated_data['url_id'] == '':
            validated_data['url_id'] = None
        if 'room' in validated_data.keys() and validated_data['room'] == '':
            validated_data['room'] = None

        return Club.objects.create(**validated_data)


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class CommunityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityEvent
        fields = '__all__'


class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lab
        fields = '__all__'
