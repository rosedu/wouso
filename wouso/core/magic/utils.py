from wouso.core.magic.models import ArtifactGroup

def setup_magic():
    # Default artifact group
    default_group = ArtifactGroup.objects.get_or_create(name='Default')[0]
    # Add a group for spells
    spells_group = ArtifactGroup.objects.get_or_create(name='Spells')[0]