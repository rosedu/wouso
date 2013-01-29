from django.http import HttpResponseRedirect
HttpResponseRedirect.allowed_schemes = ['https', 'http', 'ftp', 'web+wouso']