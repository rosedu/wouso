# Credit to: http://stackoverflow.com/questions/2242909/django-user-impersonation-by-admin
from django import http

KEYWORD = "_as"

class ImpersonateMiddleware(object):
    def get_impersonation(self, request):
        if KEYWORD in request.GET:
            return request.GET[KEYWORD]
        if KEYWORD in request.session:
            return request.session[KEYWORD]
        return None

    @classmethod
    def set_impersonation(cls, request, player):
        request.session[KEYWORD] = player.id

    @classmethod
    def clear(cls, request):
        if KEYWORD in request.session:
            del request.session[KEYWORD]
            request.user.real_user = None

    def process_request(self, request):
        if not hasattr(request, 'user') or not hasattr(request, 'session'):
            return
        real_user = request.user
        impersonated_id = self.get_impersonation(request)
        if request.user.is_superuser and impersonated_id:
            from django.contrib.auth.models import User
            try:
                request.user = User.objects.get(id=int(impersonated_id))
            except ValueError:
                request.user = User.objects.get(username=impersonated_id)
            except User.DoesNotExist:
                request.user = real_user
            request.user.real_user = real_user

    def process_response(self, request, response):
        """ Handle redirects
        """
        if not hasattr(request, 'user') or not hasattr(request, 'session'):
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