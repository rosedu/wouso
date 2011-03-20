from django.contrib import admin
from models import Quest

# should filter questions:
# return get_questions_with_tags('quest', 'quest-%d' % self.id, 'all')
admin.site.register(Quest)
