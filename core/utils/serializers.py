'''
    Core Application Serializer Utility Functions
    core/utils/serializers.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from collections import OrderedDict

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from core.utils.profanity import validate_profanity


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
