import re
from django.db import connection
from django.contrib.auth.models import User, Permission
from django.contrib.auth.backends import RemoteUserBackend

from shibboleth.app_settings import USERNAME_TRANSLATIONS

import logging
logger = logging.getLogger(__name__)

class ShibbolethRemoteUserBackend(RemoteUserBackend):
    """
    This backend is to be used in conjunction with the ``RemoteUserMiddleware``
    found in the middleware module of this package, and is used when the server
    is handling authentication outside of Django.

    By default, the ``authenticate`` method creates ``User`` objects for
    usernames that don't already exist in the database.  Subclasses can disable
    this behavior by setting the ``create_unknown_user`` attribute to
    ``False``.
    """

    # Create a User object if not already in the database?
    create_unknown_user = True

    def authenticate(self, remote_user, shib_meta, appBrand):
        """
        The username passed as ``remote_user`` is considered trusted.  This
        method simply returns the ``User`` object with the given username,
        creating a new ``User`` object if ``create_unknown_user`` is ``True``.

        Returns None if ``create_unknown_user`` is ``False`` and a ``User``
        object with the given username is not found in the database.
        """
        
        logger.debug('ShibbolethRemoteUserBackend {}'.format(remote_user))
        
        if not remote_user:
            return
        
        user = None
        username = self.clean_username(remote_user)
        
        shib_user_params = dict([(k, shib_meta[k]) for k in User._meta.get_all_field_names() if k in shib_meta])
        # logger.debug(repr(shib_user_params))
        # Note that this could be accomplished in one try-except clause, but
        # instead we use get_or_create when creating unknown users since it has
        # built-in safeguards for multiple threads.
        if self.create_unknown_user:
            logger.debug('create_unknown_user {}'.format(username))
            logger.debug('shib_user_params {}'.format(repr(shib_user_params)))
            
            user, created = User.objects.get_or_create(username=username, defaults=shib_user_params)
            if created:
                logger.debug('create_unknown_user: created')
                # this does nothing in RemoteBackend:
                user = self.configure_user(user)

                # passing password in shib_user_params didn't work
                user.set_password(User.objects.make_random_password()) # doesn't save
                user.save() # save password
                
                up = user.userprofile
                up.organization = appBrand.organization
                up.save()
        else:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                logger.info('ShibbolethRemoteUserBackend User.DoesNotExist')
                pass
        #logger.debug('authenticate returning {}'.format(user))
        return user

def clean_username(self, username):
    """
    Performs any cleaning on the "username" prior to using it to get or
    create the user object.  Returns the cleaned username.
    """
    
    for pattern in USERNAME_TRANSLATIONS:
        username = re.sub(pattern, USERNAME_TRANSLATIONS[pattern], username, 1)

    return username
