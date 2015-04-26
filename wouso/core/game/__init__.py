from django.db.models import get_models
from models import Game

def get_games():
    """Get a list of available games. This needs to be updated each time
    a game is added."""
    from wouso.games.challenge.models import ChallengeGame
    from wouso.games.grandchallenge.models import GrandChallengeGame
    from wouso.games.qotd.models import QotdGame
    from wouso.games.quest.models import QuestGame
    from wouso.games.quiz.models import QuizGame
    from wouso.games.specialchallenge.models import SpecialChallengeGame
    from wouso.games.specialquest.models import SpecialQuestGame
    from wouso.games.teamquest.models import TeamQuestGame
    from wouso.games.workshop.models import WorkshopGame

    return [ChallengeGame, GrandChallengeGame, QotdGame, QuestGame,
            QuizGame, SpecialChallengeGame, SpecialQuestGame, TeamQuestGame,
            WorkshopGame]
