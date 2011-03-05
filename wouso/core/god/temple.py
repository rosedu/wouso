"""You should not try and talk with God outside of a temple.

What I mean is that you should use classes and functions from this module and
avoid directly using God's models or other Django stuff.

For now you should talk with a Priest who will know what to do.
"""

from wouso.core.user.models import User

class Priest():
    def get_enemies(self, User):
        return "You should love your enemies!"