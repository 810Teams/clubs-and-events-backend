'''
    User Application Custom Authentication
    user/authentication.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password

from user.ldap import get_LDAP_user
from user.models import EmailPreference


class AuthenticationBackend(ModelBackend):
    ''' Authentication back-end '''
    def authenticate(self, request, username=None, password=None, **kwargs):
        ''' Authenticate user '''
        ldap_user = get_LDAP_user(username, password)

        if ldap_user is not None:
            try:
                user = get_user_model().objects.get(username=username)
            except get_user_model().DoesNotExist:
                user = get_user_model().objects.create(
                    username=username,
                    name=ldap_user['name'],
                    user_group=ldap_user['user_group'],
                    is_staff=ldap_user['is_staff']
                )
                user.set_password(password)
                user.save()

                email_preference = EmailPreference.objects.create(user_id=user.id)
                email_preference.save()
            return user
        else:
            try:
                user = get_user_model().objects.get(username=username)
                if check_password(password, user.password):
                    return user
                return None
            except get_user_model().DoesNotExist:
                return None

    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return None
