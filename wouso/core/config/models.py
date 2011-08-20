from django.db import models

class Setting(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    value = models.TextField(default='', null=True, blank=True)

    def set_value(self, v):
        self.value = v
        self.save()

    def get_value(self):
        return self.value

    def form(self):
        return '<label for="%s">%s</label><textarea name="%s" id="%s">%s</textarea>' \
                    % (self.name, self.name, self.name, self.name, self.value)

    @classmethod
    def get(kls, name):
        obj, new = kls.objects.get_or_create(name=name)
        return obj

class HTMLSetting(Setting):
    class Meta:
        proxy = True

class BoolSetting(Setting):
    class Meta:
        proxy = True

    def set_value(self, b):
        self.value = 'True' if b else 'False'

    def get_value(self):
        return (self.value == 'True')

    def form(self):
        return '<label for="%s">%s</label><input type="checkbox" name="%s" id="%s" %s />' \
                    % (self.name, self.name, self.name, self.name, 'checked' if self.get_value() else '')

class ChoicesSetting(Setting):
    class Meta:
        proxy = True

    choices = []

    def form(self):
        html = '<label for="%s">%s</label><select id="%s" name="%s">' % (self.name, self.name, self.name, self.name)
        for n,v in self.choices:
            html += '<option value="%s" %s>%s</option>' % (v, 'selected' if self.value == v else '', n)
        html += '</select>'
        return html
    
