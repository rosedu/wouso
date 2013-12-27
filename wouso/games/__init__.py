#import logging

#logging.basicConfig(filename='/home/wouso/sites/wouso.cs.pub.ro/next/wouso.log',level=logging.INFO,format='%(levelname)s:%(filename)s:%(funcName)s:%(lineno)d:%(message)s')

def get_games():
    import os
    res = []

    games_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))

    for g in os.listdir(games_dir):
        if os.path.exists(games_dir + '/' + g + '/urls.py'):
            res.append(g)
    return res
