from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from wouso.core.magic.models import Bazaar

class Command(BaseCommand):
    help = 'Wouso repetitive tasks (cron)'

    def handle(self, *args, **options):
        self.stdout.write('Magic management task...\n')
        Bazaar.management_task()