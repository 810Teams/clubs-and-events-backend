'''
    User Application Serializers
    user/serializers.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.utils import raise_validation_errors, add_error_message, validate_profanity_serializer
from user.models import EmailPreference, StudentCommitteeAuthority


class UserSerializer(serializers.ModelSerializer):
    ''' User serializer '''
    is_student_committee = serializers.SerializerMethodField()

    class Meta:
        ''' Meta '''
        model = get_user_model()
        exclude = ('password', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'groups', 'user_permissions')
        read_only_fields = ('username', 'name', 'is_lecturer', 'created_by', 'updated_by')

    def validate(self, data):
        ''' Validate data '''
        errors = dict()

        if 'birthdate' in data.keys() and data['birthdate'] is not None and data['birthdate'] > datetime.now().date():
            add_error_message(errors, key='birthdate', message='Birthdates are not able to be set as a future date.')

        validate_profanity_serializer(data, 'nickname', errors, field_name='Nickname')
        validate_profanity_serializer(data, 'bio', errors, field_name='Bio')

        raise_validation_errors(errors)

        return data

    def get_is_student_committee(self, obj):
        ''' Retrieve student committee member status '''
        try:
            authority = StudentCommitteeAuthority.objects.get(user_id=obj.id)
            return authority.start_date <= datetime.now().date() <= authority.end_date
        except StudentCommitteeAuthority.DoesNotExist:
            return False


class LimitedUserSerializer(serializers.ModelSerializer):
    ''' Limited user serializer '''
    class Meta:
        ''' Meta '''
        model = get_user_model()
        fields = ('id', 'username', 'name', 'profile_picture', 'cover_photo')
        read_only_fields = ('id', 'username', 'name', 'profile_picture', 'cover_photo')


class EmailPreferenceSerializer(serializers.ModelSerializer):
    ''' Email preference serializer '''
    class Meta:
        ''' Meta '''
        model = EmailPreference
        fields = '__all__'
        read_only_fields = ('user',)


class StudentCommitteeAuthoritySerializer(serializers.ModelSerializer):
    ''' Student committee authority serializer '''
    is_active = serializers.SerializerMethodField()

    class Meta:
        ''' Meta '''
        model = StudentCommitteeAuthority
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')

    def get_is_active(self, obj):
        ''' Retrieve active status '''
        return obj.start_date <= datetime.now().date() <= obj.end_date
