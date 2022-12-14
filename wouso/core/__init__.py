import logging
import sys
import warnings
from functools import wraps
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.signals import user_logged_in
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from wouso.core.config.models import BoolSetting

logger = logging.getLogger('core')


def deprecated(message):
    """ Mark function as deprecated.

        >>> @deprecated("thenineties is deprecated")
        ... def thenineties():
        ...     print 'hi'

    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def block_if_not_staff(sender, user, request, **kwargs):
    staff_only_login = BoolSetting.get('setting-staff-only-login').get_value()
    if staff_only_login and not user.is_staff:
        messages.error(request, _('Only staff members can log in'))
        logout(request)


if 'test' not in sys.argv:
    user_logged_in.connect(block_if_not_staff)
