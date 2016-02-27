from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from wouso.core.game import get_games
from wouso.core.config.models import Setting


class Command(BaseCommand):
    help = 'Wouso repetitive tasks (cron)'

    def handle(self, *args, **options):
        self.stdout.write('Starting at: %s\n' % datetime.now())

        # Now handle other apps
        from wouso.interface.apps import get_apps
        apps = get_apps()

        for a in apps:
            if a.management_task:
                self.stdout.write('%s ...\n' % a.name())
                a.management_task(stdout=self.stdout)

        # Now handle games
        for g in get_games():
            if g.management_task:
                self.stdout.write('%s ...\n' % g.name())
                g.management_task(stdout=self.stdout)

        now = datetime.now()
        Setting.get('wousocron_lastrun').set_value('%s' % now)
        self.stdout.write('Finished at: %s\n' % now)
