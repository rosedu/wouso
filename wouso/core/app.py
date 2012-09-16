import sys

class App:
    """ Interface extended by Game and by Top and Qproposal Activity"""

    @classmethod
    def name(kls):
        return kls.__name__

    @classmethod
    def disabled(kls):
        """ Search for a disabled config setting.
        """
        from wouso.core.config.models import BoolSetting

        return BoolSetting.get('disable-%s' % kls.name()).get_value()

    @classmethod
    def get_modifiers(kls):
        """ Return a list of modifiers - as names (this translates to artifact names)
        Player has_modifier checks if the user has an artifact with the modifier id.
        """
        return []

    @classmethod
    def get_sidebar_widget(kls, request):
        """ Return the sidebar widget, for current HttpRequest request.
        This is called in interface.context_processors.sidebar """
        return None

    @classmethod
    def get_unread_count(kls, request):
        """ Return the app-specific unread counter.
        """
        return 0

    @classmethod
    def get_header_link(kls, request):
        """ Return dictionary containing (link, text, count) for the content
        to be displayed in the page header.
        Called in interface.context_processors.header """
        return None

    @classmethod
    def get_footer_link(kls, request):
        """ Return html content to be displayed in the footer
        Called in interface.context_processors.footer """
        return None

    @classmethod
    def get_profile_actions(kls, request, player):
        """ Return html content for player's profile view """
        return ''

    @classmethod
    def get_profile_superuser_actions(kls, request, player):
        """ Return html content for player's profile view
        in the superuser row """
        return ''

    @classmethod
    def get_api(kls):
        """ Return a dictionary with url-regex keys, and PistonHandler values.
        """

        return {}

    @classmethod
    def management_task(cls, datetime=lambda: datetime.now(), stdout=sys.stdout):
        """ Execute maintance task, such as:
        - calculate top ranks
        - inactivate expired spells
        - expire challenges not played
        This method is called from wousocron management task, and the datetime might be faked.
        """
        pass

    management_task = None # Disable it by default