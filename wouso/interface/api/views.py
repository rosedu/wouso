__author__ = 'alex'
from django.shortcuts import render_to_response
from django.template import RequestContext
from piston import forms
from piston.models import Consumer
from wouso.core.decorators import api_enabled_required


@api_enabled_required
def request_token_ready(request, token=None):
    """
    It shows an easy-to-copy verifier, needed by consumer in order
    to receive its access token.

    It isn't used, if a callback URL is specified in the authorize call.
    """
    error = request.GET.get('error', '')
    ctx = RequestContext(request, {
        'error' : error,
        'token' : token,
    })
    return render_to_response(
        'piston/request_token_ready.html',
        context_instance = ctx
    )

@api_enabled_required
def oauth_auth_view(request, token, callback, params):
    """ This shows the: "Do you want to authorize X on Y?" message

    It contains the token and callback (next url).

    It is called by: piston.authentication.oauth_user_auth,
    and it doesn't have an associated URL.
    """
    form = forms.OAuthAuthenticationForm(initial={
        'oauth_token': token.key,
        'oauth_callback': token.get_callback_url() or callback,
        })

    consumer_key = request.GET.get('oauth_consumer_key', '')
    consumer = Consumer.objects.get(key=consumer_key)

    return render_to_response('piston/authorize_token.html',
            { 'form': form, 'consumer': consumer }, RequestContext(request))
