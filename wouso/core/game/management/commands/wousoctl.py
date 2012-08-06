from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from wouso.core.magic.utils import setup_magic
from wouso.core.scoring.sm import check_setup, setup_scoring
from wouso.core.user.utils import setup_user_groups


class Command(BaseCommand):
    args = '[--check-setup|--setup]'
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

            self.stdout.write('Setting up scoring...')
            setup_scoring()
            self.stdout.write('\n')
            self.stdout.write('Setting up user groups...')
            setup_user_groups()
            self.stdout.write('\n')
            self.stdout.write('Setting up magic...')
            setup_magic()
            self.stdout.write('\n')
            self.stdout.write('Done.\n')

        else:
            self.print_help('wousoctl', '')
