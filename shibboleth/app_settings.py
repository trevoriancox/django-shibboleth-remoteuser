
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# "REMOTE_USER" need not be listed here since it is configured in remoteuser backend.
# so this is only useful for additional attributes for creating user.
default_shib_attributes = {
   # Note any extra attributes end up in request.META so could conflict. Minimize in attribute-map.xml.
   # Shibboleth auth backend uses all attributes to look for existing user, so use RemoteUserBackend
   # In Shibboleth2.xml, upn should be REMOTE_USER so don't list here.
   #"upn": (True, "username"),
   
   # We also need the email in the email field.
   "upn": (False, "email"),
   
   # ticket:1045 Create new student user
   "givenname": (False, "first_name"),
   "surname": (False, "last_name"),
}

SHIB_ATTRIBUTE_MAP = getattr(settings, 'SHIBBOLETH_ATTRIBUTE_MAP', default_shib_attributes)
#Set to true if you are testing and want to insert sample headers.
SHIB_MOCK_HEADERS = getattr(settings, 'SHIBBOLETH_MOCK_HEADERS', False)

LOGIN_URL = getattr(settings, 'LOGIN_URL', None)

# TC: see AppBrand.login_path
#if not LOGIN_URL:
#    raise ImproperlyConfigured("A LOGIN_URL is required.  Specify in settings.py")

#Optional logout parameters
#This should look like: https://sso.school.edu/idp/logout.jsp?return=%s
#The return url variable will be replaced in the LogoutView.
LOGOUT_URL = getattr(settings, 'SHIBBOLETH_LOGOUT_URL', None)
#LOGOUT_REDIRECT_URL specifies a default logout page that will always be used when
#users logout from Shibboleth.
LOGOUT_REDIRECT_URL = getattr(settings, 'SHIBBOLETH_LOGOUT_REDIRECT_URL', None)
#Name of key.  Probably no need to change this.  
LOGOUT_SESSION_KEY = getattr(settings, 'SHIBBOLETH_FORCE_REAUTH_SESSION_KEY', 'shib_force_reauth')
