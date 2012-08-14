from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from wouso.core.app import App
from wouso.core.magic.models import PlayerSpellDue

class Bazaar(App):
    @classmethod
    def get_header_link(kls, request):
        url = reverse('bazaar_home')
        player = request.user.get_profile() if request.user.is_authenticated() else None
        if player:
            count = PlayerSpellDue.objects.filter(player=player, seen=False).count()
        else:
            count = 0

        return dict(link=url, text=_('Magic'), count=count)
    