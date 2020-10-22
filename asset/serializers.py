'''
    Asset Application Serializers
    asset/serializers.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.utils.translation import gettext as _
from rest_framework import serializers

from asset.models import Announcement, Album, Comment, AlbumImage
from community.models import Event, CommunityEvent
from core.utils import get_client_ip
from membership.models import Membership


class ExistingAnnouncementSerializer(serializers.ModelSerializer):
    ''' Existing announcement serializer '''
    is_able_to_edit = serializers.SerializerMethodField()

    class Meta:
        ''' Meta '''
        model = Announcement
        fields = '__all__'
        read_only_fields = ('community', 'created_by', 'updated_by')

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


class NotExistingAnnouncementSerializer(serializers.ModelSerializer):
    ''' Not existing announcement serializer '''
    class Meta:
        ''' Meta'''
        model = Announcement
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')

    def validate(self, data):
        ''' Validate data '''
        membership = Membership.objects.filter(
            user_id=self.context['request'].user.id,
            position__in=(1, 2, 3),
            community_id=data['community'].id,
            status='A'
        )

        if len(membership) == 0:
            raise serializers.ValidationError(
                _('Announcements are not able to be created in communities the user is not a staff.'),
                code='permission_denied'
            )

        return data


class ExistingAlbumSerializer(serializers.ModelSerializer):
    ''' Existing album serializer '''
    photo_amount = serializers.SerializerMethodField()
    is_able_to_edit = serializers.SerializerMethodField()

    class Meta:
        ''' Meta '''
        model = Album
        fields = '__all__'
        read_only_fields = ('community', 'created_by', 'updated_by')

    def validate(self, data):
        ''' Validate data '''
        if data['community_event'] is not None:
            try:
                if Event.objects.get(pk=data['community'].id) is not None:
                    raise serializers.ValidationError(
                        _('Albums are not able to be linked to community events if created under an event.'),
                        code='hierarchy_error'
                    )
            except Event.DoesNotExist:
                pass

            if data['community_event'].created_under.id != data['community'].id:
                raise serializers.ValidationError(
                    _('Albums are not able to be linked to community events created under other communities.'),
                    code='hierarchy_error'
                )

        return data

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


class NotExistingAlbumSerializer(serializers.ModelSerializer):
    ''' Not existing album serializer'''
    class Meta:
        ''' Meta '''
        model = Album
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')

    def validate(self, data):
        ''' Validate data '''
        try:
            if CommunityEvent.objects.get(pk=data['community'].id):
                raise serializers.ValidationError(
                    _('Albums are not able to be created under community events.'), code='hierarchy_error'
                )
        except CommunityEvent.DoesNotExist:
            pass

        if data['community_event'] is not None:
            try:
                if Event.objects.get(pk=data['community'].id) is not None:
                    raise serializers.ValidationError(
                        _('Albums are not able to be linked to community events if created under an event.'),
                        code='hierarchy_error'
                    )
            except Event.DoesNotExist:
                pass

            if data['community_event'].created_under.id != data['community'].id:
                raise serializers.ValidationError(
                    _('Albums are not able to be linked to community events created under other communities.'),
                    code='hierarchy_error'
                )

        return data


class AlbumImageSerializer(serializers.ModelSerializer):
    ''' Album image serializer'''
    class Meta:
        ''' Meta '''
        model = AlbumImage
        fields = '__all__'
        read_only_fields = ('created_by',)


class CommentSerializer(serializers.ModelSerializer):
    ''' Comment serializer '''
    class Meta:
        ''' Meta '''
        model = Comment
        fields = '__all__'
        read_only_fields = ('ip_address', 'created_by')

    def validate(self, data):
        ''' Validate data '''
        request = self.context['request']
        user = request.user
        event = data['event']

        # Restricts anonymous users from commenting on non-publicly visible events
        if not user.is_authenticated and not event.is_publicly_visible:
            raise serializers.ValidationError(
                _('Comments are not able to be made by an anonymous user in non-publicly visible events.'),
                code='comment_permission_error'
            )

        # Restricts event non-member users from commenting on community events that does not allow outside participators
        if isinstance(event, CommunityEvent) and not event.allows_outside_participators:
            try:
                Membership.objects.get(community_id=event.id, user_id=user.id, status__in=('A', 'R'))
            except Membership.DoesNotExist:
                raise serializers.ValidationError(
                    _('Comments are not able to be made by non-members in community events that does not allow ' +
                      'outside participators.'),
                    code='comment_permission_error'
                )

        # Retrieve comments from a specific event
        comments = Comment.objects.filter(event_id=event.id)

        # Restricts user making duplicated comments based on user ID if authenticated
        if user.is_authenticated and user.id in [i.created_by.id for i in comments.exclude(created_by=None)]:
            raise serializers.ValidationError(
                _('Comment from this user is already made in this event.'), code='comment_already_exists'
            )

        # Restricts user making duplicated comments based on IP address if not authenticated
        elif not user.is_authenticated and get_client_ip(request) in [i.ip_address for i in comments]:
            raise serializers.ValidationError(
                _('Comment from this IP Address is already made in this event.'), code='comment_already_exists'
            )

        return data
