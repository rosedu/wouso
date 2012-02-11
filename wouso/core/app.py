
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

        name = kls.__name__
        return BoolSetting.get('disable-%s' % name).get_value()

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