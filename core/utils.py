'''
    Core Application Utilities
    core/utils.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from core.validators import validate_profanity


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


def add_error_message(errors, key='non_field_errors', message=str(), wrap=True):
    ''' Add error message to dictionary in the correct format of the ValidationError class '''
    if wrap:
        message = _(message)

    if key in errors.keys():
        if isinstance(errors[key], list):
            errors[key].append(message)
        else:
            errors[key] = [errors[key], message]
    else:
        errors[key] = message


def validate_profanity_serializer(data, key, errors, field_name=str()):
    ''' Validate profanity of data in the field, then add the error message to the errors list '''
    if field_name.strip() == '':
        field_name = key.replace('_', ' ').capitalize()

    try:
        validate_profanity(data[key])
    except ValidationError:
        add_error_message(errors, key=key, message='{} contains profanity.'.format(field_name))
    except KeyError:
        pass

    return errors


def raise_validation_errors(errors):
    ''' Raise validation errors if exist '''
    if len(errors) > 0:
        raise ValidationError(errors)
