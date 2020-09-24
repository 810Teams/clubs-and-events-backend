from django.utils.translation import gettext as _
from rest_framework import serializers

from community.models import Club, Event, CommunityEvent, Lab


class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = '__all__'

    def validate(self, data):
        errors = list()

        # If the 'is_official' field is not present or false, validate these.
        if 'is_official' not in data.keys() or ('is_official' in data.keys() and not data['is_official']):
            # If present, the 'room' field must be null, but if blank, it will be set to null later.
            if 'room' in data.keys() and data['room'] is not None and data['room'].strip() != '':
                errors.append(serializers.ValidationError(
                    _('Unofficial clubs are not able to occupy a room.'),
                    code='unofficial_club_limitations'
                ))
            # If present, the 'url_id' field must be null, but if blank, it will be set to null later.
            if 'url_id' in data.keys() and data['url_id'] is not None and data['url_id'].strip() != '':
                errors.append(serializers.ValidationError(
                    _('Unofficial clubs are not able to set custom URL ID.'),
                    code='unofficial_club_limitations'
                ))
            # If present, the 'is_publicly_visible' field must be false.
            if 'is_publicly_visible' in data.keys() and data['is_publicly_visible'] == True:
                errors.append(serializers.ValidationError(
                    _('Unofficial clubs cannot be publicly visible.'),
                    code='unofficial_club_limitations'
                ))

        if len(errors) > 0:
            raise serializers.ValidationError(errors)

        return data

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
