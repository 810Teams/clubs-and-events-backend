'''
    Core Application User Utility Functions
    core/utils/users.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from crum import get_current_request

from clubs_and_events.settings import EMAIL_DOMAIN_NAME
from user.permissions import IsStudentObject


def get_email(user):
    ''' Retrieves default IT KMITL email '''
    if IsStudentObject().has_object_permission(get_current_request(), None, user) and user.username[0:2] == 'it':
        return user.username[2:] + '@' + EMAIL_DOMAIN_NAME
    return user.username + '@' + EMAIL_DOMAIN_NAME


def get_client_ip(request):
    ''' Retrieves client's IP address '''
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for is not None:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
