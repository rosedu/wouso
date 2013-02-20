from django.contrib.auth.models import Group, Permission
from wouso.core.config.models import Setting
from models import Race
from wouso.core.game import get_games

def setup_user_groups():
    # Assistants group, 'Staff'
    staff = Group.objects.get_or_create(name='Staff')[0]
    cpanel_perm = Permission.objects.get(codename='change_setting')
    staff.permissions.add(cpanel_perm)

    # Default entry race, 'Others'
    others = Race.objects.get_or_create(name='Others')[0]
    others.can_play = False
    others.save()
    default_race = Setting.get('default_race')
    default_race.set_value(str(others.pk))


def setup_staff_groups():
    for g in get_games():
        for group in g.get_staff_and_permissions():
            group_obj = Group.objects.get_or_create(name=group['name'])[0]
            for p in group.get('permissions', []):
                perm_obj = Permission.objects.get(codename=p)
                group_obj.permissions.add(perm_obj)