# Credit to: http://stackoverflow.com/questions/2242909/django-user-impersonation-by-admin
from django import http

KEYWORD = "_as"

class ImpersonateMiddleware(object):
    def process_request(self, request):
        if not hasattr(request, 'user'):
            return
        if request.user.is_superuser and KEYWORD in request.GET:
            from django.contrib.auth.models import User
            real_user = request.user
            try:
                request.user = User.objects.get(id=int(request.GET[KEYWORD]))
            except ValueError:
                request.user = User.objects.get(username=request.GET[KEYWORD])
            except User.DoesNotExist:
                request.user = real_user

    def process_response(self, request, response):
        if not hasattr(request, 'user'):
            return response
        if request.user.is_superuser and KEYWORD in request.GET:
            if isinstance(response, http.HttpResponseRedirect):
                location = response["Location"]
                if "?" in location:
                    location += "&"
                else:
                    location += "?"
                location += "%s=%s" % (KEYWORD, request.GET[KEYWORD])
                response["Location"] = location
        return response