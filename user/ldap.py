'''
    User Application LDAP
    user/ldap.py
    @author Teerapat Kraisrisirikul (810Teams)
'''

from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import LDAPBindError

from clubs_and_events.settings import LDAP_URL, LDAP_BIND_USERNAME, LDAP_BIND_PASSWORD, LDAP_BASE
from clubs_and_events.settings import LDAP_USER_GROUPS, LDAP_USERNAME_FIELD


def get_LDAP_user(username, password, display_response=False):
    ''' Check user authentication in the LDAP server and return the information '''
    # LDAP Server Set-up
    server = Server(LDAP_URL, get_info=ALL)

    # LDAP Server Binding
    connection = Connection(
        server,
        user=LDAP_BIND_USERNAME,
        password=LDAP_BIND_PASSWORD,
        auto_bind=True
    )

    # Search User in each Group
    user_group = None

    for group in LDAP_USER_GROUPS:
        connection.search(
            '{},{}'.format(group['sub_base'], LDAP_BASE),
            '({}={})'.format(LDAP_USERNAME_FIELD, username),
            attributes=['cn']
        )

        if len(connection.response) != 0 and 'dn' in connection.response[0].keys():
            user_group = group
            break

    # User Not Found
    if user_group is None:
        return None

    # Display Response Log
    if display_response:
        for i in connection.response[0]:
            if "raw" not in i:
                print('[LOG] "{}": {}'.format(i, connection.response[0][i]))

    # Login Attempt
    try:
        Connection(
            server,
            user=connection.response[0]['dn'],
            password=password,
            auto_bind=True
        )
    except (LDAPBindError, IndexError, KeyError):
        return None

    # Login Successful
    return {
        'username': username,
        'password': password,
        'name': connection.response[0]['attributes']['cn'],
        'user_group': user_group['user_group'],
        'is_staff': user_group['is_staff']
    }
