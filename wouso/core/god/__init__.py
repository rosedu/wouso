
# A God singleton for all of us
God = None
def get_god():
    global God
    if God is None:
        from wouso.core.god.god import DefaultGod
        God = DefaultGod()

    return God

God = get_god()
