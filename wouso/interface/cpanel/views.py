from django.contrib.auth.decorators import login_required
from django.http import Http404
from wouso.core.config.models import Setting
from wouso.interface import render_response
from models import Customization

@login_required
def dashboard(request):
    customization = Customization()

    if request.method == "POST":
        for s in customization.props():
            val = request.POST.get(s.name, '')
            s.set_value(val)

    return render_response('cpanel/index.html', request, \
            {'settings': customization}
    )

