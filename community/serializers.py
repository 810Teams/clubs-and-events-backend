from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from rest_framework import serializers

from community.models import Community, Club, Event, CommunityEvent, Lab
from community.permissions import IsRenewableClub, IsAbleToDeleteClub, IsAbleToDeleteEvent
from community.permissions import IsAbleToDeleteCommunityEvent, IsAbleToDeleteLab
from membership.models import Membership, ApprovalRequest


class CommunitySerializerTemplate(serializers.ModelSerializer):
    community_type = serializers.SerializerMethodField()
    own_membership_id = serializers.SerializerMethodField()
    own_membership_position = serializers.SerializerMethodField()
    available_actions = serializers.SerializerMethodField()

    def validate(self, data):
        if 'external_links' in data.keys() and data['external_links'] is not None:
            urls = [i.replace('\r', '') for i in data['external_links'].split('\n') if i.strip() != '']
            validate = URLValidator()

            for i in urls:
                try:
                    validate(i)
                except ValidationError:
                    raise serializers.ValidationError(
                        _('External links contains an invalid URL. Each URL must be written on a new line.'),
                        code='invalid_url'
                    )

        return data


    def get_community_type(self, obj):
        try:
            Club.objects.get(pk=obj.id)
            return 'club'
        except Club.DoesNotExist:
            pass

        try:
            CommunityEvent.objects.get(pk=obj.id)
            return 'community_event'
        except CommunityEvent.DoesNotExist:
            pass

        try:
            Event.objects.get(pk=obj.id)
            return 'event'
        except Event.DoesNotExist:
            pass

        try:
            Lab.objects.get(pk=obj.id)
            return 'lab'
        except Lab.DoesNotExist:
            pass

        return None


    def get_own_membership_id(self, obj):
        try:
            membership = Membership.objects.get(
                user_id=self.context['request'].user.id, community_id=obj.id, status__in=('A', 'R')
            )
            return membership.id
        except Membership.DoesNotExist:
            return None

    def get_own_membership_position(self, obj):
        try:
            membership = Membership.objects.get(
                user_id=self.context['request'].user.id, community_id=obj.id, status='A'
            )
            return membership.position
        except Membership.DoesNotExist:
            return None

    def get_available_actions(self, obj):
        request = self.context['request']

        try:
            # Declare an empty action list and fetch a membership
            actions = list()
            membership = Membership.objects.get(user_id=request.user.id, community_id=obj.id, status__in=('A', 'R'))

            # Try retrieving base membership
            if isinstance(obj, CommunityEvent):
                try:
                    base_membership = Membership.objects.get(
                        user_id=request.user.id,
                        community_id=obj.created_under.id,
                        status__in=('A', 'R')
                    )
                except Membership.DoesNotExist:
                    base_membership = None
            else:
                base_membership = None

            # If the user is a deputy leader or leader, the user can edit the community.
            if membership.position in (2, 3) or (base_membership is not None and base_membership.position in (2, 3)):
                actions.append('edit')

            # If the user is not the leader, the user can leave the community.
            if membership.position != 3:
                actions.append('leave')

                # The user can switch between being active and retired.
                if membership.status == 'A':
                    actions.append('retire')
                if membership.status == 'R':
                    actions.append('active')

            # If the user is the leader...
            if membership.position == 3 or (base_membership is not None and base_membership.position == 3):
                # If the community is available for deletion.
                if isinstance(obj, Club):
                    if IsAbleToDeleteClub().has_object_permission(request, None, obj):
                        actions.append('delete')
                elif isinstance(obj, Event) and not isinstance(obj, CommunityEvent):
                    if IsAbleToDeleteEvent().has_object_permission(request, None, obj):
                        actions.append('delete')
                elif isinstance(obj, CommunityEvent):
                    if IsAbleToDeleteCommunityEvent().has_object_permission(request, None, obj):
                        actions.append('delete')
                elif isinstance(obj, Lab):
                    if IsAbleToDeleteLab().has_object_permission(request, None, obj):
                        actions.append('delete')

                # If the object is an unofficial or a renewable club, check for actions related to approval requests.
                if isinstance(obj, Club) and IsRenewableClub().has_object_permission(request, None, obj):
                    try:
                        ApprovalRequest.objects.get(community_id=obj.id, status='W')
                        actions.append('cancel-approval-request')
                    except ApprovalRequest.DoesNotExist:
                        actions.append('send-approval-request')

                # If the object is an unapproved event, check for actions related to approval requests.
                if isinstance(obj, Event) and not obj.is_approved:
                    try:
                        ApprovalRequest.objects.get(community_id=obj.id, status='W')
                        actions.append('cancel-approval-request')
                    except ApprovalRequest.DoesNotExist:
                        actions.append('send-approval-request')

            return actions
        except Membership.DoesNotExist:
            return list()


