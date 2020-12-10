'''
    Generator Application Serializers
    generator/serializers.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.translation import gettext as _
from rest_framework import serializers

from core.permissions import IsDeputyLeaderOfCommunity
from core.utils.serializer import raise_validation_errors, add_error_message
from generator.models import QRCode, JoinKey, GeneratedDocx
from membership.models import Membership
from user.permissions import IsLecturerObject


class QRCodeSerializerTemplate(serializers.ModelSerializer):
    ''' QR code serializer template '''
    class Meta:
        ''' Meta '''
        model = QRCode
        fields = '__all__'
        abstract = True

    def validate(self, data, get_errors=False):
        ''' Validate data'''
        errors = dict()

        try:
            validator = URLValidator()
            validator(data['url'])
        except ValidationError:
            errors['url'] = _('Invalid URL.')

        if get_errors:
            return errors

        raise_validation_errors(errors)

        return data


class ExistingQRCodeSerializer(QRCodeSerializerTemplate):
    ''' Existing QR code serializer '''
    class Meta:
        ''' Meta '''
        model = QRCode
        fields = '__all__'
        read_only_fields = ('url', 'image', 'community', 'created_by')


class NotExistingQRCodeSerializer(QRCodeSerializerTemplate):
    ''' Not existing QR code serializer '''
    class Meta:
        ''' Meta '''
        model = QRCode
        fields = '__all__'
        read_only_fields = ('image', 'created_by')

    def validate(self, data, get_errors=False):
        ''' Validate data '''
        errors = super(NotExistingQRCodeSerializer, self).validate(data, get_errors=True)

        membership = Membership.objects.filter(
            user_id=self.context['request'].user.id, position__in=(2, 3), community_id=data['event'].id, status='A'
        )
        if len(membership) == 0:
            add_error_message(errors, message='QRCodes must only be created by a deputy leader of the community.')

        raise_validation_errors(errors)

        return data


class ExistingJoinKeySerializer(serializers.ModelSerializer):
    ''' Existing join key serializer '''
    class Meta:
        ''' Meta '''
        model = JoinKey
        exclude = ('created_at', 'created_by')
        read_only_fields = ('key', 'event')


class NotExistingJoinKeySerializer(serializers.ModelSerializer):
    ''' Not existing join key serializer '''
    class Meta:
        ''' Meta '''
        model = JoinKey
        exclude = ('created_at', 'created_by')

    def validate(self, data):
        ''' Validate data '''
        errors = dict()

        membership = Membership.objects.filter(
            user_id=self.context['request'].user.id, position__in=(2, 3), community_id=data['event'].id, status='A'
        )
        if len(membership) == 0:
            add_error_message(errors, message='Join keys must only be created by a deputy leader of the community.')

        if not data['key'].isalnum():
            errors['key'] = _('Join keys must only contain alphanumerical characters.')

        raise_validation_errors(errors)

        return data


class GeneratedDocxSerializerTemplate(serializers.ModelSerializer):
    ''' Generated Microsoft Word document serializer template '''
    class Meta:
        ''' Meta '''
        model = GeneratedDocx
        fields = '__all__'
        abstract = True

    def validate(self, data, get_errors=False):
        ''' Validate data '''
        errors = dict()

        if 'advisor' in data.keys():
            if not IsLecturerObject().has_object_permission(self.context['request'], None, data['advisor']):
                errors['advisor'] = _('Advisor must be a lecturer.')

        if 'objective' in data.keys() and '\n' in data['objective']:
            errors['objective'] = _('Club brief objective must be a single line.')

        if 'room' in data.keys() and '\n' in data['room']:
            errors['room'] = _('Room must be a single line.')

        if get_errors:
            return errors

        raise_validation_errors(errors)

        return data


class ExistingGeneratedDocxSerializer(GeneratedDocxSerializerTemplate):
    ''' Existing generated Microsoft Word document serializer '''
    class Meta:
        ''' Meta '''
        model = GeneratedDocx
        fields = '__all__'
        read_only_fields = ('club', 'document', 'created_by', 'updated_by')


class NotExistingGeneratedDocxSerializer(GeneratedDocxSerializerTemplate):
    ''' Not existing generated Microsoft Word document serializer '''
    class Meta:
        ''' Meta '''
        model = GeneratedDocx
        fields = '__all__'
        read_only_fields = ('document', 'created_by', 'updated_by')

    def validate(self, data, get_errors=False):
        ''' Validate data '''
        errors = super(NotExistingGeneratedDocxSerializer, self).validate(data, get_errors=True)

        if not IsDeputyLeaderOfCommunity().has_object_permission(self.context['request'], None, data['club']):
            add_error_message(
                errors,
                message='Club approval and renewal documents can only be generated by deputy leaders of the club.'
            )

        raise_validation_errors(errors)

        return data
