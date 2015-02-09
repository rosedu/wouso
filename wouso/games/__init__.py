def get_games():
    import os
    res = []

    games_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))

    for g in os.listdir(games_dir):
        if os.path.exists(games_dir + '/' + g + '/urls.py'):
            res.append(g)
    return res
