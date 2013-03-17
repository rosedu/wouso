from wouso.core.config.models import *
from wouso.core.user.models import PlayerGroup, Race
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
        default_group.choices = [('', '')] + [(unicode(g), str(g.id)) for g in PlayerGroup.objects.all()]

        default_race = ChoicesSetting.get('default_race')
        default_race.choices = [(unicode(g), str(g.id)) for g in Race.objects.all()]

        return [title, intro, theme, logo, hf, default_group, default_race, einfo]

class Switchboard(ConfigGroup):
    name = 'Disable features'

    def props(self):
        p = []
        for a in ('Qproposal', 'Top', 'Magic', 'Chat', 'Private-Chat', 'Bazaar', 'Bazaar-Exchange', 'Contactbox', 'Chat-Archive', 'Statistics',
                  'Challenge-Top', 'Top-Pyramid'):
            p.append(BoolSetting.get('disable-%s' % a))

        p.append(BoolSetting.get('disable_login'))
        p.append(BoolSetting.get('enable_header_autoreload'))
        p.append(BoolSetting.get('disable-challenge-random'))
        coin_tops = Setting.get('top-coins')
        coin_tops.help_text = 'Coin names, comma separated'
        #coin_tops.choices = [(g.name, unicode(g)) for g in Coin.objects.all()]
        p.append(coin_tops)

        return p

class GamesSwitchboard(ConfigGroup):
    name = 'Disable games'

    def props(self):
        p = []
        for g in get_games():
            p.append(BoolSetting.get('disable-%s' % g.__name__))

        return p
