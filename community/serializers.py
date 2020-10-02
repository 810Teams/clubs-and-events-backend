from django.utils.translation import gettext as _
from rest_framework import serializers

from community.models import Club, Event, CommunityEvent, Lab, Community
from membership.models import Membership


class OfficialClubSerializer(serializers.ModelSerializer):
    own_membership_id = serializers.SerializerMethodField()
    is_able_to_manage = serializers.SerializerMethodField()
    available_actions = serializers.SerializerMethodField()

    class Meta:
        model = Club
        fields = '__all__'
        read_only_fields = ('is_official', 'created_by', 'updated_by')

    def get_own_membership_id(self, obj):
        try:
            membership = Membership.objects.get(
                user_id=self.context['request'].user.id, community_id=obj.id, status__in=('A', 'R')
            )
            return membership.id
        except Membership.DoesNotExist:
            return None

    def get_is_able_to_manage(self, obj):
        try:
            Membership.objects.get(
                user_id=self.context['request'].user.id, position__in=(1, 2, 3), community_id=obj.id, status='A'
            )
            return True
        except Membership.DoesNotExist:
            return False

    def get_available_actions(self, obj):
        try:
            actions = list()
            membership = Membership.objects.get(
                user_id=self.context['request'].user.id, community_id=obj.id, status__in=('A', 'R')
            )

            if membership.position in (2, 3):
                actions.append('E')
            if membership.position != 3:
                actions.append('L')
                if membership.status == 'A':
                    actions.append('R')
                if membership.status == 'R':
                    actions.append('A')
            if membership.position == 3:
                actions.append('D')
            return actions
        except Membership.DoesNotExist:
            return list()


class UnofficialClubSerializer(serializers.ModelSerializer):
    own_membership_id = serializers.SerializerMethodField()
    is_able_to_manage = serializers.SerializerMethodField()
    available_actions = serializers.SerializerMethodField()

    class Meta:
        model = Club
        exclude = ('url_id', 'is_publicly_visible', 'room')
        read_only_fields = ('is_official', 'created_by', 'updated_by')

    def get_own_membership_id(self, obj):
        try:
            membership = Membership.objects.get(
                user_id=self.context['request'].user.id, community_id=obj.id, status__in=('A', 'R')
            )
            return membership.id
        except Membership.DoesNotExist:
            return None

    def get_is_able_to_manage(self, obj):
        try:
            Membership.objects.get(
                user_id=self.context['request'].user.id, position__in=(1, 2, 3), community_id=obj.id, status='A'
            )
            return True
        except Membership.DoesNotExist:
            return False

    def get_available_actions(self, obj):
        try:
            actions = list()
            membership = Membership.objects.get(
                user_id=self.context['request'].user.id, community_id=obj.id, status__in=('A', 'R')
            )

            if membership.position in (2, 3):
                actions.append('E')
            if membership.position != 3:
                actions.append('L')
                if membership.status == 'A':
                    actions.append('R')
                if membership.status == 'R':
                    actions.append('A')
            if membership.position == 3:
                actions.append('D')
            return actions
        except Membership.DoesNotExist:
            return list()


class ApprovedEventSerializer(serializers.ModelSerializer):
    own_membership_id = serializers.SerializerMethodField()
    is_able_to_manage = serializers.SerializerMethodField()
    available_actions = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ('is_approved', 'created_by', 'updated_by')

    def get_own_membership_id(self, obj):
        try:
            membership = Membership.objects.get(
                user_id=self.context['request'].user.id, community_id=obj.id, status__in=('A', 'R')
            )
            return membership.id
        except Membership.DoesNotExist:
            return None

    def get_is_able_to_manage(self, obj):
        try:
            Membership.objects.get(
                user_id=self.context['request'].user.id, position__in=(1, 2, 3), community_id=obj.id, status='A'
            )
            return True
        except Membership.DoesNotExist:
            return False

    def get_available_actions(self, obj):
        try:
            actions = list()
            membership = Membership.objects.get(
                user_id=self.context['request'].user.id, community_id=obj.id, status__in=('A', 'R')
            )

            if membership.position in (2, 3):
                actions.append('E')
            if membership.position != 3:
                actions.append('L')
                if membership.status == 'A':
                    actions.append('R')
                if membership.status == 'R':
                    actions.append('A')
            if membership.position == 3:
                actions.append('D')
            return actions
        except Membership.DoesNotExist:
            return list()


