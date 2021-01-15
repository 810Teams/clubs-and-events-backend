'''
    Core Application Objects Utility Functions
    core/utils/objects.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from crum import get_current_user


def save_user_attributes(obj, created_by_field_name='created_by', updated_by_field_name='updated_by', allows_null=True):
    ''' Save user-related attributes of the object '''
    user = get_current_user()
    if user is not None and user.pk is None:
        user = None

    if obj.id is None and (allows_null or (user is not None)):
        if isinstance(created_by_field_name, str):
            exec('obj.{} = user'.format(created_by_field_name))

    if isinstance(updated_by_field_name, str):
        exec('obj.{} = user'.format(updated_by_field_name))
