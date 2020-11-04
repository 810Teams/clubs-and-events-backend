'''
    Community Application Serializers
    community/serializers.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from rest_framework import serializers

from asset.models import Comment
from community.models import Community, Club, Event, CommunityEvent, Lab
from community.permissions import IsRenewableClub, IsAbleToDeleteClub, IsAbleToDeleteEvent
from community.permissions import IsAbleToDeleteCommunityEvent, IsAbleToDeleteLab
from core.utils import get_client_ip, has_instance
from core.utils import add_error_message, validate_profanity_serializer, raise_validation_errors
from core.validators import is_th, is_en
from membership.models import Membership, ApprovalRequest


class CommunitySerializerTemplate(serializers.ModelSerializer):
    ''' Community serializer template'''
    meta = serializers.SerializerMethodField()

    class Meta:
        ''' Meta '''
        model = Community
        fields = '__all__'
        abstract = True

    def validate(self, data, get_errors=False):
        ''' Validate data '''
        errors = dict()

        validate_profanity_serializer(data, 'name_th', errors, field_name='Community\'s Thai name', lang=('th',))
        validate_profanity_serializer(data, 'name_en', errors, field_name='Community\'s English name', lang=('en',))
        validate_profanity_serializer(data, 'url_id', errors, field_name='URL ID')
        validate_profanity_serializer(data, 'description', errors, field_name='Community description')

        # Community Thai name language and length validation
        if len(data['name_th']) < 4:
            add_error_message(errors, 'name_th', 'Community name must be at least 4 characters in length.')
        elif not is_th(data['name_th']):
            add_error_message(errors, 'name_th', 'This field must be in the Thai language.')

        # Community English name language and length validation
        if len(data['name_en']) < 4:
            add_error_message(errors, 'name_en', 'Community name must be at least 4 characters in length.')
        elif not is_en(data['name_en']):
            add_error_message(errors, 'name_en', 'This field must be in English.')

        # External links validation
        if 'external_links' in data.keys() and data['external_links'] is not None:
            urls = [
                i.replace('\r', str()) for i in data['external_links'].split('\n')
                if i.replace('\r', str()).strip() != str()
            ]
            validate = URLValidator()

            for i in urls:
                try:
                    validate(i)
                except ValidationError:
                    errors['external_links'] = _(
                        'External links contains an invalid URL. Each URL must be written on a new line.'
                    )

            data['external_links'] = '\r\n'.join(urls)

        # URL ID validation
        if 'url_id' in data.keys() and data['url_id'] is not None and len(data['url_id']) > 0:
            allowed_characters = 'abcdefghijklmnopqrsstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.'

            for i in data['url_id']:
                if i not in allowed_characters:
                    add_error_message(
                        errors, key='url_id',
                        message='URL ID must only contain alphabetical characters, numbers, and dots'
                    )
                    break

            if data['url_id'][0] == '.' or data['url_id'][-1] in '.':
                add_error_message(
                    errors, key='url_id', message='URL ID must start and end with an alphanumerical character.'
                )

            if len(data['url_id']) < 4:
                add_error_message(errors, key='url_id', message='URL ID must be at least 4 characters in length.')

            if '..' in data['url_id']:
                add_error_message(
                    errors, key='url_id', message='URL ID is not able to contain consecutive special characters.'
                )
        elif 'url_id' in data.keys() and data['url_id'] is not None and data['url_id'].strip() == str():
            data['url_id'] = None

        # Return errors
        if get_errors:
            return errors

        raise_validation_errors(errors)

        return data


    def get_meta(self, obj):
        ''' Retrieve meta data '''
        return {
            'community_type': self.get_community_type(obj),
            'own_membership_id': self.get_own_membership_id(obj),
            'own_membership_position': self.get_own_membership_position(obj),
            'available_actions': self.get_available_actions(obj)
        }

    def get_community_type(self, obj):
        ''' Retrieve community type '''
        if has_instance(obj, Club):
            return 'club'
        elif has_instance(obj, Event) and not has_instance(obj, CommunityEvent):
            return 'event'
        elif has_instance(obj, CommunityEvent):
            return 'community_event'
        elif has_instance(obj, Lab):
            return 'lab'

        return None


    def get_own_membership_id(self, obj):
        ''' Retrieve own membership ID '''
        try:
            membership = Membership.objects.get(
                user_id=self.context['request'].user.id, community_id=obj.id, status__in=('A', 'R')
            )
            return membership.id
        except Membership.DoesNotExist:
            return None

    def get_own_membership_position(self, obj):
        ''' Retrieve own membership position '''
        try:
            membership = Membership.objects.get(
                user_id=self.context['request'].user.id, community_id=obj.id, status='A'
            )
            return membership.position
        except Membership.DoesNotExist:
            return None

    def get_available_actions(self, obj):
        ''' Retrieve available actions '''
        request = self.context['request']
        user = request.user
        actions = list()

        try:
            # Fetch membership
            membership = Membership.objects.get(user_id=user.id, community_id=obj.id, status__in=('A', 'R'))

            # Try retrieving base membership
            if has_instance(obj, CommunityEvent):
                try:
                    base_membership = Membership.objects.get(
                        user_id=user.id,
                        community_id=CommunityEvent.objects.get(pk=obj.id).created_under.id,
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

            # If the user is the leader, check for delete community and send/cancel approval request permissions.
            if membership.position == 3 or (base_membership is not None and base_membership.position == 3):
                # If the community is available for deletion.
                if isinstance(obj, Club) and IsAbleToDeleteClub().has_object_permission(request, None, obj):
                    actions.append('delete')
                elif isinstance(obj, Event) and not isinstance(obj, CommunityEvent) \
                        and IsAbleToDeleteEvent().has_object_permission(request, None, obj):
                    actions.append('delete')
                elif isinstance(obj, CommunityEvent) \
                        and IsAbleToDeleteCommunityEvent().has_object_permission(request, None, obj):
                    actions.append('delete')
                elif isinstance(obj, Lab) and IsAbleToDeleteLab().has_object_permission(request, None, obj):
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

        except Membership.DoesNotExist:
            pass

        # Check if the community is event, and able to comment on the current session.
        if isinstance(obj, Event):
            is_able_to_comment = True

            if not user.is_authenticated and not obj.is_publicly_visible:
                is_able_to_comment = False
            if has_instance(obj, CommunityEvent) \
                    and not CommunityEvent.objects.get(pk=obj.id).allows_outside_participators:
                try:
                    Membership.objects.get(community_id=obj.id, user_id=user.id, status__in=('A', 'R'))
                except Membership.DoesNotExist:
                    is_able_to_comment = False

            commentators = Comment.objects.filter(event_id=obj.id)

            if user.is_authenticated and user.id in [i.created_by.id for i in commentators.exclude(created_by=None)]:
                is_able_to_comment = False
            elif not user.is_authenticated and get_client_ip(request) in [i.ip_address for i in commentators]:
                is_able_to_comment = False

            if is_able_to_comment:
                actions.append('comment')

        return actions


class CommunitySerializer(CommunitySerializerTemplate):
    ''' Community serializer '''
    class Meta:
        ''' Meta '''
        model = Community
        exclude = ('created_at', 'updated_at', 'created_by', 'updated_by')

    def get_meta(self, obj):
        ''' Retrieve meta data '''
        return {
            'community_type': self.get_community_type(obj)
        }


class OfficialClubSerializer(CommunitySerializerTemplate):
    ''' Official club serializer '''
    class Meta:
        ''' Meta '''
        model = Club
        exclude = ('created_at', 'updated_at', 'created_by', 'updated_by')
        read_only_fields = ('is_official', 'valid_through')

    def validate(self, data, get_errors=False):
        errors = super(OfficialClubSerializer, self).validate(data, get_errors=True)

        validate_profanity_serializer(data, 'room', errors, field_name='Club room')

        raise_validation_errors(errors)

        # Data Cleaning
        if 'room' in data.keys() and data['room'] is not None and data['room'].strip() == str():
            data['room'] = None

        return data


class UnofficialClubSerializer(CommunitySerializerTemplate):
    ''' Unofficial club serializer '''
    class Meta:
        ''' Meta '''
        model = Club
        exclude = ('url_id', 'is_publicly_visible', 'room', 'created_at', 'updated_at', 'created_by', 'updated_by')
        read_only_fields = ('is_official', 'valid_through')


class ApprovedEventSerializer(CommunitySerializerTemplate):
    ''' Approved event serializer '''
    class Meta:
        ''' Meta '''
        model = Event
        exclude = ('created_at', 'updated_at', 'created_by', 'updated_by')
        read_only_fields = ('is_approved',)

    def validate(self, data, get_errors=False):
        errors = super(ApprovedEventSerializer, self).validate(data, get_errors=True)

        validate_profanity_serializer(data, 'location', errors, field_name='Event location')

        raise_validation_errors(errors)

        return data


class UnapprovedEventSerializer(CommunitySerializerTemplate):
    ''' Unapproved event serializer '''
    class Meta:
        ''' Meta '''
        model = Event
        exclude = ('url_id', 'is_publicly_visible', 'created_at', 'updated_at', 'created_by', 'updated_by')
        read_only_fields = ('is_approved',)

    def validate(self, data, get_errors=False):
        errors = super(UnapprovedEventSerializer, self).validate(data, get_errors=True)

        validate_profanity_serializer(data, 'location', errors, field_name='Event location')

        raise_validation_errors(errors)

        return data


class ExistingCommunityEventSerializer(CommunitySerializerTemplate):
    ''' Existing community event serializer '''
    meta = serializers.SerializerMethodField()
    
    class Meta:
        ''' Meta '''
        model = CommunityEvent
        exclude = ('created_at', 'updated_at', 'created_by', 'updated_by')
        read_only_fields = ('is_approved', 'created_under')

    def validate(self, data, get_errors=False):
        errors = super(ExistingCommunityEventSerializer, self).validate(data, get_errors=True)

        validate_profanity_serializer(data, 'location', errors, field_name='Event location')

        raise_validation_errors(errors)

        return data

    def get_meta(self, obj):
        meta = super(ExistingCommunityEventSerializer, self).get_meta(obj)
        meta['created_under_name_en'] = obj.created_under.name_en

        return meta


class NotExistingCommunityEventSerializer(CommunitySerializerTemplate):
    ''' Not existing community event serializer '''
    class Meta:
        ''' Meta '''
        model = CommunityEvent
        exclude = ('created_at', 'updated_at', 'created_by', 'updated_by')
        read_only_fields = ('is_approved',)

    def validate(self, data, get_errors=False):
        ''' Validate data '''
        errors = super(NotExistingCommunityEventSerializer, self).validate(data, get_errors=True)

        validate_profanity_serializer(data, 'location', errors, field_name='Event location')

        # Creation permission validation
        base_community = Community.objects.get(pk=data['created_under'].id)
        base_membership = Membership.objects.filter(
            user_id=self.context['request'].user.id, position__in=(1, 2, 3), community_id=base_community.id, status='A'
        )

        if len(base_membership) != 1:
            add_error_message(
                errors, message='Community events are not able to be created under communities you are not a staff.'
            )

        try:
            if not Club.objects.get(pk=data['created_under']).is_official:
                add_error_message(
                    errors,
                    key='created_under',
                    message='Community events are not able to be created under communities you are not a staff.'
                )
        except Club.DoesNotExist:
            pass

        # Parent community validation
        if has_instance(data['created_under'], Event):
            add_error_message(
                errors, key='created_under', message='Community events are not able to be created under events.'
            )

        raise_validation_errors(errors)

        return data


class LabSerializer(CommunitySerializerTemplate):
    ''' Lab serializer '''
    class Meta:
        ''' Meta '''
        model = Lab
        exclude = ('created_at', 'updated_at', 'created_by', 'updated_by')

    def validate(self, data, get_errors=False):
        ''' Validate data '''
        errors = super(LabSerializer, self).validate(data, get_errors=True)

        validate_profanity_serializer(data, 'room', errors, field_name='Lab room')
        validate_profanity_serializer(data, 'tags', errors, field_name='Tags')

        # Tags validation
        characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-., '

        if 'tags' in data.keys() and data['tags'] is not None:
            for i in data['tags']:
                if i not in characters:
                    add_error_message(
                        errors, key='tags',
                        message='Tags must only consist of alphabetical characters, numbers, dashes, dots, and ' +
                                'spaces. Each tag are separated by commas.'
                    )
                    break

        # Raise validation errors
        raise_validation_errors(errors)

        # Data cleaning
        if 'room' in data.keys() and data['room'] is not None and data['room'].strip() == str():
            data['room'] = None

        return data
