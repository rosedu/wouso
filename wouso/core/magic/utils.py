from wouso.core.magic.models import ArtifactGroup


def setup_magic():
    # Default artifact group
    default_group = ArtifactGroup.objects.get_or_create(name='Default')[0]
