import warnings
from functools import wraps
import logging

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
