from datetime import datetime

from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from email_validator import validate_email, EmailNotValidError
from rest_framework import serializers

from user.models import EmailPreference, StudentCommitteeAuthority


class UserSerializer(serializers.ModelSerializer):
    is_student_committee = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        exclude = ('password', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'groups', 'user_permissions')
        read_only_fields = ('username', 'name', 'created_by', 'updated_by')

    def validate(self, data):
        if 'birthdate' in data.keys() and data['birthdate'] is not None and data['birthdate'] > datetime.now().date():
            raise serializers.ValidationError(
                _('Birthdates are not able to be set as a future date.'),
                code='date_error'
            )

        if 'email' in data.keys():
            try:
                validate_email(data['email'], check_deliverability=False)
            except EmailNotValidError:
                raise serializers.ValidationError(_('Invalid email.'), code='invalid_email')

        return data

    def get_is_student_committee(self, obj):
        try:
            authority = StudentCommitteeAuthority.objects.get(user_id=obj.id)
            return authority.start_date <= datetime.now().date() <= authority.end_date
        except StudentCommitteeAuthority.DoesNotExist:
            return False


class LimitedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'name', 'profile_picture', 'cover_photo')
        read_only_fields = ('id', 'username', 'name', 'profile_picture', 'cover_photo')


class EmailPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailPreference
        fields = '__all__'
        read_only_fields = ('user',)


class StudentCommitteeAuthoritySerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = StudentCommitteeAuthority
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')

    def get_is_active(self, obj):
        return obj.start_date <= datetime.now().date() <= obj.end_date
