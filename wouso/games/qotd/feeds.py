from django.contrib.syndication.views import Feed
from wouso.core.qpool.models import Question


class LatestQuestionsFeed(Feed):
    title = "WoUSO Question of the Day"
    link = "/qotdfeed/"
    description = "WoUSO Question of the Day"

    def items(self):
        #return Question.objects.order_by('-date')[:5]
        return Question.objects.all()[:5]

    def item_title(self, item):
        return "WoUSO question for %s" % item.schedule

    def item_description(self, item):
        return item.__unicode__()

    def item_link(self):
        return "/qotd/"

