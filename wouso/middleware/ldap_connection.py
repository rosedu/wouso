from django.contrib.auth.models import User
import ldap
import logging

LDAP_URL = 'ldaps://swarm.cs.pub.ro:636'
LDAP_BINDNAME = '' # 'cn=admin,dc=swarm,dc=cs,dc=pub,dc=ro'
LDAP_BINDPASS = ''
LDAP_BASECN = 'dc=swarm,dc=cs,dc=pub,dc=ro'
LDAP_FILTER = '(uid=%s)'

# Overwrite settings
from wouso.settings import *

class LDAPBackend:
    def authenticate(self, username=None, password=None):
        if password == "" or password is None or username is None:
            raise Exception('Invalid user or password')

        username, password = username.strip(), password.strip()
        try:
            conn = ldap.initialize(LDAP_URL)
            if LDAP_BINDNAME != '':
                conn.simple_bind_s(LDAP_BINDNAME, LDAP_BINDPASS)
            result = conn.search_ext_s(LDAP_BASECN, ldap.SCOPE_SUBTREE, \
                    LDAP_FILTER % username, None)
            conn.unbind_s()
        except ldap.SERVER_DOWN:
            #raise Exception('Authentication server is down')
            return None

        if len(result) == 0:
            return None
        dn = result[0][0]

        try:
            conn = ldap.initialize(LDAP_URL)
            conn.simple_bind_s(dn, password)
            conn.unbind_s()
        except ldap.NO_SUCH_OBJECT:
            return None
        except ldap.INVALID_CREDENTIALS:
            return None
        except ldap.UNWILLING_TO_PERFORM:
            return None
        except UnicodeEncodeError:
            logging.error('Unicode password crashed ldap')
            return None

        # create or get user here:
        data = result[0][1]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User(username=username, first_name=data['givenName'][0], \
                    last_name=data['sn'][0], email=data['mail'][0])
            user.is_staff = False
            user.is_superuser = False
            user.is_active = True
            # IMPORTANT: login only via ldap
            user.set_unusable_password()
            user.save()
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
