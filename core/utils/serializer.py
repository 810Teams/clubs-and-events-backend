'''
    Core Application Serializer Utility Functions
    core/utils/serializers.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from collections import OrderedDict
from datetime import datetime

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext as _

from community.models import Event, Club
from core.utils.nlp import validate_profanity


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
    if field_name.strip() == str():
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


def is_valid_club(club):
    ''' Verify if the club is valid or not '''
    if not isinstance(club, Club):
        return False
    return club.is_official and club.valid_through is not None and club.valid_through >= timezone.now().date()


def is_ended_event(event):
    ''' Verify if the event has ended or not '''
    if not isinstance(event, Event):
        return False

    if event.end_date < datetime.now().date():
        return True
    elif event.end_date == datetime.now().date() and event.end_time <= datetime.now().time():
        return True
    return False
