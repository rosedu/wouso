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
        theme.choices = [(t, t) for t in get_themes()]
        logo = Setting.get('logo')

        default_group = ChoicesSetting.get('default_group')
        default_group.choices = [('', '')] + [(unicode(g), str(g.id)) for g in PlayerGroup.objects.all()]

        default_race = ChoicesSetting.get('default_race')
        default_race.choices = [(unicode(g), str(g.id)) for g in Race.objects.all()]

        question_number_of_answers = IntegerSetting.get('question_number_of_answers')

        level_limits = IntegerListSetting.get('level_limits')

        return [title, intro, theme, logo, hf, default_group, default_race, einfo, question_number_of_answers,
                level_limits]


class Switchboard(ConfigGroup):
    name = 'Disable features'

    @staticmethod
    def props():
        p = []
        for a in ('Qproposal', 'Top', 'Magic', 'Bazaar', 'Bazaar-Exchange',
                  'Statistics', 'Challenge-Top', 'Top-Pyramid', 'Lesson',
                  'MessageApp', 'File'):
            p.append(BoolSetting.get('disable-%s' % a))

        login = BoolSetting.get('login')
        login.help_text = 'Staff only login?'
        p.append(login)
        p.append(BoolSetting.get('header_autoreload'))
        p.append(BoolSetting.get('random_challenge'))
        coin_tops = Setting.get('top-coins')
        coin_tops.help_text = 'Coin names, comma separated'
        p.append(coin_tops)

        return p


class GamesSwitchboard(ConfigGroup):
    name = 'Games'

    def props(self):
        p = []
        for g in get_games():
            p.append(BoolSetting.get('disable-%s' % g.__name__))

        return p
