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
from clubs_and_events.settings import VOTE_LIMIT_PER_EVENT
from community.models import Community, Club, Event, CommunityEvent, Lab
from community.permissions import IsRenewableClub, IsAbleToDeleteClub, IsAbleToDeleteEvent, IsPubliclyVisibleCommunity
from community.permissions import IsMemberOfBaseCommunity, IsAbleToDeleteCommunityEvent, IsAbleToDeleteLab
from core.permissions import IsMemberOfCommunity, IsStaffOfCommunity, IsInActiveCommunity
from core.utils.general import has_instance
from core.utils.serializer import add_error_message, validate_profanity_serializer, raise_validation_errors
from core.utils.serializer import field_exists, clean_field, is_valid_club, is_ended_event
from core.utils.users import get_client_ip
from core.utils.nlp import is_th, is_en
from membership.models import Membership, ApprovalRequest, Invitation, Request
from misc.models import Vote
from user.permissions import IsStudent, IsLecturer


class CommunitySerializerTemplate(serializers.ModelSerializer):
    ''' Community serializer template'''
    meta = serializers.SerializerMethodField()

    class Meta:
        ''' Meta '''
        model = Community
        exclude = ('is_active',)
        abstract = True

    def validate(self, data, get_errors=False):
        ''' Validate data '''
        errors = dict()

        validate_profanity_serializer(data, 'name_th', errors, field_name='Community\'s Thai name', lang=('th',))
        validate_profanity_serializer(data, 'name_en', errors, field_name='Community\'s English name', lang=('en',))
        validate_profanity_serializer(data, 'url_id', errors, field_name='URL ID')
        validate_profanity_serializer(data, 'description', errors, field_name='Community description')

        # Community Thai name language and length validation
        if field_exists(data, 'name_th'):
            if len(data['name_th']) < 4:
                add_error_message(errors, 'name_th', 'Community name must be at least 4 characters in length.')
            elif not is_th(data['name_th']):
                add_error_message(errors, 'name_th', 'This field must be in the Thai language.')

        # Community English name language and length validation
        if field_exists(data, 'name_en'):
            if len(data['name_en']) < 4:
                add_error_message(errors, 'name_en', 'Community name must be at least 4 characters in length.')
            elif not is_en(data['name_en']):
                add_error_message(errors, 'name_en', 'This field must be in English.')

        # External links validation
        if field_exists(data, 'external_links'):
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
        if field_exists(data, 'url_id') and len(data['url_id']) > 0:
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
        else:
            clean_field(data, 'url_id')

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
            'available_actions': self.get_available_actions(obj),
            'request_ability': self.get_request_ability(obj)
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

        # Standard actions
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

        # Commenting actions
        if isinstance(obj, Event):
            is_able_to_comment = True

            if not IsPubliclyVisibleCommunity().has_object_permission(request, None, obj):
                is_able_to_comment = False
            if has_instance(obj, CommunityEvent):
                community_event = CommunityEvent.objects.get(pk=obj.id)
                if not community_event.allows_outside_participators:
                    if not IsMemberOfCommunity().has_object_permission(request, None, community_event):
                        is_able_to_comment = False

            comments = Comment.objects.filter(event_id=obj.id)
            commentators = [i.created_by.id for i in comments.exclude(created_by=None)]
            ip_addresses = [i.ip_address for i in comments.exclude(ip_address=None)]

            if user.is_authenticated and user.id in commentators:
                is_able_to_comment = False
            elif not user.is_authenticated and get_client_ip(request) in ip_addresses:
                is_able_to_comment = False

            if is_able_to_comment:
                actions.append('comment')

        return actions

    def get_request_ability(self, obj):
        ''' Retrieve sending join request ability '''
        request = self.context['request']
        user = request.user

        is_able_to_send_request, code, message, message_th = True, None, None, None

        # Joining Allowance
        if not Community.objects.get(pk=obj.id).is_accepting_requests:
            is_able_to_send_request = False
            code = 'restricted'
            message = 'This community does not accept requests.'
            message_th = 'ไม่เปิดรับคำขอเข้าร่วม'

        # Joining Permissions
        if has_instance(obj, Club) and not IsStudent().has_permission(request, None):
            is_able_to_send_request = False
            code = 'restricted'
            message = 'Only students are able to join the club.'
            message_th = 'เฉพาะนักศึกษาเท่านั้นที่สามารถเข้าร่วมชุมนุมได้'
        elif has_instance(obj, Lab):
            if not IsStudent().has_permission(request, None) and not IsLecturer().has_permission(request, None):
                is_able_to_send_request = False
                code = 'restricted'
                message = 'Only students and lecturers are able to join the lab.'
                message_th = 'เฉพาะนักศึกษาและอาจารย์เท่านั้นที่สามารถเข้าร่วมห้องปฏิบัติการได้'
        elif has_instance(obj, CommunityEvent):
            community_event = CommunityEvent.objects.get(pk=obj.id)
            if not community_event.allows_outside_participators:
                if not IsMemberOfBaseCommunity().has_object_permission(request, None, community_event):
                    is_able_to_send_request = False
                    code = 'restricted'
                    message = 'The event does not allow outside participators.'
                    message_th = 'กิจกรรมไม่เปิดรับผู้เข้าร่วมภายนอก'

        # Joining Validations
        if IsMemberOfCommunity().has_object_permission(request, None, obj):
            is_able_to_send_request = False
            code = 'already_member'
            message = 'You are already a member of the community.'
            message_th = 'คุณเป็นสมาชิกอยู่แล้ว'
        elif user.id in [i.invitee.id for i in Invitation.objects.filter(community_id=obj.id, status='W')]:
            is_able_to_send_request = False
            code = 'pending_invitation'
            message = 'You already have a pending invitation from this community.'
            message_th = 'คุณมีคำเชิญที่ยังไม่ได้ตอบรับอยู่'
        elif user.id in [i.user.id for i in Request.objects.filter(community_id=obj.id, status='W')]:
            is_able_to_send_request = False
            code = 'pending_request'
            message = 'You have already sent a pending request to this community.'
            message_th = 'คุณได้ส่งคำขอเข้าร่วมแล้ว'

        # Wrapping
        if message is not None:
            message = _(message)
        if message_th is not None:
            message_th = _(message_th)

        # Return
        return {
            'is_able_to_send_request': is_able_to_send_request,
            'code': code,
            'message': message,
            'message_th': message_th
        }


