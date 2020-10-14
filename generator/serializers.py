from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.translation import gettext as _
from rest_framework import serializers

from generator.models import QRCode, JoinKey
from membership.models import Membership


class QRCodeSerializer(serializers.ModelSerializer):
    def validate(self, data):
        try:
            validator = URLValidator()
            validator(data['url'])
        except ValidationError:
            raise serializers.ValidationError(_('Invalid URL.'),code='invalid_url')

        return data


class ExistingQRCodeSerializer(QRCodeSerializer):
    class Meta:
        model = QRCode
        fields = '__all__'
        read_only_fields = ('url', 'image', 'community', 'created_by')


class NotExistingQRCodeSerializer(QRCodeSerializer):
    class Meta:
        model = QRCode
        fields = '__all__'
        read_only_fields = ('image', 'created_by')

    def validate(self, data):
        membership = Membership.objects.filter(
            user_id=self.context['request'].user.id, position__in=(2, 3), community_id=data['community'].id, status='A'
        )
        if len(membership) == 0:
            raise serializers.ValidationError(
                _('QRCodes must only be created by a deputy leader of the community.'),
                code='permission_denied'
            )

        super(NotExistingQRCodeSerializer, self).validate(data)

        return data


class ExistingJoinKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = JoinKey
        fields = '__all__'
        read_only_fields = ('key', 'event', 'created_by')


class NotExistingJoinKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = JoinKey
        fields = '__all__'
        read_only_fields = ('created_by',)

    def validate(self, data):
        membership = Membership.objects.filter(
            user_id=self.context['request'].user.id, position__in=(2, 3), community_id=data['event'].id, status='A'
        )
        if len(membership) == 0:
            raise serializers.ValidationError(
                _('Join keys must only be created by a deputy leader of the community.'),
                code='permission_denied'
            )

        if not data['key'].isalnum():
            raise serializers.ValidationError(
                _('Join keys must only contain alphabetical characters and numbers.'), code='invalid_join_key'
            )

        return data
