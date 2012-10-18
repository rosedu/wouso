from django.contrib.auth.decorators import user_passes_test
from django.http import Http404

def staff_required(function=None, login_url=None):
    """
    Require current user to be logged in, have a profile, and be in staff group.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and u.get_profile().in_staff_group(),
        login_url=login_url
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def api_enabled_required(function=None):

    def _dec(function):
        def _view(request, *args, **kwargs):
            if settings.API_ENABLED:
                return function(request, *args, **kwargs)
            else:
                return Htttp404
        _view.__name__ = function.__name__
        _view.__dict__ = function.__dict__
        _view.__doc__ = function.__doc__

        return _view

    if function is None:
        return _dec
    else:
        return _dec(function)