class UnapprovedEventSerializer(serializers.ModelSerializer):
    own_membership_id = serializers.SerializerMethodField()
    is_able_to_manage = serializers.SerializerMethodField()
    available_actions = serializers.SerializerMethodField()

    class Meta:
        model = Event
        exclude = ('url_id', 'is_publicly_visible')
        read_only_fields = ('is_approved', 'created_by', 'updated_by')

    def get_own_membership_id(self, obj):
        try:
            membership = Membership.objects.get(
                user_id=self.context['request'].user.id, community_id=obj.id, status__in=('A', 'R')
            )
            return membership.id
        except Membership.DoesNotExist:
            return None

    def get_is_able_to_manage(self, obj):
        try:
            Membership.objects.get(
                user_id=self.context['request'].user.id, position__in=(1, 2, 3), community_id=obj.id, status='A'
            )
            return True
        except Membership.DoesNotExist:
            return False

    def get_available_actions(self, obj):
        try:
            actions = list()
            membership = Membership.objects.get(
                user_id=self.context['request'].user.id, community_id=obj.id, status__in=('A', 'R')
            )

            if membership.position in (2, 3):
                actions.append('E')
            if membership.position != 3:
                actions.append('L')
                if membership.status == 'A':
                    actions.append('R')
                if membership.status == 'R':
                    actions.append('A')
            if membership.position == 3:
                actions.append('D')
            return actions
        except Membership.DoesNotExist:
            return list()


class ExistingCommunityEventSerializer(serializers.ModelSerializer):
    own_membership_id = serializers.SerializerMethodField()
    is_able_to_manage = serializers.SerializerMethodField()
    available_actions = serializers.SerializerMethodField()

    class Meta:
        model = CommunityEvent
        fields = '__all__'
        read_only_fields = ('is_approved', 'created_under', 'created_by', 'updated_by')

    def get_own_membership_id(self, obj):
        try:
            membership = Membership.objects.get(
                user_id=self.context['request'].user.id, community_id=obj.id, status__in=('A', 'R')
            )
            return membership.id
        except Membership.DoesNotExist:
            return None

    def get_is_able_to_manage(self, obj):
        try:
            Membership.objects.get(
                user_id=self.context['request'].user.id, position__in=(1, 2, 3), community_id=obj.id, status='A'
            )
            return True
        except Membership.DoesNotExist:
            return False

    def get_available_actions(self, obj):
        try:
            actions = list()
            membership = Membership.objects.get(
                user_id=self.context['request'].user.id, community_id=obj.id, status__in=('A', 'R')
            )

            if membership.position in (2, 3):
                actions.append('E')
            if membership.position != 3:
                actions.append('L')
                if membership.status == 'A':
                    actions.append('R')
                if membership.status == 'R':
                    actions.append('A')
            if membership.position == 3:
                actions.append('D')
            return actions
        except Membership.DoesNotExist:
            return list()


class NotExistingCommunityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityEvent
        fields = '__all__'
        read_only_fields = ('is_approved', 'created_by', 'updated_by')

    def validate(self, data):
        base_community = Community.objects.get(pk=data['created_under'].id)
        base_membership = Membership.objects.filter(
            user_id=self.context['request'].user.id, position__in=[1, 2, 3], community_id=base_community.id, status='A'
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


class LabSerializer(serializers.ModelSerializer):
    own_membership_id = serializers.SerializerMethodField()
    is_able_to_manage = serializers.SerializerMethodField()
    available_actions = serializers.SerializerMethodField()

    class Meta:
        model = Lab
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')

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

    def get_own_membership_id(self, obj):
        try:
            membership = Membership.objects.get(
                user_id=self.context['request'].user.id, community_id=obj.id, status__in=('A', 'R')
            )
            return membership.id
        except Membership.DoesNotExist:
            return None

    def get_is_able_to_manage(self, obj):
        try:
            Membership.objects.get(
                user_id=self.context['request'].user.id, position__in=(1, 2, 3), community_id=obj.id, status='A'
            )
            return True
        except Membership.DoesNotExist:
            return False

    def get_available_actions(self, obj):
        try:
            actions = list()
            membership = Membership.objects.get(
                user_id=self.context['request'].user.id, community_id=obj.id, status__in=('A', 'R')
            )

            if membership.position in (2, 3):
                actions.append('E')
            if membership.position != 3:
                actions.append('L')
                if membership.status == 'A':
                    actions.append('R')
                if membership.status == 'R':
                    actions.append('A')
            if membership.position == 3:
                actions.append('D')
            return actions
        except Membership.DoesNotExist:
            return list()
