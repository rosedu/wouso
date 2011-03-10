from wouso.interface import logger, render_response

def homepage(request):
    """ First page shown """
    logger.debug('Everything is fine')

    return render_response('site_base.html', request)
