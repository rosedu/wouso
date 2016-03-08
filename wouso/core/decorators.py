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


def _get_cache_key(function, *args, **kwargs):
    params = inspect.getargspec(function)[0]
    cache_key = 'F-%s-' % function.__name__
    for i, param_name in enumerate(params):
        if i < len(args):
            value = args[i]
        else:
            value = kwargs.get(param_name, None)
        # post processing
        if hasattr(value, 'id'):
            value = value.id
        cache_key += '%s-%s' % (param_name, value)
    cache_key = cache_key.replace(' ', '')
    return cache_key


def cached_method(function=None):
    def _dec(function):
        def _cached(*args, **kwargs):
            cache_key = _get_cache_key(function, *args, **kwargs)
            if cache_key in cache:
                logging.debug('Returning  : %s' % cache_key)
                return cache.get(cache_key)
            result = function(*args, **kwargs)
            cache.set(cache_key, result)
            logging.debug('Setting    : %s' % cache_key)
            return result
        _cached._function = function
        return _cached

    if function:
        return _dec(function)
    return _dec


def drop_cache(function, *args, **kwargs):
    if hasattr(function, '_function'):
        cache_key = _get_cache_key(function._function, *args, **kwargs)
        cache.delete(cache_key)
        logging.debug('Deleted key: %s' % cache_key)
    else:
        logging.exception('Invalid function: %s' % str(function))
