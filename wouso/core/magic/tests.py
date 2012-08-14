import unittest
from django.db import IntegrityError
from models import *

class ArtifactTestCase(unittest.TestCase):

    def testArtifactCreateUnique(self):
        """ Test if we cannot create two artifacts with the same name in a group
        """
        group = ArtifactGroup.objects.create(name='gigi')

        a1 = Artifact.objects.create(group=group, name='name')

        self.assertRaises(IntegrityError, Artifact.objects.create, group=group, name='name')
