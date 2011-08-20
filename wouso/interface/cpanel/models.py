from wouso.core.config.models import *

class ConfigGroup:
    pass

class Customization(ConfigGroup):
    def props(self):
        title = HTMLSetting.get('title')
        intro = HTMLSetting.get('intro')
        return [title, intro]
