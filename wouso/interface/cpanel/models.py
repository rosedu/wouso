from wouso.core.config.models import *
from wouso.core.user.models import PlayerGroup
from wouso.utils import get_themes
from wouso.core.game import get_games

class ConfigGroup:
    name = 'Customizations'

class Customization(ConfigGroup):
    def props(self):
        title = HTMLSetting.get('title')
        intro = HTMLSetting.get('intro')
        einfo = HTMLSetting.get('extrainfo')
        hf = HTMLSetting.get('hidden_footer')
        theme = ChoicesSetting.get('theme')
        theme.choices = [(t,t) for t in get_themes()]
        logo = Setting.get('logo')

        default_group = ChoicesSetting.get('default_group')
        default_group.choices = [(unicode(g), str(g.id)) for g in PlayerGroup.objects.all()]

        # TODO: default Race
        #default_series = ChoicesSetting.get('default_series')
        #default_series.choices = [(unicode(g), str(g.id)) for g in PlayerGroup.objects.filter(gclass=1)]

        return [title, intro, theme, logo, hf, default_group, default_series, einfo]

class Switchboard(ConfigGroup):
    name = 'Disable features'

    def props(self):
        p = []
        for a in ('Qproposal', 'Top', 'Magic', 'Chat', 'Bazaar-Exchange'):
            p.append(BoolSetting.get('disable-%s' % a))

        p.append(BoolSetting.get('disable_login'))
        p.append(BoolSetting.get('disable_header_autoreload'))

        return p

class GamesSwitchboard(ConfigGroup):
    name = 'Disable games'

    def props(self):
        p = []
        for g in get_games():
            p.append(BoolSetting.get('disable-%s' % g.__name__))

        return p
