from wouso.core.app import App
from views import footer_link

class Statistics(App):

    @classmethod
    def get_footer_link(kls, request):
        return footer_link(request)