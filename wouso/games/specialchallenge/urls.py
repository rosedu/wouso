from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='specialchallenge_index'),
    url(r'^create/$', CreateChallenge.as_view(), name='specialchallenge_create'),
    url(r'^challenge/(?P<pk>\d+)/$', ChallengeView.as_view(), name='specialchallenge_challenge'),
    url(r'^challenge/(?P<pk>\d+)/configure/$', ConfigureChallenge.as_view(), name='specialchallenge_configure'),
    url(r'^challenge/(?P<pk>\d+)/launch/$', ChallengeLaunch.as_view(), name='specialchallenge_launch'),
    url(r'^challenge/(?P<challenge>\d+)/add/$', ChallengeQuestionAdd.as_view(), name='specialchallenge_add_question'),
    url(r'^challenge/(?P<challenge>\d+)/edit/(?P<pk>\d+)/$', ChallengeQuestionEdit.as_view(), name='specialchallenge_edit_question'),
    url(r'^challenge/(?P<challenge>\d+)/del/(?P<pk>\d+)/$', ChallengeQuestionDelete.as_view(), name='specialchallenge_del_question'),
)