class CommunitySerializer(CommunitySerializerTemplate):
    ''' Community serializer '''
    class Meta:
        ''' Meta '''
        model = Community
        exclude = ('is_active', 'created_at', 'updated_at', 'created_by', 'updated_by')

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
        exclude = ('is_active', 'created_at', 'updated_at', 'created_by', 'updated_by')
        read_only_fields = ('is_official', 'valid_through')

    def validate(self, data, get_errors=False):
        ''' Validate data '''
        errors = super(OfficialClubSerializer, self).validate(data, get_errors=True)

        validate_profanity_serializer(data, 'room', errors, field_name='Club room')
        raise_validation_errors(errors)
        clean_field(data, 'room')

        return data

    def get_meta(self, obj):
        ''' Retrieve meta data '''
        meta = super(OfficialClubSerializer, self).get_meta(obj)
        meta['is_valid'] = is_valid_club(obj)

        return meta


class UnofficialClubSerializer(CommunitySerializerTemplate):
    ''' Unofficial club serializer '''
    class Meta:
        ''' Meta '''
        model = Club
        exclude = ('url_id', 'is_publicly_visible', 'room', 'is_active', 'created_at', 'updated_at', 'created_by',
                   'updated_by')
        read_only_fields = ('is_official', 'valid_through')

    def get_meta(self, obj):
        ''' Retrieve meta data '''
        meta = super(UnofficialClubSerializer, self).get_meta(obj)
        meta['is_valid'] = False

        return meta


