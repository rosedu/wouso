from django.contrib.syndication.views import Feed
from wouso.games.qotd.models import Question

class LatestQuestionsFeed(Feed):
    title = "WoUSO question of the day"
    link = "/qotdfeed/"
    description = "WoUSO question of the day"

    def items(self):
        return Question.objects.order_by('-date')[:5]

    def item_title(self, item):
        return "WoUSO question for %s" % item.date

    def item_description(self, item):
        return item.text

    def item_link(self):
        return "/qotd/"

