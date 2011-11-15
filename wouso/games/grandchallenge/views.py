# Create your views here.

@login_required
def gchalls(request):
    gchalls = GrandChallenge.objects.all()
    return render_to_response('cpanel/lastchalls.html',
                            {'last30': gchalls},
                            context_instance=RequestContext(request))
