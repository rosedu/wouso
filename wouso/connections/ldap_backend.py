from django.contrib.auth.models import User
import ldap

LDAP_URL = "ldaps://localhost:636/"
LDAP_BINDNAME = ""
LDAP_BINDPASS = ""
LDAP_BASECN = "dc=cs,dc=curs,dc=pub,dc=ro"
LDAP_FILTER = '(uid=%s)'

# Overwrite settings
from wouso.settings import *

class LDAPBackend:
    def authenticate(self, username=None, password=None):
        if password == "" or password == None or username == None:
            return None
        
        # prima conexiune
        try:
            l = ldap.initialize(LDAP_URL)        
            l.simple_bind_s(LDAP_BINDNAME, LDAP_BINDPASS)
            result = l.search_ext_s(LDAP_BASECN, ldap.SCOPE_SUBTREE, LDAP_FILTER % username, None)
            l.unbind_s()
        except ldap.SERVER_DOWN:
            # TODO raise somehow this error
            return None
        
        if len(result) == 0:
            return None
        
        # user dn:
        dn = result[0][0]
        # a doua conexiune
        try:
            l = ldap.initialize(LDAP_URL)
            l.simple_bind_s(dn, password)
            l.unbind_s()
        except ldap.NO_SUCH_OBJECT:
            return None
        except ldap.INVALID_CREDENTIALS:
            return None
        except ldap.UNWILLING_TO_PERFORM:
            return None
        
        # create or get user here:
        data = result[0][1]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User(username=username,first_name=data['givenName'][0],last_name=data['sn'][0],email=data['mail'][0])
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
