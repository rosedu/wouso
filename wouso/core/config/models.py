from django.db import models
from django.core.cache import cache


class Setting(models.Model):
    """ Generic configuration (name, value) pair definition, stored in db """
    name = models.CharField(max_length=100, primary_key=True)
    value = models.TextField(default='', null=True, blank=True)

    @classmethod
    def _cache_key(cls, name):
        return '%s-' % cls.__name__ + name

    def set_value(self, v):
        """ value setter, overridden by subclasses """
        self.value = v
        self.save()

    def get_value(self):
        """ value getter, overridden by subclasses """
        return self.value

    def form(self):
        """ Get HTML form input and label. """
        html = """
                <div class="form-group">
                <label for="%s" class="col-sm-2 control-label">%s</label>
                    <div class="col-sm-10">
                        <textarea name="%s" id="%s" class="form-control">%s</textarea>
                    """ % (self.name, self.title, self.name, self.name, self.value)
        if hasattr(self, 'help_text'):
            html += '<br/><em>' + self.help_text + '</em>'

        html += "</div></div>"
        return html

    @classmethod
    def get(cls, name):
        """ Get or create a Setting with the name name """
        cache_key = cls._cache_key(name)
        if cache_key in cache:
            return cache.get(cache_key)
        obj, new = cls.objects.get_or_create(name=name)
        cache.set(cache_key, obj)
        return obj

    def save(self, **kwargs):
        cache_key = self.__class__._cache_key(self.name)
        cache.delete(cache_key)
        # Also flush generic
        cache_key = Setting._cache_key(self.name)
        cache.delete(cache_key)
        return super(Setting, self).save(**kwargs)

    @property
    def title(self):
        """ Capitalize name to create a setting title for display """
        if self.name.startswith('disable-'):
            # Remove 'disable-', capitalize, remove '-' and add a space before
            # game
            # Ex: challengegame -> Challenge game
            return self.name[8:].capitalize().replace('game', ' game').replace('-', ' ')

        return self.name.capitalize().replace('_', ' ')

    def __unicode__(self):
        return self.name


class HTMLSetting(Setting):
    """ Setting storing a generic text or HTML """
    class Meta:
        proxy = True


class BoolSetting(Setting):
    """ Setting storing boolean values (as string True/False) """
    class Meta:
        proxy = True

    def set_value(self, b):
        if isinstance(b, bool):
            self.value = 'True' if b else 'False'
        else:
            self.value = not b
        self.save()

    def get_value(self):
        return self.value == 'True'

    def form(self):
        return """
        <div class="form-group">
            <label for"%s" class="col-sm-2 control-label">%s<span class="help-block">%s</span></label>
            <div class="col-sm-10">
                <div class="checkbox">
                    <input type="checkbox" name="%s" id="%s" %s value="True"></input>
                </div>
            </div>
        </div>
        """ % (self.name, self.title, self.help_text if hasattr(self, 'help_text') else '',
               self.name, self.name, '' if self.get_value() else 'checked')


class ChoicesSetting(Setting):
    """ Setting storing string values, but having a choices list of tuple
    (value, text) choices
    """
    class Meta:
        proxy = True

    choices = []

    def form(self):

        html = """
        <div class="form-group">
            <label for="%s" class="col-sm-2 control-label">%s</label>
            <div class="col-sm-10">
                <select id="%s" name="%s" class="form-control">
        """ % (self.name, self.title, self.name, self.name)

        for n, v in self.choices:
            html += '<option value="%s" %s>%s</option>' % (v, 'selected' if self.value == v else '', n)
        html += '</select></div></div>'
        return html


class IntegerSetting(Setting):
    def set_value(self, v):
        self.value = unicode(v)
        self.save()

    def get_value(self):
        try:
            return int(self.value)
        except ValueError:
            return 0


class IntegerListSetting(Setting):
    """ Setting storing integer values as strings """

    def set_value(self, v):
        self.value = unicode(v)
        self.save()

    def get_value(self):
        l = []
        for n in self.value.split():
            try:
                l.append(int(n))
            except ValueError:
                l.append(0)
        return l

    def form(self):
        return ''
