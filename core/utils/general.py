'''
    Core Application General Utility Functions
    core/utils/general.py
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
    if isinstance(file_name, str) and len(file_name.split('.')) > 1:
        return file_name.split('.')[-1].lower()
    return None


def remove_duplicates(list_data):
    ''' Removes all duplicated elements from a list and return '''
    return list(dict.fromkeys(list_data))


def has_instance(obj, model):
    ''' Check if an object has an instance in a specific model '''
    if isinstance(obj, models.Model):
        try:
            model.objects.get(pk=obj.id)
            return True
        except model.DoesNotExist:
            return False
    return False
