from wouso.core.config.models import *
from wouso.utils import get_themes
from wouso.core.game import get_games

class ConfigGroup:
    name = 'Customizations'

class Customization(ConfigGroup):
    def props(self):
        title = HTMLSetting.get('title')
        intro = HTMLSetting.get('intro')
        hf = HTMLSetting.get('hidden_footer')
        theme = ChoicesSetting.get('theme')
        theme.choices = [(t,t) for t in get_themes()]
        logo = Setting.get('logo')

        return [title, intro, theme, logo, hf]

class Switchboard(ConfigGroup):
    name = 'Disable features'

    def props(self):
        p = []
        for a in ('Qproposal', 'Top', 'Magic', 'Chat'):
            p.append(BoolSetting.get('disable-%s' % a))

        return p

class GamesSwitchboard(ConfigGroup):
    name = 'Disable games'

    def props(self):
        p = []
        for g in get_games():
            p.append(BoolSetting.get('disable-%s' % g.__name__))

        return p
