'''
    Asset Application Serializers
    asset/serializers.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.utils.translation import gettext as _
from rest_framework import serializers

from asset.models import Announcement, Album, Comment, AlbumImage
from community.models import Event, CommunityEvent
from core.permissions import IsStaffOfCommunity
from core.utils import get_client_ip, has_instance
from core.utils import add_error_message, validate_profanity_serializer, raise_validation_errors
from membership.models import Membership


class AnnouncementSerializerTemplate(serializers.ModelSerializer):
    ''' Announcement serializer template '''
    class Meta:
        ''' Meta '''
        model = Announcement
        fields = '__all__'
        abstract = True

    def validate(self, data, get_errors=False):
        ''' Validate data '''
        errors = dict()

        validate_profanity_serializer(data, 'text', errors, field_name='Announcement text')

        if get_errors:
            return errors

        raise_validation_errors(errors)

        return data


class ExistingAnnouncementSerializer(AnnouncementSerializerTemplate):
    ''' Existing announcement serializer '''
    # TODO: Remove `is_able_to_edit` when the front-end is able to fix the bug where calling `meta` is undefined.
    meta = serializers.SerializerMethodField()
    is_able_to_edit = serializers.SerializerMethodField()

    class Meta:
        ''' Meta '''
        model = Announcement
        fields = '__all__'
        read_only_fields = ('community', 'created_by', 'updated_by')

    def validate(self, data, get_errors=False):
        ''' Validate data '''
        errors = super(ExistingAnnouncementSerializer, self).validate(data, get_errors=True)

        raise_validation_errors(errors)

        return data

    def get_meta(self, obj):
        ''' Retrieve meta data '''
        return {
            'is_able_to_edit': self.get_is_able_to_edit(obj)
        }

    def get_is_able_to_edit(self, obj):
        ''' Retrieve edit-ability '''
        try:
            Membership.objects.get(
                user_id=self.context['request'].user.id,
                position__in=(1, 2, 3),
                community_id=obj.community.id,
                status='A'
            )
            return True
        except Membership.DoesNotExist:
            return False


class NotExistingAnnouncementSerializer(AnnouncementSerializerTemplate):
    ''' Not existing announcement serializer '''
    class Meta:
        ''' Meta'''
        model = Announcement
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')

    def validate(self, data, get_errors=False):
        ''' Validate data '''
        errors = super(NotExistingAnnouncementSerializer, self).validate(data, get_errors=True)

        membership = Membership.objects.filter(
            user_id=self.context['request'].user.id,
            position__in=(1, 2, 3),
            community_id=data['community'].id,
            status='A'
        )

        if len(membership) == 0:
            errors['community'] = _('Announcements are not able to be created in communities the user is not a staff.')

        raise_validation_errors(errors)

        return data


class AlbumSerializerTemplate(serializers.ModelSerializer):
    ''' Album serializer template '''
    class Meta:
        ''' Meta '''
        model = Album
        fields = '__all__'
        abstract = True

    def validate(self, data, get_errors=False):
        ''' Validate data '''
        errors = dict()

        validate_profanity_serializer(data, 'name', errors, field_name='Album name')

        # Validates community event linking
        if 'community_event' in data.keys() and data['community_event'] is not None:
            # In case of PATCH request, the community field might not be sent.
            if 'community' not in data.keys():
                data['community'] = Album.objects.get(pk=self.instance.id).community

            if has_instance(data['community'], Event):
                add_error_message(
                    errors, key='community_event',
                    message='Albums are not able to be linked to community events if created under an event.'
                )

            if data['community_event'].created_under.id != data['community'].id:
                add_error_message(
                    errors, key='community_event',
                    message='Albums are not able to be linked to community events created under other communities.'
                )

        if get_errors:
            return errors

        raise_validation_errors(errors)

        return data


class ExistingAlbumSerializer(AlbumSerializerTemplate):
    ''' Existing album serializer '''
    meta = serializers.SerializerMethodField()

    class Meta:
        ''' Meta '''
        model = Album
        fields = '__all__'
        read_only_fields = ('community', 'created_by', 'updated_by')

    def validate(self, data, get_errors=False):
        ''' Validate data '''
        errors = super(ExistingAlbumSerializer, self).validate(data, get_errors=True)

        raise_validation_errors(errors)

        return data

    def get_meta(self, obj):
        ''' Retrieve meta data '''
        return {
            'photo_amount': self.get_photo_amount(obj),
            'is_able_to_edit': self.get_is_able_to_edit(obj)
        }

    def get_photo_amount(self, obj):
        ''' Retrieve photos amount '''
        return len(AlbumImage.objects.filter(album_id=obj.id))

    def get_is_able_to_edit(self, obj):
        ''' Retrieve edit-ability '''
        try:
            Membership.objects.get(
                user_id=self.context['request'].user.id,
                position__in=(1, 2, 3),
                community_id=obj.community.id,
                status='A'
            )
            return True
        except Membership.DoesNotExist:
            return False


class NotExistingAlbumSerializer(AlbumSerializerTemplate):
    ''' Not existing album serializer'''
    class Meta:
        ''' Meta '''
        model = Album
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')

    def validate(self, data, get_errors=False):
        ''' Validate data '''
        errors = super(NotExistingAlbumSerializer, self).validate(data, get_errors=True)

        if has_instance(data['community'], CommunityEvent):
            errors['community'] = (_('Albums are not able to be created under community events.'))

        raise_validation_errors(errors)

        return data


class AlbumImageSerializer(serializers.ModelSerializer):
    ''' Album image serializer'''
    class Meta:
        ''' Meta '''
        model = AlbumImage
        fields = '__all__'
        read_only_fields = ('created_by',)

    def validate(self, data):
        ''' Validate data '''
        errors = dict()

        if not IsStaffOfCommunity().has_object_permission(self.context['request'], None, data['album']):
            add_error_message(
                errors, key='album',
                message='Album images can only be created or deleted by staff of the community the album is created in.'
            )

        raise_validation_errors(errors)

        return data


class CommentSerializer(serializers.ModelSerializer):
    ''' Comment serializer '''
    class Meta:
        ''' Meta '''
        model = Comment
        exclude = ('created_by', 'ip_address')

    def validate(self, data):
        ''' Validate data '''
        errors = dict()

        request = self.context['request']
        user = request.user
        event = data['event']

        # Restricts anonymous users from commenting on non-publicly visible events
        if not user.is_authenticated and not event.is_publicly_visible:
            add_error_message(
                errors, key='event',
                message='Comments are not able to be made by an anonymous user in non-publicly visible events.'
            )

        # Restricts event non-member users from commenting on community events that does not allow outside participators
        if isinstance(event, CommunityEvent) and not event.allows_outside_participators:
            try:
                Membership.objects.get(community_id=event.id, user_id=user.id, status__in=('A', 'R'))
            except Membership.DoesNotExist:
                add_error_message(
                    errors, key='event',
                    message='Comments are not able to be made by non-members in community events that does not allow ' +
                            'outside participators.'
                )

        # Retrieve comments from a specific event
        comments = Comment.objects.filter(event_id=event.id)

        # Restricts user making duplicated comments based on user ID if authenticated
        if user.is_authenticated and user.id in [i.created_by.id for i in comments.exclude(created_by=None)]:
            add_error_message(errors, key='event', message='Comment from this user is already made in this event.')

        # Restricts user making duplicated comments based on IP address if not authenticated
        if not user.is_authenticated and get_client_ip(request) in [i.ip_address for i in comments]:
            add_error_message(
                errors, key='event', message='Comment from this IP Address is already made in this event.'
            )

        # Check profanity
        validate_profanity_serializer(data, 'text', errors, field_name='Comment text')
        validate_profanity_serializer(data, 'written_by', errors, field_name='Writer\'s name')

        # Raise errors
        raise_validation_errors(errors)

        return data
