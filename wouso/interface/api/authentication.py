from django.contrib.auth.models import User

__author__ = 'alex'

# This code is copied from http://yml-blog.blogspot.com/2009/10/django-piston-authentication-against.html
class SessionAuthentication(object):
    """
    Session-based authentication
    """
    def is_authenticated(self, request):
        """
        This method call the `is_authenticated` method of django
        User in django.contrib.auth.models.

        `is_authenticated`: Will be called when checking for
        authentication. It returns True if the user is authenticated
        False otherwise.
        """
        self.request = request
        return request.user.is_authenticated()

    #TODO: A real challenge here would be nice
    def challenge(self):
        import piston
        return piston.authentication.OAuthAuthentication().challenge()

class SimpleAuthentication(SessionAuthentication):

    def is_authenticated(self, request):
        user = request.GET.get('user')

        if not user:
            return False

        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:
            return False

        request.user = user
        return True