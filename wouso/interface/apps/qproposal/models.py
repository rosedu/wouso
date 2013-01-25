from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.translation import ugettext as _
from wouso.core.common import App

class Qproposal(App):
    @classmethod
    def get_footer_link(kls, request):
        try:
            url = reverse('propose')
            return '<a href="%s">' % url + _('Propose question') + '</a>'
        except NoReverseMatch:
            return '-'
