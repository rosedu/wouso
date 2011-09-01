from wouso.core.config.models import *
from wouso.utils import get_themes

class ConfigGroup:
    pass

class Customization(ConfigGroup):
    def props(self):
        title = HTMLSetting.get('title')
        intro = HTMLSetting.get('intro')
        theme = ChoicesSetting.get('theme')
        theme.choices = [(t,t) for t in get_themes()]
        logo = Setting.get('logo')

        return [title, intro, theme, logo]
