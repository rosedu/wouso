import os

def get_themes():
    themes_dir = os.path.abspath(os.path.dirname(__file__) + '/../resources/static/themes/')
    themes = []

    for g in os.listdir(themes_dir):
        if os.path.exists(themes_dir + '/' + g + '/styles.css'):
            themes.append(g)
    return themes

# TODO: move scripts in this module to management commands.