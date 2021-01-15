'''
    Asset Application Serializers
    asset/serializers.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import serializers

from asset.models import Announcement, Album, Comment, AlbumImage
from clubs_and_events.settings import COMMENT_LIMIT_PER_INTERVAL, COMMENT_INTERVAL_TIME
from community.models import Event, CommunityEvent
from community.permissions import IsPubliclyVisibleCommunity
from core.permissions import IsStaffOfCommunity, IsMemberOfCommunity
from core.utils.general import has_instance
from core.utils.serializer import add_error_message, validate_profanity_serializer, raise_validation_errors
from core.utils.serializer import field_exists
from core.utils.users import get_client_ip


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
        return IsStaffOfCommunity().has_object_permission(self.context['request'], None, obj)


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

        if not IsStaffOfCommunity().has_object_permission(self.context['request'], None, data['community']):
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
        if field_exists(data, 'community_event'):
            # In case of PATCH request, the community field might not be sent.
            if not field_exists(data, 'community'):
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
        return IsStaffOfCommunity().has_object_permission(self.context['request'], None, obj)


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

        if not IsStaffOfCommunity().has_object_permission(self.context['request'], None, data['community']):
            errors['community'] = _('Albums are not able to be created in communities the user is not a staff.')

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
        if not IsPubliclyVisibleCommunity().has_object_permission(request, None, event):
            add_error_message(
                errors, key='event',
                message='Comments are not able to be made by an anonymous user in non-publicly visible events.'
            )

        # Restricts event non-member users from commenting on community events that does not allow outside participators
        if has_instance(event, CommunityEvent):
            community_event = CommunityEvent.objects.get(pk=event.id)
            if not community_event.allows_outside_participators:
                if not IsMemberOfCommunity().has_object_permission(request, None, community_event):
                    add_error_message(
                        errors, key='event',
                        message='Comments are not able to be made by non-members in community events that does not ' +
                                'allow outside participators.'
                    )

        # Retrieve comments from a specific event
        comments = Comment.objects.filter(event_id=event.id)

        # Restricts user making a comment if a URL is included
        validate = URLValidator()
        for i in data['text'].split():
            try:
                validate(i)
                add_error_message(errors, key='text', message='Comments are not able to contain a URL.')
                break
            except ValidationError:
                pass

        # Restricts user making too many comments based on user ID if authenticated, or IP address if unauthenticated
        if user.is_authenticated:
            user_comments = comments.filter(created_by_id=user.id).order_by('created_at')
        else:
            user_comments = comments.filter(ip_address=get_client_ip(request)).order_by('created_at')

        if len(user_comments) >= COMMENT_LIMIT_PER_INTERVAL:
            target_comment = user_comments[len(user_comments) - COMMENT_LIMIT_PER_INTERVAL]
            if target_comment.created_at + timedelta(minutes=COMMENT_INTERVAL_TIME) > timezone.now():
                add_error_message(
                    errors, key='event',
                    message='Comments from this user has reached the limit. Please try again after a while.'
                )

        # Check profanity
        validate_profanity_serializer(data, 'text', errors, field_name='Comment text')
        validate_profanity_serializer(data, 'written_by', errors, field_name='Writer\'s name')

        # Raise errors
        raise_validation_errors(errors)

        return data
