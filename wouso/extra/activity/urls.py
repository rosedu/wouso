from django.conf.urls.defaults import patterns

urlpatterns = patterns('wouso.extra.activity.views',
    (r'^public/$', 'public'),
    (r'^private/$', 'private'),
)

urlpatterns += patterns('', 
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/activity/public/'})
)