""" God is a singleton object. Its implementation can be changed
in wouso Django settings.

Each module needing God should do a:
    from wouso.core.god import God

and then use god's methods directly, such as:
    God.get_user_level(...)

"""

# A God singleton for all of us
God = None


def get_god():
    global God
    if God is None:
        from wouso.core.god.god import DefaultGod
        God = DefaultGod()

    return God


God = get_god()
