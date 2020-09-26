from django.utils.translation import gettext as _
from rest_framework import serializers

from asset.models import Announcement, Album, Comment, AlbumImage
from community.models import Event, CommunityEvent
from membership.models import Membership


class ExistingAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'
        read_only_fields = ('community', 'created_by', 'updated_by')


class NotExistingAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')

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


class ExistingAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = '__all__'
        read_only_fields = ('community', 'created_by', 'updated_by')

    def validate(self, data):
        errors = list()

        if data['community_event'] is not None:
            try:
                if Event.objects.get(pk=data['community'].id) is not None:
                    errors.append(serializers.ValidationError(
                        _('Albums are not able to be linked to community events if created under an event.'),
                        code='hierarchy_error'
                    ))
            except Event.DoesNotExist:
                pass

            if data['community_event'].created_under.id != data['community'].id:
                errors.append(serializers.ValidationError(
                    _('Albums are not able to be linked to community events created under other communities.'),
                    code='hierarchy_error'
                ))

        if len(errors) > 0:
            raise serializers.ValidationError(errors)

        return data


class NotExistingAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')

    def validate(self, data):
        errors = list()

        try:
            if CommunityEvent.objects.get(pk=data['community'].id):
                errors.append(serializers.ValidationError(
                    _('Albums are not able to be created under community events.'),
                    code='hierarchy_error'
                ))
        except CommunityEvent.DoesNotExist:
            pass

        if data['community_event'] is not None:
            try:
                if Event.objects.get(pk=data['community'].id) is not None:
                    errors.append(serializers.ValidationError(
                        _('Albums are not able to be linked to community events if created under an event.'),
                        code='hierarchy_error'
                    ))
            except Event.DoesNotExist:
                pass

            if data['community_event'].created_under.id != data['community'].id:
                errors.append(serializers.ValidationError(
                    _('Albums are not able to be linked to community events created under other communities.'),
                    code='hierarchy_error'
                ))

        if len(errors) > 0:
            raise serializers.ValidationError(errors)

        return data


class AlbumImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlbumImage
        fields = '__all__'
        read_only_fields = ('created_by',)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('created_by', 'event')
