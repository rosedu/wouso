from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from wouso.core.app import App

class Qproposal(App):
    @classmethod
    def get_footer_link(kls, request):
        url = reverse('propose')

        return '<a href="%s">' % url + _('Propose question') + '</a>'
  