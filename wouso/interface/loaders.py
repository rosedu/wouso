import os.path
from django.conf import settings
from django.template.loader import BaseLoader, TemplateDoesNotExist
from wouso.core.config.models import Setting

class Loader(BaseLoader):
    """ Theme template loader: the selected theme can override
    templates
    """
    is_usable = True

    def get_theme_dir(self):
        """ Note (AE): I'm unhappy with this approach, since a Setting.get
        call is done for every request. THIS must be cached somehow
        """
        theme = Setting.get('theme').value
        return os.path.join(settings.THEMES_ROOT, theme, 'templates')

    def load_template_source(self, template_name, template_dirs=None):
        filepath = os.path.join(self.get_theme_dir(), template_name)
        if filepath:
            try:
                file = open(filepath)
                try:
                    return (file.read().decode(settings.FILE_CHARSET), filepath)
                finally:
                    file.close()
            except IOError:
                pass
        raise TemplateDoesNotExist(template_name)