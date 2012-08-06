from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from wouso.core.scoring.sm import check_setup, setup_scoring


class Command(BaseCommand):
    args = '[--check-setup]'
    help = 'Wouso management tasks'
    option_list = BaseCommand.option_list + (
        make_option('--check-setup',
            action='store_true',
            dest='check_setup',
            default=False,
            help='Check the current instance for scoring, artifacts and other running requirements.'
        ),
        make_option('--setup',
            action='store_true',
            dest='setup',
            default=False,
            help='Setup the current instance, including a syncdb.'
        ),
    )

    def handle(self, *args, **options):
        if options['check_setup']:
            ok = True
            # Check scoring
            if not check_setup():
                self.stdout.write('FAIL: Scoring module not setup.')
                ok = False

            if ok:
                self.stdout.write('OK.\n')

        elif options['setup']:
            call_command('syncdb')

            setup_scoring()
            self.stdout.write('Done.\n')