class EventSerializerTemplate(CommunitySerializerTemplate):
    meta = serializers.SerializerMethodField()

    class Meta:
        ''' Meta '''
        model = Event
        exclude = ('is_active',)

    def get_meta(self, obj):
        ''' Retrieve meta data '''
        meta = super(EventSerializerTemplate, self).get_meta(obj)
        meta['is_ended'] = is_ended_event(obj)

        return meta

    def validate(self, data, get_errors=False):
        ''' Validate data '''
        errors = super(EventSerializerTemplate, self).validate(data, get_errors=True)

        validate_profanity_serializer(data, 'location', errors, field_name='Event location')

        # Fill missing fields for validation
        if not field_exists(data, 'start_date'):
            data['start_date'] = self.instance.start_date
        if not field_exists(data, 'end_date'):
            data['end_date'] = self.instance.end_date
        if not field_exists(data, 'start_time'):
            data['start_time'] = self.instance.start_time
        if not field_exists(data, 'end_time'):
            data['end_time'] = self.instance.end_time

        # Validate start date and end date
        if data['start_date'] > data['end_date']:
            add_error_message(errors, key='start_date', message='Start date is not able to come before the end date.')
            add_error_message(errors, key='end_date', message='End date is not able to come after the start date.')

        # Validate end time and end time
        if data['start_date'] == data['end_date'] and data['start_time'] > data['end_time']:
            add_error_message(
                errors, key='start_time',
                message='Start time is not able to come before the end time if the event is 1 day in length.'
            )
            add_error_message(
                errors, key='end_time',
                message='End time is not able to come before the start time if the event is 1 day in length.'
            )

        if get_errors:
            return errors

        raise_validation_errors(errors)

        return data


class ApprovedEventSerializer(EventSerializerTemplate):
    ''' Approved event serializer '''
    meta = serializers.SerializerMethodField()

    class Meta:
        ''' Meta '''
        model = Event
        exclude = ('is_active', 'created_at', 'updated_at', 'created_by', 'updated_by')
        read_only_fields = ('is_approved',)

    def get_meta(self, obj):
        ''' Retrieve meta data '''
        meta = super(ApprovedEventSerializer, self).get_meta(obj)
        meta['remaining_votes'] = self.get_remaining_votes(obj)

        return meta

    def get_remaining_votes(self, obj):
        ''' Retrieve remaining votes '''
        request = self.context['request']

        # Event must be approved
        if not obj.is_approved:
            return 0

        # Must already ended
        if not is_ended_event(obj):
            return 0

        # Must be a member of the event
        if not IsMemberOfCommunity().has_object_permission(request, None, obj):
            return 0

        membership_ids = [i.id for i in Membership.objects.filter(community_id=obj.id)]
        user_votes = Vote.objects.filter(voted_for_id__in=membership_ids, voted_by_id=request.user.id)

        return VOTE_LIMIT_PER_EVENT - len(user_votes)


class UnapprovedEventSerializer(EventSerializerTemplate):
    ''' Unapproved event serializer '''
    class Meta:
        ''' Meta '''
        model = Event
        exclude = ('is_active', 'url_id', 'is_publicly_visible', 'created_at', 'updated_at', 'created_by', 'updated_by')
        read_only_fields = ('is_approved',)


