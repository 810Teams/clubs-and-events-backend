from rest_framework import serializers
from django.utils.translation import gettext as _

from community.models import Club, Event, CommunityEvent, Lab
from membership.models import Membership

import datetime


class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = '__all__'

    def validate(self, data):
        errors = list()

        if not data['is_official']:
            if data['room'] is not None:
                errors.append(serializers.ValidationError(
                    _('Unofficial clubs are not able to occupy a room.'),
                    code='unofficial_club_limitations'
                ))
            if data['url_id'] is not None:
                errors.append(serializers.ValidationError(
                    _('Unofficial clubs are not able to set custom URL ID.'),
                    code='unofficial_club_limitations'
                ))
            if data['is_publicly_visible']:
                errors.append(serializers.ValidationError(
                    _('Unofficial clubs cannot be publicly visible.'),
                    code='unofficial_club_limitations'
                ))

        if len(errors) > 0:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        club = Club.objects.create(**validated_data)
        # TODO: CREATE MEMBERSHIP

        return club


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
