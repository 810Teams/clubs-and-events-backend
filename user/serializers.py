from datetime import datetime

from django.utils.translation import gettext as _
from rest_framework import serializers

from user.models import User, EmailPreference


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'groups', 'user_permissions')
        read_only_fields = ('username', 'name')

    def validate(self, data):
        if 'birthdate' in data.keys() and data['birthdate'] is not None and data['birthdate'] > datetime.now().date():
            raise serializers.ValidationError(
                _('Birthdates are not able to be set as a future date.'),
                code='date_error'
            )

        return data


class LimitedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'name', 'nickname', 'profile_picture')
        read_only_fields = ('username', 'name', 'nickname', 'profile_picture')


class EmailPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailPreference
        fields = '__all__'
        read_only_fields = ('user',)