class ExistingCommunityEventSerializer(EventSerializerTemplate):
    ''' Existing community event serializer '''
    meta = serializers.SerializerMethodField()
    
    class Meta:
        ''' Meta '''
        model = CommunityEvent
        exclude = ('is_active', 'created_at', 'updated_at', 'created_by', 'updated_by')
        read_only_fields = ('is_approved', 'created_under')

    def get_meta(self, obj):
        ''' Retrieve meta data '''
        meta = super(ExistingCommunityEventSerializer, self).get_meta(obj)
        meta['remaining_votes'] = self.get_remaining_votes(obj)
        meta['created_under_name_en'] = self.get_created_under_name_en(obj)

        return meta

    def get_remaining_votes(self, obj):
        ''' Retrieve remaining votes '''
        request = self.context['request']

        # Event must be approved
        if not obj.is_approved:
            return 0

        # Must already ended
        if not is_ended_event(obj):
            return 0

        # Must be a member of the event
        if not IsMemberOfCommunity().has_object_permission(request, None, obj):
            return 0

        membership_ids = [i.id for i in Membership.objects.filter(community_id=obj.id)]
        user_votes = Vote.objects.filter(voted_for_id__in=membership_ids, voted_by_id=request.user.id)

        return VOTE_LIMIT_PER_EVENT - len(user_votes)

    def get_created_under_name_en(self, obj):
        ''' Retrieve community English name created under '''
        return obj.created_under.name_en


class NotExistingCommunityEventSerializer(EventSerializerTemplate):
    ''' Not existing community event serializer '''
    class Meta:
        ''' Meta '''
        model = CommunityEvent
        exclude = ('is_active', 'created_at', 'updated_at', 'created_by', 'updated_by')
        read_only_fields = ('is_approved',)

    def validate(self, data, get_errors=False):
        ''' Validate data '''
        errors = super(NotExistingCommunityEventSerializer, self).validate(data, get_errors=True)

        # Creation permission validation
        base_community = Community.objects.get(pk=data['created_under'].id)

        if not IsStaffOfCommunity().has_object_permission(self.context['request'], None, base_community):
            add_error_message(
                errors, message='Community events are not able to be created under communities you are not a staff.'
            )

        if has_instance(data['created_under'], Club):
            if not is_valid_club(Club.objects.get(pk=data['created_under'].id)):
                add_error_message(
                    errors, key='created_under',
                    message='Community events are not able to be created under unofficial or expired clubs.'
                )

        # Parent community validation
        if has_instance(data['created_under'], Event):
            add_error_message(
                errors, key='created_under', message='Community events are not able to be created under events.'
            )

        # Restrict creation under non-active clubs or labs
        if not IsInActiveCommunity().has_object_permission(self.context['request'], None, data['created_under']):
            add_error_message(
                errors, key='created_under', message='Comments are not able to be created in non-active events.'
            )

        # Raise validation errors
        raise_validation_errors(errors)

        return data


class LabSerializer(CommunitySerializerTemplate):
    ''' Lab serializer '''
    class Meta:
        ''' Meta '''
        model = Lab
        exclude = ('is_active', 'created_at', 'updated_at', 'created_by', 'updated_by')

    def validate(self, data, get_errors=False):
        ''' Validate data '''
        errors = super(LabSerializer, self).validate(data, get_errors=True)

        validate_profanity_serializer(data, 'room', errors, field_name='Lab room')
        validate_profanity_serializer(data, 'tags', errors, field_name='Tags')

        # Tags validation
        characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-., '

        if field_exists(data, 'tags'):
            for i in data['tags']:
                if i not in characters:
                    add_error_message(
                        errors, key='tags',
                        message='Tags must only consist of alphabetical characters, numbers, dashes, dots, and ' +
                                'spaces. Tags are separated by commas.'
                    )
                    break

            if len(data['tags']) > 0 and (data['tags'].strip()[0] == ',' or data['tags'].strip()[-1] == ','):
                add_error_message(errors, key='tags', message='Tags must not start or end with a comma.')

            if ',,' in data['tags'].replace(' ', str()):
                add_error_message(errors, key='tags', message='Tags must not contain consecutive commas.')

        # Raise validation errors
        raise_validation_errors(errors)

        # Data cleaning
        clean_field(data, 'room')

        return data
