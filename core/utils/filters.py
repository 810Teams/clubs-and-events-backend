'''
    Core Application Queryset Filtering Functions
    core/utils/filters.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.core.exceptions import ValidationError

from community.models import Community
from core.permissions import IsMemberOfCommunity
from membership.models import Membership, MembershipLog


def filter_queryset(queryset, request, target_param=None, is_foreign_key=False):
    ''' Filters queryset by target parameter '''
    try:
        query = request.query_params.get(target_param)
        if query is not None:
            queryset = eval('queryset.filter({}{}=query)'.format(target_param, '_id' * is_foreign_key))
    except (ValueError, ValidationError):
        queryset = None

    return queryset


def filter_queryset_permission(queryset, request, permissions):
    ''' Filters queryset with permissions '''
    for i in permissions:
        visible_ids = [
            j.id for j in queryset if i.has_permission(request, None) and i.has_object_permission(request, None, j)
        ]
        queryset = queryset.filter(pk__in=visible_ids)

    return queryset


def filter_queryset_exclude_own(queryset, request, target_param='exclude_own'):
    ''' Filters queryset by excluding communities which the user is the member '''
    try:
        query = request.query_params.get(target_param)
        if query is not None and eval(query):
            queryset = queryset.exclude(
                id__in=[i.id for i in queryset if IsMemberOfCommunity().has_object_permission(request, None, i)]
            )
    except ValueError:
        queryset = None

    return queryset


def limit_queryset(queryset, request, target_param='limit', block_param='block', reverse_param='reversed'):
    ''' Limit queryset items not to exceed a specific amount '''
    # Retrieve reverse status and reverse the queryset
    try:
        is_reversed = request.query_params.get(reverse_param)
        if is_reversed is not None and bool(int(is_reversed)):
            queryset = list(reversed(queryset))
    except TypeError:
        pass

    # Retrieve block number
    try:
        block = int(request.query_params.get(block_param))
    except TypeError:
        block = 0

    # Retrieve limit and slice queryset
    try:
        limit = request.query_params.get(target_param)
        if limit is not None:
            limit = int(limit)
            queryset = queryset[block * limit:min(block * limit + limit, len(queryset))]
    except IndexError:
        pass

    return queryset


def get_previous_membership_log(obj):
    ''' Retrieves the previous membership log object from a membership log object '''
    if not isinstance(obj, MembershipLog):
        return None

    logs = MembershipLog.objects.filter(membership_id=obj.membership.id)

    current = 0
    for i in range(len(logs)):
        if logs[i].id == obj.id:
            current = i
            break

    if current == 0:
        return None
    return logs[current - 1]


def get_latest_membership_log(membership):
    ''' Retrieves the latest membership log object from a membership object '''
    if not isinstance(membership, Membership):
        return None

    logs = MembershipLog.objects.filter(membership_id=membership.id)

    if len(logs) > 0:
        return logs[len(logs) - 1]
    return None


def get_active_community_ids():
    ''' Get all active community IDs '''
    return [i.id for i in Community.objects.filter(is_active=True)]


def get_membership_in_active_community_ids():
    ''' Get all memberships in active communities IDs '''
    return [i.id for i in Membership.objects.filter(community_id__in=get_active_community_ids())]
