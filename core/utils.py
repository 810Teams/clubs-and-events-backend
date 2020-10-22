'''
    Core Application Utilities
    core/utils.py
    @author Teerapat Kraisrisirikul (810Teams)
'''


from django.core.exceptions import ValidationError
from django.db import models

from membership.models import MembershipLog


def truncate(text, max_length=64):
    ''' Truncates text if the length is above the max length '''
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'


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


def limit_queryset(queryset, request, target_param='limit'):
    ''' Limit queryset items not to exceed a specific amount '''
    try:
        limit = request.query_params.get(target_param)
        if limit is not None:
            queryset = queryset[:min(int(limit), len(queryset))]
    except ValueError:
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
    logs = MembershipLog.objects.filter(membership_id=membership.id)

    if len(logs) > 0:
        return logs[len(logs) - 1]
    return None


def get_email(user, domain_name='it.kmitl.ac.th', is_student=True):
    ''' Retrieves default IT KMITL email '''
    if is_student and user.username[0:2] == 'it':
        return user.username[2:] + '@' + domain_name
    return user.username + '@' + domain_name


def get_client_ip(request):
    ''' Retrieves client's IP address '''
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for is not None:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def has_instance(obj, model):
    ''' Check if an object has an instance in a specific model '''
    if isinstance(obj, models.Model):
        try:
            model.objects.get(pk=obj.id)
            return True
        except model.DoesNotExist:
            return False
    return False
