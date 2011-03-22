from wouso.core.game import get_games

def sidebar(request):
    """ For each registered game, get a widget to be displayed in sidebar 
    @remark This design needs to be analysed.
    @todo ordering, probably done by god
    
    Returns a 'sidebar' list containing html boxes.
    """
    
    sidebar = []
    for game in get_games():
        w = game.get_sidebar_widget(request)
        if w:
            sidebar.append(w)
    
    return {'sidebar': sidebar}
