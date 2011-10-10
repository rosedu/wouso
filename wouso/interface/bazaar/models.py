from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from wouso.core.app import App

class Bazaar(App):
    @classmethod
    def get_header_link(kls, request):
        url = reverse('bazaar_home')

        return dict(link=url, text=_('Bazaar'))
    