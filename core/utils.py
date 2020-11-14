'''
    Core Application Utilities
    core/utils.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from collections import OrderedDict
from datetime import datetime

from crum import get_current_request
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from clubs_and_events.settings import EMAIL_DOMAIN_NAME
from core.validators import validate_profanity
from user.permissions import IsStudentObject


class Colors:
    ''' Colors class '''
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def colored(text, color):
    ''' Returns colorize text '''
    return color + text + Colors.ENDC


def _log(text, color=str()):
    ''' Display Django log base function '''
    months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

    now = datetime.now()
    formatted_datetime = '{:02d}/{}/{:04d} {:02d}:{:02d}:{:02d}'.format(
        now.day, months[now.month - 1], now.year, now.hour, now.minute, now.second
    )

    print(colored('[{}] {}'.format(formatted_datetime, text), color))


def log(text):
    ''' Display Django plain log '''
    _log(text)


def warning(text):
    ''' Display Django warning log '''
    _log(text, color=Colors.WARNING)


def error(text):
    ''' Display Django error log '''
    _log(text, color=Colors.FAIL)


def truncate(text, max_length=64):
    ''' Truncates text if the length is above the max length '''
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'


def get_file_extension(file_name):
    ''' Returns a file extension '''
    if isinstance(file_name, str) and len(file_name.split('.')) > 1:
        return file_name.split('.')[-1].lower()
    return None


def remove_duplicates(list_data):
    ''' Removes all duplicated elements from a list and return '''
    return list(dict.fromkeys(list_data))


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


def validate_profanity_serializer(data, key, errors, field_name=str(), lang=('en', 'th')):
    ''' Validate profanity of data in the field, then add the error message to the errors list '''
    if field_name.strip() == '':
        field_name = key.replace('_', ' ').capitalize()

    try:
        validate_profanity(data[key], lang=lang)
    except ValidationError:
        add_error_message(errors, key=key, message='{} contains profanity.'.format(field_name))
    except KeyError:
        pass

    return errors


def raise_validation_errors(errors):
    ''' Raise validation errors if exist '''
    if len(errors) > 0:
        raise ValidationError(errors)


def field_exists(data, field_name):
    ''' Check if a value of the field exists in a data of dictionary form '''
    if isinstance(data, (dict, OrderedDict)) and isinstance(field_name, str):
        if field_name in data.keys() and data[field_name] is not None:
            return True
    return False


def clean_field(data, field_name, replacement=None):
    ''' Set a field to None or any designated value if an empty string is input '''
    if isinstance(data, (dict, OrderedDict)) and isinstance(field_name, str):
        if field_name in data.keys() and isinstance(data[field_name], str):
            if data[field_name].replace('\n', str()).replace('\r', str()).strip() == str():
                data[field_name] = replacement
    return data
