from django.utils.translation import gettext as _
from rest_framework import serializers

from asset.models import Announcement, Album, Comment
from membership.models import Membership


class ExistingAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by', 'community')


class NotExistingAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        exclude = ('created_by', 'updated_by')

    def validate(self, data):
        errors = list()

        membership = Membership.objects.filter(
            user_id=self.context['request'].user.id,
            position__in=[1, 2, 3],
            community_id=data['community'].id,
            end_date=None
        )

        if len(membership) == 0:
            errors.append(serializers.ValidationError(
                _('Permission denied creating an announcement in a certain community.'),
                code='unauthorized'
            ))

        if len(errors) > 0:
            raise serializers.ValidationError(errors)

        return data


class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('created_by', 'event')
