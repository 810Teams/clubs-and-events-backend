'''
    Core Application Utilities
    core/utils.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.db import models


def truncate(text, max_length=64):
    ''' Truncates text if the length is above the max length '''
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'


def get_file_extension(file_name):
    ''' Returns a file extension '''
    if isinstance(file_name, str):
        return file_name.split('.')[-1].lower()
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
