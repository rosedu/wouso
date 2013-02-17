from django.core.cache import cache
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404
import inspect
import logging

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
            from django.conf import settings
            if settings.API_ENABLED:
                return function(request, *args, **kwargs)
            else:
                return Http404
        _view.__name__ = function.__name__
        _view.__dict__ = function.__dict__
        _view.__doc__ = function.__doc__

        return _view

    if function is None:
        return _dec
    else:
        return _dec(function)


def _get_cache_key(function, **kwargs):
    params = inspect.getargspec(function)[0]
    cache_key = 'F-%s-' % function.__name__
    for param_name in params:
        value = kwargs.get(param_name, None)
        cache_key += '%s-%s' % (param_name, value)
    return cache_key


def cached_method(function=None):
    def _dec(function):
        def _cached(**kwargs):
            cache_key = _get_cache_key(function, **kwargs)
            if cache_key in cache:
                return cache.get(cache_key)
            return function(**kwargs)
        return _cached

    if function:
        return _dec(function)
    return _dec


def drop_cache(function, **kwargs):
    cache_key = _get_cache_key(function, **kwargs)
    if cache_key in cache:
        cache.delete(cache_key)