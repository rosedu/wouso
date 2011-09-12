.. _user:

Core - `User`
=============

The UserProfile is a Django-specific way to extend the User class. In
WoUSO, we use this to store login information, basic level and title
information, group membership, and also the artifact inventory.
Moreover, each game may extend this class in order to store user-game
specific data.

Extensions
----------

Example
~~~~~~~

::

    # games/qotd/models.py:
    class QotdUser(UserProfile):
        last_answered = models.DateTimeField()
        last_answer = models.IntegerField()

        @property
        def has_answered(self):
            """ Check if last_answered was today """
            if self.last_answered is None:
                return False
            else:
                return (datetime.now() - self.last_answered) < timedelta (days = 1)

    # games/qotd/views.py
    @login_required
    def index(request):
        profile = request.user.get_profile()
        qotd_user = profile.get_extension(QotdUser)

        if qotd_user.has_answered:
            return HttpResponseRedirect('/done/')

:mod:`wouso.core.user.models`
-----------------------------
.. automodule:: wouso.core.user.models
    :members:

:mod:`wouso.core.user.templatetags.user`
----------------------------------------
.. automodule:: wouso.core.user.templatetags.user
    :members:
