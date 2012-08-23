from django.contrib.auth.decorators import user_passes_test

def staff_required(function=None, login_url=None):
    """
    Require current user to be logged in, have a profile, and be in staff group.
    """
    actual_decorator = user_passes_test(
        lambda u: u.get_profile().in_staff_group(),
        login_url=login_url
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
