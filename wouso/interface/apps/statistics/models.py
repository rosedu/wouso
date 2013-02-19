from wouso.core.common import App
from views import footer_link

class Statistics(App):

    @classmethod
    def get_footer_link(cls, request):
        return footer_link(request)