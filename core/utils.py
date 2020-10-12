from django.core.exceptions import ValidationError

from membership.models import MembershipLog


def truncate(text, max_length=64):
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'


def filter_queryset(queryset, request, target_param=None, is_foreign_key=False):
    try:
        query = request.query_params.get(target_param)
        if query is not None:
            queryset = eval('queryset.filter({}{}=query)'.format(target_param, '_id' * is_foreign_key))
    except (ValueError, ValidationError):
        queryset = None

    return queryset


def limit_queryset(queryset, request, target_param='limit'):
    try:
        limit = request.query_params.get(target_param)
        if limit is not None:
            queryset = queryset[:min(int(limit), len(queryset))]
    except ValueError:
        pass

    return queryset


def get_previous_membership_log(obj):
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


def get_email(user, domain_name='it.kmitl.ac.th'):
    return user.username + '@' + domain_name