class CommunitySerializer(CommunitySerializerTemplate):
    class Meta:
        model = Community
        fields = '__all__'


class OfficialClubSerializer(CommunitySerializerTemplate):
    class Meta:
        model = Club
        fields = '__all__'
        read_only_fields = ('is_official', 'valid_through', 'created_by', 'updated_by')


class UnofficialClubSerializer(CommunitySerializerTemplate):
    class Meta:
        model = Club
        exclude = ('url_id', 'is_publicly_visible', 'room')
        read_only_fields = ('is_official', 'created_by', 'updated_by')


class ApprovedEventSerializer(CommunitySerializerTemplate):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ('is_approved', 'created_by', 'updated_by')


class UnapprovedEventSerializer(CommunitySerializerTemplate):
    class Meta:
        model = Event
        exclude = ('url_id', 'is_publicly_visible')
        read_only_fields = ('is_approved', 'created_by', 'updated_by')


class ExistingCommunityEventSerializer(CommunitySerializerTemplate):
    class Meta:
        model = CommunityEvent
        fields = '__all__'
        read_only_fields = ('is_approved', 'created_under', 'created_by', 'updated_by')


class NotExistingCommunityEventSerializer(ExistingCommunityEventSerializer):
    class Meta:
        model = CommunityEvent
        fields = '__all__'
        read_only_fields = ('is_approved', 'created_by', 'updated_by')

    def validate(self, data):
        super(NotExistingCommunityEventSerializer, self).validate(data)

        base_community = Community.objects.get(pk=data['created_under'].id)
        base_membership = Membership.objects.filter(
            user_id=self.context['request'].user.id, position__in=(1, 2, 3), community_id=base_community.id, status='A'
        )

        if len(base_membership) != 1:
            raise serializers.ValidationError(
                _('Community events are not able to be created under communities you are not a staff.'),
                code='permission_denied'
            )

        try:
            if not Club.objects.get(pk=data['created_under']).is_official:
                raise serializers.ValidationError(
                    _('Community events are not able to be created under unofficial clubs.'),
                    code='unofficial_club_limitations'
                )
        except Club.DoesNotExist:
            pass

        try:
            Event.objects.get(pk=data['created_under'])
            raise serializers.ValidationError(
                _('Community events are not able to be created under events.'),
                code='hierarchy_error'
            )
        except Event.DoesNotExist:
            pass

        return data


class LabSerializer(CommunitySerializerTemplate):
    class Meta:
        model = Lab
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')

    def validate(self, data):
        super(LabSerializer, self).validate(data)

        characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-., '

        if 'tags' in data.keys() and data['tag'] is not None:
            for i in data['tags']:
                if i not in characters:
                    raise serializers.ValidationError(
                        _('Tags must only consist of alphabetical characters, numbers, dashes, dots, and spaces. ' +
                          'Each tag are separated by commas.'),
                        code='invalid_tags'
                    )

        return data

    def create(self, validated_data):
        if 'url_id' in validated_data.keys() and validated_data['url_id'].strip() == '':
            validated_data['url_id'] = None
        if 'room' in validated_data.keys() and validated_data['room'].strip() == '':
            validated_data['room'] = None

        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if 'url_id' in validated_data.keys() and validated_data['url_id'].strip() == '':
            validated_data['url_id'] = None
        if 'room' in validated_data.keys() and validated_data['room'].strip() == '':
            validated_data['room'] = None

        instance.__dict__.update(**validated_data)
        instance.save()

        return instance
