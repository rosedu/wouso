
class App:
    """ Interface extended by Game and by Top and Activity"""

    @classmethod
    def get_sidebar_widget(kls, request):
        """ Return the sidebar widget, for current HttpRequest request.
        This is called in interface.context_processors.sidebar """
        return None

    
