from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.core.management.commands.dumpdata import Command as DumpdataCommand
from optparse import make_option
from wouso.core.magic.utils import setup_magic
from wouso.core.scoring.sm import check_setup, setup_scoring
from wouso.core.user.utils import setup_user_groups


class Command(BaseCommand):
    args = '[--check-setup|--setup|--save|--load]'
    help = 'Wouso management tasks'
    option_list = DumpdataCommand.option_list + (
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
        make_option('--load',
            action='store',
            dest='load',
            default=False,
            help='Load game configuration.'
        ),
        make_option('--save',
            action='store',
            dest='save',
            default=False,
            help='Save game configuration to a file.'
        ),
        make_option('--reset',
            action='store_true',
            dest='reset',
            default=False,
            help='Reset scoring and artifacts'
        ),
    )

    def handle(self, *args, **options):
        save_load_labels = ['magic', 'scoring.coin', 'scoring.formula', 'config', 'pages']
        reset_labels = ['magic', 'scoring', 'config', 'pages']
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

        elif options['save']:
            c = DumpdataCommand()
            with open(options['save'], 'w') as fout:
                data = c.handle(*save_load_labels, **options)
                fout.write(data)
            self.stdout.write('Saved!\n')

        elif options['load']:
            call_command('loaddata', options['load'])
            self.stdout.write('Loaded!\n')

        elif options['reset']:
            call_command('sqlreset', *reset_labels)

        else:
            self.print_help('wousoctl', '')
