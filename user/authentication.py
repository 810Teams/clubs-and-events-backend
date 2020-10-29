'''
    User Application Authentication
    user/authentication.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password

from user.ldap import get_LDAP_user
from user.models import User


class AuthenticationBackend(ModelBackend):
    ''' Authentication back-end '''
    def authenticate(self, request, username=None, password=None, **kwargs):
        ''' Authenticate user '''
        ldap_user = get_LDAP_user(username, password)

        if ldap_user is not None:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User(username=username)
                user.set_password(password)
                user.name = ldap_user['name']
                user.user_group = ldap_user['user_group']
                user.is_staff = ldap_user['is_staff']
                user.save()
            return user

        else:
            try:
                user = User.objects.get(username=username)

                if check_password(password, user.password):
                    return user

                return None
            except User.DoesNotExist:
                return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
