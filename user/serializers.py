from datetime import datetime

from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from rest_framework import serializers

from user.models import EmailPreference


class UserSerializer(serializers.ModelSerializer):
    is_lecturer = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        exclude = ('password', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'groups', 'user_permissions')
        read_only_fields = ('username', 'name')

    def validate(self, data):
        if 'birthdate' in data.keys() and data['birthdate'] is not None and data['birthdate'] > datetime.now().date():
            raise serializers.ValidationError(
                _('Birthdates are not able to be set as a future date.'),
                code='date_error'
            )

        return data

    def get_is_lecturer(self, obj):
        return obj.groups.filter(name='lecturer').exists()


class LimitedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('username', 'name', 'profile_picture', 'cover_photo')
        read_only_fields = ('username', 'name', 'profile_picture', 'cover_photo')


class EmailPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailPreference
        fields = '__all__'
        read_only_fields = ('user',)
