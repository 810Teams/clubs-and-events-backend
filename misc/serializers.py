'''
    Miscellaneous Application Serializers
    misc/serializers.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.utils import timezone
from rest_framework import serializers

from clubs_and_events.settings import VOTE_LIMIT_PER_EVENT
from community.models import Event
from core.permissions import IsMemberOfCommunity
from core.utils.serializer import raise_validation_errors, add_error_message, validate_profanity_serializer
from membership.models import Membership
from misc.models import FAQ, Vote


class FAQSerializer(serializers.ModelSerializer):
    ''' Frequently asked question (FAQ) serializer '''
    class Meta:
        ''' Meta '''
        model = FAQ
        exclude = ('created_by', 'updated_by')


class VoteSerializerTemplate(serializers.ModelSerializer):
    ''' Vote serializer template '''
    meta = serializers.SerializerMethodField()

    class Meta:
        ''' Meta '''
        model = Vote
        exclude = ('voted_by', 'created_at')

    def get_meta(self, obj):
        ''' Retrieve meta data '''
        return {
            'event': self.get_event(obj),
            'voted_for_user': self.get_voted_for_user(obj)
        }

    def get_event(self, obj):
        ''' Retrieve event '''
        return obj.voted_for.community.id

    def get_voted_for_user(self, obj):
        ''' Retrieve user receive a vote '''
        return obj.voted_for.user.id


class ExistingVoteSerializer(VoteSerializerTemplate):
    ''' Existing vote serializer '''
    class Meta:
        ''' Meta '''
        model = Vote
        exclude = ('comment', 'voted_by', 'created_at')
        read_only_fields = ('voted_for',)


class NotExistingVoteSerializer(VoteSerializerTemplate):
    ''' Not existing vote serializer '''
    class Meta:
        ''' Meta '''
        model = Vote
        exclude = ('voted_by', 'created_at')

    def validate(self, data):
        ''' Validate data '''
        errors = dict()

        request = self.context['request']

        # Validate community type, if not event, ignores any further validations
        try:
            event = Event.objects.get(pk=data['voted_for'].community.id)
        except Event.DoesNotExist:
            add_error_message(errors, message='Votes are not able to be casted in non-events.')
            raise_validation_errors(errors)
            return data

        # Validate event, must be approved
        if not event.is_approved:
            add_error_message(errors, key='voted_for', message='Votes are not able to be casted in unapproved events.')

        # Validate event, must already ended
        if event.end_date > timezone.now().date() and event.end_time > timezone.now().time():
            add_error_message(
                errors, key='voted_for', message='Votes are not able to be casted in on-going or future events.'
            )

        # Validate voter, must be a member
        if not IsMemberOfCommunity().has_object_permission(request, None, event):
            add_error_message(errors, key='voted_for', message='Non-event members are not able to vote.')

        # Validate user receiving a vote, must not be yourself
        if data['voted_for'].user.id == request.user.id:
            add_error_message(errors, key='voted_for', message='Users are not able to cast votes on themselves.')

        # Validate vote amount, after voting the amount must not exceed the limit
        membership_ids = [i.id for i in Membership.objects.filter(community_id=event.id)]
        user_votes = Vote.objects.filter(voted_for_id__in=membership_ids, voted_by_id=request.user.id)
        if len(user_votes) + 1 > VOTE_LIMIT_PER_EVENT:
            add_error_message(
                errors, key='voted_for', message='User has already voted in this event at the maximum amount.'
            )

        # Validate vote, must not be a duplicate
        user_votes = user_votes.filter(voted_for_id=data['voted_for'].id, voted_by_id=request.user.id)
        if len(user_votes) != 0:
            add_error_message(errors, key='voted_for', message='User has already voted for this person in the event.')

        # Validate profanity
        validate_profanity_serializer(data, 'comment', errors, field_name='Comment')

        raise_validation_errors(errors)

        return data


class OwnVoteSerializer(VoteSerializerTemplate):
    ''' Own vote serializer '''
    class Meta:
        ''' Meta '''
        model = Vote
        exclude = ('voted_by', 'created_at')
        read_only_fields = ('comment', 'voted_for')
